"""Conformance: LangGraph ToolNode dispatch routes tool args into AGT (P1 fix).

Closes the PR #13 review finding — the ToolNode path discarded tool args, so AGT
skipped argument-level checks there. Parity with the BaseTool arg-safety path.
"""

from __future__ import annotations

import pytest

from qortara_governance.agt_engine import AgtDecisionClient, AgtPolicyAdapter
from qortara_governance.context import AgentContext, set_context
from qortara_governance.context import _ctx_var
from qortara_governance.exceptions import QortaraPolicyDenied
from qortara_governance.patches.langgraph_patches import (
    _decide_each,
    _extract_tool_calls,
)


def _state(name: str, args: dict) -> dict:
    return {"messages": [{"tool_calls": [{"name": name, "args": args, "id": "1"}]}]}


def _client() -> AgtDecisionClient:
    return AgtDecisionClient(AgtPolicyAdapter().allow("agent-x", ["database_query"]))


@pytest.fixture(autouse=True)
def _ctx() -> None:
    set_context(AgentContext(tenant_id="t", agent_id="agent-x", session_id="s"))
    yield
    _ctx_var.set(None)


def test_extract_tool_calls_returns_args() -> None:
    calls = _extract_tool_calls(_state("database_query", {"query": "SELECT 1"}))
    assert calls == [("database_query", {"query": "SELECT 1"})]


def test_toolnode_denies_destructive_sql() -> None:
    calls = _extract_tool_calls(_state("database_query", {"query": "DROP TABLE users"}))
    with pytest.raises(QortaraPolicyDenied):
        _decide_each(calls, _client())


def test_toolnode_allows_safe_arg() -> None:
    calls = _extract_tool_calls(_state("database_query", {"query": "SELECT 1"}))
    _decide_each(calls, _client())  # must not raise


def test_toolnode_denies_unlisted_tool() -> None:
    calls = _extract_tool_calls(_state("delete_db", {"query": "x"}))
    with pytest.raises(QortaraPolicyDenied):
        _decide_each(calls, _client())
