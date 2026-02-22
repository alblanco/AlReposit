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

### Git backups
- Workspace repo has GitHub remote: `https://github.com/alblanco/AlReposit.git`
- Daily auto-push cron is configured: `daily-git-push` (6pm America/New_York)

### Memory search troubleshooting
- If `memory_search` fails with missing `node:sqlite`, ensure the Gateway LaunchAgent uses a modern Node binary:
  - `~/Library/LaunchAgents/ai.openclaw.gateway.plist` should point to `/opt/homebrew/bin/node`

---
_last update: 2026-02-22_
