# Research Brief — Documentation Alignment Audit

**Date**: 2026-06-09
**Analyst**: The Qor-logic Analyst
**Target**: All repo documentation vs. code reality + internal consistency, after the AGT pivot (Phases 07–09) and the pulled public/hosted-boundary docs.
**Scope**: drift between authoritative docs and the current AGT-in-process reality; sidecar references; Python floor; Quickstart accuracy; package metadata; cross-doc consistency.

---

## Executive Summary

The AGT pivot (Phase 07–09: sidecar package deleted, AGT in-process engine wired, Python floor 3.11) has **not yet propagated to several forward-facing authoritative docs**, which still describe the retired local-sidecar architecture. The newly pulled `ARCHITECTURE-BOUNDARIES.md` + README hosted/public sections are **well-aligned** with the AGT/hosted model. **6 drift clusters** warrant remediation; all are documentation-only (L1). Historical artifacts (ADR-0001, component map, phase plans, ledger, prior briefs) are correct archaeology and are explicitly **out of scope** — they must not be rewritten.

## Findings (drift — forward-facing authoritative docs)

### DRIFT-1 (HIGH) — `docs/ARCHITECTURE_PLAN.md` is internally self-contradictory
Its Foundation note (`ARCHITECTURE_PLAN.md:10`) says the sidecar was retired and AGT is the in-process engine, but the body still describes the old sidecar architecture:
- `:33` file tree `launcher.py # sidecar process launch`
- `:54` "Qortara Local Sidecar (launcher.py → external runtime; not yet delivered in-repo)"
- `:78` data flow "→ sidecar evaluation"
- `:87` Dependencies row "external `qortara-governance-sidecar` | GAP — not delivered in-repo"
- `:95` Known Gaps "Default `init()` path depends on a sidecar executable not delivered"
→ The blueprint contradicts its own header and Phase 08 reality (AGT in-process; no sidecar needed locally).

### DRIFT-2 (HIGH) — `docs/SYSTEM_STATE.md` describes a deleted package + stale Python
- `:113`/`:117` list "New package `qortara-governance-sidecar` (S1/S2, 28 tests)" as **Created** — that package was **deleted in Phase 07**.
- `:97` "green on Python **3.10**–3.13" — floor is now **3.11** (Phase 07).
- `:139` next-action "Resolve BACKLOG security blockers (sidecar delivery…)" — superseded by AGT.
→ SYSTEM_STATE is meant to be *current reality*; it is frozen at batch-2 (pre-Phase-07).

### DRIFT-3 (MED) — Quickstart shows bare `init()` that no longer works locally
`README.md:46-52` (and the package README quickstart) show `pip install …` + `qortara_governance.init()` with "tool dispatches now pass through policy evaluation." Post-pivot, bare `init()` requires a sidecar endpoint or raises `QortaraSidecarUnavailable`; the **working local path is `init_agt(agent_id, allowed_tools)`** (Phase 08). Quickstart is misleading.

### DRIFT-4 (MED) — package metadata calls it a "sidecar SDK"
`packages/qortara-governance-langchain/pyproject.toml:4` description: *"LangChain **sidecar SDK** … companion to LangSmith."* Inaccurate post-pivot (AGT-backed, in-process enforcement; not a sidecar SDK).

### DRIFT-5 (MED) — `docs/security/THREAT-MODEL.md` is sidecar-centric
Scope (`:4`,`:12`), trust boundaries (`:28` "Loopback sidecar boundary"), and threats 2/3 (sidecar impersonation, port hijack) assume the loopback sidecar as the decision channel. Post-pivot, default local enforcement is **in-process via AGT** — those threats are moot for the default path; the model needs an AGT-in-process boundary (and should keep the sidecar threats scoped to the optional remote-daemon mode).

### DRIFT-6 (MED) — contributor/security docs describe the sidecar HTTP client as the model
`CONTRIBUTING.md:35,47` ("ships … the sidecar HTTP client"; "Sidecar wire-protocol changes") and `SECURITY.md:23` ("The sidecar wire protocol as consumed by these SDKs") present the sidecar as the architecture. It is now optional/legacy (remote-daemon); AGT in-process is primary.

### LOW — minor residual mentions
`FEATURE_INDEX.md:39` ("driving sidecar endpoints"), `.github/ISSUE_TEMPLATE/feature_request.yml:43`. Cosmetic.

## Aligned (verified MATCH — no action)
- `docs/ARCHITECTURE-BOUNDARIES.md` (pulled) ↔ `CONCEPT.md` ↔ `ADR-0001`: public local / hosted decision service / managed Azure layering is **consistent** with "extends AGT + Azure upstream." 
- `README.md` "Built on AGT" + "Public and hosted layers": consistent.
- `pyproject.toml` Python floor 3.11 + CI matrix 3.11–3.13 (Phase 07): consistent.

## Blueprint Alignment

| Doc claim | Code reality | Status |
|---|---|---|
| ARCHITECTURE_PLAN body: local sidecar, init() needs sidecar | AGT in-process; `init_agt()`; sidecar package deleted | **DRIFT (1)** |
| SYSTEM_STATE: sidecar package Created; Python 3.10–3.13 | package deleted; floor 3.11 | **DRIFT (2)** |
| README Quickstart: `init()` governs dispatch | bare `init()` needs endpoint; `init_agt()` is the local path | **DRIFT (3)** |
| pyproject: "sidecar SDK" | AGT-backed in-process | **DRIFT (4)** |
| THREAT-MODEL: loopback sidecar boundary is the decision channel | in-process AGT default | **DRIFT (5)** |
| CONTRIBUTING/SECURITY: sidecar HTTP client is the model | sidecar optional/legacy | **DRIFT (6)** |
| ARCHITECTURE-BOUNDARIES / CONCEPT / ADR-0001 layering | matches AGT+hosted+Azure | MATCH |

## Recommendations (feed the remediation cycle)

1. **(HIGH)** Rewrite `ARCHITECTURE_PLAN.md` body to the AGT-in-process architecture; demote the sidecar to "optional remote-daemon mode."
2. **(HIGH)** Refresh `SYSTEM_STATE.md` to current reality (Phase 09): sidecar package removed; Python 3.11; AGT enforcement; correct test counts.
3. **(MED)** Fix Quickstarts (root + package README) to `init_agt(...)`; keep `init()` documented as the remote-daemon path.
4. **(MED)** Update `pyproject.toml` description (drop "sidecar SDK"; reflect AGT-backed dispatch enforcement).
5. **(MED)** Re-scope `THREAT-MODEL.md` around the in-process AGT boundary; mark sidecar threats as remote-daemon-only.
6. **(MED)** Update `CONTRIBUTING.md`/`SECURITY.md` to "AGT-backed in-process enforcement; optional sidecar client."
7. **Out of scope:** ADR-0001, AGT-COMPONENT-MAP, `plan-qor-phase*`, `research-brief-*`, META_LEDGER — historical; do not edit.

## Updated Knowledge
Doc-drift pattern for the genome: a multi-phase architecture pivot (sidecar→AGT-in-process) updated code + the blueprint *header* but left the blueprint *body*, SYSTEM_STATE, Quickstart, package metadata, and threat model describing the retired design. SYSTEM_STATE drift is the highest-signal (it is the canonical "current reality" artifact and went stale).

---

_Research complete. Findings are advisory — implementation decisions remain with the Governor._
