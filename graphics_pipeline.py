#!/usr/bin/env python3
"""
Robust local graphics ingestion + display pipeline.

Features
- Local workspace storage with content-addressed files
- Work directories for normalized assets, previews, and exports
- Format-aware conversion pipeline with multiple backend fallbacks
- Batch ingestion and gallery HTML generation
- Professional format support via optional system tools

Supported (depending on installed tools):
- Raster: png, jpg/jpeg, webp, tiff, bmp, gif, heic/heif, avif
- Vector: svg, pdf, eps, ai (tool-dependent)
- Design/docs: psd, tga, dxf, odg (tool-dependent)
- Motion: mp4/mov/webm/gif (first-frame previews via ffmpeg)
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import mimetypes
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Iterable

ROOT_DEFAULT = Path("./graphics")

RASTER_EXT = {
    ".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp", ".tif", ".tiff", ".heic", ".heif", ".avif"
}
VECTOR_EXT = {".svg", ".pdf", ".eps", ".ps", ".ai"}
VIDEO_EXT = {".mp4", ".mov", ".mkv", ".avi", ".webm", ".m4v", ".gifv"}


def now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def sha256_file(path: Path, chunk: int = 1024 * 1024) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            b = f.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def has(bin_name: str) -> bool:
    return shutil.which(bin_name) is not None


def run(cmd: list[str]) -> tuple[int, str, str]:
    p = subprocess.run(cmd, capture_output=True, text=True)
    return p.returncode, p.stdout.strip(), p.stderr.strip()


def ensure_tree(root: Path) -> dict[str, Path]:
    dirs = {
        "root": root,
        "incoming": root / "incoming",
        "store": root / "store",
        "work": root / "work",
        "normalized": root / "work" / "normalized",
        "previews": root / "work" / "previews",
        "exports": root / "exports",
        "meta": root / "meta",
        "logs": root / "logs",
    }
    for d in dirs.values():
        d.mkdir(parents=True, exist_ok=True)
    (dirs["meta"] / "manifest.jsonl").touch(exist_ok=True)
    return dirs


def load_manifest(path: Path) -> dict[str, dict]:
    out: dict[str, dict] = {}
    if not path.exists():
        return out
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            s = line.strip()
            if not s:
                continue
            obj = json.loads(s)
            out[obj["id"]] = obj
    return out


def append_manifest(path: Path, item: dict) -> None:
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(item, ensure_ascii=False) + "\n")


def ext_of(path: Path) -> str:
    return path.suffix.lower()


def kind_for(path: Path) -> str:
    e = ext_of(path)
    if e in VIDEO_EXT:
        return "video"
    if e in VECTOR_EXT:
        return "vector"
    return "raster"


def detect_mime(path: Path) -> str:
    m, _ = mimetypes.guess_type(path.name)
    return m or "application/octet-stream"


def ingest_file(path: Path, dirs: dict[str, Path], manifest: dict[str, dict]) -> dict:
    src = path.resolve()
    digest = sha256_file(src)
    fid = digest[:16]
    e = ext_of(src) or ""

    if fid in manifest:
        return {"status": "exists", "id": fid, "path": manifest[fid]["storedPath"]}

    dest = dirs["store"] / digest[:2] / f"{digest}{e}"
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)

    item = {
        "id": fid,
        "sha256": digest,
        "ingestedAt": now_iso(),
        "sourcePath": str(src),
        "storedPath": str(dest),
        "filename": src.name,
        "ext": e,
        "mime": detect_mime(src),
        "sizeBytes": src.stat().st_size,
        "kind": kind_for(src),
        "tags": [],
    }
    append_manifest(dirs["meta"] / "manifest.jsonl", item)
    return {"status": "ingested", "id": fid, "path": str(dest)}


def choose_convert_backend(src: Path, dst: Path) -> tuple[str, list[str]]:
    se, de = ext_of(src), ext_of(dst)

    # video -> image preview
    if se in VIDEO_EXT and de in {".png", ".jpg", ".jpeg", ".webp"} and has("ffmpeg"):
        return "ffmpeg", ["ffmpeg", "-y", "-i", str(src), "-frames:v", "1", str(dst)]

    # vector -> raster via inkscape/rsvg/gs/magick
    if se == ".svg" and de in {".png", ".jpg", ".jpeg", ".webp"}:
        if has("inkscape"):
            return "inkscape", ["inkscape", str(src), "--export-filename", str(dst)]
        if has("rsvg-convert") and de == ".png":
            return "rsvg-convert", ["rsvg-convert", "-o", str(dst), str(src)]
        if has("magick"):
            return "magick", ["magick", str(src), str(dst)]

    if se == ".pdf" and de in {".png", ".jpg", ".jpeg"}:
        if has("magick"):
            return "magick", ["magick", f"{src}[0]", str(dst)]
        if has("gs") and de == ".png":
            return "ghostscript", [
                "gs", "-dSAFER", "-dBATCH", "-dNOPAUSE", "-sDEVICE=png16m", "-r144",
                f"-sOutputFile={dst}", str(src)
            ]

    # generic conversion
    if has("magick"):
        return "magick", ["magick", str(src), str(dst)]

    # macOS fallback for raster
    if sys.platform == "darwin" and has("sips") and se in RASTER_EXT and de in {".png", ".jpg", ".jpeg", ".tiff"}:
        fmt = de.lstrip(".")
        if fmt == "jpg":
            fmt = "jpeg"
        return "sips", ["sips", "-s", "format", fmt, str(src), "--out", str(dst)]

    return "", []


def convert_file(src: Path, dst: Path) -> dict:
    dst.parent.mkdir(parents=True, exist_ok=True)
    backend, cmd = choose_convert_backend(src, dst)
    if not cmd:
        # macOS QuickLook fallback for png previews/conversions
        if dst.suffix.lower() == ".png" and sys.platform == "darwin":
            return quicklook_preview(src, dst)
        return {"ok": False, "error": f"No conversion backend for {src.suffix} -> {dst.suffix}"}

    code, out, err = run(cmd)
    if code != 0:
        return {"ok": False, "backend": backend, "cmd": cmd, "stderr": err, "stdout": out}
    if not dst.exists():
        return {"ok": False, "backend": backend, "cmd": cmd, "error": "converter returned success but output missing"}
    return {"ok": True, "backend": backend, "out": str(dst)}


def quicklook_preview(src: Path, dst_png: Path) -> dict:
    """macOS fallback using qlmanage thumbnail generation."""
    if sys.platform != "darwin" or not has("qlmanage"):
        return {"ok": False, "error": "quicklook unavailable"}

    tmpdir = dst_png.parent / f".ql-{dst_png.stem}"
    tmpdir.mkdir(parents=True, exist_ok=True)
    code, out, err = run(["qlmanage", "-t", "-s", "1024", "-o", str(tmpdir), str(src)])
    if code != 0:
        return {"ok": False, "backend": "qlmanage", "stderr": err, "stdout": out}

    candidate = tmpdir / f"{src.name}.png"
    if not candidate.exists():
        # Some variants may produce basename without full extension chain.
        cands = list(tmpdir.glob("*.png"))
        if not cands:
            return {"ok": False, "backend": "qlmanage", "error": "thumbnail not generated"}
        candidate = cands[0]

    shutil.move(str(candidate), str(dst_png))
    shutil.rmtree(tmpdir, ignore_errors=True)
    return {"ok": True, "backend": "qlmanage", "out": str(dst_png)}


def to_preview(src: Path, previews_dir: Path, base_id: str) -> dict:
    out = previews_dir / f"{base_id}.png"
    r = convert_file(src, out)
    if r.get("ok"):
        return r
    # Last-resort macOS preview fallback for unsupported but previewable formats
    if sys.platform == "darwin":
        qr = quicklook_preview(src, out)
        if qr.get("ok"):
            return qr
    return r


def iter_inputs(inputs: list[str], recursive: bool = True) -> Iterable[Path]:
    for x in inputs:
        p = Path(x).expanduser()
        if p.is_file():
            yield p
        elif p.is_dir():
            it = p.rglob("*") if recursive else p.glob("*")
            for c in it:
                if c.is_file():
                    yield c


def cmd_init(args):
    dirs = ensure_tree(Path(args.root).expanduser().resolve())
    print(json.dumps({"ok": True, "root": str(dirs["root"])}))


def cmd_ingest(args):
    root = Path(args.root).expanduser().resolve()
    dirs = ensure_tree(root)
    manifest_path = dirs["meta"] / "manifest.jsonl"
    existing = load_manifest(manifest_path)

    results = []
    for f in iter_inputs(args.inputs, recursive=not args.no_recursive):
        try:
            r = ingest_file(f, dirs, existing)
            if r["status"] == "ingested":
                existing[r["id"]] = {"storedPath": r["path"]}
            results.append({"file": str(f), **r})
        except Exception as e:
            results.append({"file": str(f), "status": "error", "error": str(e)})

    # preview generation pass
    manifest = load_manifest(manifest_path)
    preview_results = []
    for fid, item in manifest.items():
        src = Path(item["storedPath"])
        if not src.exists():
            continue
        pr = to_preview(src, dirs["previews"], fid)
        preview_results.append({"id": fid, **pr})

    ok_previews = sum(1 for x in preview_results if x.get("ok"))
    out = {"ok": True, "ingested": results, "preview": preview_results}
    log = dirs["logs"] / f"ingest-{dt.datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
    log.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps({"ok": True, "files": len(results), "log": str(log), "previews_ok": ok_previews, "previews_total": len(preview_results)}))


def cmd_inspect(args):
    root = Path(args.root).expanduser().resolve()
    m = load_manifest(root / "meta" / "manifest.jsonl")
    item = m.get(args.id)
    if not item:
        print(json.dumps({"ok": False, "error": "id not found"}))
        return
    print(json.dumps({"ok": True, "item": item}, indent=2))


def cmd_convert(args):
    root = Path(args.root).expanduser().resolve()
    dirs = ensure_tree(root)

    src: Path
    if args.id:
        m = load_manifest(dirs["meta"] / "manifest.jsonl")
        if args.id not in m:
            print(json.dumps({"ok": False, "error": "id not found"}))
            return
        src = Path(m[args.id]["storedPath"])
        name = Path(m[args.id]["filename"]).stem
    else:
        src = Path(args.input).expanduser().resolve()
        name = src.stem

    if args.out:
        dst = Path(args.out).expanduser().resolve()
    else:
        ext = args.to if args.to.startswith(".") else f".{args.to}"
        dst = dirs["exports"] / f"{name}{ext}"

    r = convert_file(src, dst)
    print(json.dumps(r, indent=2))


def cmd_gallery(args):
    root = Path(args.root).expanduser().resolve()
    dirs = ensure_tree(root)
    m = load_manifest(dirs["meta"] / "manifest.jsonl")

    cards = []
    for fid, item in m.items():
        p = dirs["previews"] / f"{fid}.png"
        if not p.exists():
            continue
        cards.append((fid, item, p))

    html = [
        "<!doctype html><html><head><meta charset='utf-8'><title>Graphics Gallery</title>",
        "<style>body{font-family:system-ui;background:#111;color:#eee} .grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:14px} .card{background:#1a1a1a;padding:10px;border-radius:10px} img{max-width:100%;height:auto;border-radius:8px} .muted{color:#aaa;font-size:12px;word-break:break-all}</style>",
        "</head><body><h1>Graphics Gallery</h1><div class='grid'>",
    ]
    for fid, item, p in cards:
        html.append(
            f"<div class='card'><img src='{p.relative_to(root)}' alt='{item['filename']}'/>"
            f"<div><b>{item['filename']}</b></div><div class='muted'>{fid} · {item['mime']} · {item['sizeBytes']} bytes</div></div>"
        )
    html.append("</div></body></html>")

    out = root / "gallery.html"
    out.write_text("\n".join(html), encoding="utf-8")
    print(json.dumps({"ok": True, "gallery": str(out), "items": len(cards)}))


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Graphics ingest + conversion + display pipeline")
    p.add_argument("--root", default=str(ROOT_DEFAULT), help="Pipeline root directory")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("init")

    ing = sub.add_parser("ingest")
    ing.add_argument("inputs", nargs="+", help="Files and/or directories to ingest")
    ing.add_argument("--no-recursive", action="store_true")

    insp = sub.add_parser("inspect")
    insp.add_argument("--id", required=True)

    conv = sub.add_parser("convert")
    g = conv.add_mutually_exclusive_group(required=True)
    g.add_argument("--id")
    g.add_argument("--input")
    conv.add_argument("--to", help="Output extension, e.g. png, webp, jpg")
    conv.add_argument("--out", help="Explicit output path")

    sub.add_parser("gallery")
    return p


def main():
    p = parser()
    args = p.parse_args()

    if args.cmd == "init":
        cmd_init(args)
    elif args.cmd == "ingest":
        cmd_ingest(args)
    elif args.cmd == "inspect":
        cmd_inspect(args)
    elif args.cmd == "convert":
        cmd_convert(args)
    elif args.cmd == "gallery":
        cmd_gallery(args)


if __name__ == "__main__":
    main()
