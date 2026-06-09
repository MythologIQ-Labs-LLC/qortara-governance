"""Conformance: the dispatch patch enforces via Microsoft AGT's PolicyEngine.

Proves qortara routes BaseTool dispatch decisions into AGT's real in-process
engine (ADR-0001 Increment B): allow-listed tools run; unlisted tools are
blocked with QortaraPolicyDenied before the body executes.
"""

from __future__ import annotations

import pytest
from langchain_core.tools import tool

import qortara_governance
from qortara_governance import context as _ctxmod
from qortara_governance.agt_engine import AgtDecisionClient, AgtPolicyAdapter
from qortara_governance.context import AgentContext, set_context
from qortara_governance.exceptions import QortaraPolicyDenied
from qortara_governance.patches import apply_patches
from qortara_protocol import DecisionKind
from qortara_governance.patches.action_builder import build_tool_action

_LOG: list[str] = []


@tool
def search(payload: str) -> str:
    """Allow-listed tool."""
    _LOG.append(payload)
    return f"searched:{payload}"


@tool
def delete_db(payload: str) -> str:
    """Tool NOT on the allow-list."""
    _LOG.append(f"deleted:{payload}")
    return "deleted"


@pytest.fixture(autouse=True)
def _isolate() -> None:
    _LOG.clear()
    yield
    qortara_governance.unpatch_all()
    _ctxmod._ctx_var.set(None)


def _adapter() -> AgtPolicyAdapter:
    return AgtPolicyAdapter().allow("agent-x", ["search"])


# --- unit: AgtDecisionClient maps AGT's verdict onto an ActionDecision ---

def test_agt_client_allows_permitted_tool() -> None:
    client = AgtDecisionClient(_adapter())
    req = build_tool_action("search", {}, AgentContext(tenant_id="t", agent_id="agent-x", session_id="s"))
    assert client.decide(req).decision_kind == DecisionKind.ALLOW


def test_agt_client_denies_unpermitted_tool() -> None:
    client = AgtDecisionClient(_adapter())
    req = build_tool_action("delete_db", {}, AgentContext(tenant_id="t", agent_id="agent-x", session_id="s"))
    decision = client.decide(req)
    assert decision.decision_kind == DecisionKind.DENY
    assert "delete_db" in decision.rationale  # AGT's violation names the tool


# --- integration: the real BaseTool dispatch patch enforces via AGT ---

def test_dispatch_patch_routes_allow_through_agt() -> None:
    apply_patches(AgtDecisionClient(_adapter()))
    set_context(AgentContext(tenant_id="t", agent_id="agent-x", session_id="s"))
    assert search.invoke({"payload": "q"}) == "searched:q"
    assert _LOG == ["q"]


def test_dispatch_patch_blocks_deny_through_agt() -> None:
    apply_patches(AgtDecisionClient(_adapter()))
    set_context(AgentContext(tenant_id="t", agent_id="agent-x", session_id="s"))
    with pytest.raises(QortaraPolicyDenied):
        delete_db.invoke({"payload": "drop"})
    assert _LOG == []  # body never ran


def test_init_agt_entry_point_enforces() -> None:
    qortara_governance.init_agt("agent-x", ["search"])
    set_context(AgentContext(tenant_id="t", agent_id="agent-x", session_id="s"))
    assert search.invoke({"payload": "ok"}) == "searched:ok"
    with pytest.raises(QortaraPolicyDenied):
        delete_db.invoke({"payload": "x"})
