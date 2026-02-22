# Subagent Supervision & Session Strategy

## Purpose
Document the aggressive subagent supervision and strict session isolation policy now active for all critical OpenClaw subagents.

---

## Supervision Policy

- **Every critical subagent (e.g., vision-worker, build) MUST run in its own session.**
- **Health checks run every 1 minute** via OpenClaw's cron system.
- **Immediate action if a subagent is unresponsive or shows no progress:**
   - Kill stalled session
   - Respawn as a fresh, uniquely labeled session
   - Log all events, actions, and outcomes in `OPENCLAW_ALERTS.md` (no redundant user alerts—continuous background compliance)

## Change Log
- 2026-02-21: Policy updated to enforce individual session isolation and more aggressive 1-min interval health checks.

## References
- See also: `best-practices.md`, `TROUBLESHOOTING.md`, primary cron job definition in system config.
