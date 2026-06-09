"""LangGraph ToolNode.invoke / .ainvoke patches — optional (silent skip if absent)."""

from __future__ import annotations

import asyncio
from types import MappingProxyType
from typing import Any, Callable

from qortara_governance.client import SidecarClient
from qortara_governance.context import get_context
from qortara_governance.contract.state import CONTRACT_VERSION, AdapterState
from qortara_governance.patches.action_builder import build_toolnode_action
from qortara_governance.patches.tool_patches import (
    enforce_decision,
    warn_missing_context,
)

_OriginalMethod = Callable[..., Any]


def _langgraph_available() -> bool:
    try:
        import langgraph.prebuilt  # noqa: F401

        return True
    except ImportError:
        return False


def _extract_tool_calls(state: Any) -> list[tuple[str, dict]]:
    """Best-effort extraction of (tool name, args) pairs from a ToolNode state.

    LangGraph passes state with a `messages` list whose last AI message may carry
    `tool_calls`, each with a `name` and `args` dict. Returning the args (not just
    the name) lets AGT run argument-level checks on the ToolNode path, matching
    the BaseTool path. Falls back to [("<unknown>", {})] if structure doesn't match.
    """
    try:
        messages = (
            state.get("messages", [])
            if isinstance(state, dict)
            else getattr(state, "messages", [])
        )
        if not messages:
            return [("<unknown>", {})]
        last = messages[-1]
        tool_calls = getattr(last, "tool_calls", None) or (
            last.get("tool_calls") if isinstance(last, dict) else None
        )
        if not tool_calls:
            return [("<unknown>", {})]
        calls: list[tuple[str, dict]] = []
        for tc in tool_calls:
            if isinstance(tc, dict):
                name = tc.get("name", "<unknown>")
                args = tc.get("args", {})
            else:
                name = getattr(tc, "name", "<unknown>")
                args = getattr(tc, "args", {})
            calls.append((name, args if isinstance(args, dict) else {}))
        return calls
    except (AttributeError, TypeError, KeyError):
        return [("<unknown>", {})]


def _decide_each(
    tool_calls: list[tuple[str, dict]], client: SidecarClient, observe: bool = False
) -> None:
    ctx = get_context()
    if ctx is None:
        # Ungoverned dispatch (GAP-SEC-01): signal rather than silently skip.
        # Shared helper with the BaseTool path so the two can't diverge.
        first_name = tool_calls[0][0] if tool_calls else "<toolnode>"
        warn_missing_context(first_name)
        return
    for name, args in tool_calls:
        # Thread args as tool_input so the in-process AGT decision source runs
        # argument-level checks (SQL/code/path); SidecarClient ignores it.
        # enforce_decision fails closed on any non-permit verdict (shared with
        # the BaseTool path so the two can't diverge); observe -> log not raise.
        enforce_decision(
            client.decide(build_toolnode_action(name, ctx), args), observe=observe
        )


def _make_wrapper(
    original: _OriginalMethod, client: SidecarClient, observe: bool = False
) -> _OriginalMethod:
    def wrapper(self: object, input: Any, config: Any = None, **kwargs: Any) -> Any:
        _decide_each(_extract_tool_calls(input), client, observe)
        return original(self, input, config, **kwargs)

    wrapper.__qualname__ = original.__qualname__
    wrapper.__qortara_wrapped__ = True  # type: ignore[attr-defined]
    # No __qortara_original__ handle exposed (GAP-SEC-07); originals live in the
    # dict returned by apply() for unpatch().
    return wrapper


def _make_async_wrapper(
    original: _OriginalMethod, client: SidecarClient, observe: bool = False
) -> _OriginalMethod:
    async def wrapper(
        self: object, input: Any, config: Any = None, **kwargs: Any
    ) -> Any:
        calls = _extract_tool_calls(input)
        if getattr(client, "blocking_io", True):
            # Sidecar (blocking httpx) — run decisions off the event loop;
            # asyncio.to_thread propagates contextvars for get_context().
            await asyncio.to_thread(_decide_each, calls, client, observe)
        else:
            _decide_each(calls, client, observe)
        return await original(self, input, config, **kwargs)

    wrapper.__qualname__ = original.__qualname__
    wrapper.__qortara_wrapped__ = True  # type: ignore[attr-defined]
    # No __qortara_original__ handle exposed (GAP-SEC-07); originals live in the
    # dict returned by apply() for unpatch().
    return wrapper


def apply(
    client: SidecarClient, observe: bool = False
) -> dict[str, _OriginalMethod] | None:
    """Install ToolNode.invoke + .ainvoke patches if langgraph present; else skip."""
    if not _langgraph_available():
        return None
    from langgraph.prebuilt import ToolNode

    for method in ("invoke", "ainvoke"):
        if getattr(getattr(ToolNode, method), "__qortara_wrapped__", False):
            raise RuntimeError(
                f"ToolNode.{method} is already wrapped by Qortara - refusing to "
                "double-install. Call langgraph_patches.unpatch(originals) first."
            )
    originals: dict[str, _OriginalMethod] = {
        "invoke": ToolNode.invoke,
        "ainvoke": ToolNode.ainvoke,
    }
    ToolNode.invoke = _make_wrapper(ToolNode.invoke, client, observe)  # type: ignore[method-assign]
    ToolNode.ainvoke = _make_async_wrapper(ToolNode.ainvoke, client, observe)  # type: ignore[method-assign]
    return originals


def unpatch(originals: dict[str, _OriginalMethod] | None) -> None:
    """Restore ToolNode.invoke/.ainvoke. No-op if originals is None (langgraph absent)."""
    if originals is None:
        return
    from langgraph.prebuilt import ToolNode

    ToolNode.invoke = originals["invoke"]  # type: ignore[method-assign]
    if "ainvoke" in originals:
        ToolNode.ainvoke = originals["ainvoke"]  # type: ignore[method-assign]


class LangGraphToolNodeAdapter:
    """FrameworkAdapter wrapping langgraph.prebuilt.ToolNode.invoke patches."""

    name: str = "langgraph-toolnode"
    framework_module: str = "langgraph.prebuilt"
    contract_version: str = CONTRACT_VERSION

    def __init__(self, observe: bool = False) -> None:
        self._observe = observe

    def apply(self, client: SidecarClient) -> AdapterState:
        """Install the ToolNode patch and return an AdapterState.

        Raises ImportError when langgraph is not installed; the registry is
        expected to probe `framework_module` importability and skip the
        adapter before calling apply.
        """
        originals = apply(client, self._observe)
        if originals is None:
            raise ImportError(
                "langgraph is not installed; LangGraphToolNodeAdapter.apply() "
                "requires the optional [langgraph] extra"
            )
        return AdapterState(
            adapter_name=self.name,
            originals=MappingProxyType(dict(originals)),
        )

    def unpatch(self, state: AdapterState) -> None:
        """Restore ToolNode.invoke from the snapshot in `state`."""
        unpatch(dict(state.originals))
