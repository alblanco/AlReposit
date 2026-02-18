#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

DEFAULT_POS = {
    "wokwi-arduino-uno": (0, 0),
    "wokwi-arduino-mega": (0, 0),
    "wokwi-led": (220, -20),
    "wokwi-resistor": (160, -20),
    "wokwi-pushbutton": (220, 100),
}


def part_to_wokwi(part, idx):
    ptype = part["type"]
    left, top = DEFAULT_POS.get(ptype, (120 + (idx * 30), idx * 30))
    return {
        "id": part["id"],
        "type": ptype,
        "left": left,
        "top": top,
        "attrs": part.get("attrs", {}),
    }


def net_to_connections(net):
    pins = net["pins"]
    color = net.get("color", "green")
    conns = []
    # chain adjacent nodes in declared order
    for i in range(len(pins) - 1):
        a = f"{pins[i]['part']}:{pins[i]['pin']}"
        b = f"{pins[i+1]['part']}:{pins[i+1]['pin']}"
        conns.append([a, b, color, []])
    return conns


def convert(netlist):
    board = netlist["board"]
    parts = [board] + netlist.get("parts", [])
    wokwi_parts = [part_to_wokwi(p, i) for i, p in enumerate(parts)]
    connections = []
    for net in netlist.get("nets", []):
        connections.extend(net_to_connections(net))
    return {
        "version": 1,
        "author": "openclaw-agent",
        "editor": "wokwi",
        "parts": wokwi_parts,
        "connections": connections,
        "serialMonitor": {"display": "always", "newline": "lf"},
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="infile", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    data = json.loads(Path(args.infile).read_text(encoding="utf-8"))
    diagram = convert(data)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(diagram, indent=2), encoding="utf-8")
    print(json.dumps({"ok": True, "out": str(out), "parts": len(diagram['parts']), "connections": len(diagram['connections'])}, indent=2))


if __name__ == "__main__":
    main()
