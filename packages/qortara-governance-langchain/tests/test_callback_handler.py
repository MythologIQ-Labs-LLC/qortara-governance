"""QortaraCallbackHandler coverage (GAP-H-6).

The callback is additive observability — it emits OBSERVE evidence for
chain/retriever boundaries, only when an agent context is set, and never raises
into the caller.
"""

from __future__ import annotations

from qortara_governance.callback import QortaraCallbackHandler
from qortara_governance.context import AgentContext, set_context
from qortara_governance.context import _ctx_var
from qortara_protocol import DecisionKind, EvidenceRecord


class _RecordingClient:
    blocking_io = True

    def __init__(self) -> None:
        self.evidence: list[EvidenceRecord] = []

    def submit_evidence(self, records: list[EvidenceRecord]) -> None:
        self.evidence.extend(records)


class _BoomClient:
    blocking_io = True

    def submit_evidence(self, records: list[EvidenceRecord]) -> None:
        raise RuntimeError("submit failed")


def _ctx() -> AgentContext:
    return AgentContext(tenant_id="t", agent_id="a", session_id="s")


def test_chain_start_emits_observe_evidence_with_context() -> None:
    client = _RecordingClient()
    handler = QortaraCallbackHandler(client)
    set_context(_ctx())
    handler.on_chain_start({"name": "my_chain"}, {})
    assert len(client.evidence) == 1
    rec = client.evidence[0]
    assert rec.decision.decision_kind == DecisionKind.OBSERVE
    # Built via qortara_governance.evidence.decision_evidence (B5): observe is a
    # terminal observed state.
    from qortara_protocol import ExecutionResult

    assert rec.execution_result == ExecutionResult.OBSERVED
    assert rec.tenant_id == "t"


def test_retriever_start_emits_evidence_with_context() -> None:
    client = _RecordingClient()
    handler = QortaraCallbackHandler(client)
    set_context(_ctx())
    handler.on_retriever_start({"name": "vec"}, "a query")
    assert len(client.evidence) == 1


def test_no_context_emits_nothing() -> None:
    client = _RecordingClient()
    handler = QortaraCallbackHandler(client)
    _ctx_var.set(None)  # no agent context
    handler.on_chain_start({"name": "my_chain"}, {})
    assert client.evidence == []


def test_callback_never_raises_on_client_error() -> None:
    handler = QortaraCallbackHandler(_BoomClient())  # type: ignore[arg-type]
    set_context(_ctx())
    # None of these may propagate the client's RuntimeError.
    handler.on_chain_start({"name": "c"}, {})
    handler.on_retriever_start({"name": "r"}, "q")
    handler.on_retriever_error(ValueError("boom"))
