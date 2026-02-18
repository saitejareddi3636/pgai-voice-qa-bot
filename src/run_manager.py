from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from src.config import RUNS_DIR


@dataclass(frozen=True)
class RunPaths:
    run_id: str
    base: Path
    recordings: Path
    transcripts: Path
    bugs: Path
    meta: Path
    patient: Path


def create_new_run() -> RunPaths:
    root = Path(RUNS_DIR)
    root.mkdir(parents=True, exist_ok=True)

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_id = f"run_{stamp}"
    base = root / run_id

    recordings = base / "recordings"
    transcripts = base / "transcripts"
    bugs = base / "bugs"
    meta = base / "meta"
    patient = base / "patient"

    for p in [recordings, transcripts, bugs, meta, patient]:
        p.mkdir(parents=True, exist_ok=True)

    latest = root / "latest"
    if latest.exists() or latest.is_symlink():
        try:
            latest.unlink()
        except Exception:
            pass
    try:
        latest.symlink_to(base, target_is_directory=True)
    except Exception:
        pass

    return RunPaths(
        run_id=run_id,
        base=base,
        recordings=recordings,
        transcripts=transcripts,
        bugs=bugs,
        meta=meta,
        patient=patient,
    )