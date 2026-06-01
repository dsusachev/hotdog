"""
Запускает все сервисы разом:
  - ML-сервис    → http://localhost:8001  (реальная модель или заглушка)
  - Backend API  → http://localhost:8000
  - Frontend     → http://localhost:3000

Использование:
    python start.py

Остановка: Ctrl+C
"""
import os
import signal
import subprocess
import sys
import threading
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FRONT_DIR = ROOT / "src" / "front"
ARTIFACT  = ROOT / "ml" / "artifacts" / "resnet50_v1_20260519.pt"

RESET  = "\033[0m"
COLORS = ["\033[36m", "\033[32m", "\033[35m"]  # cyan, green, magenta

# Run the real model only when we can actually load it: torch installed AND the
# artifact present. The artifact is fetched on demand from the GitHub Release, so
# a fresh clone gets the real model automatically. Anything missing (no torch, no
# network) gracefully falls back to the stub instead of crashing the service.
def _torch_available() -> bool:
    import importlib.util
    return importlib.util.find_spec("torch") is not None


use_real_ml = False
if not _torch_available():
    print("  [start] torch не установлен (pip install -r ml/requirements.txt) — заглушка")
else:
    if not ARTIFACT.exists():
        try:
            sys.path.insert(0, str(ROOT / "ml"))
            from scripts.download_model import ensure_artifact

            ensure_artifact()
        except Exception as exc:  # noqa: BLE001 - offline / download error -> stub
            print(f"  [start] не удалось скачать модель ({exc}); использую заглушку")
    use_real_ml = ARTIFACT.exists()

if use_real_ml:
    ml_cmd = [sys.executable, "ml/serve.py"]
    ml_label = "ml "
else:
    ml_cmd = [sys.executable, "-m", "uvicorn", "ml.stub:app",
              "--host", "0.0.0.0", "--port", "8001"]
    ml_label = "ml~"  # тильда = заглушка

SERVICES = [
    {
        "name": ml_label,
        "cmd": ml_cmd,
        "cwd": ROOT,
    },
    {
        "name": "api",
        "cmd": [sys.executable, "-m", "uvicorn", "src.main:app",
                "--host", "0.0.0.0", "--port", "8000", "--reload"],
        "cwd": ROOT,
    },
    {
        "name": "ui ",
        "cmd": ["npm", "run", "dev"] if sys.platform != "win32"
               else ["npm.cmd", "run", "dev"],
        "cwd": FRONT_DIR,
    },
]


def stream(proc: subprocess.Popen, label: str, color: str) -> None:
    prefix = f"{color}[{label}]{RESET} "
    for line in proc.stdout:
        sys.stdout.write(prefix + line)
        sys.stdout.flush()


def main() -> None:
    procs: list[subprocess.Popen] = []

    env = {**os.environ, "PYTHONPATH": str(ROOT)}

    for i, svc in enumerate(SERVICES):
        proc = subprocess.Popen(
            svc["cmd"],
            cwd=svc["cwd"],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
        procs.append(proc)
        t = threading.Thread(
            target=stream,
            args=(proc, svc["name"], COLORS[i % len(COLORS)]),
            daemon=True,
        )
        t.start()

    ml_mode = "реальная модель" if use_real_ml else "заглушка (положи артефакт в ml/artifacts/)"
    print(f"\n  ML  ({ml_mode}) → http://localhost:8001")
    print(f"  API → http://localhost:8000")
    print(f"  UI  → http://localhost:3000")
    print(f"\n  Остановка: Ctrl+C\n")

    def shutdown(sig, frame):
        print("\nОстанавливаю сервисы...")
        for p in procs:
            if p.poll() is None:
                p.terminate()
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    for p in procs:
        p.wait()


if __name__ == "__main__":
    main()
