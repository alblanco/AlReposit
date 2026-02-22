# OpenClaw: Best Practices and External Research

## 1. Monitoring & Supervision
- Always spawn subagents with unique labels for easier auditing.
- Use scheduled cron jobs (every 2–5 min) to check subagent status: probe using `session_status`, nudge stalled agents, kill/respawn on failure.
- Log all actions/outcomes in an audit file for easy troubleshooting.

## 2. OpenClaw Documentation Highlights
- Security: Review [OpenClaw Security Settings](https://docs.openclaw.ai/gateway/security) for visibility scopes and session supervision.
- Subagent Management: Reference [DeepWiki Subagent Guide](https://deepwiki.com/openclaw/openclaw/9.6-subagent-management) for session limits and safe policies.
- Production setup/cron: See [Medium Production Guide](https://medium.com/@rentierdigital/the-complete-openclaw-architecture-that-actually-scales-memory-cron-jobs-dashboard-and-the-c96e00ab3f35).

## 3. Watchdog/External Monitoring
- Consider external schedulers or job runners like [Clawtick](https://github.com/Clawtick/cli) for robust cron and real-time notifications.
- Implement watchdog strategies for crash recovery and missed trigger defense, per [Amankhan1’s config primer](https://amankhan1.substack.com/p/how-to-make-your-openclaw-agent-useful).

## 4. Incident Protocol
- Document unexpected stops/stalls, note the outcome of health probes, and track recovery success or escalate.

## 5. Supabase MCP Quick Commands (mcporter)

**Config file:** `/Users/albertoblanco/.openclaw/workspace/config/mcporter.json`

We keep two Supabase server entries:
- `supabase` = **read-only** (safe default)
- `supabase_rw` = **write-enabled** (use intentionally)

### Verify tools are available
```bash
cd /Users/albertoblanco/.openclaw/workspace
mcporter list supabase --config ./config/mcporter.json --schema
```

### List tables
```bash
mcporter call supabase.list_tables --config ./config/mcporter.json
# or explicitly
mcporter call supabase.list_tables --config ./config/mcporter.json schemas='["public","auth","storage"]'
```

### Run a safe read-only query
```bash
mcporter call supabase.execute_sql --config ./config/mcporter.json query="select now() as now;"
```

### Write SQL (intentional)
Use the write-enabled server name:
```bash
mcporter call supabase_rw.execute_sql --config ./config/mcporter.json \
  query="create table if not exists public.example(id bigserial primary key);"
```

### Common gotcha: token not visible in your shell
If you run mcporter manually and see a header substitution error (missing `SUPABASE_ACCESS_TOKEN`), set it in your shell session:
```bash
export SUPABASE_ACCESS_TOKEN="..."
```
The token is also stored for the OpenClaw Gateway service in `~/.openclaw/openclaw.json` under `env`.
