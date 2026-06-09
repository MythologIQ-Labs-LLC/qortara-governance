# Plan: Phase 13 — Red-team CRITICAL remediation (fail-open / bypass)

**change_class**: hotfix

**doc_tier**: standard

**high_risk_target**: false

**originating_remediation**: research-brief-deep-audit-redteam-2026-06-09.md (GAP-SEC-02/-03/-04/-05/-06)

**boundaries**:
- limitations: Closes the confirmed CRITICAL bypass/fail-open set only. AGT internals are NOT modified (ADR-0001) — GAP-SEC-05 is mitigated at the qortara boundary (truth + opt-in capability map), not by changing AGT's name-keyed checks. Deferred (tracked in the brief): GAP-CAP-01, SEC-01/07/08, CFG-01, CI-01/02, DOC-01, MED/LOW hardening.
- non_goals: No new transform/redact/sandbox behavior; no protocol change; no doc/CI cycle (separate follow-up).
- exclusions: design-judgment items (no-context warn, unpatch/exempt hardening) deferred.

## Open Questions

None. All five verified CONFIRMED in the brief with file:line.

## Phase 1: Fail-closed hardening (SEC-02/-03/-04/-06)

### Affected Files

- `packages/qortara-governance-langchain/src/qortara_governance/patches/langgraph_patches.py` — **(SEC-06)** add `_make_async_wrapper` + patch `ToolNode.ainvoke` in `apply()` (guard double-patch; restore in `unpatch`). **(SEC-02)** `_decide_each` permits only ALLOW/EXEMPT/OBSERVE; REQUIRE_APPROVAL → approval; DENY + any other kind → fail-closed `QortaraPolicyDenied`.
- `packages/qortara-governance-langchain/src/qortara_governance/patches/tool_patches.py` — **(SEC-02)** same fail-closed decision mapping in `_decide_or_raise`.
- `packages/qortara-governance-langchain/src/qortara_governance/client.py` — **(SEC-03)** `decide()` also catches `pydantic.ValidationError` + `ValueError` (malformed 2xx / bad JSON) → `_record_failure()` + deny-closed.
- `packages/qortara-governance-langchain/src/qortara_governance/agt_engine.py` — **(SEC-04)** wrap `self._adapter.check(...)` in try/except → any exception returns fail-closed DENY. **(SEC-05)** `AgtPolicyAdapter(capability_aliases=...)`: `allow()` also allow-lists mapped capability names; `check()` runs a second `check_violation` under the mapped capability so AGT arg-checks reach mapped tools. Correct the docstring (arg-checks apply to AGT-recognized capability names, else role+tool allow-listing).

### Unit Tests (adversarial — try to bypass)

- `tests/conformance/test_redteam_failclosed.py` (NEW):
  - `test_toolnode_ainvoke_is_patched`: after `apply`, `ToolNode.ainvoke.__qortara_wrapped__` is True (SEC-06 — was unpatched).
  - `test_async_toolnode_wrapper_blocks_deny`: the async ToolNode wrapper raises `QortaraPolicyDenied` on a denied tool and does NOT call the original (await).
  - `test_unsupported_decision_kind_fails_closed`: a fake client returning `DecisionKind.SANDBOX` (and `DOWNGRADE`) makes `BaseTool.invoke` raise `QortaraPolicyDenied` and the tool body does NOT run (SEC-02).
  - `test_observe_allows`: `DecisionKind.OBSERVE` permits execution (non-blocking).
  - `test_malformed_2xx_denies_closed`: `SidecarClient.decide` against a MockTransport returning 200 + garbage JSON returns DENY and increments the breaker (SEC-03), not an escaping exception.
  - `test_agt_engine_exception_fails_closed`: an `AgtPolicyAdapter` whose engine `check_violation` raises → `decide` returns DENY (SEC-04).

- `tests/conformance/test_agt_arg_safety.py` (extend):
  - `test_unmapped_dangerous_tool_is_not_argchecked`: tool `sql_db_query` (NOT an AGT-recognized name), allow-listed, args `{"query":"DROP TABLE x"}` → ALLOW — documents the SEC-05 boundary explicitly.
  - `test_capability_alias_enables_argcheck`: `capability_aliases={"sql_db_query":"database_query"}` → same DROP args now → `QortaraPolicyDenied` (arg-check reached via the alias).

## Phase 2: init_agt capability_aliases passthrough

### Affected Files

- `packages/qortara-governance-langchain/src/qortara_governance/__init__.py` — `init_agt(agent_id, allowed_tools, *, capability_aliases=None)` forwards the map to `AgtPolicyAdapter`.

## Feature Inventory Touches

| entry_id | operation | test_path | test_descriptor |
|---|---|---|---|
| FX-agt-enforcement | MODIFIED | packages/qortara-governance-langchain/tests/conformance/test_redteam_failclosed.py | ToolNode.ainvoke governed; unsupported decision kinds + malformed-2xx + engine-exception all fail closed (deny, body not run) |
| FX-agt-enforcement | MODIFIED | packages/qortara-governance-langchain/tests/conformance/test_agt_arg_safety.py | arg-safety boundary documented (unmapped tool not arg-checked) and closed for mapped tools via capability_aliases |

## Definition of Done

- **D1**: No confirmed CRITICAL fail-open/bypass remains: ToolNode async governed; non-allow verdicts fail closed; malformed sidecar response + engine exceptions deny-closed; arg-safety honestly scoped + mappable.
- **D2**: the 5 source files patched; `init_agt` gains `capability_aliases`.
- **D3**: META_LEDGER GATE+SEAL; brief's GAP-SEC-02/03/04/05/06 marked RESOLVED with the test names; committed to PR #13.
- **D4**: 8 new/extended adversarial tests pass; full suite green; ruff format-check + lint + mypy(0) clean.

## CI Commands

- `uv run --package qortara-governance-langchain pytest packages/qortara-governance-langchain`
- `uv tool run ruff format --check . ; uv tool run ruff check . ; uv run mypy src` (package dir)
