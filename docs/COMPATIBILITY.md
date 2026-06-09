# Compatibility Matrix

This is the **tested** support matrix — every cell is exercised by CI, not asserted.
The dependency floor in `pyproject.toml` (`langchain-core>=0.3`) is verified by the
`compat (langchain-core 0.3 floor)` job, which runs the full suite against the lower
bound on every pull request.

## Tested

| Axis | Floor (CI: `compat-floor`) | Latest (CI: `test` matrix) |
|---|---|---|
| Python | 3.11 | 3.11, 3.12, 3.13 |
| `langchain-core` | `>=0.3,<0.4` (verified: `invoke`→`run` / `ainvoke`→`arun` hold; full suite passes) | latest resolved 1.x |
| `langgraph` (optional `[langgraph]` extra) | `>=0.2,<0.3` | latest resolved |

The dispatch hook lives on `BaseTool.run`/`.arun` — the funnel `invoke`/`ainvoke`/`stream`
pass through (see [`security/THREAT-MODEL.md`](security/THREAT-MODEL.md) §5). That funnel
relationship was confirmed to hold across `langchain-core` 0.3.0 → 1.4.x, so enforcement
coverage is consistent over the supported range.

## How the floor is enforced

`.github/workflows/ci.yml` → job `compat-floor`:

```bash
uv run --with "langchain-core>=0.3,<0.4" --with "langgraph>=0.2,<0.3" pytest -q
```

If a future `langchain-core` 0.3.x or `langgraph` 0.2.x change breaks the suite, this
job fails the PR — at which point either the incompatibility is fixed or the documented
floor (and `pyproject.toml`) is raised. The claim and the test move together.

## Not tested / out of scope

- `langchain-core` < 0.3 (below the declared floor).
- Frameworks other than LangChain / LangGraph (CrewAI / LlamaIndex / AutoGen are post-Beta — BACKLOG W1).
- A live-LLM `create_agent` end-to-end run (post-Beta — BACKLOG B1-followup); the agent
  tool-dispatch path is covered structurally via `ToolNode` + the run/arun funnel.
