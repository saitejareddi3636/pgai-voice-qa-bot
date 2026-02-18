# Architecture

## Overview

This is a phone-based QA system that calls healthcare agents and tests their responses. It places real phone calls, records conversations, and generates bug reports.

## How it works

1. **TwiML Server**: FastAPI server that handles Twilio webhooks and controls call flow
2. **Scenarios**: Predefined patient scripts for different test cases
3. **Run Management**: Each call creates a timestamped folder with all artifacts  
4. **Transcription**: Uses FasterWhisper locally (no external API needed)
5. **QA Analysis**: Dual system - OpenAI API with heuristic fallback

## Call Flow

Each call follows this pattern:
- Pick a scenario (rotates through 5 different patient types)
- Play patient line, record agent response  
- Repeat for multiple turns
- Transcribe all recordings
- Generate bug report
- Update batch summary

## Key Design Decisions

**Local transcription**: Uses FasterWhisper so the system works without external API quota limits.

**Deterministic scenarios**: Each run folder contains the exact patient script used, making results reproducible.

**Dual QA mode**: Falls back to heuristic analysis if OpenAI API is unavailable.

**Run isolation**: Each test creates a separate timestamped folder. No overwriting of previous results.
