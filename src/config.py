import os
from dotenv import load_dotenv

load_dotenv()

def get_env(name: str) -> str:
    v = os.getenv(name)
    if not v:
        raise RuntimeError(f"Missing env var: {name}")
    return v

TWILIO_ACCOUNT_SID = get_env("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = get_env("TWILIO_AUTH_TOKEN")
TWILIO_FROM_NUMBER = get_env("TWILIO_FROM_NUMBER")

TARGET_NUMBER = os.getenv("TARGET_NUMBER", "+18054398008")

OPENAI_API_KEY = get_env("OPENAI_API_KEY")

PUBLIC_BASE_URL = get_env("PUBLIC_BASE_URL")

RUNS_DIR = os.getenv("RUNS_DIR", "runs")
MAX_TURNS = int(os.getenv("MAX_TURNS", "6"))
RECORD_SECONDS = int(os.getenv("RECORD_SECONDS", "35"))