#!/usr/bin/env python3
import os
import subprocess
import tempfile
from pathlib import Path
from flask import Flask, jsonify, request, send_from_directory

ROOT = Path(__file__).resolve().parent
WHISPER_MODEL = os.environ.get("BOB_WHISPER_MODEL", "turbo")
app = Flask(__name__, static_folder=str(ROOT), static_url_path="")

@app.get("/health")
def health():
    return jsonify({"ok": True, "model": WHISPER_MODEL})

@app.post("/transcribe")
def transcribe():
    if "audio" not in request.files:
        return jsonify({"ok": False, "error": "missing_audio"}), 400

    audio = request.files["audio"]
    suffix = Path(audio.filename or "clip.webm").suffix or ".webm"

    with tempfile.TemporaryDirectory(prefix="bob-voice-") as td:
        td_path = Path(td)
        in_file = td_path / f"input{suffix}"
        out_dir = td_path / "out"
        out_dir.mkdir(parents=True, exist_ok=True)
        audio.save(str(in_file))

        cmd = [
            "whisper", str(in_file),
            "--model", WHISPER_MODEL,
            "--language", "en",
            "--output_format", "txt",
            "--output_dir", str(out_dir),
        ]

        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
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

@app.get("/")
def root():
    return send_from_directory(ROOT, "index.html")

@app.get("/<path:path>")
def static_proxy(path):
    return send_from_directory(ROOT, path)

if __name__ == "__main__":
    port = int(os.environ.get("BOB_VOICE_PORT", "8787"))
    print(f"Bob Voice Studio server on http://127.0.0.1:{port} (model={WHISPER_MODEL})")
    app.run(host="127.0.0.1", port=port, debug=False)
