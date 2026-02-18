# Graphics Pipeline (Ingest + Display + Conversion)

This adds a robust local graphics capability for agent workflows.

## Goals
- Reliable ingestion of graphics into local storage
- Stable workspace layout for processing pipelines
- Multi-backend conversions for professional formats
- Preview generation for inline display and web gallery use
- Auditability via manifest + logs

## Script
- `graphics_pipeline.py`

## Directory layout
Default root is `./graphics` (override with `--root`):

- `incoming/` raw drop zone
- `store/` content-addressed immutable assets (`sha256` names)
- `work/normalized/` normalized intermediates
- `work/previews/` preview PNGs
- `exports/` explicit conversions
- `meta/manifest.jsonl` asset metadata index
- `logs/` ingest/processing reports
- `gallery.html` visual browser

## Supported formats (tool-dependent)
- Raster: PNG, JPG/JPEG, WEBP, GIF, TIFF, BMP, HEIC/HEIF, AVIF
- Vector: SVG, PDF, EPS/PS, AI
- Motion previews: MP4/MOV/MKV/AVI/WEBM

## Backends and fallbacks
The pipeline automatically chooses available tools:
1. `ffmpeg` (video frame extraction)
2. `inkscape` / `rsvg-convert` (SVG rasterization)
3. `magick` (ImageMagick universal conversion)
4. `gs` (Ghostscript PDF to image fallback)
5. `sips` (macOS raster fallback)

If no backend exists for a conversion pair, it reports a clear error.

## Usage

### 1) Initialize
```bash
python3 graphics_pipeline.py --root ./graphics init
```

### 2) Ingest files/folders (recursive)
```bash
python3 graphics_pipeline.py --root ./graphics ingest ./some_images ./docs/diagram.pdf
```

### 3) Inspect one asset by id
```bash
python3 graphics_pipeline.py --root ./graphics inspect --id <asset_id>
```

### 4) Convert by id to webp
```bash
python3 graphics_pipeline.py --root ./graphics convert --id <asset_id> --to webp
```

### 5) Convert direct file to png
```bash
python3 graphics_pipeline.py --root ./graphics convert --input ./foo.svg --to png
```

### 6) Build gallery
```bash
python3 graphics_pipeline.py --root ./graphics gallery
```
Open `graphics/gallery.html` in a browser.

## Inline display strategy in chat
- Generate preview PNGs in `work/previews/`
- Send them as chat attachments (or display in UI components)
- For large diagrams, send both:
  - downscaled preview (inline)
  - original/high-res export path (download)

## Professional pipeline ideas
- PDF/SVG/AI -> normalized SVG + PNG previews
- PSD/TIFF archival -> layered/source retained + web preview
- Video capture -> keyframe PNG + MP4 proxy
- CAD/docs ingestion -> convert-to-preview + metadata tagging

## Notes
- Content-addressed storage prevents dupes.
- Manifest supports downstream search/indexing.
- Logs make pipeline runs reproducible.
