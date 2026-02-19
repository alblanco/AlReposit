# Bob Voice Studio

Quick local voice interface for recording and playback.

## Run

From workspace root:

```bash
cd tools/voice-studio
python3 -m http.server 8787
```

Open: <http://127.0.0.1:8787>

## Features
- Record mic audio and download it
- Live browser speech-to-text dictation (when supported)
- Paste Bob text replies and play with browser TTS

## Notes
- Works best in Chrome-based browsers.
- Browser STT/TTS quality depends on OS/browser voices.
- For higher accuracy transcription, use local Whisper script:
  - `scripts/transcribe.sh <audio-file>`
