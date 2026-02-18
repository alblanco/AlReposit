#!/usr/bin/env python3
import json
import time
from pathlib import Path

import arduino_kb_ingest as kb

KB_ROOT = Path('/Users/albertoblanco/Documents/Arduino-KB')
LOG_PATH = KB_ROOT / 'logs' / 'last_ingest_report.json'
OUT_LOG = KB_ROOT / 'logs' / 'recovery_pass_report.json'


def main():
    data = json.loads(LOG_PATH.read_text(encoding='utf-8'))
    failed = [Path(e['file']) for e in data.get('errors', [])]
    total = len(failed)
    report = {
        'started_at': time.strftime('%Y-%m-%d %H:%M:%S'),
        'total_failed_input': total,
        'recovered': [],
        'still_failed': [],
        'progress': [],
    }

    print(f'[recovery] starting; targets={total}', flush=True)

    for i, pdf in enumerate(failed, start=1):
        status = 'failed'
        err = None

        for attempt in range(1, 5):
            try:
                kb.ingest_pdf(pdf, KB_ROOT, force=True)
                status = 'recovered'
                break
            except Exception as e:
                err = str(e)
                time.sleep(0.6 * attempt)

        if status == 'recovered':
            report['recovered'].append(str(pdf))
        else:
            report['still_failed'].append({'file': str(pdf), 'error': err})

        if i % 5 == 0 or i == total:
            checkpoint = {
                'done': i,
                'total': total,
                'recovered': len(report['recovered']),
                'failed': len(report['still_failed']),
                'ts': time.strftime('%H:%M:%S'),
            }
            report['progress'].append(checkpoint)
            print(
                f"[recovery] {i}/{total} complete | recovered={checkpoint['recovered']} | remaining_failed={checkpoint['failed']}",
                flush=True,
            )

    report['finished_at'] = time.strftime('%Y-%m-%d %H:%M:%S')
    OUT_LOG.write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(f"[recovery] finished | recovered={len(report['recovered'])} | still_failed={len(report['still_failed'])}", flush=True)
    print(f"[recovery] report={OUT_LOG}", flush=True)


if __name__ == '__main__':
    main()
