# Crash Investigation — 2026-02-19

## Summary
Two unexpected restart events were reported during Bob Voice Studio work.

## Evidence Collected

### 1) Kernel panic (12:59)
- File: `/Library/Logs/DiagnosticReports/panic-full-2026-02-19-125928.0002.panic`
- Panic string: `watchdog timeout: no checkins from watchdogd in 92 seconds`
- Type: kernel-level watchdog panic (system unresponsive long enough to trigger reset)

Related reset counter:
- `/Library/Logs/DiagnosticReports/ResetCounter-2026-02-19-125956.diag`
- `Boot faults: wdog,reset_in_1`

### 2) Restart event (13:25)
- `/Library/Logs/DiagnosticReports/ResetCounter-2026-02-19-132518.diag`
- `Boot faults: btn_rst,btn_seq_reset`
- Interpretation: button-sequence reset event was recorded by system firmware.

## What Bob ran before incidents
- Local dev servers (`python`/Flask for voice studio)
- Browser automation actions
- Whisper invocations
- Arduino CLI compile/upload checks

No shutdown/reboot/poweroff/sudo kernel-level commands were executed in-session.

## Likely Cause
- First incident: OS/kernel watchdog panic due system stall (not a direct software-issued shutdown command).
- Second incident: hardware/firmware-level button reset event (`btn_rst,btn_seq_reset`).

## Immediate Risk Controls
1. Keep Bob Voice Studio on dedicated port (8790) and minimal background load.
2. Avoid long-running broad `log show` scans during active work.
3. Reduce concurrent heavy tasks while transcribing.
4. If another crash occurs, capture fresh panic/reset files immediately and compare signatures.

## Next Diagnostics (if repeated)
- Correlate panic time with loaded third-party background daemons.
- Run Apple Diagnostics.
- Check external USB/peripheral influence (disconnect nonessential devices and retest).
