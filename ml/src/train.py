from __future__ import annotations

import csv
import json
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Iterable

import torch
import torch.nn as nn
from torch.amp import GradScaler, autocast
from torch.optim import AdamW
from torch.optim.lr_scheduler import CosineAnnealingLR
from torch.utils.data import DataLoader

from src.model import Backbone, set_backbone_trainable


# ---------- Config -----------------------------------------------------------


@dataclass
class StageConfig:
    name: str
    lr: float
    epochs: int
    backbone_trainable: bool
    unfreeze_top_n_blocks: int = 0  # only meaningful when backbone_trainable=True


@dataclass
class TrainConfig:
    backbone: Backbone = "efficientnet_b0"
    num_classes: int = 43
    batch_size: int = 32
    weight_decay: float = 1e-4
    label_smoothing: float = 0.1
    max_grad_norm: float = 1.0
    early_stop_patience: int = 6
    seed: int = 42

    stages: list[StageConfig] = field(
        default_factory=lambda: [
            StageConfig(
                name="feature_extraction",
                lr=1e-3,
                epochs=4,
                backbone_trainable=False,
            ),
            StageConfig(
                name="fine_tuning",
                lr=1e-4,
                epochs=15,
                backbone_trainable=True,
                unfreeze_top_n_blocks=2,
            ),
        ]
    )


# ---------- Device / AMP utils -----------------------------------------------


def pick_device() -> torch.device:
    if torch.cuda.is_available():
        return torch.device("cuda")
    if torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


def amp_enabled_for(device: torch.device) -> bool:
    # GradScaler + autocast(float16) — реально поддержано только на CUDA.
    return device.type == "cuda"


# ---------- Freeze helpers ---------------------------------------------------


def unfreeze_top_blocks(
    model: nn.Module, name: Backbone, n_blocks: int
) -> None:
    """Stage 2: keep backbone mostly frozen, unfreeze only top-N blocks + head."""
    if n_blocks <= 0:
        return
    if name == "efficientnet_b0":
        # model.features = Sequential of 9 blocks (indices 0..8).
        # Top-N blocks = last N indices.
        blocks = list(model.features.children())
        for blk in blocks[-n_blocks:]:
            for p in blk.parameters():
                p.requires_grad = True
    elif name == "resnet50":
        # ResNet has 4 layers; "top blocks" = last N of [layer1..layer4].
        layers = [model.layer1, model.layer2, model.layer3, model.layer4]
        for layer in layers[-n_blocks:]:
            for p in layer.parameters():
                p.requires_grad = True
    else:
        raise ValueError(f"Unknown backbone: {name}")


def set_bn_eval_for_frozen_backbone(model: nn.Module, name: Backbone) -> None:
    """Force BN layers inside the *frozen* part of the backbone into eval mode.

    Prevents BN running stats from drifting under our dataset during stage 1
    (ml_aproach.md §5, "Особенность работы с BatchNorm").
    """
    head_id = id(model.classifier if name == "efficientnet_b0" else model.fc)
    for module in model.modules():
        if id(module) == head_id:
            continue
        if isinstance(module, (nn.BatchNorm1d, nn.BatchNorm2d, nn.BatchNorm3d)):
            # If any of its params are still trainable, leave it alone —
            # that means the user unfroze the block containing this BN.
            if all(not p.requires_grad for p in module.parameters()):
                module.eval()


# ---------- Metrics ----------------------------------------------------------


def topk_correct(logits: torch.Tensor, targets: torch.Tensor, ks: Iterable[int]):
    """Return {k: int(correct count)} for each k."""
    ks = list(ks)
    max_k = max(ks)
    _, pred = logits.topk(max_k, dim=1)  # (B, max_k)
    pred = pred.t()  # (max_k, B)
    correct = pred.eq(targets.view(1, -1).expand_as(pred))  # (max_k, B)
    return {k: int(correct[:k].any(dim=0).sum().item()) for k in ks}


# ---------- One-epoch primitives ---------------------------------------------


def train_one_epoch(
    model: nn.Module,
    loader: DataLoader,
    criterion: nn.Module,
    optimizer: torch.optim.Optimizer,
    scaler: GradScaler | None,
    device: torch.device,
    max_grad_norm: float,
) -> dict[str, float]:
    model.train()
    use_amp = scaler is not None and amp_enabled_for(device)

    total_loss = 0.0
    total_n = 0
    correct = {1: 0, 3: 0}

    for images, labels in loader:
        images = images.to(device, non_blocking=True)
        labels = labels.to(device, non_blocking=True)

        optimizer.zero_grad(set_to_none=True)

        if use_amp:
            with autocast(device_type="cuda", dtype=torch.float16):
                logits = model(images)
                loss = criterion(logits, labels)
            scaler.scale(loss).backward()
            scaler.unscale_(optimizer)
            nn.utils.clip_grad_norm_(model.parameters(), max_grad_norm)
            scaler.step(optimizer)
            scaler.update()
        else:
            logits = model(images)
            loss = criterion(logits, labels)
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), max_grad_norm)
            optimizer.step()

        bs = labels.size(0)
        total_loss += float(loss.item()) * bs
        total_n += bs
        batch_correct = topk_correct(logits.detach(), labels, ks=(1, 3))
        for k, c in batch_correct.items():
            correct[k] += c

    return {
        "loss": total_loss / total_n,
        "top1": correct[1] / total_n,
        "top3": correct[3] / total_n,
    }


@torch.no_grad()
def evaluate(
    model: nn.Module,
    loader: DataLoader,
    criterion: nn.Module,
    device: torch.device,
) -> dict[str, float]:
    model.eval()
    total_loss = 0.0
    total_n = 0
    correct = {1: 0, 3: 0}

    for images, labels in loader:
        images = images.to(device, non_blocking=True)
        labels = labels.to(device, non_blocking=True)

        logits = model(images)
        loss = criterion(logits, labels)

        bs = labels.size(0)
        total_loss += float(loss.item()) * bs
        total_n += bs
        batch_correct = topk_correct(logits, labels, ks=(1, 3))
        for k, c in batch_correct.items():
            correct[k] += c

    return {
        "loss": total_loss / total_n,
        "top1": correct[1] / total_n,
        "top3": correct[3] / total_n,
    }


# ---------- Orchestration ----------------------------------------------------


def _trainable_params(model: nn.Module):
    return [p for p in model.parameters() if p.requires_grad]


def train_two_stage(
    model: nn.Module,
    backbone_name: Backbone,
    train_loader: DataLoader,
    val_loader: DataLoader,
    config: TrainConfig,
    run_dir: str | Path,
) -> dict:
    run_dir = Path(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)

    torch.manual_seed(config.seed)
    device = pick_device()
    model.to(device)
    criterion = nn.CrossEntropyLoss(label_smoothing=config.label_smoothing)

    # Persist config for reproducibility.
    (run_dir / "config.json").write_text(
        json.dumps(asdict(config), indent=2, ensure_ascii=False)
    )

    metrics_path = run_dir / "metrics.csv"
    metrics_file = metrics_path.open("w", newline="")
    writer = csv.writer(metrics_file)
    writer.writerow(
        [
            "stage", "epoch", "lr",
            "train_loss", "train_top1", "train_top3",
            "val_loss", "val_top1", "val_top3",
            "secs",
        ]
    )

    best_val_loss = float("inf")
    best_state = None
    epochs_since_improve = 0
    global_epoch = 0
    stop_training = False

    for stage in config.stages:
        if stop_training:
            break

        # Apply freeze schedule for this stage.
        if stage.backbone_trainable:
            set_backbone_trainable(model, backbone_name, trainable=False)
            unfreeze_top_blocks(
                model, backbone_name, stage.unfreeze_top_n_blocks
            )
        else:
            set_backbone_trainable(model, backbone_name, trainable=False)

        # AdamW only on currently-trainable params — saves memory and prevents
        # weight_decay from drifting frozen params via Adam's update rule.
        optimizer = AdamW(
            _trainable_params(model),
            lr=stage.lr,
            weight_decay=config.weight_decay,
        )
        scheduler = CosineAnnealingLR(optimizer, T_max=stage.epochs)
        scaler = GradScaler() if amp_enabled_for(device) else None

        for epoch in range(stage.epochs):
            global_epoch += 1
            epoch_t0 = time.time()

            model.train()

            # Always force BN in *currently-frozen* blocks to eval — otherwise
            # their running stats drift away from ImageNet even though their
            # gamma/beta are frozen. Particularly important for EfficientNet,
            # where BN layers are everywhere.
            set_bn_eval_for_frozen_backbone(model, backbone_name)


            train_m = train_one_epoch(
                model, train_loader, criterion, optimizer, scaler,
                device, config.max_grad_norm,
            )
            val_m = evaluate(model, val_loader, criterion, device)
            current_lr = optimizer.param_groups[0]["lr"]
            scheduler.step()

            secs = time.time() - epoch_t0
            writer.writerow([
                stage.name, global_epoch, f"{current_lr:.2e}",
                f"{train_m['loss']:.4f}", f"{train_m['top1']:.4f}", f"{train_m['top3']:.4f}",
                f"{val_m['loss']:.4f}", f"{val_m['top1']:.4f}", f"{val_m['top3']:.4f}",
                f"{secs:.1f}",
            ])
            metrics_file.flush()

            print(
                f"[{stage.name} {epoch+1}/{stage.epochs}] "
                f"train_loss={train_m['loss']:.4f} "
                f"val_loss={val_m['loss']:.4f} "
                f"val_top1={val_m['top1']:.4f} "
                f"val_top3={val_m['top3']:.4f} "
                f"lr={current_lr:.2e} "
                f"({secs:.1f}s)"
            )

            if val_m["loss"] < best_val_loss - 1e-6:
                best_val_loss = val_m["loss"]
                epochs_since_improve = 0
                best_state = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}
                torch.save(
                    {"model_state": best_state, "val_loss": best_val_loss,
                     "global_epoch": global_epoch, "config": asdict(config)},
                    run_dir / "best.pt",
                )
            else:
                epochs_since_improve += 1
                if epochs_since_improve >= config.early_stop_patience:
                    print(f"Early stopping: no val_loss improvement for "
                          f"{epochs_since_improve} epochs")
                    stop_training = True
                    break

    metrics_file.close()

    # Save the last state too — for inspection independent of "best".
    torch.save(
        {"model_state": model.state_dict(), "global_epoch": global_epoch,
         "config": asdict(config)},
        run_dir / "last.pt",
    )

    return {
        "best_val_loss": best_val_loss,
        "global_epochs": global_epoch,
        "run_dir": str(run_dir),
    }
