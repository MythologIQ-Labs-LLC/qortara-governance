"""Conformance: the modern agent runtime (create_react_agent) is governed end-to-end
(B1-followup).

langchain >=1.0 removed AgentExecutor; the modern entry point is
`langgraph.prebuilt.create_react_agent`, which builds a graph whose tools execute
via `ToolNode` (+ `BaseTool.run`). This drives a real agent graph with a
deterministic fake tool-calling model and asserts a *denied* tool is blocked
before its body runs — proving governance holds through the agent runtime, not
just at a hand-built ToolNode. No new dependency (uses the [langgraph] extra).
"""

from __future__ import annotations

from typing import Any

import pytest

from qortara_governance.context import AgentContext, set_context
from qortara_governance.exceptions import QortaraPolicyDenied
from qortara_governance.patches import apply_patches
from qortara_protocol import DecisionKind

_LOG: list[str] = []


def _has_policy_denied(exc: BaseException) -> bool:
    """True if QortaraPolicyDenied appears anywhere in the exception/cause chain."""
    seen = exc
    while seen is not None:
        if isinstance(seen, QortaraPolicyDenied):
            return True
        seen = seen.__cause__ or seen.__context__
    return False


@pytest.mark.filterwarnings("ignore:create_react_agent has been moved")
def test_create_react_agent_denied_tool_is_blocked(fake_client: Any) -> None:
    # `langgraph.prebuilt.create_react_agent` is the predecessor of langchain V1's
    # `langchain.agents.create_agent`; both build a langgraph graph that dispatches
    # tools through `ToolNode` + `BaseTool.run`, so both are governed by the same
    # patches. We exercise the prebuilt (no `langchain` test-dep) as the proxy.
    pytest.importorskip("langgraph.prebuilt")
    from langchain_core.language_models.chat_models import BaseChatModel
    from langchain_core.messages import AIMessage, HumanMessage
    from langchain_core.outputs import ChatGeneration, ChatResult
    from langchain_core.tools import tool
    from langgraph.prebuilt import create_react_agent

    _LOG.clear()

    @tool
    def blocked_tool(x: str) -> str:
        """A tool the agent will try to call — policy must block it."""
        _LOG.append(x)
        return f"ran:{x}"

    class _FakeToolCaller(BaseChatModel):
        """Minimal deterministic model: always emits one call to blocked_tool."""

        @property
        def _llm_type(self) -> str:
            return "fake-tool-caller"

        def bind_tools(self, tools: Any, **kwargs: Any) -> Any:  # noqa: ANN401
            return self

        def _generate(self, messages: Any, stop: Any = None, **kwargs: Any) -> Any:
            ai = AIMessage(
                content="",
                tool_calls=[{"name": "blocked_tool", "args": {"x": "1"}, "id": "c1"}],
            )
            return ChatResult(generations=[ChatGeneration(message=ai)])

    fake_client.scripted_decisions = [DecisionKind.DENY]
    apply_patches(fake_client)
    set_context(AgentContext(tenant_id="t", agent_id="agent-x", session_id="s"))

    agent = create_react_agent(_FakeToolCaller(), [blocked_tool])
    with pytest.raises(Exception) as excinfo:
        agent.invoke({"messages": [HumanMessage(content="please call the tool")]})

    # The core invariant: governance blocked the dispatch — the tool body never ran.
    assert _LOG == []
    # And it was our policy denial (somewhere in the chain), not an unrelated error.
    assert _has_policy_denied(excinfo.value)
