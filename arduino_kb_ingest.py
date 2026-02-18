#!/usr/bin/env python3
import argparse
import csv
import hashlib
import json
import os
import re
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple

import pdfplumber
import pytesseract
from pypdf import PdfReader
import pypdfium2 as pdfium

HEADING_RE = re.compile(r"^([A-Z][A-Za-z0-9 ,()\-_/]{3,80})$")


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
    text = pytesseract.image_to_string(pil)
    return (text or "").strip()


def find_heading_candidates(text: str) -> List[str]:
    headings = []
    for line in text.splitlines()[:80]:
        s = line.strip()
        if not s:
            continue
        if len(s) > 90:
            continue
        if HEADING_RE.match(s):
            headings.append(s)
    return headings


def extract_tables(pdf_path: Path, out_dir: Path, base_slug: str) -> int:
    count = 0
    with pdfplumber.open(str(pdf_path)) as pdf:
        for i, page in enumerate(pdf.pages, start=1):
            tables = page.extract_tables() or []
            for t_idx, table in enumerate(tables, start=1):
                if not table:
                    continue
                csv_path = out_dir / f"{base_slug}__p{i}__t{t_idx}.csv"
                with csv_path.open("w", newline="", encoding="utf-8") as f:
                    w = csv.writer(f)
                    for row in table:
                        w.writerow([c if c is not None else "" for c in row])
                count += 1
    return count


def build_page_records(pdf_path: Path, ocr_min_chars: int = 80) -> List[PageRecord]:
    texts = extract_text_pagewise(pdf_path)
    records: List[PageRecord] = []
    current_section = "Document Start"
    for i, txt in enumerate(texts, start=1):
        method = "text"
        content = txt
        if len(content) < ocr_min_chars:
            try:
                ocr_txt = ocr_page(pdf_path, i - 1)
                if len(ocr_txt) > len(content):
                    content = ocr_txt
                    method = "ocr"
            except Exception:
                pass

        for h in find_heading_candidates(content):
            current_section = h
            break

        records.append(PageRecord(page=i, text=content, method=method, section=current_section))
    return records


def write_markdown(records: List[PageRecord], src: Path, out_md: Path):
    lines = [f"# {src.name}", "", f"Source: {src}", ""]
    for r in records:
        lines.append(f"## Page {r.page} | Section: {r.section} | Method: {r.method}")
        lines.append("")
        lines.append(r.text if r.text else "[No text extracted]")
        lines.append("")
    out_md.write_text("\n".join(lines), encoding="utf-8")


def chunk_text(records: List[PageRecord], max_chars: int = 1800) -> List[dict]:
    chunks = []
    for r in records:
        txt = (r.text or "").strip()
        if not txt:
            continue
        start = 0
        while start < len(txt):
            part = txt[start : start + max_chars]
            chunks.append(
                {
                    "page": r.page,
                    "section": r.section,
                    "method": r.method,
                    "text": part,
                }
            )
            start += max_chars
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

    records = build_page_records(pdf_path)

    md_path = kb_root / "processed" / "text" / f"{slug}.md"
    write_markdown(records, pdf_path, md_path)

    table_count = extract_tables(pdf_path, kb_root / "processed" / "tables", slug)

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

    catalog_file.write_text(json.dumps(doc_meta, indent=2), encoding="utf-8")

    db_path = kb_root / "index" / "arduino_kb.sqlite"
    upsert_index(db_path, doc_meta, chunks)

    return True, doc_meta


def search(db_path: Path, query: str, limit: int = 8) -> List[dict]:
    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()
    cur.execute(
        """
        SELECT title, section, snippet(chunks_fts, 3, '[', ']', ' … ', 20), citation
        FROM chunks_fts
        WHERE chunks_fts MATCH ?
        LIMIT ?
        """,
        (query, limit),
    )
    rows = cur.fetchall()
    conn.close()
    return [
        {"title": r[0], "section": r[1], "snippet": r[2], "citation": r[3]} for r in rows
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
        log_file.write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(json.dumps({
            "found_pdfs": report["found_pdfs"],
            "ingested": report["ingested"],
            "skipped": report["skipped"],
            "errors": len(report["errors"]),
            "log": str(log_file),
            "db": str(kb_root / "index" / "arduino_kb.sqlite"),
        }, indent=2))

    elif args.cmd == "search":
        kb_root = Path(args.kb_root).expanduser().resolve()
        db = kb_root / "index" / "arduino_kb.sqlite"
        results = search(db, args.q, args.limit)
        print(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
