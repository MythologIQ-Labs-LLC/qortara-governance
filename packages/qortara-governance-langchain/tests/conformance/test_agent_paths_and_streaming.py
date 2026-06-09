"""Conformance: streaming + multi-tool ToolNode dispatch are governed (B1-followup).

On langchain >=1.0 the legacy AgentExecutor is removed; the modern `create_agent`
path executes tools via LangGraph `ToolNode` (governed below) and direct
`tool.run`/`invoke` (governed via the run/arun funnel — see
test_run_chokepoint_and_decision_model). These tests cover the remaining dispatch
surfaces: `BaseTool.stream`/`.astream` (which funnel through invoke -> run) and a
`ToolNode` carrying multiple tool_calls.
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
from qortara_protocol import DecisionKind


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


def _deny(fake_client: Any) -> Any:
    fake_client.scripted_decisions = [DecisionKind.DENY]
    return fake_client


# --- BaseTool.stream / .astream funnel through run/arun ---


def test_stream_is_governed(fake_client: Any, ctx: AgentContext) -> None:
    apply_patches(_deny(fake_client))
    tool_obj = RecordingTool()
    with pytest.raises(QortaraPolicyDenied):
        list(tool_obj.stream("x"))
    assert tool_obj._ran is False


def test_astream_is_governed(fake_client: Any, ctx: AgentContext) -> None:
    apply_patches(_deny(fake_client))
    tool_obj = RecordingTool()

    async def _drive() -> None:
        with pytest.raises(QortaraPolicyDenied):
            async for _ in tool_obj.astream("x"):
                pass

    asyncio.run(_drive())
    assert tool_obj._ran is False


# --- ToolNode with multiple tool_calls: governed before any tool body runs ---


def test_toolnode_multi_tool_denied_before_any_runs(
    fake_client: Any, ctx: AgentContext
) -> None:
    pytest.importorskip("langgraph.prebuilt")
    from langchain_core.messages import AIMessage
    from langgraph.prebuilt import ToolNode

    log_a: list[str] = []
    log_b: list[str] = []

    @tool
    def tool_a(x: str) -> str:
        """Tool A."""
        log_a.append(x)
        return x

    @tool
    def tool_b(y: str) -> str:
        """Tool B."""
        log_b.append(y)
        return y

    apply_patches(_deny(fake_client))
    node = ToolNode([tool_a, tool_b])
    msg = AIMessage(
        content="",
        tool_calls=[
            {"name": "tool_a", "args": {"x": "1"}, "id": "1"},
            {"name": "tool_b", "args": {"y": "2"}, "id": "2"},
        ],
    )
    with pytest.raises(QortaraPolicyDenied):
        node.invoke({"messages": [msg]})
    assert log_a == [] and log_b == []  # neither tool body ran
