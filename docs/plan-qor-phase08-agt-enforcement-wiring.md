# Plan: ADR-0001 Increment B — wire the dispatch patch into AGT's engine

**change_class**: feature

**doc_tier**: system

**high_risk_target**: false

**originating_remediation**: ADR-0001 (extend AGT; the decision engine is AGT's in-process PolicyEngine)

**terms_introduced**:
- term: AgtDecisionClient
  home: packages/qortara-governance-langchain/src/qortara_governance/agt_engine.py

**boundaries**:
- limitations: Maps role + tool-name onto AGT `PolicyEngine.check_violation`. Argument-level safety checks (AGT's path/SQL/code checks) need inline args, which `build_tool_action` omits by design (privacy → `payload_ref`); arg threading is a follow-up. Existing SidecarClient/HTTP path is retained for remote-daemon mode and is unchanged.
- non_goals: Not removing `qortara_protocol`, the sidecar, the launcher, or the HTTP client (separate cleanup cycle); not modifying AGT internals.
- exclusions: Argument-safety enforcement; LangGraph ToolNode wiring (BaseTool first); remote-daemon AGT.

## Open Questions

None. Verified against installed AGT 4.0.0: `agent_control_plane.PolicyEngine.check_violation(agent_role, tool_name, args) -> Optional[str]` (None = allow; string = deny+rationale; default-deny via `add_constraint(role, allowed_tools)`). In-process — no sidecar needed for local enforcement.

## Phase 1: AGT-backed in-process decision source

### Affected Files

- `packages/qortara-governance-langchain/tests/conformance/test_agt_enforcement.py` (NEW) — proves qortara drives AGT's real engine AND that the real BaseTool dispatch patch routes through it.
- `packages/qortara-governance-langchain/src/qortara_governance/agt_engine.py` (NEW) — `AgtPolicyAdapter` (wraps `PolicyEngine`; `allow(role, tools)`); `AgtDecisionClient` (drop-in for `SidecarClient`: `.decide(ActionRequest) -> ActionDecision` mapping AGT's `check_violation` result; `.require_reachable`/`.submit_evidence`/`.health`/`.close` are no-ops).
- `packages/qortara-governance-langchain/src/qortara_governance/__init__.py` — add `init_agt(agent_id, allowed_tools, *, role=None)` that builds an `AgtPolicyAdapter` + `AgtDecisionClient` and calls `apply_patches(client)`; export `AgtPolicyAdapter`, `AgtDecisionClient`, `init_agt`.

### Changes

`AgtDecisionClient.decide(request)` maps `role = request.agent_id`, `tool = request.target_resource`, `args = {}` (args not inlined by `build_tool_action`); calls `check_violation`; returns `ActionDecision(decision_kind=ALLOW)` when None, else `ActionDecision(decision_kind=DENY, rationale=<violation>, policy_pack_id="agt", policy_version_sha256=<agt-core version>)`. Because it is `.decide`-compatible, `apply_patches`/`tool_patches._decide_or_raise` use it unchanged — the existing DENY → `QortaraPolicyDenied` path applies.

### Unit Tests

- `test_agt_enforcement.py`:
  - `test_agt_client_allows_permitted_tool`: adapter configured `allow("agent-x", ["search"])`; `decide` for tool `search` → `DecisionKind.ALLOW`.
  - `test_agt_client_denies_unpermitted_tool`: `decide` for tool `delete_db` (not in allow-list) → `DecisionKind.DENY`, rationale names the role/tool (proves AGT's default-deny drives the verdict).
  - `test_dispatch_patch_routes_allow_through_agt`: `apply_patches(AgtDecisionClient(adapter))` + context; allowed `BaseTool.invoke` runs the body once.
  - `test_dispatch_patch_blocks_deny_through_agt`: disallowed `BaseTool.invoke` raises `QortaraPolicyDenied`; body did not run. (End-to-end proof the dispatch patch enforces via AGT.)

## Feature Inventory Touches

| entry_id | operation | test_path | test_descriptor |
|---|---|---|---|
| FX-agt-enforcement | NEW | packages/qortara-governance-langchain/tests/conformance/test_agt_enforcement.py | BaseTool.invoke routed through AGT `PolicyEngine`: allow-listed tool runs once; unlisted tool → `QortaraPolicyDenied` (body not run) |

## Definition of Done

### Deliverable: agt-enforcement-wiring

- **D1**: qortara's dispatch patch obtains allow/deny decisions from AGT's in-process engine; deny blocks execution.
- **D2**: `agt_engine.py` (`AgtPolicyAdapter` + `AgtDecisionClient`); `init_agt(...)` entry; exports.
- **D3**: META_LEDGER GATE+SEAL; FEATURE_INDEX FX-agt-enforcement; BACKLOG S1/S2 advanced.
- **D4**: the 4 tests pass against the real AGT engine + real patch; full langchain suite stays green; existing SidecarClient path unregressed.

## CI Commands

- `uv run --package qortara-governance-langchain pytest packages/qortara-governance-langchain` — full suite incl. AGT enforcement.
- `uv tool run ruff check .` — lint.
