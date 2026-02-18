#!/usr/bin/env python3
"""vision_to_netlist.py
MVP helper: takes a human/vision-derived JSON or emits a starter netlist template.
This is intentionally simple: vision extraction can feed this format later.
"""
import argparse
import json
from pathlib import Path

TEMPLATE = {
    "version": "0.1",
    "project": "demo-led-button",
    "board": {"id": "uno", "type": "wokwi-arduino-uno", "attrs": {}},
    "parts": [
        {"id": "led1", "type": "wokwi-led", "attrs": {"color": "red"}},
        {"id": "r1", "type": "wokwi-resistor", "attrs": {"value": "220"}},
        {"id": "btn1", "type": "wokwi-pushbutton", "attrs": {"color": "black"}}
    ],
    "nets": [
        {"name": "LED_DRIVE", "color": "green", "pins": [{"part": "uno", "pin": "13"}, {"part": "r1", "pin": "1"}]},
        {"name": "LED_CHAIN", "color": "green", "pins": [{"part": "r1", "pin": "2"}, {"part": "led1", "pin": "A"}]},
        {"name": "GND", "color": "black", "pins": [{"part": "uno", "pin": "GND.1"}, {"part": "led1", "pin": "C"}, {"part": "btn1", "pin": "2.r"}]},
        {"name": "BUTTON_SIG", "color": "blue", "pins": [{"part": "uno", "pin": "2"}, {"part": "btn1", "pin": "1.l"}]}
    ]
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True, help="Output netlist json path")
    ap.add_argument("--from-json", help="Optional pre-extracted vision JSON to normalize")
    args = ap.parse_args()

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)

    if args.from_json:
        data = json.loads(Path(args.from_json).read_text())
        # For MVP, trust shape is already close; real version maps CV output -> canonical pins.
        payload = data
    else:
        payload = TEMPLATE

    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps({"ok": True, "out": str(out), "parts": len(payload.get("parts", [])), "nets": len(payload.get("nets", []))}, indent=2))


if __name__ == "__main__":
    main()
