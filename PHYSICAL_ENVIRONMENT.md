# Physical Environment & Maker Lab Inventory

Last updated: 2026-02-19

## Purpose
Living document that describes the real-world setup (computer, devices, tools, materials, workflow constraints) so project decisions can account for actual hardware conditions.

---

## 1) Host Computer Environment

- Host: Alberto’s Mac mini
- OS: macOS (Darwin arm64)
- Workspace: `/Users/albertoblanco/.openclaw/workspace`
- Primary terminal shell: `zsh`
- Primary automation channel: OpenClaw + Browser Relay

### Installed/validated tooling (maker-relevant)
- `arduino-cli` (installed and working)
- ESP32 core: installed (`esp32:esp32`)
- ESP8266 core: installed (`esp8266:esp8266`)

---

## 2) Connected/Observed USB Serial Devices

### Known ports observed
- `/dev/cu.usbserial-0001` (active microcontroller board detected)
- Other non-target ports may appear (Bluetooth/audio/debug related).

### Current known board reality
- A board believed to be ESP32 identified itself as **ESP8266** during flashing.
- Successful upload target used:
  - `esp8266:esp8266:nodemcuv2`

---

## 3) Current Microcontroller Test Baselines

### A) ESP32 simulation baseline (Wokwi)
- HTTP server + WiFi test project verified in simulation.
- Private Gateway enabled and confirmed in Wokwi UI.

### B) Physical baseline (real USB board)
- Board-only blink + serial sketch uploaded successfully (ESP8266 target).
- No external pin wiring required.

---

## 4) Practical Constraints / Field Notes

- USB cable quality is a recurring risk; data-capable cables are mandatory.
- Board labeling can be misleading; chip probe output is authoritative.
- Browser relay may intermittently fail and need `openclaw gateway restart`.
- 2026-02-19: host experienced an unexpected crash/shutdown during voice tooling setup; root cause not yet determined.
- 2026-02-19: Voice workflow experiments in progress alongside agent orchestration and OpenRouter configuration trials.

---

## 5) Lab Inventory (to complete over time)

> Add details whenever equipment is used or discovered.

### Computers / Controllers
- [x] Mac mini (primary dev host)
- [ ] Additional laptops/workstations (TBD)

### Microcontrollers / SBCs
- [x] ESP8266-class board on USB serial (`/dev/cu.usbserial-0001`)
- [ ] ESP32 boards (model/qty TBD)
- [ ] Raspberry Pi units (TBD)

### Maker Hardware
- [ ] Breadboards (qty TBD)
- [ ] Jumper wire kits (TBD)
- [ ] Sensors/actuators catalog (TBD)
- [ ] Motors/servos catalog (TBD)
- [ ] LED/resistor bins catalog (TBD)

### Fabrication
- [ ] 3D printer(s): model, nozzle sizes, filament types, maintenance notes
- [ ] Soldering station details
- [ ] Measurement tools (multimeter, oscilloscope, logic analyzer)

### Materials
- [ ] PLA/PETG/ABS inventory
- [ ] Fasteners, inserts, adhesives
- [ ] Enclosures and prototyping supplies

---

## 6) Standard Bring-Up Procedure (Physical Board)

1. Connect board with known data cable.
2. Detect serial port via:
   - `arduino-cli board list`
3. Compile with candidate FQBN.
4. Upload.
5. Validate via LED/serial output.
6. Record results in `ARDUINO_TROUBLESHOOTING.md` + this file.

---

## 7) Update Rules

- Keep this file practical and factual.
- Record only verified observations.
- For each new hardware session, append date + what changed.
- Use `HARDWARE_SESSION_TEMPLATE.md` for consistent run logs.
