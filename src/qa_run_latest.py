from pathlib import Path

from src.qa.heuristic_qa import analyze_transcript_heuristic

try:
    from openai import OpenAI
except Exception:
    OpenAI = None


RUN_DIR = Path("runs/latest")
TRANSCRIPT = RUN_DIR / "transcripts" / "multi_turn_transcript.md"
OUT_DIR = RUN_DIR / "bugs"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def try_openai_analysis(transcript_text: str) -> str | None:
    if OpenAI is None:
        return None

    try:
        client = OpenAI()
        prompt = f"""
You are QA for a healthcare phone agent.

Find problems in this transcript.
Return a bullet list with:
Turn number
What is wrong
Why it matters
How to fix

Transcript:
{transcript_text}
"""
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
        )
        return resp.choices[0].message.content.strip()
    except Exception:
        return None


def main() -> None:
    text = TRANSCRIPT.read_text(encoding="utf-8")

    bugs = try_openai_analysis(text)
    mode = "openai"
    if not bugs:
        bugs = analyze_transcript_heuristic(text)
        mode = "heuristic"

    header = f"# Bug Report\n\nMode: {mode}\n\n"
    (OUT_DIR / "bugs.md").write_text(header + bugs, encoding="utf-8")
    print("BUG FILE CREATED")


if __name__ == "__main__":
    main()