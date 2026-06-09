"""Evidence builders: decision events vs execution events (B5)."""

from __future__ import annotations

import time

import pytest

from qortara_governance.evidence import decision_evidence, execution_evidence
from qortara_protocol import (
    ActionDecision,
    ActionRequest,
    ActionType,
    DecisionKind,
    ExecutionResult,
    Framework,
)


def _req() -> ActionRequest:
    return ActionRequest(
        tenant_id="tenant-1",
        agent_id="a",
        session_id="s",
        framework=Framework.LANGCHAIN,
        action_type=ActionType.TOOL_DISPATCH,
        target_resource="tool:x",
        requested_capability="tool:x",
        ts=time.time(),
    )


def _decision(kind: DecisionKind) -> ActionDecision:
    return ActionDecision(
        decision_kind=kind,
        policy_version_sha256="x",
        rationale="r",
        policy_pack_id="p",
        ts=time.time(),
    )


@pytest.mark.parametrize(
    "kind,expected",
    [
        (DecisionKind.DENY, ExecutionResult.DENIED),
        (DecisionKind.EXEMPT, ExecutionResult.EXEMPT),
        (DecisionKind.OBSERVE, ExecutionResult.OBSERVED),
    ],
)
def test_decision_evidence_terminal_verdicts(
    kind: DecisionKind, expected: ExecutionResult
) -> None:
    rec = decision_evidence(_req(), _decision(kind))
    assert rec.execution_result == expected
    assert rec.decision.decision_kind == kind
    assert rec.tenant_id == "tenant-1"
    assert rec.duration_ms == 0
    assert rec.evidence_id  # a fresh id was assigned


@pytest.mark.parametrize(
    "kind",
    [
        DecisionKind.ALLOW,
        DecisionKind.REQUIRE_APPROVAL,
        DecisionKind.DOWNGRADE,
        DecisionKind.REDACT,
        DecisionKind.SANDBOX,
    ],
)
def test_decision_evidence_rejects_non_terminal(kind: DecisionKind) -> None:
    # Non-terminal verdicts have no execution outcome at decision time — the
    # builder refuses rather than fabricate one.
    with pytest.raises(ValueError):
        decision_evidence(_req(), _decision(kind))


def test_execution_evidence_builder() -> None:
    rec = execution_evidence(
        _req(),
        _decision(DecisionKind.ALLOW),
        ExecutionResult.EXECUTED,
        duration_ms=42,
        result_payload_ref="ref-123",
    )
    assert rec.execution_result == ExecutionResult.EXECUTED
    assert rec.decision.decision_kind == DecisionKind.ALLOW
    assert rec.duration_ms == 42
    assert rec.result_payload_ref == "ref-123"
    assert rec.tenant_id == "tenant-1"


def test_execution_evidence_defaults() -> None:
    rec = execution_evidence(
        _req(), _decision(DecisionKind.ALLOW), ExecutionResult.ERRORED
    )
    assert rec.duration_ms == 0
    assert rec.result_payload_ref is None
