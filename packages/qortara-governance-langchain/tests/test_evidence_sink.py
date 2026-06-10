"""Unit tests for the EvidenceSink contract, safe_emit, and OTelEvidenceSink."""

from __future__ import annotations

import time

from qortara_governance.evidence import decision_evidence
from qortara_governance.evidence_sink import (
    EvidenceSink,
    OTelEvidenceSink,
    safe_emit,
)
from qortara_protocol import (
    ActionDecision,
    ActionRequest,
    ActionType,
    DecisionKind,
    EvidenceRecord,
    Framework,
)


def _record() -> EvidenceRecord:
    req = ActionRequest(
        tenant_id="t",
        agent_id="a",
        session_id="s",
        framework=Framework.LANGCHAIN,
        action_type=ActionType.TOOL_DISPATCH,
        target_resource="x",
        requested_capability="tool:x",
        ts=time.time(),
    )
    dec = ActionDecision(
        decision_kind=DecisionKind.DENY,
        policy_version_sha256="x",
        rationale="r",
        policy_pack_id="p",
        ts=time.time(),
    )
    return decision_evidence(req, dec)


class _Recording:
    def __init__(self) -> None:
        self.records: list[EvidenceRecord] = []

    def submit_evidence(self, records: list[EvidenceRecord]) -> None:
        self.records.extend(records)


class _Throwing:
    def submit_evidence(self, records: list[EvidenceRecord]) -> None:
        raise RuntimeError("down")


def test_recording_and_otel_sinks_satisfy_protocol() -> None:
    assert isinstance(_Recording(), EvidenceSink)
    assert isinstance(OTelEvidenceSink(), EvidenceSink)


def test_safe_emit_forwards_record() -> None:
    sink = _Recording()
    safe_emit(sink, _record())
    assert len(sink.records) == 1


def test_safe_emit_swallows_sink_failure() -> None:
    # Must not raise even though the sink raises.
    safe_emit(_Throwing(), _record())


def test_otel_sink_is_noop_without_recording_span() -> None:
    # No active recording span in a plain test process — must not raise.
    OTelEvidenceSink().submit_evidence([_record()])
