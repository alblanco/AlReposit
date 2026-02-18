#!/usr/bin/env python3
import argparse
import hashlib
import json
import re
from pathlib import Path

import requests
from bs4 import BeautifulSoup

import arduino_kb_ingest as kb

KB_ROOT = Path('/Users/albertoblanco/Documents/Arduino-KB')
OUT_DIR = KB_ROOT / 'processed' / 'web'
CATALOG_DIR = KB_ROOT / 'catalog' / 'web'

DEFAULT_URLS = [
    'https://docs.arduino.cc/',
    'https://docs.arduino.cc/arduino-cli/getting-started/',
    'https://docs.arduino.cc/arduino-cli/sketch-build-process/',
    'https://learn.adafruit.com/adafruit-all-about-arduino-libraries-install-use',
    'https://learn.sparkfun.com/tutorials/installing-an-arduino-library',
    'https://learn.sparkfun.com/tutorials/how-to-install-ftdi-drivers',
    'https://github.com/arduino/ArduinoCore-avr',
    'https://github.com/esp8266/Arduino',
]


def slugify(u: str) -> str:
    s = re.sub(r'^https?://', '', u)
    s = re.sub(r'[^a-zA-Z0-9]+', '-', s).strip('-').lower()
    return s[:180]


def extract_text(html: str) -> str:
    soup = BeautifulSoup(html, 'html.parser')
    for tag in soup(['script', 'style', 'noscript', 'header', 'footer', 'nav']):
        tag.decompose()
    title = (soup.title.get_text(' ', strip=True) if soup.title else 'Untitled')
    body = soup.get_text('\n', strip=True)
    body = re.sub(r'\n{3,}', '\n\n', body)
    return f'# {title}\n\n{body}'


def ingest_url(url: str):
    headers = {'User-Agent': 'Mozilla/5.0 (OpenClaw Arduino KB Builder)'}
    r = requests.get(url, headers=headers, timeout=30)
    r.raise_for_status()
    text = extract_text(r.text)

    slug = slugify(url)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    CATALOG_DIR.mkdir(parents=True, exist_ok=True)

    md_path = OUT_DIR / f'{slug}.md'
    md_path.write_text(text, encoding='utf-8')

    sha = hashlib.sha256(text.encode('utf-8')).hexdigest()

    # Reuse SQLite index from KB by injecting as pseudo-doc
    doc_meta = {
        'doc_key': f'web-{slug}',
        'title': slug,
        'src_path': url,
        'sha256': sha,
        'pages': 1,
        'table_count': 0,
    }
    rec = kb.PageRecord(page=1, text=text, method='web', section='Web Document')
    chunks = kb.chunk_text([rec], max_chars=1600)
    db_path = KB_ROOT / 'index' / 'arduino_kb.sqlite'
    kb.upsert_index(db_path, doc_meta, chunks)

    (CATALOG_DIR / f'{slug}.json').write_text(json.dumps(doc_meta, indent=2), encoding='utf-8')


def load_urls(url_file: str | None) -> list[str]:
    urls: list[str] = []
    if url_file:
        p = Path(url_file).expanduser().resolve()
        for line in p.read_text(encoding='utf-8').splitlines():
            s = line.strip()
            if not s or s.startswith('#'):
                continue
            urls.append(s)
    else:
        urls.extend(DEFAULT_URLS)
    # De-duplicate preserving order
    seen = set()
    dedup = []
    for u in urls:
        if u in seen:
            continue
        seen.add(u)
        dedup.append(u)
    return dedup


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--url-file', help='Path to newline-separated URL list')
    args = ap.parse_args()

    urls = load_urls(args.url_file)
    results = {'ok': [], 'failed': []}
    total = len(urls)
    for i, u in enumerate(urls, start=1):
        try:
            ingest_url(u)
            results['ok'].append(u)
            print(f'[web-ingest] {i}/{total} OK: {u}', flush=True)
        except Exception as e:
            results['failed'].append({'url': u, 'error': str(e)})
            print(f'[web-ingest] {i}/{total} FAIL: {u} :: {e}', flush=True)

    log = KB_ROOT / 'logs' / 'web_ingest_report.json'
    log.write_text(json.dumps(results, indent=2), encoding='utf-8')
    print(json.dumps({'ok': len(results['ok']), 'failed': len(results['failed']), 'log': str(log)}, indent=2))


if __name__ == '__main__':
    main()
