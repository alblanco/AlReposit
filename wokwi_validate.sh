#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <project_dir_with_diagram_json>"
  exit 1
fi

PROJECT_DIR="$1"
DIAGRAM="$PROJECT_DIR/diagram.json"

if [[ ! -f "$DIAGRAM" ]]; then
  echo "diagram.json not found at $DIAGRAM"
  exit 1
fi

echo "[validate] Found: $DIAGRAM"

if command -v wokwi-cli >/dev/null 2>&1; then
  echo "[validate] Running wokwi-cli lint"
  (cd "$PROJECT_DIR" && wokwi-cli lint)
  echo "[validate] lint OK"
else
  echo "[validate] wokwi-cli not installed; doing JSON sanity check only"
  python3 - <<'PY' "$DIAGRAM"
import json, sys
p = sys.argv[1]
d = json.load(open(p))
assert 'parts' in d and isinstance(d['parts'], list)
assert 'connections' in d and isinstance(d['connections'], list)
print('[validate] JSON structure OK')
PY
fi
