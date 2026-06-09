"""Conformance: BaseTool.invoke / .ainvoke flow through policy enforcement.

Each test names the dispatch path, injects a decision via SidecarClient.decide,
and asserts (a) whether the underlying tool body executed and (b) the exception
raised. A silently broken enforcement path turns these red.
"""

from __future__ import annotations

import time

import pytest
from langchain_core.tools import tool

import qortara_governance
from qortara_governance import context as _ctxmod
from qortara_governance.client import SidecarClient
from qortara_governance.context import AgentContext, set_context
from qortara_governance.decorators import qortara_exempt
from qortara_governance.exceptions import QortaraApprovalRequired, QortaraPolicyDenied
from qortara_protocol import ActionDecision, DecisionKind

_LOG: list[str] = []


@tool
def recording_tool(payload: str) -> str:
    """Echo tool that records that its body executed."""
    _LOG.append(payload)
    return f"ran:{payload}"


@tool
def exempt_tool(payload: str) -> str:
    """Echo tool marked exempt from enforcement."""
    _LOG.append(f"exempt:{payload}")
    return f"exempt-ran:{payload}"


qortara_exempt(exempt_tool)


@pytest.fixture(autouse=True)
def _isolate(monkeypatch: pytest.MonkeyPatch) -> None:
    _LOG.clear()
    monkeypatch.setenv("QORTARA_SIDECAR_ENDPOINT", "http://127.0.0.1:9999")
    monkeypatch.setattr(SidecarClient, "require_reachable", lambda self: None)
    yield
    qortara_governance.unpatch_all()
    _ctxmod._ctx_var.set(None)


def _inject(monkeypatch: pytest.MonkeyPatch, kind: DecisionKind) -> None:
    decision = ActionDecision(
        decision_kind=kind,
        policy_version_sha256="conformance",
        rationale="conformance-injected",
        policy_pack_id="conformance",
        approval_url="https://approve.example/x" if kind == DecisionKind.REQUIRE_APPROVAL else None,
        ts=time.time(),
    )
    monkeypatch.setattr(
        SidecarClient, "decide", lambda self, request, tool_input=None: decision
    )


def _govern(monkeypatch: pytest.MonkeyPatch, kind: DecisionKind) -> None:
    qortara_governance.init(tenant_key="tk-conformance")
    _inject(monkeypatch, kind)
    set_context(AgentContext(tenant_id="t", agent_id="a", session_id="s"))


def test_basetool_sync_allow(monkeypatch: pytest.MonkeyPatch) -> None:
    _govern(monkeypatch, DecisionKind.ALLOW)
    result = recording_tool.invoke({"payload": "x"})
    assert result == "ran:x"
    assert _LOG == ["x"]  # executed exactly once


def test_basetool_sync_deny(monkeypatch: pytest.MonkeyPatch) -> None:
    _govern(monkeypatch, DecisionKind.DENY)
    with pytest.raises(QortaraPolicyDenied):
        recording_tool.invoke({"payload": "x"})
    assert _LOG == []  # body never ran


def test_basetool_sync_require_approval(monkeypatch: pytest.MonkeyPatch) -> None:
    _govern(monkeypatch, DecisionKind.REQUIRE_APPROVAL)
    with pytest.raises(QortaraApprovalRequired):
        recording_tool.invoke({"payload": "x"})
    assert _LOG == []


@pytest.mark.asyncio
async def test_basetool_async_allow(monkeypatch: pytest.MonkeyPatch) -> None:
    _govern(monkeypatch, DecisionKind.ALLOW)
    result = await recording_tool.ainvoke({"payload": "y"})
    assert result == "ran:y"
    assert _LOG == ["y"]


@pytest.mark.asyncio
async def test_basetool_async_deny(monkeypatch: pytest.MonkeyPatch) -> None:
    _govern(monkeypatch, DecisionKind.DENY)
    with pytest.raises(QortaraPolicyDenied):
        await recording_tool.ainvoke({"payload": "y"})
    assert _LOG == []


def test_exempt_tool_bypasses_enforcement(monkeypatch: pytest.MonkeyPatch) -> None:
    # Even with a DENY decision, an exempt tool executes (short-circuits eval).
    _govern(monkeypatch, DecisionKind.DENY)
    result = exempt_tool.invoke({"payload": "z"})
    assert result == "exempt-ran:z"
    assert _LOG == ["exempt:z"]


def test_no_context_no_enforcement(monkeypatch: pytest.MonkeyPatch) -> None:
    # Cooperative-process boundary (THREAT-MODEL §5): no agent context => the
    # patch returns early and the tool runs even under a DENY decision.
    qortara_governance.init(tenant_key="tk-conformance")
    _inject(monkeypatch, DecisionKind.DENY)
    # deliberately do NOT set_context
    result = recording_tool.invoke({"payload": "nc"})
    assert result == "ran:nc"
    assert _LOG == ["nc"]
