# Arduino KB

## What this does
- Scans a source folder for PDFs
- Extracts text page-by-page
- Runs OCR fallback for low-text pages
- Extracts tables to CSV when possible
- Stores searchable full-text index in SQLite FTS5
- Returns detailed citations (`file + page + section + extraction method`)

## Setup
```bash
cd /Users/albertoblanco/.openclaw/workspace
python3 -m venv .venv-kb
. .venv-kb/bin/activate
pip install pypdf pypdfium2 pytesseract pdfplumber
```

## Ingest
```bash
. .venv-kb/bin/activate
python arduino_kb_ingest.py ingest \
  --source /Users/albertoblanco/Documents/Arduino \
  --kb-root /Users/albertoblanco/Documents/Arduino-KB
```

## Search
```bash
. .venv-kb/bin/activate
python arduino_kb_ingest.py search \
  --kb-root /Users/albertoblanco/Documents/Arduino-KB \
  --q "ESP8266 operating voltage" --limit 5
```

## Outputs
- `catalog/*.json` metadata per document
- `processed/text/*.md` extracted page text
- `processed/tables/*.csv` extracted tables
- `index/arduino_kb.sqlite` searchable index
- `logs/last_ingest_report.json` latest ingest summary
