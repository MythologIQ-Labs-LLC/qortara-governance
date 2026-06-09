"""Evidence event builders — decision events vs execution events (B5).

`qortara_protocol.EvidenceRecord` carries both the policy `decision` and an
`execution_result`. This module separates the two event kinds so they are not
conflated:

- **decision_evidence** — a TERMINAL gate verdict (the policy stopped here):
  `deny`, `exempt`, `observe`. No tool ran, so the execution_result IS the
  terminal state. Non-terminal verdicts (`allow`, `require_approval`, and the
  transform kinds) are *refused* — they have no execution outcome at decision
  time; emit `execution_evidence` after the run instead.
- **execution_evidence** — the outcome of actually running the tool:
  `executed`, `errored`, `timed_out`, `approved`, `denied`.

Both are pure constructors (no IO). Wiring emission into the dispatch path is a
separate, deferred design decision (see docs/evidence-schema.md).
"""

from __future__ import annotations

import time
import uuid

from qortara_protocol import (
    ActionDecision,
    ActionRequest,
    DecisionKind,
    EvidenceRecord,
    ExecutionResult,
)

# Terminal gate verdicts: the decision is the final state, no tool executed.
_TERMINAL_RESULT: dict[DecisionKind, ExecutionResult] = {
    DecisionKind.DENY: ExecutionResult.DENIED,
    DecisionKind.EXEMPT: ExecutionResult.EXEMPT,
    DecisionKind.OBSERVE: ExecutionResult.OBSERVED,
}


def _record(
    request: ActionRequest,
    decision: ActionDecision,
    execution_result: ExecutionResult,
    duration_ms: int,
    result_payload_ref: str | None,
) -> EvidenceRecord:
    return EvidenceRecord(
        evidence_id=str(uuid.uuid4()),
        tenant_id=request.tenant_id,
        request=request,
        decision=decision,
        execution_result=execution_result,
        result_payload_ref=result_payload_ref,
        duration_ms=duration_ms,
        ts=time.time(),
    )


def decision_evidence(
    request: ActionRequest, decision: ActionDecision
) -> EvidenceRecord:
    """Evidence for a TERMINAL gate verdict (deny/exempt/observe) — no tool ran.

    Raises ``ValueError`` for a non-terminal verdict (allow/require_approval/
    transform): those have no execution outcome at decision time — emit
    ``execution_evidence`` after the run instead. The refusal is deliberate: it
    forbids fabricating an execution result for a decision that hasn't executed.
    """
    result = _TERMINAL_RESULT.get(decision.decision_kind)
    if result is None:
        raise ValueError(
            "decision_evidence requires a terminal verdict (deny/exempt/observe); "
            f"got {decision.decision_kind.value!r}. Emit execution_evidence after "
            "the run instead."
        )
    return _record(request, decision, result, 0, None)


def execution_evidence(
    request: ActionRequest,
    decision: ActionDecision,
    result: ExecutionResult,
    *,
    duration_ms: int = 0,
    result_payload_ref: str | None = None,
) -> EvidenceRecord:
    """Evidence for the outcome of actually running the tool (post-run)."""
    return _record(request, decision, result, duration_ms, result_payload_ref)
