"""BaseTool.invoke / .ainvoke patches — deep-hook tool-dispatch interception.

Closes AGT issue #73: callback-level wrappers observe tool calls but don't
reliably block native tool-calling dispatch. This module patches the actual
invoke methods on BaseTool so every dispatch path flows through policy.

Exports:
    apply()              -> originals  (module-level; install patches)
    unpatch(originals)                  (module-level; restore)
    LangChainToolAdapter                (FrameworkAdapter class wrapping the above)
"""

from __future__ import annotations

from types import MappingProxyType
from typing import Any, Callable

from qortara_governance.client import SidecarClient
from qortara_governance.context import get_context
from qortara_governance.contract.state import CONTRACT_VERSION, AdapterState
from qortara_governance.decorators import is_exempt
from qortara_governance.exceptions import QortaraApprovalRequired, QortaraPolicyDenied
from qortara_governance.patches.action_builder import build_tool_action
from qortara_protocol import ActionDecision, DecisionKind

_OriginalMethod = Callable[..., Any]

# Kinds that permit execution. Everything else is treated as blocking so the
# default is fail-closed: a decision the SDK does not explicitly understand
# (DOWNGRADE/REDACT/SANDBOX/unknown — transform semantics are not implemented)
# must NOT let the tool run. Shared by BaseTool + LangGraph patches so the two
# dispatch paths can never diverge.
_PERMIT_KINDS = (DecisionKind.ALLOW, DecisionKind.EXEMPT, DecisionKind.OBSERVE)


def enforce_decision(decision: ActionDecision) -> None:
    """Raise on any non-permit decision (fail-closed). Permit = ALLOW/EXEMPT/OBSERVE."""
    kind = decision.decision_kind
    if kind in _PERMIT_KINDS:
        return
    if kind == DecisionKind.REQUIRE_APPROVAL:
        raise QortaraApprovalRequired(
            rationale=decision.rationale,
            approval_url=decision.approval_url,
            policy_pack_id=decision.policy_pack_id,
        )
    rationale = (
        decision.rationale
        if kind == DecisionKind.DENY
        else f"unsupported decision_kind '{kind.value}' — fail-closed"
    )
    raise QortaraPolicyDenied(
        rationale=rationale,
        policy_pack_id=decision.policy_pack_id,
        policy_version_sha256=decision.policy_version_sha256,
    )


def _decide_or_raise(tool: object, tool_input: Any, client: SidecarClient) -> None:
    """Request a decision; permit only ALLOW/EXEMPT/OBSERVE, else fail closed."""
    if is_exempt(tool):
        return
    ctx = get_context()
    if ctx is None:
        return
    tool_name = getattr(tool, "name", type(tool).__name__)
    request = build_tool_action(tool_name, tool_input, ctx)
    enforce_decision(client.decide(request, tool_input))


def _make_sync_wrapper(
    original: _OriginalMethod, client: SidecarClient
) -> _OriginalMethod:
    def wrapper(self: object, input: Any, config: Any = None, **kwargs: Any) -> Any:
        _decide_or_raise(self, input, client)
        return original(self, input, config, **kwargs)

    wrapper.__qualname__ = original.__qualname__
    wrapper.__qortara_wrapped__ = True  # type: ignore[attr-defined]
    wrapper.__qortara_original__ = original  # type: ignore[attr-defined]
    return wrapper


def _make_async_wrapper(
    original: _OriginalMethod, client: SidecarClient
) -> _OriginalMethod:
    async def wrapper(
        self: object, input: Any, config: Any = None, **kwargs: Any
    ) -> Any:
        _decide_or_raise(self, input, client)
        return await original(self, input, config, **kwargs)

    wrapper.__qualname__ = original.__qualname__
    wrapper.__qortara_wrapped__ = True  # type: ignore[attr-defined]
    wrapper.__qortara_original__ = original  # type: ignore[attr-defined]
    return wrapper


def apply(client: SidecarClient) -> dict[str, _OriginalMethod]:
    """Install BaseTool.invoke/ainvoke patches. Returns originals for unpatch."""
    from langchain_core.tools import BaseTool

    if getattr(BaseTool.invoke, "__qortara_wrapped__", False):
        raise RuntimeError(
            "BaseTool.invoke is already wrapped by Qortara - refusing to "
            "double-install. Call tool_patches.unpatch(originals) before "
            "re-installing."
        )
    if getattr(BaseTool.ainvoke, "__qortara_wrapped__", False):
        raise RuntimeError(
            "BaseTool.ainvoke is already wrapped by Qortara - refusing to "
            "double-install. Call tool_patches.unpatch(originals) before "
            "re-installing."
        )
    originals: dict[str, _OriginalMethod] = {
        "invoke": BaseTool.invoke,
        "ainvoke": BaseTool.ainvoke,
    }
    BaseTool.invoke = _make_sync_wrapper(BaseTool.invoke, client)  # type: ignore[method-assign]
    BaseTool.ainvoke = _make_async_wrapper(BaseTool.ainvoke, client)  # type: ignore[method-assign]
    return originals


def unpatch(originals: dict[str, _OriginalMethod]) -> None:
    """Restore BaseTool.invoke/ainvoke to byte-identical originals."""
    from langchain_core.tools import BaseTool

    BaseTool.invoke = originals["invoke"]  # type: ignore[method-assign]
    BaseTool.ainvoke = originals["ainvoke"]  # type: ignore[method-assign]


class LangChainToolAdapter:
    """FrameworkAdapter wrapping BaseTool.invoke / BaseTool.ainvoke patches."""

    name: str = "langchain-basetool"
    framework_module: str = "langchain_core.tools"
    contract_version: str = CONTRACT_VERSION

    def apply(self, client: SidecarClient) -> AdapterState:
        """Install patches and return an AdapterState snapshot of the originals."""
        originals = apply(client)
        return AdapterState(
            adapter_name=self.name,
            originals=MappingProxyType(dict(originals)),
        )

    def unpatch(self, state: AdapterState) -> None:
        """Restore BaseTool methods from the snapshot in `state`."""
        unpatch(dict(state.originals))
