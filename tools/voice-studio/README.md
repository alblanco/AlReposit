# Bob Voice Studio

Push-to-talk voice interface using local Whisper transcription.

## Start (safe profile)

```bash
cd tools/voice-studio
./start_safe.sh
```

Open: <http://127.0.0.1:8790>

## Features
- Hold-to-talk recording
- Auto transcription via local Whisper (`/transcribe`)
- Transcript auto-copied for quick paste into Bob chat
- Browser TTS playback for Bob responses

## Health check

```bash
curl http://127.0.0.1:8787/health
```
