from pathlib import Path
import re

from src.config import RUNS_DIR
from src.audio.stt import transcribe_file


def get_turn_recordings(recordings_dir: Path) -> dict:
    """Get all turn recordings sorted by turn number"""
    turn_files = {}
    for wav_path in recordings_dir.glob("turn_*_agent_*.wav"):
        # Extract turn number from filename like "turn_01_agent_RExxxx.wav"
        match = re.search(r"turn_(\d+)_agent_", wav_path.name)
        if match:
            turn_num = int(match.group(1))
            turn_files[turn_num] = wav_path
    return turn_files


def main() -> None:
    base = Path(RUNS_DIR) / "latest"
    recordings_dir = base / "recordings"
    transcripts_dir = base / "transcripts"
    patient_dir = base / "patient"
    transcripts_dir.mkdir(parents=True, exist_ok=True)

    # Get patient script
    patient_script_path = patient_dir / "script.txt"
    if patient_script_path.exists():
        patient_lines = patient_script_path.read_text(encoding="utf-8").strip().split("\n")
    else:
        patient_lines = []

    # Get all turn recordings
    turn_recordings = get_turn_recordings(recordings_dir)
    
    if not turn_recordings:
        print("No turn recordings found!")
        return

    print(f"Found {len(turn_recordings)} turn recordings")

    # Build transcript
    transcript_lines = [
        "# Multi-Turn Call Transcript",
        "",
        f"Total Turns: {len(turn_recordings)}",
        "",
    ]

    # Process each turn
    for turn_num in sorted(turn_recordings.keys()):
        wav_path = turn_recordings[turn_num]
        
        print(f"Transcribing Turn {turn_num}: {wav_path.name}")
        
        # Get patient text for this turn
        if turn_num <= len(patient_lines):
            patient_text = patient_lines[turn_num - 1]
        else:
            patient_text = "[No patient script for this turn]"
        
        # Transcribe agent response
        try:
            agent_text = transcribe_file(wav_path, model_size="base")
        except Exception as e:
            agent_text = f"[Transcription failed: {e}]"
        
        # Add to transcript
        transcript_lines.extend([
            f"## Turn {turn_num}",
            "",
            f"**Recording:** `{wav_path.name}`",
            "",
            "**Patient:**",
            patient_text,
            "",
            "**Agent:**",
            agent_text or "[empty transcript]", 
            "",
        ])

    # Write final transcript
    out_md = transcripts_dir / "multi_turn_transcript.md"
    out_md.write_text("\n".join(transcript_lines), encoding="utf-8")

    print(f"Saved multi-turn transcript: {out_md}")


if __name__ == "__main__":
    main()