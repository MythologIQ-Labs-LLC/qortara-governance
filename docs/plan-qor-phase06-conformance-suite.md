# Plan: B1 — LangChain enforcement conformance suite

**change_class**: feature

**doc_tier**: standard

## Open Questions

None. Enforcement path verified by read (`patches/tool_patches.py`): `_decide_or_raise` short-circuits on `is_exempt`, returns early when `get_context()` is None, else calls `client.decide` and raises `QortaraPolicyDenied` on DENY / `QortaraApprovalRequired` on REQUIRE_APPROVAL before the original runs. Decisions are driven in tests by monkeypatching `SidecarClient.decide`.

## Phase 1: BaseTool sync/async conformance

### Affected Files

- `packages/qortara-governance-langchain/tests/conformance/test_basetool_dispatch.py` (NEW) — the named conformance suite.

### Changes

A conformance module that, for each path, states: the path under test, the decision injected, whether the underlying tool executed, and the expected exception. Decisions are injected via `monkeypatch.setattr(SidecarClient, "decide", ...)`; the agent context is set with `set_context`. Tool execution is observed through a module-level execution log.

### Unit Tests

- `test_basetool_sync_allow`: ALLOW → `tool.invoke` returns the body's value and the execution log records the call.
- `test_basetool_sync_deny`: DENY → `tool.invoke` raises `QortaraPolicyDenied` and the body did NOT run (log empty).
- `test_basetool_sync_require_approval`: REQUIRE_APPROVAL → raises `QortaraApprovalRequired`; body did not run.
- `test_basetool_async_allow`: `await tool.ainvoke` runs the body under ALLOW.
- `test_basetool_async_deny`: `await tool.ainvoke` raises `QortaraPolicyDenied`; body did not run.
- `test_exempt_tool_bypasses_enforcement`: a `qortara_exempt`-marked tool executes even when the injected decision is DENY (exempt short-circuits before evaluation).
- `test_no_context_no_enforcement`: with no agent context set, the tool runs even under a DENY decision — documenting the cooperative-process boundary (THREAT-MODEL §5).

## Feature Inventory Touches

| entry_id | operation | test_path | test_descriptor |
|---|---|---|---|
| FX-enforcement-dispatch | NEW | packages/qortara-governance-langchain/tests/conformance/test_basetool_dispatch.py | DENY blocks BaseTool.invoke/ainvoke (body not run, QortaraPolicyDenied); ALLOW runs once; exempt bypasses; no-context = no enforcement |

## Definition of Done

### Deliverable: conformance-suite

- **D1**: The core enforcement promise is test-backed: deny blocks execution, allow permits exactly one execution, exempt bypasses, async behaves as sync, and the context boundary is explicit.
- **D2**: `tests/conformance/test_basetool_dispatch.py` with the 7 named tests.
- **D3**: META_LEDGER GATE+SEAL; FEATURE_INDEX FX-enforcement-dispatch row; BACKLOG B1 updated (remaining paths scoped as B1-followup).
- **D4**: all 7 conformance tests pass; full SDK suite stays green.

## CI Commands

- `uv run --package qortara-governance-langchain pytest packages/qortara-governance-langchain/tests/conformance` — conformance suite.
- `uv run --package qortara-governance-langchain pytest` — full SDK suite stays green.
- `uv tool run ruff check .` — lint.
