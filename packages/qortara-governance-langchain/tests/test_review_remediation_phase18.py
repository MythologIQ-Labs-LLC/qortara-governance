"""Phase 18 — e2e-review remediation: init guard, DecisionClient Protocol,
4xx rationale, protocol-version guard.
"""

from __future__ import annotations

import time

import httpx
import pytest

import qortara_governance
from qortara_governance.agt_engine import AgtDecisionClient, AgtPolicyAdapter
from qortara_governance.client import SidecarClient
from qortara_governance.decision_client import DecisionClient
from qortara_governance.exceptions import QortaraProtocolMismatch
from qortara_governance.protocol_version import require_compatible_protocol
from qortara_protocol import ActionRequest, ActionType, DecisionKind, Framework


@pytest.fixture(autouse=True)
def _reset() -> None:
    yield
    # The exported unpatch_all is the override that also resets the init
    # fingerprint + active AGT adapter (the registry one does not).
    qortara_governance.unpatch_all()


def _req() -> ActionRequest:
    return ActionRequest(
        tenant_id="t",
        agent_id="a",
        session_id="s",
        framework=Framework.LANGCHAIN,
        action_type=ActionType.TOOL_DISPATCH,
        target_resource="fake",
        requested_capability="fake",
        ts=time.time(),
    )


# --- C-1: unified init guard (init_agt idempotent; mismatches raise cleanly) ---


def test_init_agt_idempotent_same_args_returns_same_adapter() -> None:
    a1 = qortara_governance.init_agt("agent-x", ["tool_a"])
    a2 = qortara_governance.init_agt("agent-x", ["tool_a"])
    assert a1 is a2  # no-op re-call, same live adapter


def test_init_agt_different_args_raises() -> None:
    qortara_governance.init_agt("agent-x", ["tool_a"])
    with pytest.raises(RuntimeError):
        qortara_governance.init_agt("agent-x", ["tool_b"])


def test_init_after_init_agt_raises() -> None:
    qortara_governance.init_agt("agent-x", ["tool_a"])
    with pytest.raises(RuntimeError):
        qortara_governance.init(tenant_key="k", sidecar_endpoint="http://127.0.0.1:9")


def test_unpatch_all_allows_reinit_after_init_agt() -> None:
    qortara_governance.init_agt("agent-x", ["tool_a"])
    qortara_governance.unpatch_all()
    # Fresh init_agt with different args now succeeds (fingerprint cleared).
    adapter = qortara_governance.init_agt("agent-y", ["tool_b"])
    assert adapter is not None


# --- C-2: both decision clients satisfy the DecisionClient Protocol ---


def test_decision_clients_satisfy_protocol() -> None:
    ac = AgtDecisionClient(AgtPolicyAdapter())
    assert isinstance(ac, DecisionClient)
    with SidecarClient("http://127.0.0.1:9", None) as sc:
        assert isinstance(sc, DecisionClient)


# --- H-3: 4xx gives a distinct (non-"unreachable") deny rationale ---


def test_client_4xx_has_distinct_rationale() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(403, json={"error": "forbidden"})

    c = SidecarClient("http://fake", None)
    c._client = httpx.Client(
        base_url="http://fake", transport=httpx.MockTransport(handler)
    )
    decision = c.decide(_req())
    assert decision.decision_kind == DecisionKind.DENY
    assert "403" in decision.rationale
    assert "unreachable" not in decision.rationale.lower()


# --- M-3: protocol-version guard rejects None/empty cleanly ---


@pytest.mark.parametrize("bad", [None, ""])
def test_require_compatible_protocol_rejects_missing(bad: object) -> None:
    with pytest.raises(QortaraProtocolMismatch):
        require_compatible_protocol(bad)  # type: ignore[arg-type]
