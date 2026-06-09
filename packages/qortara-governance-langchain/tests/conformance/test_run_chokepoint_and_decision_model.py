"""Conformance: run/arun is the governed chokepoint + honest AGT decision model.

Closes deferred red-team HIGH items:
  GAP-SEC-08 — a direct `tool.run(...)`/`tool.arun(...)` bypassed an invoke-only
               hook. The patch now lives on the run/arun funnel, so invoke,
               ainvoke, run AND arun are all governed (one decision each).
  GAP-CAP-01 — the in-process AGT engine is binary (allow/deny); `require_approval`
               is produced only by the sidecar/hosted decision plane. The SDK still
               routes a require_approval decision to QortaraApprovalRequired when one
               arrives (proven here), but the AGT path never emits it.
"""

from __future__ import annotations

import asyncio
from typing import Any

import pytest
from langchain_core.tools import BaseTool
from pydantic import PrivateAttr

from qortara_governance.agt_engine import AgtDecisionClient, AgtPolicyAdapter
from qortara_governance.context import AgentContext
from qortara_governance.exceptions import QortaraApprovalRequired, QortaraPolicyDenied
from qortara_governance.patches import apply_patches
from qortara_governance.patches.action_builder import build_tool_action
from qortara_protocol import DecisionKind


def _scripted(fake_client: Any, *kinds: DecisionKind) -> Any:
    """Script a FakeClient (conftest fixture) with the given decisions."""
    fake_client.scripted_decisions = list(kinds)
    return fake_client


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


# --- GAP-SEC-08: the direct run/arun bypass is closed ---


def test_direct_run_is_governed(fake_client: Any, ctx: AgentContext) -> None:
    apply_patches(_scripted(fake_client, DecisionKind.DENY))
    tool = RecordingTool()
    with pytest.raises(QortaraPolicyDenied):
        tool.run("delete_prod")  # direct .run() — the old bypass
    assert tool._ran is False  # body never reached


def test_direct_arun_is_governed(fake_client: Any, ctx: AgentContext) -> None:
    apply_patches(_scripted(fake_client, DecisionKind.DENY))
    tool = RecordingTool()

    async def _call() -> None:
        with pytest.raises(QortaraPolicyDenied):
            await tool.arun("delete_prod")

    asyncio.run(_call())
    assert tool._ran is False


def test_invoke_still_governed_via_run(fake_client: Any, ctx: AgentContext) -> None:
    # Regression: invoke() funnels through the patched run and is still blocked.
    apply_patches(_scripted(fake_client, DecisionKind.DENY))
    tool = RecordingTool()
    with pytest.raises(QortaraPolicyDenied):
        tool.invoke("delete_prod")
    assert tool._ran is False


def test_run_arun_are_the_wrapped_methods(fake_client: Any) -> None:
    apply_patches(fake_client)
    assert getattr(BaseTool.run, "__qortara_wrapped__", False) is True
    assert getattr(BaseTool.arun, "__qortara_wrapped__", False) is True
    # invoke/ainvoke are NOT replaced — they reach policy via run/arun.
    assert getattr(BaseTool.invoke, "__qortara_wrapped__", False) is False
    assert getattr(BaseTool.ainvoke, "__qortara_wrapped__", False) is False


# --- GAP-CAP-01: AGT path is binary; require_approval is a sidecar/hosted kind ---


def test_agt_path_is_binary_allow_deny() -> None:
    c = AgentContext(tenant_id="t", agent_id="agent-x", session_id="s")
    allowed = AgtDecisionClient(AgtPolicyAdapter().allow("agent-x", ["t"]))
    denied = AgtDecisionClient(AgtPolicyAdapter())  # empty allow-list
    allow = allowed.decide(build_tool_action("t", {}, c), {})
    deny = denied.decide(build_tool_action("t", {}, c), {})
    assert allow.decision_kind == DecisionKind.ALLOW
    assert deny.decision_kind == DecisionKind.DENY
    # The AGT engine never emits the richer kinds (CAP-01 boundary).
    for d in (allow, deny):
        assert d.decision_kind != DecisionKind.REQUIRE_APPROVAL
        assert d.decision_kind not in (
            DecisionKind.DOWNGRADE,
            DecisionKind.REDACT,
            DecisionKind.SANDBOX,
        )


def test_sidecar_require_approval_routes_to_approval(
    fake_client: Any, ctx: AgentContext
) -> None:
    # When a decision plane DOES emit require_approval, the SDK routes it to
    # QortaraApprovalRequired through the (now run-level) dispatch — so the
    # four-state model is real where the plane supports it.
    apply_patches(_scripted(fake_client, DecisionKind.REQUIRE_APPROVAL))
    tool = RecordingTool()
    with pytest.raises(QortaraApprovalRequired):
        tool.run("wire_funds")
    assert tool._ran is False
