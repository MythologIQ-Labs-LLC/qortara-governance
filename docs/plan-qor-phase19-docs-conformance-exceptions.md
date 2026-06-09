# Plan — Phase 19: README truth (N1) + agent-path conformance (N2/B1-followup) + config exception (N3/B2-followup)

**Risk Grade**: L3 (touches the public claim surface + adds a test dependency + a public exception)
**iteration**: ready-for-audit
**Author**: Governor (auto-dev-1)
**Base**: fresh branch off merged `main` (`aade67d`); new PR after the cycle.
**Cycle scope**: N1 + N2 + N3 (recommended batch). Overflow deferred with rationale, not silently dropped.

## Evidence (verified)
- Root `README.md` (on `main`) claims adapters hook `BaseTool.invoke`/`ToolNode.invoke` and are
  "impossible to bypass" — but Phase 15 moved the chokepoint to `run`/`arun`, and THREAT-MODEL §5
  documents a *cooperative-process* boundary (not absolute). Stale + overclaim.
- `BaseTool.stream` → `invoke` → `run`; `astream` → `ainvoke` → `arun` (langchain_core 1.4.2 source) —
  streaming is governed via the funnel, testable with no new runtime dep.
- `langchain.agents` (AgentExecutor / create_tool_calling_agent) is **not installed** (only
  `langchain-core`). A real agent-path conformance test needs `langchain` as a **test-only** dep.
- `config.py` raises bare `ValueError` for invalid `policy_mode` (`_env_policy_mode`, `load_config`);
  the dispatch path is otherwise **fail-closed by contract** (it denies, it does not raise) — so the
  other §8.3 exceptions (PolicyInvalid/DecisionMalformed/AuthenticationError/Timeout) have **no clean
  raise site** without breaking deny-closed.

## Promise (Definition of Done)

### D1 — Vision
The public README states the *actual* hook point and an honest, boundary-qualified bypass claim;
the real agent dispatch paths users run are empirically proven governed; config errors raise a
typed, catchable exception.

### D2 — Code / Docs
1. **N1 (GAP-DOC-01 rest)**: root `README.md` — hook point → `BaseTool.run`/`.arun` (the funnel
   `invoke`/`ainvoke` pass through); replace "impossible to bypass" with "deterministic and
   bypass-resistant within the cooperative-process boundary (THREAT-MODEL §5)". No behavior change.
2. **N2 (B1-followup)** — *amended after research*: `langchain` is **NOT** added. Verified that
   langchain **1.3.4** removed the legacy `AgentExecutor`; the modern entry point is
   `langchain.agents.create_agent`, which builds a **langgraph** graph whose tools execute through
   `ToolNode` (already patched + conformance-tested) and direct `tool.run`/`invoke` (governed via the
   funnel). So the agent-dispatch intent is already covered; a `create_agent` end-to-end test would
   need a fake chat-model harness and only re-exercises `ToolNode`. New conformance (no new dep):
   - `tool.stream(...)` / `await tool.astream(...)` under DENY → blocked (stream→invoke→run funnel).
   - LangGraph `ToolNode` with **multiple** tool_calls + a nested message-state shape → each governed.
   Update `BACKLOG.md` [B1-followup]: record the AgentExecutor-removal finding + that the agent path is
   satisfied by ToolNode/run-arun coverage; streaming + ToolNode-multi added; live-LLM `create_agent`
   matrix noted as post-Beta.
3. **N3 (B2-followup)**: add `QortaraConfigurationError(QortaraError, ValueError)` (multiple
   inheritance keeps existing `pytest.raises(ValueError)` callers green) to `exceptions.py` `__all__`
   + package export; raise it from `config.py` (both invalid-mode sites) and `init_agt`'s
   `PolicyMode(...)` coercion. Update `BACKLOG.md` [B2-followup].

### D3 — Governance
Ledger GATE + SEAL; BACKLOG updated; this plan recorded.

### D4 — Empirical
- `test_stream_is_governed` / `test_astream_is_governed` — DENY blocks the streamed dispatch.
- `test_toolnode_multi_tool_each_governed` — a ToolNode state with 2 tool_calls denies before any runs.
- `test_config_error_is_typed_and_valueerror` — invalid `policy_mode` raises
  `QortaraConfigurationError` AND is catchable as `ValueError` (back-compat).

## Non-goals (deferred, with rationale)
- **PolicyInvalid / DecisionMalformed / AuthenticationError / Timeout** exceptions — the dispatch
  path is **fail-closed** (deny, not raise) by design; these get real raise sites only in the
  post-Beta remote-daemon error-surfacing path. Wiring them now would contradict deny-closed.
- **Live-LLM `create_agent` / dynamic-tool** variants — the modern agent path executes via `ToolNode`
  (governed + tested); a live-LLM end-to-end matrix (needs a fake-model harness) is post-Beta.
- Breaker half-open, `policy_version_sha256` naming, `require_compatible_protocol` wiring — unchanged
  standing residuals.

## Section 4 Razor
One doc edit; new conformance tests (no new dep); one exception class + raise-site swap. No new
dependency at all, no new module, no behavior change to the enforcement path.

## Blast radius
README: text only. No dependency change (`langchain` was investigated and rejected — not needed).
`QortaraConfigurationError` subclasses `ValueError`, so all existing `ValueError` catchers/tests stay
green; it's an additive public name (minor-compatible). Conformance tests are additive.

## Review Boundary
Per the standing session norm: commit + push + open a **new PR**, track CI to green, then hand off
for review/merge. NO tag, NO PyPI, NO merge without explicit approval. No AI footer.
