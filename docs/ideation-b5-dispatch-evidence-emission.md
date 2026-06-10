# Ideation — Dispatch-Path Evidence Emission (B5 emission)

**Phase**: ideation (Phase 59 / Issue #20) · **Persona**: Analyst · **Risk Grade (proposed)**: L3
**Status**: `research_required` → next phase **/qor-research**
**Scope note**: ideation only — no implementation, no Review Boundary mutation. Frames the
problem *before* solutioning (SG-PrematureSolutioning-A).

---

## 1. Spark Record
- **observation**: The enforcement dispatch path (`BaseTool.run`/`.arun`, `ToolNode`) makes a
  policy decision at *every* gate, but emits **no auditable evidence**. Only the observability
  `QortaraCallbackHandler` emits — and only for chain/retriever OBSERVE events, not for the
  security-relevant tool-dispatch decision or its execution outcome.
- **initial_question**: How should governance emit a *decision event* per gate and an *execution
  event* per permitted run from the dispatch path — without weakening fail-closed enforcement,
  blocking the call, or generating evidence with nowhere to go?
- **why_now**: Phase 20 (B5) **defined** the evidence schema + builders
  (`qortara_governance.evidence.decision_evidence` / `execution_evidence`) but nothing on the
  dispatch path calls them. The schema is ready; the wiring is the gap. Compliance/audit surfaces
  (EU AI Act Art. 12 logging, NIST AI RMF MEASURE/MANAGE) want a decision+execution trail.

## 2. Problem Frame
- **affected_actors**: compliance/audit owner; security operator (incident forensics);
  agent developer/operator (perf + ergonomics); hosted-plane consumer (evidence pipeline).
- **failure_mode**: Two opposed failures. **(a) Under-instrumentation** — enforcement leaves no
  per-call record of *what was decided* and *what then executed*; post-incident there is no
  evidence of allow/deny/approval + run outcome. **(b) Naive instrumentation** — always-on
  emission adds per-dispatch latency, generates evidence with no sink on the in-process default
  (silent drop = false sense of audit), or lets emission errors propagate and break governed calls.
- **cost_of_failure**: (a) → demonstrable-compliance gap + weak forensics; (b) → hot-path perf
  regression, silently-dropped audit (worse than none — it *looks* audited), or emission faults
  weakening the fail-closed guarantee that is the product's core value.

## 3. Transformation Statement
> A **compliance/security operator** moves from *"enforcement happens but leaves no per-call audit
> trail"* to *"every gate decision and every permitted execution produces a decision/execution
> evidence event routed to a configured sink"* — **without** adding blocking latency to the dispatch
> path, generating evidence with nowhere to go, or weakening fail-closed enforcement.

## 4. Assumption Ledger
| # | Statement | Category | Conf. | Impact if wrong | Validate | Blocking |
|---|---|---|---|---|---|---|
| A1 | The Phase-20 `decision_evidence`/`execution_evidence` builders are the right shape | technical | high | low | research | no |
| A2 | Operators want emission **opt-in**, not default-on | operational | med | high | design review | **yes** |
| A3 | Best-effort, never-raises emission (like the callback's try/except) is acceptable for evidence | security | high | high | threat-model | no |
| A4 | The in-process AGT path needs a **pluggable sink** (AgtDecisionClient.submit_evidence is a no-op) | technical | high | high | research | **yes** |
| A5 | Async emission can reuse `asyncio.to_thread` (already used for the decision) | technical | med | low | research | no |
| A6 | Execution-evidence requires wrapping the tool body to capture outcome + duration — a deeper hook than the current pre-dispatch decision point | technical | med | high | research | **yes** |

## 5. Scope Boundary (anti-goals)
- **non_goals (NOT building for Beta)**: a hosted evidence ledger / retention (Qortara Cloud);
  evidence **signing** (Ed25519 / RFC 8785 JCS — sidecar/hosted concern); **default-on** emission;
  a new evidence transport protocol.
- **limitations**: the in-process default sink is local + best-effort only; execution-evidence
  depends on capturing the tool result, which today's *pre-dispatch* hook does not do.
- **exclusions**: `timed_out` execution_result (no timeout mechanism on the sync path) — deferred
  unless a timeout wrapper exists; transform-kind (`downgrade`/`redact`/`sandbox`) evidence — those
  decision kinds are not implemented.
- **forbidden_interpretations**: emission must NOT be mandatory/blocking; an emission failure must
  NOT raise into the caller or alter the decision; raw tool args/results must NOT be inlined into
  evidence (privacy — `result_payload_ref` only).

## 6. Options Matrix
| Option | Summary | Selected | Rejection reason |
|---|---|---|---|
| **A — Opt-in EvidenceSink on the dispatch path** | A configurable sink (`init(..., evidence_sink=...)`); decision-evidence emitted at the gate (best-effort); execution-evidence emitted after a permitted run by wrapping `original(...)` in try/finally to capture executed/errored + duration. **Default: no sink → no emission (zero overhead).** | ✅ | — |
| B — Always-on via `client.submit_evidence` | Simplest wiring | ✗ | Generates evidence with no sink on the in-process default (silent drop = false audit); unconditional hot-path overhead; conflates "no sink" with "audited". |
| C — Callback-only (extend `QortaraCallbackHandler`) | Reuse the existing callback | ✗ | Callbacks fire *around* dispatch, not on the run/arun chokepoint — reintroduces the exact AGT #73 bypass gap the SDK closes; can't reliably capture the gate decision or bypass-proof execution outcome. |
| D — OTel spans/events as a sink | Emit via the existing `otel` module | (folds into A) | Not a competing architecture — a *sink implementation* under Option A. |

## 7. Governance Profile
- **risk_grade**: **L3** — touches the enforcement dispatch path + a compliance/audit surface.
- **evidence_required**: conformance proving — (1) no sink ⇒ zero emission + zero hot-path overhead;
  (2) emission never raises into the caller; (3) a decision event is emitted on deny/allow/approval;
  (4) an execution event captures executed/errored + duration; (5) fail-closed enforcement is
  unchanged even with a *throwing* sink; (6) the async path stays non-blocking.
- **escalation_triggers**: if execution-evidence wrapping risks the run/arun bypass-resistance →
  threat-model review; if the per-dispatch perf budget can't be met → re-scope to
  decision-evidence-only for Beta.

## 8. Failure Remediation Plan
| Failure class | Detection signal | Containment | Return phase |
|---|---|---|---|
| Emission adds unacceptable latency | hot-path perf test | keep default no-sink (zero overhead); split execution-evidence opt-in from decision-evidence | plan |
| A throwing/blocking sink breaks governed calls | conformance test w/ raising sink | best-effort try/except; never raise, never block the decision | research |
| Execution-evidence wrapping weakens run/arun bypass-resistance | red-team / threat-model review | decision-evidence-only for Beta; defer execution-evidence | research |
| Evidence generated with no sink (silent drop) | design review | opt-in: no sink = no emission, explicit | ideation/plan |
| Privacy: raw args/results inlined | secret-scan / threat-model | `result_payload_ref` only; never inline payloads | audit |

## 9. Readiness + Routing
- **status**: `research_required`
- **recommended_next_phase**: **/qor-research**
- **why**: the heaviest unknowns are empirical — (A4) the sink contract for the in-process path,
  (A6) whether execution-evidence can be captured by wrapping `run`/`arun` results *without*
  disturbing the bypass-resistant chokepoint, and the per-dispatch perf budget. Research verifies
  these against `langchain_core` run/arun result semantics + the `EvidenceRecord` sink options,
  then `/qor-plan` can act on a stable success boundary.

---
_Ideation artifact — advisory. No implementation; no Review Boundary mutation. The selected
direction (Option A, opt-in EvidenceSink) and the success criteria are the contract a later
/qor-research + /qor-plan must honor._
