# VOICE_WORKFLOW.md

Goal: fluid voice in/out for Bob interviews and project updates.

## Recommended stack (now)
1. **Input STT (local):** `whisper` CLI (already installed)
2. **Assistant reasoning/orchestration:** Bob (main OpenClaw session)
3. **Output TTS:** OpenClaw `tts` tool

## Fast path
- Record memo (m4a/wav) from phone or desktop.
- Drop file in workspace (e.g., `inbox/audio/`).
- Run whisper transcription (local, no API key).
- Feed transcript to Bob.
- Bob answers and can return voice via `tts`.

## Whisper command baseline
```bash
whisper <audio-file> --model turbo --language en --output_format txt --output_dir <out-dir>
```

## Model guidance
- `turbo`: fastest default
- `small`/`medium`: better quality, slower

## Optional API upgrades
- OpenAI Whisper API for cleaner transcripts/noisy audio fallback
- Optional diarization provider if multi-speaker meetings become common

## Operational notes
- Keep raw audio + transcript paired by timestamp.
- Save transcript summaries into daily memory and important decisions into `ops/DECISIONS.md`.
