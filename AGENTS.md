# AGENTS.md - Workspace Agents

## Configured Agents (as of 2026-02-20)

1. main  — openrouter/openai/gpt-4.1 [default]
2. dev-worker  — openrouter/openai/gpt-4.1-mini
3. dev-worker-claude — openrouter/anthropic/claude-3-opus-20240229 (Claude Opus, dedicated to coding)
4. research-worker — openrouter/google/gemini-2.0-flash-001
5. embeddings-worker — openai/gpt-4.1-mini
6. vision-worker — openai/gpt-4o-mini

- Each worker has specific models and tool access tailored to its purpose.
- dev-worker-claude is newly added for Anthropic Claude Opus model coding tasks.

---

**Update steps:**
- Ensure that new agents added to config are reflected here.
- Persistent agent inventory is maintained for all sessions and for context recall.

_Last updated: 2026-02-20_