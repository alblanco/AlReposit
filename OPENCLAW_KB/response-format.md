# Canonical Response Header Format (OpenClaw)

## Policy Purpose
Mandate for all agents and subagents (including BOB, VisionWorker, etc): every response must include an explicit header with the following fields—enforced across all projects and major system communications.

## Required Response Header Template

- **Agent Name:** (ex: BOB, VisionWorker, etc.)
- **Session Number:** (unique per agent spawn, ex: Session #1043)
- **Project Name:** (ex: VTT, Environment Setup)
- **Tasks:** Concise, 1-line descriptor of the active tasks

## Example

BOB | Session #1043 | Project: VTT | Tasks: Health check & auto-respawn

## Cross-Link Policy
- This format is referenced from BOOTSTRAP.md, LONG_TERM_MEMORY.md, and all project <PROJECT>.md scaffolds for full continuity and onboarding/training of new agents.

---

_Last updated: 2026-02-21_
