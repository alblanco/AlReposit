# Wiring Workflow MVP (Vision -> Netlist -> Wokwi)

This workflow gives the agent a machine-friendly wiring pipeline.

## Files
- `wiring_netlist.schema.json` - canonical wiring format
- `vision_to_netlist.py` - starter/stub for vision extraction output
- `netlist_check.py` - rule-based electrical sanity checks (grounding, LED resistor, relay diode, voltage-mix heuristics)
- `netlist_to_wokwi.py` - converts canonical netlist to `diagram.json`
- `wokwi_validate.sh` - validates wiring diagram (lint if `wokwi-cli` exists)

## Simple demo scenario
LED + resistor on D13, plus a pushbutton on D2.

### 1) Create canonical netlist
```bash
python3 vision_to_netlist.py --out demo/simple.netlist.json
```

### 2) Run electrical sanity checks
```bash
python3 netlist_check.py --in demo/simple.netlist.json --out demo/check-report.json
```

### 3) Convert to Wokwi diagram
```bash
python3 netlist_to_wokwi.py --in demo/simple.netlist.json --out demo/diagram.json
```

### 4) Validate diagram
```bash
bash wokwi_validate.sh demo
```

## How this scales
- Vision model parses uploaded breadboard photo/schematic into canonical netlist.
- Agent can auto-detect risky patterns:
  - missing shared ground
  - no series resistor for LED
  - relay/noisy load without flyback diode
  - 5V/3.3V rail mismatches
- Then the agent simulates with Wokwi and iterates before real upload via `arduino-cli`.
