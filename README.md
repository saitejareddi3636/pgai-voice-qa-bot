# Pretty Good AI Engineering Challenge Voice QA Bot

Automated voice QA system that places real patient calls, records responses, generates transcripts, and produces structured bug reports and ranked scenario summaries.

## What it does
1. Calls a target phone number using Twilio
2. Runs a multi turn patient scenario
3. Saves per turn recordings
4. Generates a transcript and bug report per call
5. Generates a ranked batch report across calls

## Setup

### 1. Create environment
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure environment variables

Copy `.env.example` to `.env` and fill values.

**Required:**
- `TWILIO_ACCOUNT_SID`
- `TWILIO_AUTH_TOKEN`
- `TWILIO_FROM_NUMBER`
- `PUBLIC_BASE_URL`
- `OPENAI_API_KEY` (optional)

**Notes:**
- Twilio trial accounts can only call verified numbers.
- Use your own verified phone for development.
- For submission, set `TARGET_NUMBER` to the provided test line.

### 3. Start the TwiML server
```bash
uvicorn src.telephony.twiml_server:app --host 0.0.0.0 --port 8000
```

Expose it publicly using ngrok:
```bash
ngrok http 8000
```

Set `PUBLIC_BASE_URL` to your ngrok https URL.

## Run

### Single call
In a new terminal:
```bash
python -m src.telephony.twilio_client
```

### Batch run
Places multiple calls and writes `runs/BATCH_REPORT.md`:
```bash
python -m src.batch_run
```

## Output artifacts

Each call creates a folder under `runs/run_YYYYMMDD_HHMMSS/`:
- `recordings/`
- `transcripts/`
- `bugs/`
- `meta/`
- `patient/`

Latest run is also accessible via `runs/latest`
