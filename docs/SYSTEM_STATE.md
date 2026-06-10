# System State

## Snapshot Metadata

| Attribute | Value |
|-----------|-------|
| **Last Updated** | 2026-06-10 |
| **Updated By** | Judge (auto-dev) |
| **Phase** | MERGED — Phases 01–23 sealed (META_LEDGER #54); GA-candidate |
| **Iteration** | 23 |
| **Session Seal** | `main` @ `b79f845` (PRs #13, #15, #16, #17, #18 merged; #11/#12/#14 closed) |

---

## File Tree (Current Reality)

```
qortara-governance/
|-- .github/workflows/        (ci.yml, security.yml, compliance.yml)
|-- docs/
|   |-- CONCEPT.md  ARCHITECTURE_PLAN.md  META_LEDGER.md  SYSTEM_STATE.md
|   |-- BACKLOG.md  FEATURE_INDEX.md  GOVERNANCE_INDEX.md  SHADOW_GENOME.md
|   |-- ARCHITECTURE-BOUNDARIES.md  COMPATIBILITY.md  evidence-schema.md
|   |-- adr/0001-agt-foundation-vendoring.md
|   |-- architecture/AGT-COMPONENT-MAP.md
|   |-- security/THREAT-MODEL.md
|   |-- plan-qor-phase01..23-*.md     (sealed per-phase plans)
|   |-- ideation-b5-*.md  research-brief-*.md
|-- packages/qortara-governance-langchain/
|   |-- src/qortara_governance/
|   |   |-- __init__.py            (public API: init/init_agt, exceptions, evidence,
|   |   |                           EvidenceSink/OTelEvidenceSink, collect_status, ...)
|   |   |-- agt.py  agt_engine.py  (Microsoft AGT in-process decision source)
|   |   |-- client.py             (SidecarClient: HTTP + circuit breaker)
|   |   |-- decision_client.py    (DecisionClient Protocol — shared contract)
|   |   |-- config.py  context.py  decorators.py  launcher.py  otel.py
|   |   |-- exceptions.py         (frozen Beta exception + warning hierarchy)
|   |   |-- protocol_version.py   (PROTOCOL_VERSION + compat gate)
|   |   |-- evidence.py           (decision_evidence / execution_evidence builders)
|   |   |-- evidence_sink.py      (EvidenceSink Protocol + OTelEvidenceSink + safe_emit)
|   |   |-- doctor.py             (diagnostics CLI: python -m qortara_governance.doctor)
|   |   |-- callback.py           (QortaraCallbackHandler — additive observability)
|   |   |-- contract/             (FrameworkAdapter Protocol, AdapterState, conformance)
|   |   `-- patches/              (registry, tool_patches[run/arun], langgraph_patches,
|   |                              action_builder)
|   |-- tests/                    (44 files: conformance/, patches/, unit + e2e)
|   |-- pyproject.toml  README.md  CHANGELOG.md
|-- pyproject.toml  README.md
```

---

## Metrics

| Metric | Value |
|--------|-------|
| Source modules (`src/qortara_governance/`) | 25 |
| Test files | 44 |
| Test result | **180 passed / 2 skipped** (Python 3.11–3.13 + langchain-core 0.3 floor) |
| Lint / type | `ruff` clean; `mypy` 0 issues / 25 files |
| Runtime version | `0.2.1` (post-0.2.1 work is unreleased — Review Boundary held all tags) |

---

## Blueprint Compliance

| Status | Notes |
|--------|-------|
| Reality == Promise | **VERIFIED** — each merge substantiated; #54 sealed-content re-hashes identically on `main` |
| Unplanned files | none outside the governed plans |
| Missing files | none |

**Compliance Rate**: 100% (every sealed phase verified at merge).

---

## Section 4 Razor Compliance

Held throughout: the enforcement core stays small (single `run`/`arun` chokepoint shared with
`ToolNode`); features reuse existing contracts (one `DecisionClient` Protocol, one `EvidenceSink`
contract, the `PolicyMode` enum, stdlib `warnings`) rather than adding surface. No new runtime
dependency was added across Phases 13–23.

---

## Test Coverage

`uv run pytest` → **180 passed / 2 skipped**; also green against the `langchain-core>=0.3,<0.4` +
`langgraph>=0.2,<0.3` floor via the CI `compat-floor` job. Coverage spans dispatch enforcement
(allow/deny/approval/exempt, sync+async, run/arun/stream, ToolNode multi-tool), the adversarial
fail-closed suite, OBSERVE shadow mode, ungoverned-dispatch signalling, opt-in evidence emission,
the agent-runtime end-to-end path, init-time exceptions, and the doctor CLI.

---

## Recent Changes (Phases 11–23 summary)

| Phase(s) | Theme |
|----------|-------|
| 11 | CI security + compliance gates (later hardened) |
| 13 | Red-team CRITICAL set — fail-open/bypass closed (SEC-02/03/04/05/06) |
| 14 | Ungoverned-dispatch signal (SEC-01) + real OBSERVE mode; dead config removed |
| 15 | `run`/`arun` chokepoint (SEC-08) + honest binary-AGT / sidecar decision model (CAP-01) |
| 16 | Defense-in-depth (no `__qortara_original__`; sentinel exempt) + blocking CI gates + pinned gitleaks |
| 17 | Non-blocking async decisions + cleartext-credential warning |
| 18 | `DecisionClient` Protocol + unified init guard + e2e-review remediation |
| 19 | README hook-point truth + agent-path conformance + `QortaraConfigurationError` |
| 20 | CI-verified compatibility matrix + evidence event schema (builders) |
| 21 | Opt-in dispatch-path evidence emission (`EvidenceSink`) |
| 22 | Live-agent end-to-end conformance + init-time `QortaraTimeout`/`QortaraAuthenticationError` |
| 23 | `qortara-governance doctor` diagnostics CLI |

---

## Health Indicators

| Indicator | Status | Details |
|-----------|--------|---------|
| Merkle Chain | VALID | Entries #1–#54; chain links re-verified at each merge |
| Blueprint Sync | SYNCED | Reality == Promise verified post-merge |
| Section 4 Compliance | PASS | No bloat; reused contracts; no new runtime dep |
| Test Status | PASS | 180 passed / 2 skipped; all CI checks green |

---

## Next Actions

Beta-relevant backlog is complete; remaining are standing follow-ups (none Beta-blocking):

- [ ] ToolNode per-tool execution evidence (node runs tools internally — deeper hook).
- [ ] `require_compatible_protocol` init-wiring (blocked: needs a sidecar health-version field).
- [ ] Circuit-breaker half-open probing; `timed_out` execution result.
- [ ] `QortaraPolicyInvalid` / `QortaraDecisionMalformed` (no raise site under deny-closed).

**Declined (maintainer):** W1 sibling adapters, W2 hosted Cloud preview — the SDK stays a single
LangChain/LangGraph package.

---

*State snapshot updated by Qor-logic A.E.G.I.S. Run `python -m qortara_governance.doctor` for live
governance state.*
