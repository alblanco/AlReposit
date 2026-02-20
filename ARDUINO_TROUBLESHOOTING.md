# Arduino / ESP Troubleshooting KB

Last updated: 2026-02-19

## Purpose
Capture practical notes from real sessions: known problems, fast diagnostics, and confirmed fixes for Arduino/ESP projects.

---

## Session Notes (Confirmed)

### 1) Wokwi Servo build error: `Servo.h: No such file or directory`
**Symptoms**
- Build failed in Wokwi with missing `Servo.h`.

**Observed causes**
- `libraries.txt` content/state mismatch.
- Library state in Wokwi not aligned with sketch includes.

**Working fixes**
1. Ensure sketch has:
   - `#include <Servo.h>`
2. Open Wokwi **Library Manager** and verify `Servo` is installed.
3. Set `libraries.txt` to exactly:
   - `Servo`
4. Save + rebuild.

**Result**
- Build resumed and simulation worked.

---

### 2) Wokwi diagram not rendering / wiring not visible
**Symptoms**
- Simulation panel looked wrong/empty or wiring did not display correctly.

**Observed causes**
- `diagram.json` malformed (invalid JSON, extra braces).

**Working fixes**
1. Replace with valid `diagram.json`.
2. Save and switch/refresh simulation panel.
3. If still odd: use zoom/fit controls in Wokwi.

**Result**
- Diagram + wiring rendered correctly.

---

### 3) Wokwi browser relay instability (OpenClaw)
**Symptoms**
- Browser actions intermittently fail with control-service timeout/unreachable errors.

**Working fixes**
1. Restart gateway:
   - `openclaw gateway restart`
2. Re-attach Wokwi tab with OpenClaw Browser Relay extension.
3. Re-run snapshot/actions.

**Result**
- Control usually restored.

---

### 4) Physical board identification mismatch (expected ESP32, actual ESP8266)
**Symptoms**
- Upload attempt to ESP32 target fails with:
  - `This chip is ESP8266, not ESP32. Wrong chip argument?`

**Working fixes**
1. Trust chip probe result.
2. Install proper core and compile for matching target.
3. Upload with matching FQBN.

**Result (this session)**
- Board on `/dev/cu.usbserial-0001` was ESP8266-class.
- Successful upload using `esp8266:esp8266:nodemcuv2`.
- 2026-02-19: Initial flashing confusion due to board labeled ESP32 but detected as ESP8266, resolved by target FQBN switch.

---

## Fast Diagnostic Checklist

### A) Board not detected
1. Try known data USB cable (not charge-only).
2. Replug + try different USB port.
3. Press reset/EN once after plugging.
4. Check ports:
   - `arduino-cli board list`
   - `ls /dev/cu.*`

### B) Wrong target / upload failures
1. Probe chip via upload error text.
2. Confirm board core installed:
   - `arduino-cli core list`
3. Compile with explicit FQBN first, then upload.

### C) Compile succeeds, runtime seems dead
1. Check serial baud matches sketch.
2. Press reset after upload.
3. Confirm onboard LED polarity (ESP8266 often active-low).

---

## Known Good Commands

```bash
# Detect boards
arduino-cli board list

# Install ESP32 core
arduino-cli core install esp32:esp32

# Add ESP8266 package index + install core
arduino-cli config add board_manager.additional_urls http://arduino.esp8266.com/stable/package_esp8266com_index.json
arduino-cli core update-index
arduino-cli core install esp8266:esp8266

# Compile examples
arduino-cli compile --fqbn esp32:esp32:esp32 <sketch-dir>
arduino-cli compile --fqbn esp8266:esp8266:nodemcuv2 <sketch-dir>

# Upload
arduino-cli upload -p /dev/cu.usbserial-0001 --fqbn esp8266:esp8266:nodemcuv2 <sketch-dir>
```

---

## Open TODOs
- Add board-ID playbook (ESP32 DevKit vs NodeMCU vs clones by USB VID/PID).
- Add serial-monitor helper scripts for macOS.
- Add Wokwi-to-hardware “minimum reproducible test” templates.

## Session Logging
Use `HARDWARE_SESSION_TEMPLATE.md` after each physical run and append finalized notes to this KB.
