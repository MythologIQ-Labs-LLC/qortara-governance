# Plan — Phase 21: opt-in dispatch-path evidence emission (B5)

**Risk Grade**: L3 — **high-risk target**: touches the enforcement dispatch hot path.
**iteration**: ready-for-audit
**Author**: Governor (auto-dev-1)
**Base**: `main` (`166a688`); carries the uncommitted ideation + research briefs + ledger #48.
**Inputs**: ideation `dispatch-path-evidence-emission` + research brief
`docs/research-brief-b5-dispatch-evidence-emission-2026-06-09.md` (plan-ready, no DRIFT).

## High-risk-target / impact assessment
Touches `tool_patches`/`langgraph_patches` — the bypass-resistant enforcement chokepoint. The
binding invariants (must all hold, verified by tests):
1. **No sink (default) ⇒ zero behavior change** and zero added work beyond a `None` check.
2. **Emission NEVER raises into the caller** (best-effort `try/except`, mirroring `callback.py:84-87`).
3. **Emission NEVER alters the decision** — the gate + `enforce_decision` run identically with or
   without a sink, and even with a *throwing* sink the deny still raises (fail-closed unchanged).
4. **No new bypass surface** — emission only wraps the *already-occurring* `original(...)` call
   (research F1: the gate fires before `original`, so the run/arun funnel is untouched).
5. **Async path stays non-blocking** — sink calls on the async path go through `asyncio.to_thread`.

## Promise (Definition of Done)

### D1 — Vision
An operator can opt into an evidence trail — a decision event on each terminal deny, an execution
event after each permitted run — routed to a configured sink, with zero cost when unconfigured and
no weakening of fail-closed enforcement.

### D2 — Code
1. **`EvidenceSink` Protocol** (new `evidence_sink.py`): `submit_evidence(records: list[EvidenceRecord]) -> None`
   — the existing best-effort contract (research F2). `SidecarClient` already satisfies it. Ship one
   built-in: `OTelEvidenceSink` (emits a span event + `tag_evidence_id`, built on `otel.py`; guarded
   no-op without OTel). Add `_safe_emit(sink, record)` (never raises).
2. **Thread `evidence_sink`** from `init(..., evidence_sink=None)` / `init_agt(..., evidence_sink=None)`
   → `apply_patches(client, *, observe, evidence_sink=None)` → `_default_adapters(observe, evidence_sink)`
   → adapters → module `apply(client, observe, evidence_sink)` → wrappers. Default `None`.
3. **`_decide_or_raise` returns `tuple[ActionRequest, ActionDecision] | None`** (research F5): exempt /
   no-context → `None`; on a **terminal deny** (enforce, not observe) emit `decision_evidence` via
   `_safe_emit` **before** `enforce_decision` raises; on permit/observe return `(request, decision)`.
4. **BaseTool wrappers — execution-evidence** (research F1): when a sink is set and a pair is returned,
   wrap `original(...)` in `perf_counter` + `try/except`: emit `execution_evidence(EXECUTED, duration)`
   on success, `execution_evidence(ERRORED, duration)` on exception (then re-raise). Async: emit via
   `asyncio.to_thread`. No sink ⇒ the wrapper takes the existing fast path unchanged.
5. **`_decide_each` (ToolNode)**: emit `decision_evidence` on terminal deny per tool_call via
   `_safe_emit`. (ToolNode execution-evidence is deferred — the node runs tools internally; per-tool
   post-run outcome needs deeper hooking. Documented.)
6. Export `EvidenceSink`, `OTelEvidenceSink`.

### D3 — Governance/docs
Update `docs/evidence-schema.md` (emission now wired, opt-in; what fires where). README/Configuration
note the `evidence_sink` param. BACKLOG [B5] → done (opt-in emission shipped; ToolNode execution-evidence
follow-up noted). Ledger GATE + SEAL; commit the carried ideation/research artifacts.

### D4 — Empirical (the ideation `evidence_required` set)
- `test_no_sink_zero_emission` — no sink ⇒ no records, behavior identical (allow runs, deny raises).
- `test_emission_never_raises` — a sink whose `submit_evidence` raises does NOT break the call
  (allow still runs; deny still raises `QortaraPolicyDenied`) — fail-closed unchanged.
- `test_deny_emits_decision_evidence` — terminal deny ⇒ one `decision_evidence` (execution_result=denied)
  and the tool body never runs.
- `test_allow_emits_execution_evidence` — permitted run ⇒ one `execution_evidence` (executed) with
  `duration_ms >= 0`.
- `test_errored_run_emits_errored_evidence` — a tool that raises ⇒ `execution_evidence(errored)` +
  the exception propagates.
- `test_async_emission_off_loop` — async permitted run emits without stalling the loop (sink called
  off the event-loop thread).
- `test_toolnode_deny_emits_decision_evidence` — ToolNode terminal deny ⇒ decision_evidence.

## Section 4 Razor
One Protocol + one built-in sink + a `_safe_emit` helper; thread one optional param (mirrors the
Phase-14 `observe` threading); refactor `_decide_or_raise`'s return + wrap `original(...)`. No new
runtime dep (OTel already present). Default path unchanged.

## Blast radius
The hot path gains: when `evidence_sink is None` → one `if` (fast path, unchanged). When set → a
best-effort emit on deny + a `perf_counter`/`try/except` around the run. `_decide_or_raise`'s return
type changes (internal); callers updated. `init`/`init_agt`/`apply_patches` gain an optional kwarg
(additive). New public `EvidenceSink`/`OTelEvidenceSink` (additive). ToolNode execution-evidence
explicitly out of scope.

## Non-goals (deferred, with rationale)
- ToolNode per-tool execution-evidence (node runs tools internally — deeper hook; follow-up).
- `timed_out` result (no timeout mechanism on the sync path — ideation exclusion).
- Default-on emission, evidence signing, hosted ledger (ideation non-goals).
- Standing residuals unchanged.

## Review Boundary
Commit (incl. carried ideation/research) + push + open a new PR off `main`; track CI; hand off for
review/merge. NO tag, NO PyPI, NO merge without approval. No AI footer.
