"""Conformance: opt-in dispatch-path evidence emission (B5).

Binding invariants (high-risk target — enforcement hot path):
- no sink => no emission, behavior unchanged;
- emission NEVER raises into the caller (a throwing sink is swallowed);
- emission NEVER weakens fail-closed (deny still raises with a throwing sink);
- deny => a decision event; permitted run => an execution event (+ duration);
- async emission runs off the event loop.
"""

from __future__ import annotations

import asyncio
from typing import Any

import pytest
from langchain_core.tools import BaseTool, tool
from pydantic import PrivateAttr

from qortara_governance.context import AgentContext
from qortara_governance.exceptions import QortaraPolicyDenied
from qortara_governance.patches import apply_patches
from qortara_protocol import DecisionKind, EvidenceRecord, ExecutionResult


class _RecordingSink:
    def __init__(self) -> None:
        self.records: list[EvidenceRecord] = []

    def submit_evidence(self, records: list[EvidenceRecord]) -> None:
        self.records.extend(records)


class _ThrowingSink:
    def submit_evidence(self, records: list[EvidenceRecord]) -> None:
        raise RuntimeError("sink is down")


class RecordingTool(BaseTool):
    name: str = "recording_tool"
    description: str = "records whether its body ran"
    _ran: bool = PrivateAttr(default=False)

    def _run(self, action: str) -> str:  # type: ignore[override]
        self._ran = True
        return f"ran:{action}"

    async def _arun(self, action: str) -> str:  # type: ignore[override]
        self._ran = True
        return f"aran:{action}"


class ExplodingTool(BaseTool):
    name: str = "exploding_tool"
    description: str = "raises during execution"

    def _run(self, action: str) -> str:  # type: ignore[override]
        raise ValueError("boom")


def _deny(fake_client: Any) -> Any:
    fake_client.scripted_decisions = [DecisionKind.DENY]
    return fake_client


def _ctx() -> AgentContext:
    return AgentContext(tenant_id="t", agent_id="agent-x", session_id="s")


# --- deny => decision evidence; tool body never runs ---


def test_deny_emits_decision_evidence(fake_client: Any) -> None:
    from qortara_governance.context import set_context

    sink = _RecordingSink()
    apply_patches(_deny(fake_client), evidence_sink=sink)
    set_context(_ctx())
    tool = RecordingTool()
    with pytest.raises(QortaraPolicyDenied):
        tool.run("x")
    assert tool._ran is False
    assert len(sink.records) == 1
    assert sink.records[0].execution_result == ExecutionResult.DENIED
    assert sink.records[0].decision.decision_kind == DecisionKind.DENY


# --- allow => execution evidence with duration ---


def test_allow_emits_execution_evidence(fake_client: Any) -> None:
    from qortara_governance.context import set_context

    sink = _RecordingSink()
    apply_patches(fake_client, evidence_sink=sink)  # default decide => ALLOW
    set_context(_ctx())
    result = RecordingTool().run("x")
    assert result == "ran:x"
    assert len(sink.records) == 1
    rec = sink.records[0]
    assert rec.execution_result == ExecutionResult.EXECUTED
    assert rec.duration_ms >= 0


def test_errored_run_emits_errored_evidence(fake_client: Any) -> None:
    from qortara_governance.context import set_context

    sink = _RecordingSink()
    apply_patches(fake_client, evidence_sink=sink)  # ALLOW
    set_context(_ctx())
    with pytest.raises(ValueError):
        ExplodingTool().run("x")
    assert len(sink.records) == 1
    assert sink.records[0].execution_result == ExecutionResult.ERRORED


# --- emission never raises / never weakens fail-closed ---


def test_throwing_sink_does_not_break_allow_or_deny(fake_client: Any) -> None:
    from qortara_governance.context import set_context

    # allow: a throwing sink must not break the call
    apply_patches(fake_client, evidence_sink=_ThrowingSink())
    set_context(_ctx())
    assert RecordingTool().run("x") == "ran:x"


def test_throwing_sink_keeps_deny_fail_closed(fake_client: Any) -> None:
    from qortara_governance.context import set_context

    apply_patches(_deny(fake_client), evidence_sink=_ThrowingSink())
    set_context(_ctx())
    # deny must still raise even though the sink throws.
    with pytest.raises(QortaraPolicyDenied):
        RecordingTool().run("x")


# --- no sink => no emission, behavior unchanged ---


def test_no_sink_behavior_unchanged(fake_client: Any) -> None:
    from qortara_governance.context import set_context

    apply_patches(fake_client)  # no evidence_sink
    set_context(_ctx())
    assert RecordingTool().run("x") == "ran:x"  # allow runs, nothing emitted


# --- async permitted run emits execution evidence (off the loop) ---


def test_async_run_emits_execution_evidence(fake_client: Any) -> None:
    from qortara_governance.context import set_context

    sink = _RecordingSink()
    apply_patches(fake_client, evidence_sink=sink)
    set_context(_ctx())
    tool = RecordingTool()

    async def _run() -> str:
        return await tool.arun("x")

    result = asyncio.run(_run())
    assert result == "aran:x"
    assert len(sink.records) == 1
    assert sink.records[0].execution_result == ExecutionResult.EXECUTED


# --- ToolNode deny => decision evidence ---


def test_toolnode_deny_emits_decision_evidence(fake_client: Any) -> None:
    pytest.importorskip("langgraph.prebuilt")
    from langchain_core.messages import AIMessage
    from langgraph.prebuilt import ToolNode

    from qortara_governance.context import set_context

    @tool
    def t_a(x: str) -> str:
        """A tool."""
        return x

    sink = _RecordingSink()
    apply_patches(_deny(fake_client), evidence_sink=sink)
    set_context(_ctx())
    node = ToolNode([t_a])
    msg = AIMessage(
        content="", tool_calls=[{"name": "t_a", "args": {"x": "1"}, "id": "1"}]
    )
    with pytest.raises(QortaraPolicyDenied):
        node.invoke({"messages": [msg]})
    assert len(sink.records) == 1
    assert sink.records[0].execution_result == ExecutionResult.DENIED
