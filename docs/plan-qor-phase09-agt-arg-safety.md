# Plan: ADR-0001 follow-up — thread tool args into AGT arg-safety checks

**change_class**: feature

**doc_tier**: standard

**high_risk_target**: false

**originating_remediation**: ADR-0001 Increment B documented limitation (AGT arg-level checks not reached because args were not threaded)

**boundaries**:
- limitations: Args are passed to AGT's in-process `check_violation` only (no wire); the SidecarClient/HTTP path still does NOT inline args (wire privacy preserved). AGT arg checks fire when the tool's input is a dict whose keys match AGT's expected keys (`query`, `path`, `code`, `command`, `endpoint`).
- non_goals: No change to the wire `ActionRequest`/`qortara_protocol`; no redaction policy; no SidecarClient behavior change.
- exclusions: Remote-daemon arg forwarding (would need a redaction contract — out of scope).

## Open Questions

None. In-process privacy is not a concern (AGT runs in the same process; nothing leaves it). `PolicyEngine.check_violation` already performs path/SQL/code/endpoint arg checks (verified by read, `policy_engine.py`); they were unreached because `AgtDecisionClient` passed `args={}`.

## Phase 1: Pass tool_input to the decision source (in-process AGT consumes it)

### Affected Files

- `packages/qortara-governance-langchain/tests/conformance/test_agt_arg_safety.py` (NEW) — allow-listed tool + dangerous arg → DENY via AGT arg check; safe arg → ALLOW; end-to-end via the real dispatch patch.
- `packages/qortara-governance-langchain/src/qortara_governance/agt_engine.py` — `AgtDecisionClient.decide(request, tool_input=None)`: coerce `tool_input` to a dict (dict→itself, else `{}`) and pass to `AgtPolicyAdapter.check(...)` instead of `{}`.
- `packages/qortara-governance-langchain/src/qortara_governance/client.py` — `SidecarClient.decide(request, tool_input=None)`: accept and **ignore** `tool_input` (documented: not inlined; wire privacy preserved). Backward-compatible.
- `packages/qortara-governance-langchain/src/qortara_governance/patches/tool_patches.py` — `_decide_or_raise` calls `client.decide(request, tool_input)`.

### Caller contract (SG-AffectedFilesContract)

Callers of `.decide(`: `_decide_or_raise` (updated to pass `tool_input`); `tests/conformance/test_basetool_dispatch.py` `_inject` monkeypatch lambda (update `lambda self, request:` → `lambda self, request, tool_input=None:`); `test_client_circuit_breaker.py` + `test_agt_enforcement.py` call `decide(req)` positionally (unaffected — new param is optional).

### Changes

`AgtDecisionClient.decide` extracts `args = tool_input if isinstance(tool_input, dict) else {}` and calls `self._adapter.check(request.agent_id, request.target_resource, args)`. AGT's existing arg checks (destructive SQL, dangerous code, path traversal, internal endpoints) then run on the real arguments.

### Unit Tests

- `test_agt_arg_safety.py`:
  - `test_safe_arg_allows`: role allows `database_query`; `decide(req, {"query": "SELECT 1"})` → ALLOW.
  - `test_destructive_sql_denied`: same allow-list; `decide(req, {"query": "DROP TABLE users"})` → DENY, rationale names destructive SQL (proves AGT arg-check now reached).
  - `test_dispatch_patch_blocks_dangerous_arg`: real patch + `apply_patches(AgtDecisionClient(...))`; an allow-listed `database_query` tool invoked with a `DROP` query raises `QortaraPolicyDenied`; body not run.
  - `test_sidecar_client_ignores_tool_input`: `SidecarClient.decide(req, {"query": "DROP"})` does not inline args (no exception from the extra param; wire path unchanged).

## Feature Inventory Touches

| entry_id | operation | test_path | test_descriptor |
|---|---|---|---|
| FX-agt-enforcement | MODIFIED | packages/qortara-governance-langchain/tests/conformance/test_agt_arg_safety.py | allow-listed tool + dangerous arg (`DROP` SQL) → `QortaraPolicyDenied` via AGT arg-check; safe arg runs |

## Definition of Done

### Deliverable: agt-arg-safety

- **D1**: AGT's argument-level checks run on real tool args (in-process), closing the Increment-B coverage gap; wire privacy unchanged.
- **D2**: `AgtDecisionClient.decide(request, tool_input)`; `SidecarClient.decide(request, tool_input)` (ignored); `_decide_or_raise` threads `tool_input`.
- **D3**: META_LEDGER GATE+SEAL; FEATURE_INDEX FX-agt-enforcement note updated; BACKLOG arg-safety follow-up closed.
- **D4**: the 4 tests pass; full langchain suite green (incl. updated `test_basetool_dispatch` lambda).

## CI Commands

- `uv run --package qortara-governance-langchain pytest packages/qortara-governance-langchain` — full suite.
- `uv tool run ruff check .` — lint.
