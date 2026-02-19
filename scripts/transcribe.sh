#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <audio-file> [model]"
  exit 1
fi

AUDIO="$1"
MODEL="${2:-turbo}"
TS="$(date +%Y%m%d-%H%M%S)"
OUT_DIR="/Users/albertoblanco/.openclaw/workspace/inbox/transcripts/${TS}"
mkdir -p "$OUT_DIR"

whisper "$AUDIO" --model "$MODEL" --language en --output_format txt --output_dir "$OUT_DIR"

TXT="${OUT_DIR}/$(basename "${AUDIO%.*}").txt"
echo "Transcript: $TXT"
