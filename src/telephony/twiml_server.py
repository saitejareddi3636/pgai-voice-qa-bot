from pathlib import Path

import httpx
from fastapi import FastAPI, Request
from fastapi.responses import Response
from twilio.twiml.voice_response import VoiceResponse

from src.config import (
    MAX_TURNS,
    PUBLIC_BASE_URL,
    RECORD_SECONDS,
    RUNS_DIR,
    TWILIO_ACCOUNT_SID,
    TWILIO_AUTH_TOKEN,
)
from src.run_manager import create_new_run
from src.audio.stt import transcribe_file
from src.qa.heuristic_qa import analyze_transcript_heuristic
from src.scenarios import SCENARIOS

app = FastAPI()


def pick_scenario_name(run_id: str) -> str:
    names = sorted(SCENARIOS.keys())
    if not names:
        return "default"
    idx = sum(bytearray(run_id.encode("utf-8"))) % len(names)
    return names[idx]


PATIENT_SCRIPT = [
    "Hi, I want to schedule an appointment.",
    "Next week works. Do you have anything on Tuesday afternoon?",
    "Actually, can we do Wednesday morning instead?",
    "Also I need a refill for my medication.",
    "My name is Sai Teja Reddy Shaga. Date of birth is June fifteenth nineteen ninety nine.",
    "Thanks. That is all.",
]


def build_transcript(run_id: str) -> str:
    base = Path(RUNS_DIR) / run_id
    patient_lines = (base / "patient" / "script.txt").read_text(encoding="utf-8").splitlines()

    wavs = sorted((base / "recordings").glob("turn_*_agent_*.wav"))
    lines = []
    lines.append("# Multi Turn Call Transcript")
    lines.append("")
    lines.append(f"Run: {run_id}")
    lines.append(f"Total Turns: {min(len(patient_lines), len(wavs))}")
    lines.append("")

    for idx, wav in enumerate(wavs, start=1):
        if idx > len(patient_lines):
            break
        agent_text = transcribe_file(wav, model_size="base")
        lines.append(f"## Turn {idx}")
        lines.append("")
        lines.append(f"Recording: {wav.name}")
        lines.append("")
        lines.append("Patient:")
        lines.append(patient_lines[idx - 1])
        lines.append("")
        lines.append("Agent:")
        lines.append(agent_text or "[empty]")
        lines.append("")

    return "\n".join(lines)


def run_dir_from_id(run_id: str) -> Path:
    base = Path(RUNS_DIR) / run_id
    (base / "recordings").mkdir(parents=True, exist_ok=True)
    (base / "meta").mkdir(parents=True, exist_ok=True)
    (base / "patient").mkdir(parents=True, exist_ok=True)
    return base


@app.get("/health")
def health():
    return {"ok": True}


@app.post("/twiml/start")
async def twiml_start(request: Request):
    run = create_new_run()
    
    scenario_name = pick_scenario_name(run.run_id)
    scenario = SCENARIOS[scenario_name]

    (run.meta / "scenario.txt").write_text(scenario_name, encoding="utf-8")
    (run.patient / "script.txt").write_text("\n".join(scenario.patient_lines), encoding="utf-8")

    vr = VoiceResponse()
    vr.say("Hello. This is an automated patient test.")
    vr.redirect(f"{PUBLIC_BASE_URL}/twiml/turn?run_id={run.run_id}&scenario={scenario_name}&turn=1", method="POST")
    return Response(content=str(vr), media_type="application/xml")


@app.post("/twiml/turn")
async def twiml_turn(request: Request):
    form = await request.form()
    turn_raw = request.query_params.get("turn", "1")
    run_id = request.query_params.get("run_id", "latest")
    scenario_name = request.query_params.get("scenario", "schedule_basic")
    try:
        turn = int(turn_raw)
    except Exception:
        turn = 1

    vr = VoiceResponse()
    
    base = run_dir_from_id(run_id)
    patient_lines = (base / "patient" / "script.txt").read_text(encoding="utf-8").splitlines()

    if turn > MAX_TURNS or turn > len(patient_lines):
        vr.redirect(f"{PUBLIC_BASE_URL}/twiml/finalize?run_id={run_id}", method="POST")
        return Response(content=str(vr), media_type="application/xml")

    patient_text = patient_lines[turn - 1]
    vr.say(f"Turn {turn}. {patient_text}")

    vr.record(
        max_length=RECORD_SECONDS,
        play_beep=True,
        action=f"{PUBLIC_BASE_URL}/twiml/after_record?run_id={run_id}&scenario={scenario_name}&turn={turn}",
        method="POST",
    )
    return Response(content=str(vr), media_type="application/xml")


@app.post("/twiml/after_record")
async def twiml_after_record(request: Request):
    form = await request.form()
    recording_url = str(form.get("RecordingUrl", "")).strip()
    recording_sid = str(form.get("RecordingSid", "")).strip()

    run_id = request.query_params.get("run_id", "latest")
    turn_raw = request.query_params.get("turn", "1")
    scenario_name = request.query_params.get("scenario", "schedule_basic")
    base = run_dir_from_id(run_id)
    try:
        turn = int(turn_raw)
    except Exception:
        turn = 1

    vr = VoiceResponse()

    if recording_url:
        wav_url = recording_url + ".wav"
        out_path = base / "recordings" / f"turn_{turn:02d}_agent_{recording_sid}.wav"

        try:
            async with httpx.AsyncClient(auth=(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN), timeout=60) as client:
                r = await client.get(wav_url)
                r.raise_for_status()
                out_path.write_bytes(r.content)

            meta_path = base / "meta" / f"turn_{turn:02d}_agent_{recording_sid}.txt"
            meta_path.write_text(
                f"Turn={turn}\nRecordingUrl={recording_url}\nRecordingSid={recording_sid}\n",
                encoding="utf-8",
            )
        except Exception:
            pass

    next_turn = turn + 1
    vr.redirect(f"{PUBLIC_BASE_URL}/twiml/turn?run_id={run_id}&scenario={scenario_name}&turn={next_turn}", method="POST")
    return Response(content=str(vr), media_type="application/xml")


@app.post("/twiml/finalize")
async def twiml_finalize(request: Request):
    run_id = request.query_params.get("run_id", "latest")
    base = run_dir_from_id(run_id)

    transcript_text = build_transcript(run_id)
    (base / "transcripts").mkdir(parents=True, exist_ok=True)
    transcript_path = base / "transcripts" / "transcript.md"
    transcript_path.write_text(transcript_text, encoding="utf-8")

    bug_md = analyze_transcript_heuristic(transcript_text)
    (base / "bugs").mkdir(parents=True, exist_ok=True)
    (base / "bugs" / "bugs.md").write_text(bug_md, encoding="utf-8")

    vr = VoiceResponse()
    vr.say("Thanks. This call has been saved. Goodbye.")
    vr.hangup()
    return Response(content=str(vr), media_type="application/xml")