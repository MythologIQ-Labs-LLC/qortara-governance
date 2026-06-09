# System State

## Snapshot Metadata

| Attribute | Value |
|-----------|-------|
| **Last Updated** | 2026-06-09 |
| **Updated By** | Specialist (auto-dev) |
| **Phase** | IMPLEMENTING — AGT pivot complete (Phases 01–10 sealed) |
| **Iteration** | 10 |
| **Session Seal** | local hold (Review Boundary — no commit) |

---

## File Tree (Current Reality)

<!--
This is the ACTUAL state of the project, not the planned state.
Refreshed by /qor-substantiate after the first implementation cycle.
-->

```
qortara-governance/
|-- .agent/staging/
|-- .qor/gates/
|-- docs/
|   |-- CONCEPT.md
|   |-- ARCHITECTURE_PLAN.md
|   |-- META_LEDGER.md
|   |-- SYSTEM_STATE.md (this file)
|   |-- SHADOW_GENOME.md
|   |-- GOVERNANCE_INDEX.md
|   |-- BACKLOG.md
|   `-- FEATURE_INDEX.md
|-- packages/
|   `-- qortara-governance-langchain/
|       |-- src/qortara_governance/   (callback, client, config, context,
|       |                              decorators, exceptions, launcher, otel;
|       |                              contract/, patches/)
|       `-- tests/                     (contract/, patches/, unit suite)
|-- pyproject.toml
`-- README.md
```

---

## Metrics

Reality metrics (LoC, function/file sizes, Section 4 counts) are measured by
`/qor-substantiate` after the first governed implementation cycle. No governed
cycle has run yet, so this snapshot reports BOOTSTRAP-phase reality only.

| Metric | Value |
|--------|-------|
| Governed source files delivered this cycle | 0 (pre-implementation) |
| Governed test files delivered this cycle | 0 (pre-implementation) |
| Pre-existing package | `qortara-governance-langchain` (Alpha v0.2.x, ungoverned baseline) |

---

## Blueprint Compliance

<!--
Compare ARCHITECTURE_PLAN.md (Promise) vs actual files (Reality).
Populated at first /qor-substantiate.
-->

| Status | Planned | Actual | Notes |
|--------|---------|--------|-------|
| Delivered | 0 | 0 | No governed cycle has shipped yet |
| Unplanned | 0 | 0 | — |
| Missing | 0 | 0 | — |

**Compliance Rate**: N/A (pre-implementation)

---

## Dependency Manifest

Approved dependencies are declared in `ARCHITECTURE_PLAN.md` (langchain-core,
langgraph, opentelemetry, external sidecar). Installed-vs-approved reconciliation
runs at `/qor-substantiate`.

---

## Section 4 Razor Compliance

Not yet measured. The existing Alpha package is an ungoverned baseline; razor
compliance is assessed when a governed `/qor-implement` cycle touches `src/`.

---

## Test Coverage

Coverage reconciliation runs at `/qor-substantiate`. The package ships an
existing pytest suite under `packages/qortara-governance-langchain/tests/`
(contract + patches + unit + conformance), green on Python 3.11–3.13 per CI (3.10 dropped, Phase 07, AGT floor).

---

## Recent Changes

| File | Change Type | Notes |
|------|-------------|-------|
| src/qortara_governance/__init__.py | Modified | D1: `__version__` 0.2.0→0.2.1; B2 exports |
| tests/test_version_consistency.py | Created | D1: runtime==metadata guard |
| docs/security/THREAT-MODEL.md | Created | B4: 16-threat model + bypass model |
| src/qortara_governance/protocol_version.py | Created | B2: PROTOCOL_VERSION + compat gate |
| src/qortara_governance/exceptions.py | Modified | B2: frozen `__all__` + QortaraProtocolMismatch |
| src/qortara_governance/client.py | Modified | B2: endpoints derive from PROTOCOL_VERSION |
| tests/test_protocol_versioning.py | Created | B2: 4 behavioral tests |

**Test Status (after Phase 09)**: `uv run --package qortara-governance-langchain pytest` → **79 passed, 2 skipped**; ruff clean; prose-lint clean; governance-health clean.

**AGT pivot (Phases 07–09) superseded the S1/S2 sidecar scaffold:**

| File | Change Type | Notes |
|------|-------------|-------|
| packages/qortara-governance-sidecar/** | **Deleted** (Phase 07) | from-scratch scaffold retired; AGT is the decision engine (ADR-0001) |
| pyproject.toml (langchain) | Modified | Phase 07: depend on `agent-governance-toolkit-{core,protocols,integrations}`; Python floor 3.11 |
| src/qortara_governance/agt.py | Created | Phase 07: AGT foundation probe |
| src/qortara_governance/agt_engine.py | Created | Phase 08/09: `AgtDecisionClient` (in-process AGT decisions + arg-safety) + `init_agt()` |
| src/qortara_governance/client.py / patches/tool_patches.py | Modified | Phase 09: `decide(request, tool_input)` threads args (AGT in-process; SidecarClient ignores — wire privacy) |
| tests/conformance/{test_basetool_dispatch,test_agt_enforcement,test_agt_arg_safety}.py | Created | B1 + Phase 08/09 enforcement conformance |

---

## Health Indicators

| Indicator | Status | Details |
|-----------|--------|---------|
| Merkle Chain | VALID | Genesis hash verified at bootstrap |
| Blueprint Sync | SYNCED | Plan just authored; no drift |
| Section 4 Compliance | UNKNOWN | Measured at first substantiate |
| Test Status | PASS | CI green on existing package suite |

---

## Next Actions

Based on current state:

- [ ] Reconcile `qortara_protocol` ↔ `agent-governance-toolkit-protocols`
- [ ] Cleanup cycle: retire/relegate the optional sidecar `client.py` / `launcher.py` (remote-daemon only)
- [ ] Wire LangGraph `ToolNode` patch into AGT (BaseTool done)

---

*State snapshot updated by Qor-logic A.E.G.I.S.*
*Run `/qor-status` for live diagnostic.*
