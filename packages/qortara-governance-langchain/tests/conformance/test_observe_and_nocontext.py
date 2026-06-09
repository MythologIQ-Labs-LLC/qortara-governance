"""Behavioral conformance for OBSERVE mode + ungoverned-dispatch signalling.

Closes the deferred red-team HIGH items:
  GAP-CFG-01 — policy_mode=observe was dead config; now a real shadow/dry-run
               mode (evaluate + log would-be block, never raise).
  GAP-SEC-01 — a dispatch with no AgentContext was a silent fail-open; now it
               warns (QortaraUngovernedDispatchWarning), and escalating that
               category to an error makes ungoverned dispatch fail closed.
"""

from __future__ import annotations

import logging
import time
import warnings

import pytest
from langchain_core.tools import tool

import qortara_governance
from qortara_governance import context as _ctxmod
from qortara_governance.agt_engine import AgtDecisionClient, AgtPolicyAdapter
from qortara_governance.context import AgentContext, set_context
from qortara_governance.decorators import qortara_exempt
from qortara_governance.exceptions import (
    QortaraApprovalRequired,
    QortaraPolicyDenied,
    QortaraUngovernedDispatchWarning,
)
from qortara_governance.patches import apply_patches
from qortara_governance.patches.tool_patches import enforce_decision
from qortara_protocol import ActionDecision, DecisionKind

_LOG: list[str] = []


@tool
def denied_tool(query: str) -> str:
    """A tool whose role has no allow-list entry, so policy denies it."""
    _LOG.append(query)
    return f"ran:{query}"


@qortara_exempt
@tool
def exempt_tool(query: str) -> str:
    """Marked exempt — enforcement is skipped entirely."""
    _LOG.append(query)
    return f"ran:{query}"


@pytest.fixture(autouse=True)
def _isolate() -> None:
    _LOG.clear()
    yield
    qortara_governance.unpatch_all()
    _ctxmod._ctx_var.set(None)


def _deny_client() -> AgtDecisionClient:
    # Empty allow-list => default-deny for every (role, tool).
    return AgtDecisionClient(AgtPolicyAdapter())


def _ctx() -> AgentContext:
    return AgentContext(tenant_id="t", agent_id="agent-x", session_id="s")


# --- enforce_decision unit: observe downgrades every non-permit kind to a log ---


def _decision(kind: DecisionKind) -> ActionDecision:
    return ActionDecision(
        decision_kind=kind,
        policy_version_sha256="x",
        rationale="r",
        policy_pack_id="p",
        approval_url="https://a/x" if kind == DecisionKind.REQUIRE_APPROVAL else None,
        ts=time.time(),
    )


@pytest.mark.parametrize(
    "kind",
    [
        DecisionKind.DENY,
        DecisionKind.DOWNGRADE,
        DecisionKind.REDACT,
        DecisionKind.SANDBOX,
        DecisionKind.REQUIRE_APPROVAL,
    ],
)
def test_observe_downgrades_every_block_to_log(
    kind: DecisionKind, caplog: pytest.LogCaptureFixture
) -> None:
    with caplog.at_level(logging.WARNING, logger="qortara_governance"):
        enforce_decision(_decision(kind), observe=True)  # must NOT raise
    assert any("OBSERVE" in r.message for r in caplog.records)


def test_enforce_still_raises_when_not_observing() -> None:
    # Regression: ENFORCE (default) is byte-unchanged.
    with pytest.raises(QortaraPolicyDenied):
        enforce_decision(_decision(DecisionKind.DENY))
    with pytest.raises(QortaraApprovalRequired):
        enforce_decision(_decision(DecisionKind.REQUIRE_APPROVAL))


# --- dispatch-path: observe lets a denied tool run (and logs); enforce blocks ---


def test_observe_mode_dispatch_runs_denied_tool(
    caplog: pytest.LogCaptureFixture,
) -> None:
    apply_patches(_deny_client(), observe=True)
    set_context(_ctx())
    with caplog.at_level(logging.WARNING, logger="qortara_governance"):
        result = denied_tool.invoke({"query": "x"})  # no raise in observe mode
    assert result == "ran:x"
    assert _LOG == ["x"]  # body executed
    assert any("OBSERVE" in r.message for r in caplog.records)


def test_enforce_mode_dispatch_blocks_denied_tool() -> None:
    apply_patches(_deny_client())  # enforce (default)
    set_context(_ctx())
    with pytest.raises(QortaraPolicyDenied):
        denied_tool.invoke({"query": "x"})
    assert _LOG == []  # body never ran


# --- GAP-SEC-01: no AgentContext => warn (and, if escalated, fail closed) ---


def test_no_context_dispatch_warns_and_runs_ungoverned() -> None:
    apply_patches(_deny_client())
    # No set_context() — dispatch is ungoverned.
    with pytest.warns(QortaraUngovernedDispatchWarning):
        result = denied_tool.invoke({"query": "x"})
    assert result == "ran:x"  # ran ungoverned (warned, not blocked, by default)


def test_no_context_dispatch_fails_closed_when_warning_escalated() -> None:
    apply_patches(_deny_client())
    with warnings.catch_warnings():
        warnings.simplefilter("error", QortaraUngovernedDispatchWarning)
        with pytest.raises(QortaraUngovernedDispatchWarning):
            denied_tool.invoke({"query": "x"})
    assert _LOG == []  # body never ran — ungoverned dispatch failed closed


def test_exempt_tool_does_not_warn_without_context() -> None:
    apply_patches(_deny_client())
    with warnings.catch_warnings():
        warnings.simplefilter("error", QortaraUngovernedDispatchWarning)
        # Exempt tools skip enforcement entirely, so no ungoverned-dispatch warning.
        result = exempt_tool.invoke({"query": "x"})
    assert result == "ran:x"


# --- init_agt observe passthrough ---


def test_init_agt_observe_allows_denied_dispatch(
    caplog: pytest.LogCaptureFixture,
) -> None:
    # agent-x has no allowed tools => denied_tool would be denied under enforce.
    qortara_governance.init_agt("agent-x", [], policy_mode="observe")
    set_context(_ctx())
    with caplog.at_level(logging.WARNING, logger="qortara_governance"):
        result = denied_tool.invoke({"query": "x"})
    assert result == "ran:x"
    assert any("OBSERVE" in r.message for r in caplog.records)
