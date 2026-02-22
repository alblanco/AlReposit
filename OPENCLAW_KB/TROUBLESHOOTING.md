# OpenClaw Troubleshooting Guide

## Common Issues
- memory_search / embeddings fail with “SQLite support is unavailable … missing node:sqlite”
  - Cause: the **Gateway service** is running on an older Node version (commonly pinned in the macOS LaunchAgent plist), so `require('node:sqlite')` is unavailable.
  - Fix (macOS):
    1) Inspect the LaunchAgent:
       - `plutil -p ~/Library/LaunchAgents/ai.openclaw.gateway.plist | head`
    2) Update the Node path under `ProgramArguments` to a modern Node binary (example):
       - from: `/opt/homebrew/Cellar/node/<old>/bin/node`
       - to: `/opt/homebrew/bin/node`
    3) Reload the service:
       - `launchctl unload ~/Library/LaunchAgents/ai.openclaw.gateway.plist`
       - `launchctl load ~/Library/LaunchAgents/ai.openclaw.gateway.plist`
    4) Verify:
       - `openclaw gateway status` shows the new node path
       - `node -e "require('node:sqlite'); console.log('node:sqlite OK')"`
       - re-run `memory_search`

- Subagents stuck or unresponsive
  - Steps: Check `session_status`, try nudge via `sessions_send`. If still unresponsive, kill and respawn.
- Cron jobs not firing
  - Steps: List crons (`cron status/list`), ensure they are enabled, check schedule expression and logs for errors.
- Tool/agent permission errors
  - Review tool policies (`tools.sessions.visibility`, etc.) in your configuration. Compare with documented best practices.
- Logs not updating
  - Investigate disk space, file permissions, and agent process health.

## Escalation Protocol
- Log every intervention in `OPENCLAW_ALERTS.md`.
- Persistent failure: escalate to manual inspection or post in OpenClaw community for advanced help.

## Useful Links
- [OpenClaw Security](https://docs.openclaw.ai/gateway/security)
- [Subagent Deep Dive](https://deepwiki.com/openclaw/openclaw/9.6-subagent-management)
- [Production Scaling Guide](https://medium.com/@rentierdigital/the-complete-openclaw-architecture-that-actually-scales-memory-cron-jobs-dashboard-and-the-c96e00ab3f35)
- [Watchdog Config](https://amankhan1.substack.com/p/how-to-make-your-openclaw-agent-useful)
