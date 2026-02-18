#!/usr/bin/env python3
import argparse
import csv
import hashlib
import json
import re
import shutil
import sqlite3
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple

import pdfplumber
import pypdfium2 as pdfium
import pytesseract
from pypdf import PdfReader

# Better heading recognition for datasheets/manuals
NUMBERED_HEADING_RE = re.compile(r"^(\d+(?:\.\d+)*)(?:\s+|\s*[-:)–]\s*)(.{2,120})$")
ALL_CAPS_HEADING_RE = re.compile(r"^[A-Z][A-Z0-9 ,()\-_/]{4,120}$")
TITLE_CASE_HEADING_RE = re.compile(
    r"^(?:[A-Z][a-z0-9]+(?:\s+|$)){2,12}(?:\([^)]+\))?$"
)


@dataclass
class PageRecord:
    page: int
    text: str
    method: str  # text|ocr
    section: str


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def ensure_dirs(base: Path):
    for p in [
        base / "raw",
        base / "processed" / "text",
        base / "processed" / "tables",
        base / "index",
        base / "catalog",
        base / "logs",
    ]:
        p.mkdir(parents=True, exist_ok=True)


def slugify(name: str) -> str:
    name = re.sub(r"\s+", "-", name.strip().lower())
    name = re.sub(r"[^a-z0-9._-]", "", name)
    return name[:180] if name else "doc"


def retry_io(func, retries: int = 4, base_sleep: float = 0.2):
    last = None
    for i in range(retries):
        try:
            return func()
        except OSError as e:
            last = e
            if getattr(e, "errno", None) == 11 and i < retries - 1:
                time.sleep(base_sleep * (2**i))
                continue
            raise
    if last:
        raise last


def safe_write_text(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)

    def _write():
        with tempfile.NamedTemporaryFile("w", delete=False, dir=str(path.parent), encoding="utf-8") as tmp:
            tmp.write(content)
            tmp.flush()
            tmp_name = tmp.name
        Path(tmp_name).replace(path)

    retry_io(_write)


def materialize_local_pdf(src: Path) -> Path:
    """Copy source PDF to a local temp file to avoid cloud-lock/deadlock issues."""

    def _copy() -> Path:
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        tmp_path = Path(tmp.name)
        tmp.close()
        shutil.copyfile(src, tmp_path)
        return tmp_path

    return retry_io(_copy)


def extract_text_pagewise(pdf_path: Path) -> List[str]:
    reader = PdfReader(str(pdf_path))
    out = []
    for page in reader.pages:
        out.append((page.extract_text() or "").strip())
    return out


def ocr_page(pdf_path: Path, page_idx_zero: int, scale: float = 2.0) -> str:
    pdf = pdfium.PdfDocument(str(pdf_path))
    page = pdf[page_idx_zero]
    bmp = page.render(scale=scale)
    pil = bmp.to_pil()
    txt = pytesseract.image_to_string(pil)
    return (txt or "").strip()


def normalize_line(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip())


def find_best_heading(text: str) -> str | None:
    lines = [normalize_line(x) for x in text.splitlines() if x.strip()]
    for line in lines[:50]:
        if len(line) > 140:
            continue
        m = NUMBERED_HEADING_RE.match(line)
        if m:
            return f"{m.group(1)} {m.group(2)}"
        if ALL_CAPS_HEADING_RE.match(line):
            return line
        if TITLE_CASE_HEADING_RE.match(line):
            banned = {"Table", "Figure", "Page", "Source", "Copyright"}
            if not any(line.startswith(b) for b in banned):
                return line
    return None


def extract_tables(pdf_path: Path, out_dir: Path, base_slug: str) -> int:
    count = 0
    tables_manifest = []

    line_settings = {
        "vertical_strategy": "lines",
        "horizontal_strategy": "lines",
        "intersection_tolerance": 8,
    }
    text_settings = {
        "vertical_strategy": "text",
        "horizontal_strategy": "text",
        "snap_tolerance": 3,
        "join_tolerance": 3,
    }

    with pdfplumber.open(str(pdf_path)) as pdf:
        for i, page in enumerate(pdf.pages, start=1):
            candidates = []
            for settings, label in [(line_settings, "lines"), (text_settings, "text")]:
                try:
                    tables = page.extract_tables(table_settings=settings) or []
                    for t in tables:
                        if not t:
                            continue
                        rows = len(t)
                        cols = max((len(r) for r in t if r), default=0)
                        cells = rows * cols
                        candidates.append((cells, rows, cols, t, label))
                except Exception:
                    continue

            # Deduplicate by shape and first-row signature; keep denser table
            seen = set()
            picked = []
            for _, rows, cols, t, label in sorted(
                candidates, key=lambda x: (x[0], x[1], x[2]), reverse=True
            ):
                first_row = (t[0] if t else [])[:6] if t else []
                first = "|".join("" if c is None else str(c) for c in first_row)
                sig = (rows, cols, first[:120])
                if sig in seen:
                    continue
                seen.add(sig)
                picked.append((t, label, rows, cols))

            for t_idx, (table, method, rows, cols) in enumerate(picked, start=1):
                csv_path = out_dir / f"{base_slug}__p{i}__t{t_idx}.csv"

                def _write_csv():
                    with csv_path.open("w", newline="", encoding="utf-8") as f:
                        w = csv.writer(f)
                        for row in table:
                            w.writerow([c if c is not None else "" for c in row])

                retry_io(_write_csv)
                tables_manifest.append(
                    {
                        "page": i,
                        "table_index": t_idx,
                        "rows": rows,
                        "cols": cols,
                        "method": method,
                        "csv": str(csv_path),
                    }
                )
                count += 1

    manifest_path = out_dir / f"{base_slug}__tables.json"
    safe_write_text(manifest_path, json.dumps(tables_manifest, indent=2))
    return count


def build_page_records(pdf_path: Path, ocr_min_chars: int = 120) -> List[PageRecord]:
    texts = extract_text_pagewise(pdf_path)
    records: List[PageRecord] = []
    current_section = "Document Start"

    for i, txt in enumerate(texts, start=1):
        method = "text"
        content = txt

        # OCR fallback for sparse pages
        if len(content) < ocr_min_chars:
            try:
                ocr_txt = ocr_page(pdf_path, i - 1)
                if len(ocr_txt) > len(content):
                    content = ocr_txt
                    method = "ocr"
            except Exception:
                pass

        heading = find_best_heading(content)
        if heading:
            current_section = heading

        records.append(PageRecord(page=i, text=content, method=method, section=current_section))

    return records


def write_markdown(records: List[PageRecord], src: Path, out_md: Path):
    lines = [f"# {src.name}", "", f"Source: {src}", ""]
    for r in records:
        lines.append(f"## Page {r.page} | Section: {r.section} | Method: {r.method}")
        lines.append("")
        lines.append(r.text if r.text else "[No text extracted]")
        lines.append("")
    safe_write_text(out_md, "\n".join(lines))


def chunk_text(records: List[PageRecord], max_chars: int = 1600) -> List[dict]:
    chunks = []
    for r in records:
        txt = (r.text or "").strip()
        if not txt:
            continue

        # Prefer paragraph boundaries for cleaner snippets
        paras = [p.strip() for p in re.split(r"\n\s*\n", txt) if p.strip()]
        if not paras:
            paras = [txt]

        buf = ""
        for p in paras:
            if len(buf) + len(p) + 2 <= max_chars:
                buf = (buf + "\n\n" + p).strip()
            else:
                if buf:
                    chunks.append(
                        {
                            "page": r.page,
                            "section": r.section,
                            "method": r.method,
                            "text": buf,
                        }
                    )
                if len(p) <= max_chars:
                    buf = p
                else:
                    # hard split oversized paragraphs
                    for i in range(0, len(p), max_chars):
                        chunks.append(
                            {
                                "page": r.page,
                                "section": r.section,
                                "method": r.method,
                                "text": p[i : i + max_chars],
                            }
                        )
                    buf = ""
        if buf:
            chunks.append(
                {
                    "page": r.page,
                    "section": r.section,
                    "method": r.method,
                    "text": buf,
                }
            )
    return chunks


def upsert_index(db_path: Path, doc_meta: dict, chunks: List[dict]):
    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS docs (
            id INTEGER PRIMARY KEY,
            doc_key TEXT UNIQUE,
            title TEXT,
            src_path TEXT,
            sha256 TEXT,
            pages INTEGER,
            table_count INTEGER,
            ingested_at TEXT
        )
        """
    )
    cur.execute(
        """
        CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts
        USING fts5(
            doc_key,
            title,
            section,
            text,
            citation,
            tokenize='unicode61'
        )
        """
    )

    cur.execute(
        """
        INSERT INTO docs (doc_key, title, src_path, sha256, pages, table_count, ingested_at)
        VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
        ON CONFLICT(doc_key) DO UPDATE SET
          title=excluded.title,
          src_path=excluded.src_path,
          sha256=excluded.sha256,
          pages=excluded.pages,
          table_count=excluded.table_count,
          ingested_at=datetime('now')
        """,
        (
            doc_meta["doc_key"],
            doc_meta["title"],
            doc_meta["src_path"],
            doc_meta["sha256"],
            doc_meta["pages"],
            doc_meta["table_count"],
        ),
    )

    cur.execute("DELETE FROM chunks_fts WHERE doc_key=?", (doc_meta["doc_key"],))
    for c in chunks:
        citation = (
            f"Source: {doc_meta['src_path']} | page {c['page']} | section: {c['section']} | method: {c['method']}"
        )
        cur.execute(
            "INSERT INTO chunks_fts (doc_key, title, section, text, citation) VALUES (?, ?, ?, ?, ?)",
            (doc_meta["doc_key"], doc_meta["title"], c["section"], c["text"], citation),
        )

    conn.commit()
    conn.close()


def ingest_pdf(pdf_path: Path, kb_root: Path, force: bool = False) -> Tuple[bool, dict]:
    ensure_dirs(kb_root)
    slug = slugify(pdf_path.stem)
    doc_key = slug

    sha = sha256_file(pdf_path)
    catalog_file = kb_root / "catalog" / f"{slug}.json"
    if catalog_file.exists() and not force:
        try:
            old = json.loads(catalog_file.read_text(encoding="utf-8"))
            if old.get("sha256") == sha:
                return False, {"doc_key": doc_key, "status": "unchanged"}
        except Exception:
            pass

    temp_pdf = materialize_local_pdf(pdf_path)
    try:
        records = build_page_records(temp_pdf)

        md_path = kb_root / "processed" / "text" / f"{slug}.md"
        write_markdown(records, pdf_path, md_path)

        table_count = extract_tables(temp_pdf, kb_root / "processed" / "tables", slug)
    finally:
        try:
            temp_pdf.unlink(missing_ok=True)
        except Exception:
            pass

    chunks = chunk_text(records)
    doc_meta = {
        "doc_key": doc_key,
        "title": pdf_path.name,
        "src_path": str(pdf_path),
        "sha256": sha,
        "pages": len(records),
        "table_count": table_count,
        "processed_markdown": str(md_path),
        "tables_path": str(kb_root / "processed" / "tables"),
    }

    safe_write_text(catalog_file, json.dumps(doc_meta, indent=2))

    db_path = kb_root / "index" / "arduino_kb.sqlite"
    upsert_index(db_path, doc_meta, chunks)

    return True, doc_meta


def search(db_path: Path, query: str, limit: int = 8) -> List[dict]:
    if not db_path.exists():
        return []

    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()
    try:
        cur.execute(
            """
            SELECT title,
                   section,
                   snippet(chunks_fts, 3, '[', ']', ' … ', 20) AS snip,
                   citation,
                   bm25(chunks_fts) AS score
            FROM chunks_fts
            WHERE chunks_fts MATCH ?
            ORDER BY score
            LIMIT ?
            """,
            (query, limit),
        )
    except sqlite3.OperationalError:
        conn.close()
        return []

    rows = cur.fetchall()
    conn.close()
    return [
        {
            "title": r[0],
            "section": r[1],
            "snippet": r[2],
            "citation": r[3],
            "score": r[4],
        }
        for r in rows
    ]


def main():
    p = argparse.ArgumentParser(description="Arduino KB ingester with OCR and detailed citations")
    sub = p.add_subparsers(dest="cmd", required=True)

    ing = sub.add_parser("ingest")
    ing.add_argument("--source", required=True, help="Source directory to scan for PDFs")
    ing.add_argument("--kb-root", required=True, help="KB root directory")
    ing.add_argument("--force", action="store_true")

    sea = sub.add_parser("search")
    sea.add_argument("--kb-root", required=True)
    sea.add_argument("--q", required=True)
    sea.add_argument("--limit", type=int, default=8)

    args = p.parse_args()

    if args.cmd == "ingest":
        src = Path(args.source).expanduser().resolve()
        kb_root = Path(args.kb_root).expanduser().resolve()
        ensure_dirs(kb_root)

        pdfs = sorted(src.rglob("*.pdf"))
        report = {
            "source": str(src),
            "kb_root": str(kb_root),
            "found_pdfs": len(pdfs),
            "ingested": 0,
            "skipped": 0,
            "errors": [],
            "docs": [],
        }

        for pdf in pdfs:
            try:
                changed, meta = ingest_pdf(pdf, kb_root, force=args.force)
                if changed:
                    report["ingested"] += 1
                    report["docs"].append(meta)
                else:
                    report["skipped"] += 1
            except Exception as e:
                report["errors"].append({"file": str(pdf), "error": str(e)})

        log_file = kb_root / "logs" / "last_ingest_report.json"
        safe_write_text(log_file, json.dumps(report, indent=2))
        print(
            json.dumps(
                {
                    "found_pdfs": report["found_pdfs"],
                    "ingested": report["ingested"],
                    "skipped": report["skipped"],
                    "errors": len(report["errors"]),
                    "log": str(log_file),
                    "db": str(kb_root / "index" / "arduino_kb.sqlite"),
                },
                indent=2,
            )
        )

    elif args.cmd == "search":
        kb_root = Path(args.kb_root).expanduser().resolve()
        db = kb_root / "index" / "arduino_kb.sqlite"
        results = search(db, args.q, args.limit)
        print(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
