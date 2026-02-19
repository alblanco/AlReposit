#!/usr/bin/env python3
import os
import shutil
import subprocess
import tempfile
import threading
from pathlib import Path
from flask import Flask, jsonify, request, send_from_directory

ROOT = Path(__file__).resolve().parent
WHISPER_MODEL = os.environ.get("BOB_WHISPER_MODEL", "tiny.en")
WHISPER_THREADS = os.environ.get("BOB_WHISPER_THREADS", "2")
WHISPER_TIMEOUT_SEC = int(os.environ.get("BOB_WHISPER_TIMEOUT_SEC", "30"))
MAX_AUDIO_MB = int(os.environ.get("BOB_MAX_AUDIO_MB", "5"))
WHISPER_BIN = os.environ.get("BOB_WHISPER_BIN") or shutil.which("whisper") or "/opt/homebrew/bin/whisper"
TRANSCRIBE_LOCK = threading.Lock()

app = Flask(__name__, static_folder=str(ROOT), static_url_path="")

@app.get("/health")
def health():
    return jsonify({
        "ok": True,
        "model": WHISPER_MODEL,
        "threads": WHISPER_THREADS,
        "timeout_sec": WHISPER_TIMEOUT_SEC,
        "whisper_bin": WHISPER_BIN,
        "whisper_exists": Path(WHISPER_BIN).exists(),
        "max_audio_mb": MAX_AUDIO_MB,
    })

@app.post("/transcribe")
def transcribe():
    if "audio" not in request.files:
        return jsonify({"ok": False, "error": "missing_audio"}), 400

    if request.content_length and request.content_length > (MAX_AUDIO_MB * 1024 * 1024):
        return jsonify({"ok": False, "error": "audio_too_large"}), 413

    if not TRANSCRIBE_LOCK.acquire(blocking=False):
        return jsonify({"ok": False, "error": "busy_transcribing"}), 429

    try:
        audio = request.files["audio"]
        suffix = Path(audio.filename or "clip.webm").suffix or ".webm"

        with tempfile.TemporaryDirectory(prefix="bob-voice-") as td:
            td_path = Path(td)
            in_file = td_path / f"input{suffix}"
            out_dir = td_path / "out"
            out_dir.mkdir(parents=True, exist_ok=True)
            audio.save(str(in_file))

            cmd = [
                WHISPER_BIN,
                str(in_file),
                "--model", WHISPER_MODEL,
                "--language", "en",
                "--output_format", "txt",
                "--output_dir", str(out_dir),
                "--threads", str(WHISPER_THREADS),
            ]

            if not Path(WHISPER_BIN).exists():
                return jsonify({"ok": False, "error": "whisper_not_found", "whisper_bin": WHISPER_BIN}), 500

            env = os.environ.copy()
            env["OMP_NUM_THREADS"] = str(WHISPER_THREADS)
            env["VECLIB_MAXIMUM_THREADS"] = str(WHISPER_THREADS)

            try:
                subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=WHISPER_TIMEOUT_SEC, env=env)
            except FileNotFoundError:
                return jsonify({"ok": False, "error": "whisper_not_found", "whisper_bin": WHISPER_BIN}), 500
            except subprocess.TimeoutExpired:
                return jsonify({"ok": False, "error": "whisper_timeout"}), 504
            except subprocess.CalledProcessError as e:
                return jsonify({
                    "ok": False,
                    "error": "whisper_failed",
                    "stderr": (e.stderr or "")[-2000:],
                }), 500

            txt_file = out_dir / f"{in_file.stem}.txt"
            if not txt_file.exists():
                return jsonify({"ok": False, "error": "transcript_missing"}), 500

            text = txt_file.read_text(encoding="utf-8").strip()
            return jsonify({"ok": True, "text": text})
    finally:
        TRANSCRIBE_LOCK.release()

@app.get("/")
def root():
    return send_from_directory(ROOT, "index.html")

@app.get("/<path:path>")
def static_proxy(path):
    return send_from_directory(ROOT, path)

if __name__ == "__main__":
    port = int(os.environ.get("BOB_VOICE_PORT", "8787"))
    print(f"Bob Voice Studio server on http://127.0.0.1:{port} (model={WHISPER_MODEL}, threads={WHISPER_THREADS}, timeout={WHISPER_TIMEOUT_SEC}s)")
    app.run(host="127.0.0.1", port=port, debug=False, threaded=False)
