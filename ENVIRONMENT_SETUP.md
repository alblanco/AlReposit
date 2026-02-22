# ENVIRONMENT_SETUP.md - Base Setup Project

## Objective
This file documents and tracks the essential environment initialization, configuration, and workspace readiness steps needed for productive interactions in all other projects.

## Status
- [x] Confirm agent list and roles (see AGENTS.md)
- [ ] Validate persistent hooks and logs (boot, command logger, session memory)
- [ ] Check security and proxy config
- [x] Document API keys and model usage (OpenAI + OpenRouter configured in ~/.openclaw/openclaw.json)
- [x] SerpAPI key is set and stored at config/serpapi.env for future web/API integrations and database-related skill searches.
- [x] Record key directories, conventions, and update flows (see below)

## Milestones
- [ ] All sub-agents ready and listed in AGENTS.md/LONG_TERM_MEMORY.md
- [ ] BOOTSTRAP.md and TASKS.md reference this file for onboarding

## Notes
Always begin new sessions by scanning this file and TASKS.md. Add notes here for any environment changes. Add API keys or third-party credentials under config/ and cross-index in LONG_TERM_MEMORY.md and BOOTSTRAP.md.

## Key conventions (Al)

### CW output rule (immutable preference)
- **All user-facing output files must go to:** `/Users/albertoblanco/Documents/Claw_workspace` (**CW**)
- Only exceptions: internal temp/setup state required by tools/skills, or explicit Al approval.

### Provider key routing
- Use **OPENAI_API_KEY** for `openai/...` models
- Use **OPENROUTER_API_KEY** for non-OpenAI providers (e.g. `openrouter/...`)

### Heartbeat cost control
- Heartbeat model pinned to: `openai/gpt-4.1-mini` (see `agents.defaults.heartbeat.model` in `~/.openclaw/openclaw.json`)

### TubeScribe defaults
- Defaults: **Markdown transcript only** (no DOCX) and **no audio** unless explicitly requested
- TubeScribe config: `~/.tubescribe/config.json`
  - `document.format=md`
  - `audio.enabled=false`
  - `output.folder=CW`

### Supabase — MCP connector (multi-project ready)
- Most reliable path: **Supabase hosted MCP server** (`https://mcp.supabase.com/mcp`) via **mcporter**.
- Config lives in: `workspace/config/mcporter.json`
  - `supabase` → scoped to project `zltnvngpyxflgplwbjji` and **read-only** (default safe mode)
  - `supabase_rw` → same project, **write-enabled** (use intentionally)
- Auth: `SUPABASE_ACCESS_TOKEN` is stored in `~/.openclaw/openclaw.json` under `env` and must also be present in your shell env when running `mcporter` manually.
- Future multi-DB plan (not built yet): use additional Supabase projects for separate concerns (general DB, vector DB, auth/website). Add additional mcporter server entries (e.g. `supabase_main`, `supabase_vector`, `supabase_auth`) each with its own `project_ref`.

### Embeddings default (vector work)
- Use **OpenAI `text-embedding-3-small`** (1536 dimensions) as the default embedding model for vector DB ingestion.

### Git backups
- Workspace repo has GitHub remote: `https://github.com/alblanco/AlReposit.git`
- Daily auto-push cron is configured: `daily-git-push` (6pm America/New_York)

### Memory search troubleshooting
- If `memory_search` fails with missing `node:sqlite`, ensure the Gateway LaunchAgent uses a modern Node binary:
  - `~/Library/LaunchAgents/ai.openclaw.gateway.plist` should point to `/opt/homebrew/bin/node`

---
_last update: 2026-02-22_
