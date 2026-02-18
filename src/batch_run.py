import time
from pathlib import Path

from src.config import RUNS_DIR
from src.telephony.twilio_client import place_test_call


def score_bug_md(bug_md: str) -> tuple[int, list[str]]:
    lines = [ln.strip() for ln in bug_md.splitlines() if ln.strip()]
    issues = []
    for ln in lines:
        if ln[0].isdigit() and ". " in ln:
            issues.append(ln)

    score = 0
    for i in issues:
        low = i.lower()
        if "loop" in low:
            score += 5
        elif "contradiction" in low:
            score += 4
        elif "incorrect" in low or "workflow" in low:
            score += 3
        elif "incoherent" in low or "low quality" in low:
            score += 2
        else:
            score += 1

    return score, issues


def list_runs() -> list[Path]:
    root = Path(RUNS_DIR)
    if not root.exists():
        return []
    runs = [p for p in root.iterdir() if p.is_dir() and p.name.startswith("run_")]
    runs.sort(key=lambda p: p.stat().st_mtime)
    return runs


def read_text(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8")
    except Exception:
        return ""


def main(calls: int = 10, pause_seconds: int = 20) -> None:
    print(f"Placing {calls} calls")
    for i in range(1, calls + 1):
        sid = place_test_call()
        print(f"Call {i}/{calls} SID {sid}")
        time.sleep(pause_seconds)

    root = Path(RUNS_DIR)
    report = []
    report.append("# Batch Summary Report")
    report.append("")
    report.append(f"Total calls attempted: {calls}")
    report.append("")

    runs = list_runs()
    
    # Compute scenario ranking
    scenario_scores = {}
    for run in runs[-calls:]:
        scenario = read_text(run / "meta" / "scenario.txt").strip() or "unknown"
        bugs = read_text(run / "bugs" / "bugs.md").strip()
        s, _ = score_bug_md(bugs)
        scenario_scores.setdefault(scenario, []).append(s)

    report.append("## Scenario ranking")
    report.append("")
    ranked = sorted(scenario_scores.items(), key=lambda kv: sum(kv[1]) / max(1, len(kv[1])), reverse=True)
    for name, scores in ranked:
        avg = sum(scores) / max(1, len(scores))
        report.append(f"- {name}: avg {avg:.2f} over {len(scores)} call(s)")
    report.append("")

    report.append(f"Runs found: {len(runs)}")
    report.append("")

    for run in runs[-calls:]:
        scenario = read_text(run / "meta" / "scenario.txt").strip()
        bugs = read_text(run / "bugs" / "bugs.md").strip()
        score, issues = score_bug_md(bugs)
        
        report.append(f"## {run.name}")
        report.append("")
        report.append(f"Scenario: {scenario or 'unknown'}")
        report.append(f"Severity score: {score}")
        report.append("")
        report.append("Issues:")
        report.append("")
        if issues:
            report.extend(issues[:10])
        else:
            report.append("No issues detected by heuristic QA.")
        report.append("")

    out_path = root / "BATCH_REPORT.md"
    out_path.write_text("\n".join(report), encoding="utf-8")
    print(f"Saved {out_path}")


if __name__ == "__main__":
    main(calls=2, pause_seconds=20)