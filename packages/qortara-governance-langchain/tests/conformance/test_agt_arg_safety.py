"""Conformance: AGT argument-level checks run on real tool args (Phase 09).

Closes the Increment-B gap — tool_input is threaded to AGT's in-process
PolicyEngine so its SQL/code/path checks fire. Wire privacy is unaffected
(SidecarClient still does not inline args).
"""

from __future__ import annotations

import time

import httpx
import pytest
from langchain_core.tools import tool

import qortara_governance
from qortara_governance import context as _ctxmod
from qortara_governance.agt_engine import AgtDecisionClient, AgtPolicyAdapter
from qortara_governance.client import SidecarClient
from qortara_governance.context import AgentContext, set_context
from qortara_governance.exceptions import QortaraPolicyDenied
from qortara_governance.patches import apply_patches
from qortara_governance.patches.action_builder import build_tool_action
from qortara_protocol import DecisionKind

_LOG: list[str] = []


@tool
def database_query(query: str) -> str:
    """Allow-listed tool whose args AGT inspects for destructive SQL."""
    _LOG.append(query)
    return f"rows-for:{query}"


@pytest.fixture(autouse=True)
def _isolate() -> None:
    _LOG.clear()
    yield
    qortara_governance.unpatch_all()
    _ctxmod._ctx_var.set(None)


def _client() -> AgtDecisionClient:
    return AgtDecisionClient(AgtPolicyAdapter().allow("agent-x", ["database_query"]))


def _req():
    return build_tool_action(
        "database_query", {}, AgentContext(tenant_id="t", agent_id="agent-x", session_id="s")
    )


def test_safe_arg_allows() -> None:
    assert _client().decide(_req(), {"query": "SELECT 1"}).decision_kind == DecisionKind.ALLOW


def test_destructive_sql_denied() -> None:
    decision = _client().decide(_req(), {"query": "DROP TABLE users"})
    assert decision.decision_kind == DecisionKind.DENY
    assert "SQL" in decision.rationale or "DROP" in decision.rationale.upper()


def test_dispatch_patch_blocks_dangerous_arg() -> None:
    apply_patches(_client())
    set_context(AgentContext(tenant_id="t", agent_id="agent-x", session_id="s"))
    with pytest.raises(QortaraPolicyDenied):
        database_query.invoke({"query": "DROP TABLE users"})
    assert _LOG == []  # body never ran


def test_sidecar_client_does_not_inline_tool_input() -> None:
    # Wire privacy: SidecarClient accepts tool_input for interface parity but
    # must NOT send the raw args over the wire.
    seen: dict[str, str] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["body"] = request.content.decode()
        return httpx.Response(
            200,
            json={
                "decision_kind": "allow",
                "policy_version_sha256": "x",
                "rationale": "ok",
                "policy_pack_id": "p",
                "ts": time.time(),
            },
        )

    c = SidecarClient("http://fake", None)
    c._client = httpx.Client(base_url="http://fake", transport=httpx.MockTransport(handler))
    c.decide(_req(), {"query": "SECRET-DROP-VALUE"})
    assert "SECRET-DROP-VALUE" not in seen["body"]  # args not inlined
