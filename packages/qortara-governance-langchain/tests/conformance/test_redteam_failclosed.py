"""Adversarial fail-closed conformance (Phase 13 — red-team CRITICAL remediation).

These tests TRY TO BYPASS enforcement with realistic hostile inputs, per the
deep-audit meta-finding that happy-path conformance gave false confidence.
Covers GAP-SEC-02 (unsupported verdicts), -03 (malformed 2xx), -04 (engine
exception), -06 (ToolNode.ainvoke patched).
"""

from __future__ import annotations

import time

import httpx
import pytest

from qortara_governance.agt_engine import AgtDecisionClient, AgtPolicyAdapter
from qortara_governance.client import SidecarClient
from qortara_governance.context import AgentContext, set_context
from qortara_governance.context import _ctx_var
from qortara_governance.exceptions import QortaraApprovalRequired, QortaraPolicyDenied
from qortara_governance.patches import langgraph_patches
from qortara_governance.patches.tool_patches import enforce_decision
from qortara_protocol import ActionDecision, DecisionKind


def _decision(kind: DecisionKind) -> ActionDecision:
    return ActionDecision(
        decision_kind=kind,
        policy_version_sha256="x",
        rationale="r",
        policy_pack_id="p",
        approval_url="https://a/x" if kind == DecisionKind.REQUIRE_APPROVAL else None,
        ts=time.time(),
    )


# --- GAP-SEC-02: only ALLOW/EXEMPT/OBSERVE permit; everything else fails closed ---


@pytest.mark.parametrize(
    "kind", [DecisionKind.ALLOW, DecisionKind.EXEMPT, DecisionKind.OBSERVE]
)
def test_permit_kinds_do_not_raise(kind: DecisionKind) -> None:
    enforce_decision(_decision(kind))  # must not raise


@pytest.mark.parametrize(
    "kind",
    [
        DecisionKind.DENY,
        DecisionKind.DOWNGRADE,
        DecisionKind.REDACT,
        DecisionKind.SANDBOX,
    ],
)
def test_nonpermit_kinds_fail_closed(kind: DecisionKind) -> None:
    # DOWNGRADE/REDACT/SANDBOX previously fell through to ALLOW — now deny-closed.
    with pytest.raises(QortaraPolicyDenied):
        enforce_decision(_decision(kind))


def test_require_approval_raises_approval() -> None:
    with pytest.raises(QortaraApprovalRequired):
        enforce_decision(_decision(DecisionKind.REQUIRE_APPROVAL))


# --- GAP-SEC-03: malformed 2xx body denies closed and trips the breaker ---


def test_malformed_2xx_denies_closed() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200, json={"unexpected": "garbage"}
        )  # invalid ActionDecision

    c = SidecarClient("http://fake", None)
    c._client = httpx.Client(
        base_url="http://fake", transport=httpx.MockTransport(handler)
    )
    from qortara_protocol import (
        ActionRequest,
        ActionType,
        Framework,
    )

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
    decision = c.decide(req)
    assert decision.decision_kind == DecisionKind.DENY
    assert "malformed" in decision.rationale.lower()
    assert c._breaker.consecutive_failures == 1  # counted toward the breaker


# --- GAP-SEC-04: AGT engine exception denies closed ---


class _RaisingEngine:
    def add_constraint(self, role: str, tools: list) -> None:
        pass

    def check_violation(self, role: str, tool: str, args: dict) -> str | None:
        raise RuntimeError("boom")


def test_agt_engine_exception_fails_closed() -> None:
    client = AgtDecisionClient(AgtPolicyAdapter(engine=_RaisingEngine()))
    from qortara_governance.patches.action_builder import build_tool_action

    req = build_tool_action(
        "x", {}, AgentContext(tenant_id="t", agent_id="a", session_id="s")
    )
    decision = client.decide(req, {"q": "anything"})
    assert decision.decision_kind == DecisionKind.DENY
    assert "fail-closed" in decision.rationale.lower()


# --- GAP-SEC-06: ToolNode.ainvoke is patched + the async wrapper blocks deny ---


def test_toolnode_ainvoke_is_patched() -> None:
    pytest.importorskip("langgraph.prebuilt")
    from langgraph.prebuilt import ToolNode

    originals = langgraph_patches.apply(AgtDecisionClient(AgtPolicyAdapter()))
    try:
        assert getattr(ToolNode.ainvoke, "__qortara_wrapped__", False) is True
        assert getattr(ToolNode.invoke, "__qortara_wrapped__", False) is True
    finally:
        langgraph_patches.unpatch(originals)
        _ctx_var.set(None)


@pytest.mark.asyncio
async def test_async_toolnode_wrapper_blocks_deny() -> None:
    called = {"orig": False}

    async def _fake_original(self, input, config=None, **kwargs):  # noqa: ANN001
        called["orig"] = True
        return "ran"

    # Empty allow-list => role "a" denied for any tool (default-deny).
    client = AgtDecisionClient(AgtPolicyAdapter())
    wrapper = langgraph_patches._make_async_wrapper(_fake_original, client)
    set_context(AgentContext(tenant_id="t", agent_id="a", session_id="s"))
    state = {"messages": [{"tool_calls": [{"name": "danger", "args": {}, "id": "1"}]}]}
    try:
        with pytest.raises(QortaraPolicyDenied):
            await wrapper(object(), state)
        assert called["orig"] is False  # body never awaited
    finally:
        _ctx_var.set(None)
