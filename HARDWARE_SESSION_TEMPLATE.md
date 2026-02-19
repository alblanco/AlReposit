# Hardware Session Log Template

Use this after each physical hardware run. Keep it short and factual.

## Session Header
- **Date/Time:**
- **Project:**
- **Goal:**
- **Operator:**

## Hardware Context
- **Board label (what it says):**
- **Detected chip (what tools report):**
- **Port:**
- **Cable used (if known):**
- **Power source:**

## Software / Build Context
- **Sketch path:**
- **FQBN used:**
- **Tool versions (optional):**
- **Command(s) run:**

## Results
- **Compile:** pass/fail
- **Upload:** pass/fail
- **Runtime behavior:**
- **Serial output highlights:**

## Issues / Fixes
- **Issue(s) seen:**
- **Root cause (confirmed or suspected):**
- **Fix attempted:**
- **Fix result:**

## Follow-ups
- [ ]
- [ ]

## Copy/Paste Example

- **Date/Time:** 2026-02-19 11:13 EST
- **Project:** board-only blink test
- **Goal:** verify new USB board and cable
- **Operator:** Alberto + OpenClaw
- **Board label (what it says):** ESP32 (assumed)
- **Detected chip (what tools report):** ESP8266EX
- **Port:** /dev/cu.usbserial-0001
- **Sketch path:** esp8266-board-test/esp8266-board-test.ino
- **FQBN used:** esp8266:esp8266:nodemcuv2
- **Compile:** pass
- **Upload:** pass
- **Runtime behavior:** onboard LED blinks, serial prints LED ON/OFF
- **Issue(s) seen:** initial wrong target (ESP32)
- **Fix attempted:** switched to ESP8266 core/FQBN
- **Fix result:** successful flash and runtime
