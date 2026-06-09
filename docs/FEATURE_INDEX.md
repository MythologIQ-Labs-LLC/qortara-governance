# qortara-governance Feature Index

Single canonical cross-reference of every user-touchable feature in qortara-governance against documentation, source code, and test surface. Updated per the Phase 73 FEATURE_INDEX update obligation in every `/qor-implement` cycle (see `/qor-implement` Step 12.5).

**Generated**: 2026-06-09 by `qor-bootstrap`
**Sources**: declared by `/qor-plan` `Feature Inventory Touches` table per cycle.

## Coverage Summary

- Total entries: **6**
- **Verified**: 6
- **Unverified**: 0
- **N/A (operator-justified)**: 0

> Phase 07 (ADR-0001 Increment A): the 4 Sidecar rows were retired with the S1/S2 scaffold (AGT is the decision engine); `FX-agt-dependency` added.

---

## Section: Enforcement

| ID | Feature | Doc | Code | Test | Status | Notes |
|---|---|---|---|---|---|---|
| FX-enforcement-dispatch | BaseTool.invoke/ainvoke route through policy (deny blocks, allow runs once, exempt bypasses) | THREAT-MODEL.md §5 | `src/qortara_governance/patches/tool_patches.py` | `tests/conformance/test_basetool_dispatch.py` | Verified | B1: 7 conformance tests (sync/async × allow/deny/approval + exempt + no-context boundary) |

---

## Section: Packaging / Metadata

| ID | Feature | Doc | Code | Test | Status | Notes |
|---|---|---|---|---|---|---|
| FX-version | `qortara_governance.__version__` reports the SDK version | CHANGELOG.md | `src/qortara_governance/__init__.py` | `tests/test_version_consistency.py` | Verified | D1: aligned 0.2.0→0.2.1; test asserts runtime == packaging metadata |

---

## Section: Protocol & Contracts

| ID | Feature | Doc | Code | Test | Status | Notes |
|---|---|---|---|---|---|---|
| FX-protocol-version | SDK declares one wire `PROTOCOL_VERSION` driving sidecar endpoints + a compatibility gate | THREAT-MODEL.md (threat 10) | `src/qortara_governance/protocol_version.py` | `tests/test_protocol_versioning.py` | Verified | B2: `v0.1` literal → constant; `require_compatible_protocol` fails closed on major mismatch |
| FX-exceptions | Frozen public exception hierarchy (Beta catch-contract) | — | `src/qortara_governance/exceptions.py` | `tests/test_protocol_versioning.py` | Verified | B2: `__all__` freezes set; `QortaraProtocolMismatch` added as `QortaraError` subclass |

---

## Section: Foundation (AGT)

| ID | Feature | Doc | Code | Test | Status | Notes |
|---|---|---|---|---|---|---|
| FX-agt-dependency | AGT foundation present (extends Microsoft AGT per ADR-0001) | ADR-0001, ARCHITECTURE_PLAN.md | `src/qortara_governance/agt.py` | `tests/test_agt_dependency.py` | Verified | Phase 07: depends on `agent-governance-toolkit-{core,protocols,integrations}`; probe confirms `-core` resolves |
| FX-agt-enforcement | Dispatch patch enforces via AGT's in-process `PolicyEngine` (role+tool **and** argument-level checks) | ADR-0001, ARCHITECTURE_PLAN.md | `src/qortara_governance/agt_engine.py` | `tests/conformance/test_agt_enforcement.py`, `test_agt_arg_safety.py` | Verified | Phase 08: `AgtDecisionClient` drop-in; allow/deny + `init_agt()`. Phase 09: `tool_input` threaded in-process → AGT SQL/code/path arg checks fire (wire privacy preserved) |

> **Retired (Phase 07):** the former Sidecar rows (FX-sidecar-evaluator/-policy/-app/-auth, S1/S2 scaffold) were removed — AGT is the decision engine. The dispatch-patch→AGT wiring is Increment B.

---

## Gaps Surfaced

<!-- Reality without Promise / Promise without Reality entries land here. -->
