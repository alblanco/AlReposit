# DECISIONS.md

Record durable decisions (ADR-lite).

## D-2026-02-19-001
- **Decision:** Bob is the main orchestrator for long-term project continuity.
- **Why:** Reduce context fragmentation across many specialized runs.
- **Implication:** Specialist agents are task-bounded; Bob merges outcomes into canonical docs.

## D-2026-02-19-002
- **Decision:** Use explicit task IDs (`PRJ-YYYYMMDD-###`) for all significant work.
- **Why:** Keep queue, run logs, and outputs traceable over months.
- **Implication:** Every spawned run must reference a task ID.
