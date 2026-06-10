# Evidence Event Schema

Governance produces **evidence** — an auditable record of what policy decided and what
then happened. The wire/record type is `qortara_protocol.EvidenceRecord`, which carries
both the `decision` (an `ActionDecision`) and an `execution_result`. Because one record
can describe either *the decision* or *the run*, this project separates evidence into two
event kinds so they are never conflated. Builders live in
`qortara_governance.evidence` (`decision_evidence`, `execution_evidence`).

## Two event kinds

### Decision event — `decision_evidence(request, decision)`
A **terminal gate verdict**: the policy stopped here and **no tool ran**. The
`execution_result` *is* the terminal state.

| `decision_kind` | `execution_result` |
|---|---|
| `deny` | `denied` |
| `exempt` | `exempt` |
| `observe` | `observed` |

Non-terminal verdicts — `allow`, `require_approval`, and the transform kinds
(`downgrade`/`redact`/`sandbox`) — are **rejected** by `decision_evidence` (it raises
`ValueError`). They have no execution outcome at decision time; the tool either runs (emit
an **execution event** afterward) or is routed elsewhere. Refusing to map them prevents
fabricating an execution result for something that never executed.

### Execution event — `execution_evidence(request, decision, result, *, duration_ms=0, result_payload_ref=None)`
The outcome of **actually running the tool** (a permitted dispatch):

| `execution_result` | meaning |
|---|---|
| `executed` | ran to completion |
| `errored` | raised during execution |
| `timed_out` | exceeded its time budget |
| `approved` | a human approval was granted, then it ran |

## Field mapping

Both builders construct an `EvidenceRecord` with:

| field | source |
|---|---|
| `evidence_id` | fresh UUID4 |
| `tenant_id` | `request.tenant_id` |
| `request` | the `ActionRequest` |
| `decision` | the `ActionDecision` |
| `execution_result` | per the tables above |
| `duration_ms` | `0` for a decision event; the measured runtime for an execution event |
| `result_payload_ref` | `None` for a decision event; an optional reference for an execution event (raw payloads are never inlined) |
| `ts` | wall-clock at build time |

## Emission from the dispatch path (Phase 21 — opt-in)

Evidence is emitted from the enforcement dispatch path **only when an `EvidenceSink` is
configured** — `init(..., evidence_sink=...)` / `init_agt(..., evidence_sink=...)`. With no
sink (the default), nothing is emitted and the hot path is unchanged.

When a sink is set:
- a **decision event** is emitted on a terminal `deny` (before the call is blocked);
- an **execution event** (`executed` / `errored` + measured `duration_ms`) is emitted after
  each permitted `BaseTool.run`/`.arun`.

Guarantees (all conformance-tested): emission is best-effort and **never raises into the
caller** (`safe_emit`); it **never weakens fail-closed** (a throwing sink does not stop a
deny from raising); async emission runs **off the event loop** (`asyncio.to_thread`).
`QortaraCallbackHandler` continues to emit `observe` decision events for chain/retriever
boundaries.

### Sinks
The sink contract is the existing `submit_evidence(list[EvidenceRecord]) -> None` shape, so a
`SidecarClient` can be its own sink. Built-in: `OTelEvidenceSink` (span event +
`qortara.evidence_id` attribute; no-op without OpenTelemetry).

### Deferred (B5 follow-up)
- **ToolNode per-tool execution evidence** — `ToolNode` runs its tools internally, so only a
  *decision* event (on deny) is emitted there; per-tool post-run outcome needs a deeper hook.
- `require_approval` / transform-kind blocked dispatches emit no decision event yet (the
  terminal-result taxonomy has no clean mapping for them).
- `timed_out` (no timeout mechanism on the sync path).
