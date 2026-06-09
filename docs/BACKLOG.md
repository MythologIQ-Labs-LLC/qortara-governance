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
- [~] [B1-followup] Extend conformance to AgentExecutor / tool-calling-agent / LangGraph ToolNode / multi-tool / dynamic / streaming dispatch paths (roadmap §7.1). **MOSTLY DONE (Phase 19):** streaming (`BaseTool.stream`/`.astream`) and multi-tool `ToolNode` now conformance-tested (`tests/conformance/test_agent_paths_and_streaming.py`). **Finding:** langchain ≥1.0 **removed** the legacy `AgentExecutor`; the modern `create_agent` builds a LangGraph graph whose tools execute via `ToolNode` (governed + tested) and `tool.run`/`invoke` (governed via the run/arun funnel — Phase 15), so the agent-dispatch intent is covered by existing surfaces. **Remaining (post-Beta):** a live-LLM `create_agent` end-to-end test (needs a fake chat-model harness).
- [x] [B2] Version request/response decision schemas and freeze the exception hierarchy as Beta contracts. **DONE (Phase 03, 2026-06-09):** `PROTOCOL_VERSION` single source of truth drives sidecar endpoints; `require_compatible_protocol` fails closed on major mismatch; exception `__all__` frozen + `QortaraProtocolMismatch` added. **Deferred (B2-followup):** payload-schema versioning lives in external `qortara_protocol`; fuller §8.3 exceptions (QortaraConfigurationError/PolicyInvalid/DecisionMalformed/AuthenticationError/Timeout) added when each has a real raise site.
- [~] [B2-followup] Wire the remaining §8.3 exceptions at their raise sites; coordinate payload-schema versioning with `qortara_protocol`. **PARTIAL (Phase 19):** `QortaraConfigurationError(QortaraError, ValueError)` added + raised from `load_config`/`init_agt` on invalid `policy_mode` (back-compatible — still a `ValueError`). **Deferred w/ rationale:** `QortaraPolicyInvalid`/`DecisionMalformed`/`AuthenticationError`/`Timeout` have **no clean raise site** under the current contract — the dispatch path is **fail-closed** (it returns a deny decision, it does not raise) on malformed/auth/timeout conditions; these gain real raise sites only in the post-Beta remote-daemon error-surfacing path. Wiring them now would contradict deny-closed.
- [x] [B3] Define tested compatibility matrix (replace unbounded dependency claims). **DONE (Phase 20):** `docs/COMPATIBILITY.md` documents the tested matrix; CI `compat-floor` job runs the full suite against the `langchain-core>=0.3,<0.4` + `langgraph>=0.2,<0.3` floor on every PR (verified: `invoke`→`run` holds + 143/2 pass on the floor), so `>=0.3` is now CI-enforced, not asserted. Registered in GOVERNANCE_INDEX Tier 5.
- [x] [B4] Author `docs/security/THREAT-MODEL.md`. **DONE (Phase 02, 2026-06-09):** STRIDE-organized model covering all 16 roadmap §11.1 threats + §7.3 bypass model + fail-closed posture; registered in GOVERNANCE_INDEX Tier 2.
- [~] [B5] Define evidence event schema + separate decision evidence from execution evidence. **DEFINED (Phase 20):** `docs/evidence-schema.md` + `qortara_governance.evidence` separate **decision events** (`decision_evidence`: terminal deny/exempt/observe; refuses non-terminal verdicts) from **execution events** (`execution_evidence`: executed/errored/timed_out/approved); `QortaraCallbackHandler` now emits via the builder. **Deferred (design decision):** emitting evidence from the enforcement *dispatch path* — a hot-path behavior change, and the in-process AGT client's `submit_evidence` is a no-op (no sink) — needs a deliberate opt-in design (when/where to emit), not a default-on add.

## Wishlist (Nice to Have)
<!-- Format: - [ ] [W#] Description -->
- [ ] [W1] CrewAI / LlamaIndex / AutoGen sibling adapters (explicitly post-Beta).
- [ ] [W2] Hosted Qortara Cloud policy/approval preview.
- [ ] [W3] `qortara-governance doctor` diagnostics CLI.

---
_Updated by /qor-* commands automatically_
