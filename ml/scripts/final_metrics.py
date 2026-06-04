"""Generate final ML metrics report across all evaluation splits (task #final).

Splits evaluated:
  val        — author-provided validation set (standard in-distribution)
  test       — author-provided test set (standard in-distribution)
  ood_iconic — one iconic/catalog image per fine class; public OOD split
               (clean white-bg images vs. natural in-store training photos)
  own_mini   — personal mini-set (own_test_set/); evaluated separately because
               class coverage is incomplete — do NOT compare raw accuracy here

Output directory: ml/final_metrics/  (or --out-dir override)
  summary.json              — compact numbers for all splits
  summary_report.md         — human-readable formatted report
  {split}_metrics.json      — full metrics dict (top1/top3/cm/per-class/…)
  {split}_per_class.csv     — per-class precision/recall/f1/support
  {split}_confusion.png     — row-normalised confusion matrix heatmap
  threshold_curves.png      — coverage vs selective-accuracy for all splits

Usage:
    python ml/scripts/final_metrics.py \\
        --artifact ml/artifacts/resnet50_v1_20260519.pt

    # Use efficientnet instead:
    python ml/scripts/final_metrics.py \\
        --artifact ml/artifacts/efficientnet_b0_v1_20260519.pt

    # Skip own_mini (e.g. in CI):
    python ml/scripts/final_metrics.py --artifact ... --skip-own-mini
"""
from __future__ import annotations

import argparse
import csv as csv_mod
import json
import sys
import textwrap
from pathlib import Path
from typing import Optional

import numpy as np
import torch
from torch.utils.data import DataLoader

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "ml"))

from src.artifact import (  # noqa: E402
    build_eval_transform_from_artifact,
    build_model_from_artifact,
    class_names_from_artifact,
    load_artifact,
)
from src.evaluate import (  # noqa: E402
    compute_metrics,
    plot_confusion_matrix,
    predict_all,
    save_metrics,
    save_per_class_csv,
)
from src.ood_dataset import IconicOodDataset  # noqa: E402
from src.own_dataset import OwnMiniDataset  # noqa: E402
from src.threshold import compute_threshold_curve, recommend_threshold  # noqa: E402
from src.train import pick_device  # noqa: E402

DEFAULT_DATASET_ROOT = REPO_ROOT / "ml" / "dataset" / "GroceryStoreDataset" / "dataset"
DEFAULT_OWN_ROOT = REPO_ROOT / "ml" / "own_test_set"
DEFAULT_OUT_DIR = REPO_ROOT / "ml" / "final_metrics"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Generate final ML metrics for all evaluation splits."
    )
    p.add_argument(
        "--artifact", type=Path,
        default=REPO_ROOT / "ml" / "artifacts" / "resnet50_v1_20260519.pt",
        help="Path to .pt artifact (default: resnet50_v1_20260519.pt)",
    )
    p.add_argument("--dataset-root", type=Path, default=DEFAULT_DATASET_ROOT)
    p.add_argument("--own-root", type=Path, default=DEFAULT_OWN_ROOT)
    p.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    p.add_argument("--batch-size", type=int, default=64)
    p.add_argument("--num-workers", type=int, default=0)
    p.add_argument(
        "--skip-own-mini", action="store_true",
        help="Skip own_mini split (use in CI or when own_test_set/ is empty)",
    )
    return p.parse_args()


# ──────────────────────────────────────────────────────── threshold helpers ──

def _softmax(x: np.ndarray) -> np.ndarray:
    x = x - x.max(axis=1, keepdims=True)
    e = np.exp(x)
    return e / e.sum(axis=1, keepdims=True)


def _plot_threshold_curves(
    curves: dict[str, list[dict]],
    chosen: dict[str, dict],
    out_path: Path,
) -> None:
    import matplotlib.pyplot as plt
    import matplotlib.cm as cm

    split_names = list(curves.keys())
    colors = cm.tab10.colors  # type: ignore[attr-defined]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    for i, split in enumerate(split_names):
        curve = curves[split]
        thresholds = [r["threshold"] for r in curve]
        coverage = [r["coverage"] for r in curve]
        sel_acc = [r["selective_accuracy"] for r in curve]
        col = colors[i % len(colors)]

        ax1.plot(thresholds, coverage, label=split, color=col)
        ax2.plot(thresholds, sel_acc, label=split, color=col)

        if split in chosen:
            t = chosen[split]["threshold"]
            ax1.axvline(t, color=col, linestyle="--", alpha=0.4)
            ax2.axvline(t, color=col, linestyle="--", alpha=0.4)

    ax1.set_xlabel("threshold")
    ax1.set_ylabel("coverage")
    ax1.set_ylim(0, 1.05)
    ax1.set_title("Coverage vs threshold")
    ax1.legend()

    ax2.set_xlabel("threshold")
    ax2.set_ylabel("selective accuracy")
    ax2.set_ylim(0, 1.05)
    ax2.axhline(0.95, color="gray", linestyle=":", linewidth=0.8, alpha=0.7)
    ax2.set_title("Selective accuracy vs threshold\n(dashed = 0.95 target)")
    ax2.legend()

    fig.tight_layout()
    fig.savefig(out_path, dpi=120, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {out_path.name}")


# ─────────────────────────────────────────────────────── markdown report ────

def _fmt_pct(v: float) -> str:
    return f"{v * 100:.2f}%"


def _build_markdown_report(
    artifact_name: str,
    threshold_json: dict | None,
    split_results: dict[str, dict],
    own_mini_note: str,
) -> str:
    lines: list[str] = []
    lines.append(f"# Final ML Metrics\n")
    lines.append(f"**Model:** `{artifact_name}`\n")

    # Threshold summary
    if threshold_json:
        ch = threshold_json["chosen"]
        lines.append("## Threshold (tuned on val)")
        lines.append(
            f"| threshold | coverage | selective accuracy | target met |"
        )
        lines.append("|-----------|----------|--------------------|------------|")
        lines.append(
            f"| {ch['threshold']:.2f} | {_fmt_pct(ch['coverage'])} "
            f"| {_fmt_pct(ch['selective_accuracy'])} | {ch['target_met']} |"
        )
        lines.append("")

    # Top-level summary table
    lines.append("## Summary table\n")
    lines.append("| split | n | top-1 | top-3 | macro-F1 (all) | macro-F1 (present) | weighted-F1 |")
    lines.append("|-------|---|-------|-------|----------------|---------------------|-------------|")
    for split, m in split_results.items():
        note = " ⚠️" if split == "own_mini" else ""
        lines.append(
            f"| {split}{note} | {m['n_samples']} "
            f"| {_fmt_pct(m['top1'])} "
            f"| {_fmt_pct(m['top3'])} "
            f"| {_fmt_pct(m['macro_f1_all_classes'])} "
            f"| {_fmt_pct(m['macro_f1_present_only'])} "
            f"| {_fmt_pct(m['weighted_f1'])} |"
        )
    lines.append("")
    if own_mini_note:
        lines.append(f"> ⚠️ **own_mini**: {own_mini_note}\n")

    # Per-split details
    for split, m in split_results.items():
        lines.append(f"## Split: `{split}`\n")
        lines.append(f"- Samples: **{m['n_samples']}**")
        lines.append(f"- Classes present: {m['n_classes_present']} / {m['n_classes_total']}")
        lines.append(f"- Top-1 accuracy: **{_fmt_pct(m['top1'])}**")
        lines.append(f"- Top-3 accuracy: **{_fmt_pct(m['top3'])}**")
        lines.append(f"- Macro-F1 (all {m['n_classes_total']} classes): {_fmt_pct(m['macro_f1_all_classes'])}")
        lines.append(f"- Macro-F1 (present only): {_fmt_pct(m['macro_f1_present_only'])}")
        lines.append(f"- Weighted-F1: {_fmt_pct(m['weighted_f1'])}")
        if m.get("classes_missing_names"):
            lines.append(f"- Missing classes: {', '.join(m['classes_missing_names'])}")
        lines.append("")

        # threshold
        tc = m.get("threshold_chosen")
        if tc:
            lines.append(
                f"**Threshold analysis** (coverage/selective-accuracy at artifact threshold "
                f"t={tc.get('threshold', '?'):.2f}):\n"
                f"- Coverage: {_fmt_pct(tc['coverage'])} "
                f"({tc['n_covered']}/{tc['n_covered'] + tc['n_rejected']} samples)\n"
                f"- Selective accuracy: {_fmt_pct(tc['selective_accuracy'])}\n"
            )

        # Top-10 worst classes by recall
        per_class = sorted(m["per_class"], key=lambda r: r["recall"])
        worst = [r for r in per_class if r["support"] > 0][:10]
        if worst:
            lines.append("**10 lowest-recall classes:**\n")
            lines.append("| class | precision | recall | F1 | support |")
            lines.append("|-------|-----------|--------|----|---------|")
            for r in worst:
                lines.append(
                    f"| {r['class_name']} "
                    f"| {r['precision']:.3f} "
                    f"| {r['recall']:.3f} "
                    f"| {r['f1']:.3f} "
                    f"| {r['support']} |"
                )
            lines.append("")

    return "\n".join(lines)


# ──────────────────────────────────────────────────────────────── main ───────

def main() -> None:
    args = parse_args()
    out_dir = args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    # ── load artifact ────────────────────────────────────────────────────────
    if not args.artifact.exists():
        raise FileNotFoundError(f"Artifact not found: {args.artifact}")
    print(f"\nLoading artifact: {args.artifact.name}")
    artifact = load_artifact(args.artifact)
    print(f"  backbone={artifact['backbone']}, model_version={artifact['model_version']}")

    device = pick_device()
    print(f"  device={device}")
    model = build_model_from_artifact(artifact).to(device).eval()
    transform = build_eval_transform_from_artifact(artifact)
    class_names = class_names_from_artifact(artifact)

    # load threshold JSON if present
    stem = args.artifact.with_suffix("")
    threshold_json_path = stem.with_name(stem.name + "_threshold.json")
    threshold_json: dict | None = None
    artifact_threshold: Optional[float] = artifact.get("threshold")
    if threshold_json_path.exists():
        threshold_json = json.loads(threshold_json_path.read_text())
        print(f"  threshold={artifact_threshold} (from artifact), "
              f"threshold_json loaded from {threshold_json_path.name}")
    else:
        print(f"  threshold={artifact_threshold} (no threshold JSON found)")

    # ── evaluate splits ──────────────────────────────────────────────────────
    GSD = __import__("src.dataset", fromlist=["GroceryStoreDataset"]).GroceryStoreDataset

    splits_to_run = [
        ("val", lambda: GSD(args.dataset_root, "val", transform=transform)),
        ("test", lambda: GSD(args.dataset_root, "test", transform=transform)),
        ("ood_iconic", lambda: IconicOodDataset(args.dataset_root, transform=transform)),
    ]
    if not args.skip_own_mini:
        splits_to_run.append(
            ("own_mini", lambda: OwnMiniDataset(
                args.own_root, args.dataset_root,
                transform=transform, allow_empty=False,
            ))
        )

    split_results: dict[str, dict] = {}
    all_curves: dict[str, list[dict]] = {}
    all_chosen: dict[str, dict] = {}

    for split_name, build_ds in splits_to_run:
        print(f"\n=== {split_name} ===")
        try:
            ds = build_ds()
        except Exception as exc:
            print(f"  SKIP — could not build dataset: {exc}")
            continue

        loader = DataLoader(
            ds,
            batch_size=args.batch_size,
            shuffle=False,
            num_workers=args.num_workers,
            pin_memory=(device.type == "cuda"),
        )

        logits, labels = predict_all(model, loader, device)
        metrics = compute_metrics(logits, labels, class_names)

        # threshold curve for this split
        curve = compute_threshold_curve(logits, labels)
        chosen = recommend_threshold(curve)
        all_curves[split_name] = curve
        all_chosen[split_name] = chosen

        # attach threshold-at-artifact-threshold info to metrics
        if artifact_threshold is not None:
            # find the row in curve closest to artifact threshold
            closest = min(curve, key=lambda r: abs(r["threshold"] - artifact_threshold))
            metrics["threshold_chosen"] = closest
        else:
            metrics["threshold_chosen"] = chosen  # best available

        print(
            f"  top1={metrics['top1']:.4f}  top3={metrics['top3']:.4f}  "
            f"macro_f1={metrics['macro_f1_all_classes']:.4f}  "
            f"(present_only={metrics['macro_f1_present_only']:.4f})  "
            f"n={metrics['n_samples']}"
        )
        if metrics["classes_missing_names"]:
            print(f"  missing: {metrics['classes_missing_names']}")

        # save per-split artifacts
        save_metrics(metrics, out_dir / f"{split_name}_metrics.json")
        save_per_class_csv(metrics, out_dir / f"{split_name}_per_class.csv")
        plot_confusion_matrix(
            metrics, class_names,
            out_dir / f"{split_name}_confusion.png",
        )

        # per-split threshold curve CSV
        curve_csv = out_dir / f"{split_name}_threshold_curve.csv"
        with curve_csv.open("w", newline="") as f:
            w = csv_mod.DictWriter(f, fieldnames=list(curve[0].keys()))
            w.writeheader()
            for row in curve:
                w.writerow(row)

        split_results[split_name] = {
            "top1": metrics["top1"],
            "top3": metrics["top3"],
            "macro_f1_all_classes": metrics["macro_f1_all_classes"],
            "macro_f1_present_only": metrics["macro_f1_present_only"],
            "weighted_f1": metrics["weighted_f1"],
            "n_samples": metrics["n_samples"],
            "n_classes_total": metrics["n_classes_total"],
            "n_classes_present": metrics["n_classes_present"],
            "classes_missing_names": metrics["classes_missing_names"],
            "per_class": metrics["per_class"],
            "threshold_chosen": metrics.get("threshold_chosen"),
        }

    # ── threshold curves plot ────────────────────────────────────────────────
    if all_curves:
        _plot_threshold_curves(
            all_curves, all_chosen,
            out_dir / "threshold_curves.png",
        )

    # ── summary JSON ─────────────────────────────────────────────────────────
    summary: dict = {
        "artifact": str(args.artifact),
        "model_version": artifact["model_version"],
        "backbone": artifact["backbone"],
        "artifact_threshold": artifact_threshold,
        "splits": {},
    }
    for split, m in split_results.items():
        summary["splits"][split] = {
            "top1": m["top1"],
            "top3": m["top3"],
            "macro_f1_all_classes": m["macro_f1_all_classes"],
            "macro_f1_present_only": m["macro_f1_present_only"],
            "weighted_f1": m["weighted_f1"],
            "n_samples": m["n_samples"],
            "n_classes_present": m["n_classes_present"],
            "n_classes_total": m["n_classes_total"],
        }
    (out_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False)
    )

    # ── markdown report ──────────────────────────────────────────────────────
    own_mini_note = (
        "Only 6 out of 43 classes are covered; accuracy numbers are not "
        "representative of overall model quality."
    )
    md = _build_markdown_report(
        artifact_name=args.artifact.name,
        threshold_json=threshold_json,
        split_results=split_results,
        own_mini_note=own_mini_note if "own_mini" in split_results else "",
    )
    (out_dir / "summary_report.md").write_text(md, encoding="utf-8")

    # ── console summary ──────────────────────────────────────────────────────
    print("\n" + "=" * 65)
    print(f"{'FINAL METRICS':^65}")
    print(f"{'model: ' + artifact['backbone']:^65}")
    print("=" * 65)
    header = f"{'split':<14} {'n':>5} {'top-1':>7} {'top-3':>7} {'macF1':>7} {'macF1p':>7}"
    print(header)
    print("-" * 65)
    for split, m in split_results.items():
        marker = " *" if split == "own_mini" else "  "
        print(
            f"{split:<14}{marker}"
            f"{m['n_samples']:>5}  "
            f"{m['top1'] * 100:>6.2f}%  "
            f"{m['top3'] * 100:>6.2f}%  "
            f"{m['macro_f1_all_classes'] * 100:>6.2f}%  "
            f"{m['macro_f1_present_only'] * 100:>6.2f}%"
        )
    print("=" * 65)
    print("* own_mini: incomplete class coverage, treat separately\n")
    print(f"Output written to: {out_dir}")


if __name__ == "__main__":
    main()
