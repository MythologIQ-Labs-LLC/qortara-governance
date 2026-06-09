# Project Backlog

## Blockers (Must Fix Before Progress)

### Security Blockers
<!-- Format: - [ ] [S#] Description -->
- [x] [S1] Default `init()` path needs a delivered policy decision point. **DONE (Phase 07–08, ADR-0001):** the decision engine is **Microsoft AGT** (`agent-governance-toolkit-{core,protocols,integrations}`, dependency); the Phase 04/05 standalone scaffold was retired. **Phase 08 wired it:** `init_agt(agent_id, allowed_tools)` installs the dispatch patch with an AGT-backed in-process `PolicyEngine` decision source — a clean install now yields a working local enforcement path (no sidecar required). Verified: allow-listed tool runs, unlisted → `QortaraPolicyDenied`.
- [~] [S2] Unauthenticated local decision requests must be rejected. **LARGELY MOOT (Phase 08):** local enforcement is now **in-process** (AGT `PolicyEngine` called directly via `AgtDecisionClient`) — there is no local HTTP decision endpoint to authenticate in the default path; default-deny holds (unlisted tools blocked). **Remaining:** auth applies only if the remote-daemon SidecarClient path is used (post-Beta). **Arg-safety follow-up DONE (Phase 09):** `tool_input` is threaded to AGT's in-process engine so its argument-level checks (SQL/code/path/endpoint) fire on real args; the SidecarClient wire path still does not inline args (privacy preserved). Verified: allow-listed `database_query` with a `DROP` query → `QortaraPolicyDenied`.

### Development Blockers
<!-- Format: - [ ] [D#] Description -->
- [x] [D1] Version drift: `pyproject.toml` = `0.2.1`, runtime `__version__` = `0.2.0`, latest git tag = `v0.2.0`. Unify from one source of truth and enforce in CI. **DONE (Phase 01, 2026-06-09):** runtime bumped to 0.2.1; `tests/test_version_consistency.py` asserts runtime == packaging metadata (CI pytest enforces). Git tag `v0.2.1` is a publish-time action, deferred to Review Boundary handoff.

## Backlog (Planned Work)
<!-- Format: - [ ] [B#] Description -->
- [~] [B1] Enumerate and conformance-test all supported LangChain/LangGraph dispatch paths (build on existing `contract/conformance.py`). **CORE DONE (Phase 06, 2026-06-09):** `tests/conformance/test_basetool_dispatch.py` proves BaseTool sync + async × allow/deny/require_approval, exempt bypass, and the no-context cooperative boundary (7 tests). **Remaining (B1-followup):** AgentExecutor, `create_tool_calling_agent`, LangGraph `ToolNode`, multi-tool/dynamic/nested paths, streaming.
- [ ] [B1-followup] Extend conformance to AgentExecutor / tool-calling-agent / LangGraph ToolNode / multi-tool / dynamic / streaming dispatch paths (roadmap §7.1).
- [x] [B2] Version request/response decision schemas and freeze the exception hierarchy as Beta contracts. **DONE (Phase 03, 2026-06-09):** `PROTOCOL_VERSION` single source of truth drives sidecar endpoints; `require_compatible_protocol` fails closed on major mismatch; exception `__all__` frozen + `QortaraProtocolMismatch` added. **Deferred (B2-followup):** payload-schema versioning lives in external `qortara_protocol`; fuller §8.3 exceptions (QortaraConfigurationError/PolicyInvalid/DecisionMalformed/AuthenticationError/Timeout) added when each has a real raise site.
- [ ] [B2-followup] Wire the remaining §8.3 exceptions (QortaraConfigurationError, QortaraPolicyInvalid, QortaraDecisionMalformed, QortaraAuthenticationError, QortaraTimeout) at their raise sites; coordinate payload-schema versioning with `qortara_protocol`.
- [ ] [B3] Define tested compatibility matrix (replace unbounded dependency claims).
- [x] [B4] Author `docs/security/THREAT-MODEL.md`. **DONE (Phase 02, 2026-06-09):** STRIDE-organized model covering all 16 roadmap §11.1 threats + §7.3 bypass model + fail-closed posture; registered in GOVERNANCE_INDEX Tier 2.
- [ ] [B5] Define evidence event schema + separate decision evidence from execution evidence.

## Wishlist (Nice to Have)
<!-- Format: - [ ] [W#] Description -->
- [ ] [W1] CrewAI / LlamaIndex / AutoGen sibling adapters (explicitly post-Beta).
- [ ] [W2] Hosted Qortara Cloud policy/approval preview.
- [ ] [W3] `qortara-governance doctor` diagnostics CLI.

---
_Updated by /qor-* commands automatically_
