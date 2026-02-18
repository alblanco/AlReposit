#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


def _norm(s: str) -> str:
    return (s or "").strip().lower()


def check(netlist: dict) -> dict:
    board = netlist.get("board", {})
    board_id = board.get("id")
    parts = [board] + netlist.get("parts", [])
    part_types = {p.get("id"): _norm(p.get("type", "")) for p in parts}
    nets = netlist.get("nets", [])

    errors = []
    warnings = []
    infos = []

    if not nets:
        errors.append("No nets defined.")
        return {"ok": False, "errors": errors, "warnings": warnings, "infos": infos}

    # Build connectivity helpers
    pins_by_part = {}
    for n in nets:
        for pin in n.get("pins", []):
            pins_by_part.setdefault(pin["part"], []).append({"net": n.get("name", ""), "pin": pin["pin"]})

    # Rule: shared ground must exist + board ground should be present
    gnd_nets = [n for n in nets if "gnd" in _norm(n.get("name", ""))]
    if not gnd_nets:
        warnings.append("No net explicitly named GND; consider naming a shared ground net clearly.")

    board_has_gnd_pin = False
    for n in nets:
        for pin in n.get("pins", []):
            if pin.get("part") == board_id and "gnd" in _norm(pin.get("pin", "")):
                board_has_gnd_pin = True
                break
    if not board_has_gnd_pin:
        warnings.append("Board has no explicit GND pin connection in nets.")

    # Rule: each LED should include a resistor in one of its connected nets
    led_ids = [pid for pid, t in part_types.items() if "led" in t and "rgb" not in t]
    resistor_ids = {pid for pid, t in part_types.items() if "resistor" in t}
    for led in led_ids:
        connected_net_names = {c["net"] for c in pins_by_part.get(led, [])}
        found_series_hint = False
        for n in nets:
            if n.get("name") in connected_net_names:
                parts_on_net = {p["part"] for p in n.get("pins", [])}
                if parts_on_net & resistor_ids:
                    found_series_hint = True
                    break
        if not found_series_hint:
            warnings.append(f"LED '{led}' has no resistor detected on connected nets (heuristic check).")

    # Rule: relay loads should have flyback diode (heuristic)
    relay_ids = [pid for pid, t in part_types.items() if "relay" in t]
    diode_ids = [pid for pid, t in part_types.items() if "diode" in t]
    if relay_ids and not diode_ids:
        warnings.append("Relay detected but no diode part found. Add flyback diode across relay coil for protection.")

    # Rule: 5V and 3V3 mixed on same net (heuristic by pin names / net names)
    for n in nets:
        netname = _norm(n.get("name", ""))
        pin_names = [_norm(p.get("pin", "")) for p in n.get("pins", [])]
        has_5v = ("5v" in netname) or any("5v" in p for p in pin_names)
        has_3v3 = ("3v3" in netname) or any(("3v3" in p or "3.3" in p) for p in pin_names)
        if has_5v and has_3v3:
            warnings.append(f"Net '{n.get('name', '')}' appears to mix 5V and 3V3 references.")

    # Rule: dangling parts
    for p in parts:
        pid = p.get("id")
        if pid and pid not in pins_by_part:
            warnings.append(f"Part '{pid}' has no net connections.")

    infos.append(f"parts={len(parts)} nets={len(nets)}")
    return {"ok": len(errors) == 0, "errors": errors, "warnings": warnings, "infos": infos}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="infile", required=True, help="Path to canonical netlist JSON")
    ap.add_argument("--out", help="Optional output report JSON")
    args = ap.parse_args()

    data = json.loads(Path(args.infile).read_text(encoding="utf-8"))
    report = check(data)

    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
