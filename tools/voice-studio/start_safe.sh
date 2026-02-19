#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"
source .venv/bin/activate

# Low-risk profile for system stability
export BOB_VOICE_PORT="${BOB_VOICE_PORT:-8790}"
export BOB_WHISPER_MODEL="${BOB_WHISPER_MODEL:-base.en}"
export BOB_WHISPER_THREADS="${BOB_WHISPER_THREADS:-2}"
export BOB_WHISPER_TIMEOUT_SEC="${BOB_WHISPER_TIMEOUT_SEC:-25}"
export BOB_MAX_AUDIO_MB="${BOB_MAX_AUDIO_MB:-3}"

pkill -f 'tools/voice-studio/server.py' || true
exec python server.py
