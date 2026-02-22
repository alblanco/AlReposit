# BOOTSTRAP.md - Workspace Startup & System Guide

## System Overview
This workspace uses dedicated files for all key project and memory workflows:

- `LONG_TERM_MEMORY.md`: Persistent, indexed memory; stores agent configs, key context, API usage, etc.
- `TASKS.md`: Central task list (open/in-progress/done) for all workspace projects.
- Project-specific files (e.g. VOICE_TO_TEXT.md, ARDUINO_PROJECT.md, ENVIRONMENT_SETUP.md): Deep documentation, action logs, milestone tracking for each project.
- `config/serpapi.env`: Stores your SerpAPI key (033fa0171eb89b2e8f9d98ff712d936b5a06e9c1e8b61b534f2d1bcd47906673) for future web/API skill and service search integrations.

When onboarding, always check and update LONG_TERM_MEMORY.md, TASKS.md, your active project file, and API keys/config before beginning a new task or session.

## How to Use
- Only the human user may create new projects. The assistant must never create or name a new project—this is strictly user-controlled (see OPENCLAW_KB/project-creation-policy.md).
- Start all new projects by creating a "<PROJECT>.md" file and adding it to TASKS.md (open section)
- Reference ongoing/finished work in LONG_TERM_MEMORY.md for global continuity
- Log major changes and key decisions in the relevant project file (and cross-index for future recall)
- If your work/project needs API keys for search or integration, add them in `config/` and note in Bootstrap/WKB files for continuity.
- All agent/subagent responses MUST begin with a standardized header in this format:
  - Agent Name | Session Number | Project Name | Tasks (concise descriptor)
  - Example: BOB | Session #1043 | Project: VTT | Tasks: Health check & auto-respawn
  - See OPENCLAW_KB/response-format.md for most current spec.

---
_latest update: 2026-02-21_
