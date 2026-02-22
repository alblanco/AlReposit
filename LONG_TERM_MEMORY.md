# LONG_TERM_MEMORY.md

## Purpose
Long-term, persistent memory for OpenClaw. This file stores indexed information critical for continuity across sessions, agents, and reboots.

## Indexed Contents
- Agent roles and configs (see AGENTS.md)
- Project knowledge base mappings (all major projects have their own <PROJECT>.md file, referenced in TASKS.md)
- Sub-agent definitions and purposes
- API/model usage (with details in ENVIRONMENT_SETUP.md)
- Key workspace context (paths, scripts, conventions)
- Security, hooks, and logging summaries
- Input/output scratch directory for file exchange between user and OpenClaw: **/Users/albertoblanco/Documents/Claw_workspace** (now referenced as **CW**)
- **CW output rule (Al):** For any user-facing output files (transcripts, exports, reports, images, etc.), write to **CW only**. Do not write to other directories unless:
  1) it’s required internal temp/setup state for a tool/skill, or
  2) Al explicitly approves an override.
  When an override would be helpful/required, ask first.
- GitHub backup: All WKB/project files are routinely pushed to https://github.com/alblanco/AlReposit
- SerpAPI search enabled via config/serpapi.env
- **Brave Search API enabled via config/brave.env (key: BSAKJ1H5uS5RbnaldlGeUtQBYK0gu6B) for external skill/service discovery.**
- How to use the system: See BOOTSTRAP.md for workflow guide, ENVIRONMENT_SETUP.md for base setup, and TASKS.md for global coordination.

## Canonical Response Header
All agents and subagents MUST begin every response with a standardized header:
- Agent Name | Session Number | Project Name | Tasks
- Example: BOB | Session #1043 | Project: VTT | Tasks: Health check & auto-respawn
- See OPENCLAW_KB/response-format.md for canonical template

## Project Creation Policy
- Only the human user may create or name new projects. The agent must never initiate or assign new project names. See OPENCLAW_KB/project-creation-policy.md for details.

## Standard Guidance & Routing Policy
- All agent/subagent decisions, responses, and workflows must routinely reference core rules in BOOTSTRAP.md, project/KB docs, and relevant OPENCLAW_KB/* policies for traceability.
- LONG_TERM_MEMORY.md is always queried for continuity—never issue a project, status, or config response without referencing this or the linked rules.
- For every project/KBase, follow the policy docs in OPENCLAW_KB/ as procedural authority. See OPENCLAW_KB/routing-policy.md for routing logic.

## OpenClaw ops conventions (Alberto preferences)
- When making changes to OpenClaw config, routing, skills, gateway behavior, or automation, always consult and reference the local OpenClaw support materials first:
  - Workspace KB: `OPENCLAW_KB/*`
  - Local full docs mirror: `OPENCLAW_KB/openclaw-docs` → `/opt/homebrew/lib/node_modules/openclaw/docs`
  - Fast doc search: `openclaw docs <query>`

## Planned MCP integrations (discovery list)
Al is currently interested in MCP servers/integrations for:
- Arduino
- n8n
- Supabase
- Excel
- Google Drive
- Google Sheets

## TubeScribe / YouTube transcript defaults (Al preference)
- Default output: **Markdown transcript** (not DOCX)
- Default behavior: **no audio generation** unless Al explicitly asks
- Config file: `~/.tubescribe/config.json` (set `document.format=md`, `audio.enabled=false`, `output.folder=CW`)

## Supabase (multi-project plan)
- Connection method: Supabase hosted MCP (`https://mcp.supabase.com/mcp`) via mcporter.
- Config: `workspace/config/mcporter.json`
  - `supabase` (read-only) and `supabase_rw` (write-enabled) are set up for project `zltnvngpyxflgplwbjji`.
- Token lives in `~/.openclaw/openclaw.json` env as `SUPABASE_ACCESS_TOKEN` (do not paste in chat).

## Embeddings default (vector DB)
- Default embedding model: **OpenAI `text-embedding-3-small`** (1536 dims).

## Last Updated: 2026-02-22

**To onboard or resume work:**
- Start with BOOTSTRAP.md for the workspace/system overview
- ENVIRONMENT_SETUP.md documents the current state and readiness
- TASKS.md lists current action items and project focus
- All ongoing/future projects start with their own dedicated markdown file (<PROJECT>.md) for full traceability

## Aliases
- **CW**: /Users/albertoblanco/Documents/Claw_workspace — use as user/output scratch directory for all file exchange
- **WKB**: "Workspace Knowledge Bases" — the collection of all .md project/config files under version control and GitHub backup
- **GitHub Repo**: https://github.com/alblanco/AlReposit (main backup for all WKB context)
- **SerpAPI**: Key for web/API skill discovery is stored at config/serpapi.env
- **Brave Search API**: Stored in config/brave.env for discovery of modern integrations and skills
