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

## Status (B5)

**Defined** here, and used today by `QortaraCallbackHandler` (which emits an `observe`
decision event for chain/retriever boundaries).

**Deferred (design decision):** emitting evidence from the *enforcement dispatch path*
itself (a decision event on every gate, an execution event after each permitted run). That
is a behavior change with a perf budget, and the default in-process AGT client's
`submit_evidence` is a no-op (no sink) — so it requires a deliberate opt-in design (when to
emit, where it goes) rather than being switched on by default. Tracked in BACKLOG [B5].
