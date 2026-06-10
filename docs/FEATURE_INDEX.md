# qortara-governance Feature Index

Single canonical cross-reference of every user-touchable feature against documentation, source
code, and test surface. Updated per the FEATURE_INDEX obligation in each `/qor-implement` cycle.

**Generated**: 2026-06-09 by `qor-bootstrap` · **Last aligned**: 2026-06-10 (Phase 23 / governance-doc validation)

## Coverage Summary

- Total entries: **22**
- **Verified**: 22
- **Unverified**: 0
- **N/A (operator-justified)**: 0

---

## Section: Enforcement (dispatch path)

| ID | Feature | Doc | Code | Test | Status |
|---|---|---|---|---|---|
| FX-enforcement-dispatch | `BaseTool.run`/`.arun` (the funnel `invoke`/`ainvoke`/`stream` pass through) routed through policy: deny blocks before the body, allow runs once, exempt bypasses | README, THREAT-MODEL §5 | `patches/tool_patches.py` | `tests/conformance/test_basetool_dispatch.py`, `test_run_chokepoint_and_decision_model.py` | Verified |
| FX-toolnode-dispatch | LangGraph `ToolNode.invoke`/`.ainvoke` governed (incl. multiple tool_calls) | README | `patches/langgraph_patches.py` | `tests/conformance/test_agent_paths_and_streaming.py`, `tests/patches/test_langgraph_toolnode.py` | Verified |
| FX-streaming | `tool.stream`/`.astream` governed via the run/arun funnel | README | `patches/tool_patches.py` | `tests/conformance/test_agent_paths_and_streaming.py` | Verified |
| FX-agent-runtime | `create_react_agent` (langgraph) agent runtime governed end-to-end | BACKLOG B1-followup | `patches/langgraph_patches.py` | `tests/conformance/test_agent_runtime_governed.py` | Verified |
| FX-failclosed | Non-permit verdicts fail closed (DENY + DOWNGRADE/REDACT/SANDBOX/unknown deny-closed; malformed 2xx / engine error deny) | THREAT-MODEL | `patches/tool_patches.py` (`enforce_decision`) | `tests/conformance/test_redteam_failclosed.py` | Verified |
| FX-observe-mode | `policy_mode=observe` shadow/dry-run — evaluate + log would-be block, never raise | README (Configuration), evidence-schema | `patches/tool_patches.py`, `__init__.py` | `tests/conformance/test_observe_and_nocontext.py` | Verified |
| FX-ungoverned-signal | Dispatch with no `AgentContext` warns `QortaraUngovernedDispatchWarning` (escalatable to fail-closed) | README | `patches/tool_patches.py` (`warn_missing_context`) | `tests/conformance/test_observe_and_nocontext.py` | Verified |
| FX-exempt | `@qortara_exempt` opt-out via a module-private identity sentinel (a raw truthy attr does not exempt) | README | `decorators.py` | `tests/patches/test_exempt_sentinel.py` | Verified |

---

## Section: Foundation (Microsoft AGT, ADR-0001)

| ID | Feature | Doc | Code | Test | Status |
|---|---|---|---|---|---|
| FX-agt-dependency | Extends Microsoft AGT as a dependency (core/protocols/integrations) | ADR-0001, AGT-COMPONENT-MAP | `agt.py` | `tests/test_agt_dependency.py` | Verified |
| FX-agt-enforcement | In-process AGT `PolicyEngine` decision source via `init_agt()` (role+tool + argument-level checks) | ADR-0001 | `agt_engine.py` | `tests/conformance/test_agt_enforcement.py`, `test_agt_arg_safety.py` | Verified |
| FX-capability-aliases | Opt-in tool→AGT-capability name map so AGT arg-checks reach custom tool names | ADR-0001 | `agt_engine.py` (`AgtPolicyAdapter`) | `tests/conformance/test_agt_arg_safety.py` | Verified |

---

## Section: Decision model & clients

| ID | Feature | Doc | Code | Test | Status |
|---|---|---|---|---|---|
| FX-decision-client | `DecisionClient` Protocol — shared contract for `SidecarClient` (HTTP) + `AgtDecisionClient` (in-process) | README (Decision model) | `decision_client.py` | `tests/test_review_remediation_phase18.py` | Verified |
| FX-decision-model | Decision routing: allow/deny/require_approval/exempt; AGT path binary; transform kinds deny-closed | README (Decision model) | `patches/tool_patches.py` | `tests/conformance/test_run_chokepoint_and_decision_model.py` | Verified |
| FX-init-guard | `init`/`init_agt` unified re-init fingerprint guard (idempotent; mismatch raises) | — | `__init__.py` | `tests/test_init_idempotent.py`, `test_review_remediation_phase18.py` | Verified |

---

## Section: Resilience & transport (sidecar path)

| ID | Feature | Doc | Code | Test | Status |
|---|---|---|---|---|---|
| FX-circuit-breaker | Consecutive 5xx/4xx/unreachable fail closed to deny-all for a cooldown; recover on success | README (Sidecar) | `client.py` | `tests/test_client_circuit_breaker.py` | Verified |
| FX-init-reachability | `require_reachable()` distinguishes 401/403→auth, timeout→timeout, else→unavailable | README | `client.py` | `tests/test_require_reachable.py` | Verified |
| FX-cleartext-warning | `tenant_key` over plaintext http to a non-loopback host warns `QortaraInsecureTransportWarning` | README | `client.py` | `tests/conformance/test_async_nonblocking_and_transport.py` | Verified |
| FX-async-nonblocking | Async decisions for blocking clients run off the event loop (`asyncio.to_thread`) | — | `patches/tool_patches.py` | `tests/conformance/test_async_nonblocking_and_transport.py` | Verified |

---

## Section: Evidence

| ID | Feature | Doc | Code | Test | Status |
|---|---|---|---|---|---|
| FX-evidence-schema | Decision vs execution evidence builders (`decision_evidence`/`execution_evidence`) | evidence-schema.md | `evidence.py` | `tests/test_evidence.py` | Verified |
| FX-evidence-emission | Opt-in dispatch-path emission via `EvidenceSink` (decision on deny + execution after run; `OTelEvidenceSink`; best-effort, never weakens fail-closed) | evidence-schema.md, README | `evidence_sink.py`, `patches/tool_patches.py` | `tests/conformance/test_evidence_emission.py`, `tests/test_evidence_sink.py` | Verified |

---

## Section: Protocol, config & packaging

| ID | Feature | Doc | Code | Test | Status |
|---|---|---|---|---|---|
| FX-protocol-version | One wire `PROTOCOL_VERSION` + `require_compatible_protocol` (fails closed on major mismatch / missing) | THREAT-MODEL | `protocol_version.py` | `tests/test_protocol_versioning.py` | Verified |
| FX-exceptions | Frozen public exception/warning hierarchy (Beta catch-contract): incl. `QortaraConfigurationError`, `QortaraTimeout`, `QortaraAuthenticationError` | — | `exceptions.py` | `tests/test_protocol_versioning.py`, `test_config_precedence.py`, `test_require_reachable.py` | Verified |
| FX-config-version | `policy_mode` resolution (env > kwarg > default) + `__version__` == packaging metadata | CHANGELOG | `config.py`, `__init__.py` | `tests/test_config_precedence.py`, `test_version_consistency.py` | Verified |

---

## Section: Diagnostics & compatibility

| ID | Feature | Doc | Code | Test | Status |
|---|---|---|---|---|---|
| FX-doctor | `python -m qortara_governance.doctor [--json]` reports governance state + warns on silent traps; `collect_status()` programmatic API | README (Diagnostics) | `doctor.py` | `tests/test_doctor.py` | Verified |
| FX-compat-matrix | CI-verified support floor (langchain-core 0.3 + langgraph 0.2) | COMPATIBILITY.md | `.github/workflows/ci.yml` (`compat-floor`) | CI `compat-floor` job (full suite on the floor) | Verified |

---

## Gaps Surfaced

<!-- Reality without Promise / Promise without Reality entries land here. -->
None. Deferred follow-ups (ToolNode per-tool execution evidence, breaker half-open,
`require_compatible_protocol` wiring, `timed_out`, `QortaraPolicyInvalid`/`DecisionMalformed`)
are tracked in BACKLOG, not gaps — each has a documented rationale.
