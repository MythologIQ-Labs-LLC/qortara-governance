"""BaseTool.run / .arun patches — deep-hook tool-dispatch interception.

Closes AGT issue #73: callback-level wrappers observe tool calls but don't
reliably block native tool-calling dispatch. This module patches the actual
dispatch funnel on BaseTool so every dispatch path flows through policy.

`BaseTool.invoke()` calls `self.run(...)` and `ainvoke()` calls `self.arun(...)`
(verified against langchain_core 1.4.2), so `run`/`arun` are the single funnel
every public entry point passes through. Hooking there (rather than at
invoke/ainvoke) also governs a *direct* `tool.run(...)` / `tool.arun(...)` call —
the GAP-SEC-08 bypass that an invoke-only hook left open — with one decision per
dispatch (no double-enforcement). `BaseTool` has no `__call__`. The per-subclass
private impls `_run`/`_arun` cannot be patched at the BaseTool class level;
calling them directly to skip dispatch is the cooperative-process boundary
(THREAT-MODEL §5) — you already have in-process code execution.

Exports:
    apply()              -> originals  (module-level; install patches)
    unpatch(originals)                  (module-level; restore)
    LangChainToolAdapter                (FrameworkAdapter class wrapping the above)
"""

from __future__ import annotations

import asyncio
import logging
import warnings
from types import MappingProxyType
from typing import Any, Callable

from qortara_governance.client import SidecarClient
from qortara_governance.context import get_context
from qortara_governance.contract.state import CONTRACT_VERSION, AdapterState
from qortara_governance.decorators import is_exempt
from qortara_governance.exceptions import (
    QortaraApprovalRequired,
    QortaraPolicyDenied,
    QortaraUngovernedDispatchWarning,
)
from qortara_governance.patches.action_builder import build_tool_action
from qortara_protocol import ActionDecision, DecisionKind

_OriginalMethod = Callable[..., Any]

_log = logging.getLogger("qortara_governance")

# Kinds that permit execution. Everything else is treated as blocking so the
# default is fail-closed: a decision the SDK does not explicitly understand
# (DOWNGRADE/REDACT/SANDBOX/unknown — transform semantics are not implemented)
# must NOT let the tool run. Shared by BaseTool + LangGraph patches so the two
# dispatch paths can never diverge.
_PERMIT_KINDS = (DecisionKind.ALLOW, DecisionKind.EXEMPT, DecisionKind.OBSERVE)


def warn_missing_context(tool_name: str) -> None:
    """Signal that a patched tool dispatched with no AgentContext (UNGOVERNED).

    Closes the silent fail-open (GAP-SEC-01): the dispatch path is patched but
    enforced against nothing when no context is set. Emits a
    QortaraUngovernedDispatchWarning rather than failing closed by default
    (patched methods are global; non-agent call paths legitimately run
    uncontextualized). Operators wanting fail-closed escalate the category to an
    error via warnings.filterwarnings — which then raises on every such dispatch.
    The stdlib warnings filter handles dedup ("once" per call-site by default),
    so no bespoke warn-once state is kept here.
    """
    warnings.warn(
        f"qortara: tool {tool_name!r} dispatched with no AgentContext set — this "
        "dispatch is UNGOVERNED (policy did not run). Call set_context(...) on this "
        "code path, or escalate QortaraUngovernedDispatchWarning to an error to fail "
        "closed.",
        QortaraUngovernedDispatchWarning,
        stacklevel=3,
    )


def enforce_decision(decision: ActionDecision, *, observe: bool = False) -> None:
    """Raise on any non-permit decision (fail-closed). Permit = ALLOW/EXEMPT/OBSERVE.

    When ``observe`` is True (policy_mode=observe — shadow/dry-run), a non-permit
    decision is LOGGED at WARNING and execution proceeds; nothing is raised. This
    is the documented OBSERVE contract: evaluate policy and surface what enforcement
    *would* do, without blocking. ENFORCE (observe=False) is the default.
    """
    kind = decision.decision_kind
    if kind in _PERMIT_KINDS:
        return
    if observe:
        _log.warning(
            "qortara OBSERVE: would have blocked dispatch (decision_kind=%s): %s "
            "— allowing because policy_mode=observe",
            kind.value,
            decision.rationale,
        )
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


def _decide_or_raise(
    tool: object, tool_input: Any, client: SidecarClient, observe: bool = False
) -> None:
    """Request a decision; permit only ALLOW/EXEMPT/OBSERVE, else fail closed."""
    if is_exempt(tool):
        return
    tool_name = getattr(tool, "name", type(tool).__name__)
    ctx = get_context()
    if ctx is None:
        warn_missing_context(tool_name)
        return
    request = build_tool_action(tool_name, tool_input, ctx)
    enforce_decision(client.decide(request, tool_input), observe=observe)


def _tool_input_of(args: tuple[Any, ...], kwargs: dict[str, Any]) -> Any:
    """Extract `tool_input` from a run/arun call (1st positional or keyword)."""
    return args[0] if args else kwargs.get("tool_input")


def _make_sync_wrapper(
    original: _OriginalMethod, client: SidecarClient, observe: bool = False
) -> _OriginalMethod:
    def wrapper(self: object, *args: Any, **kwargs: Any) -> Any:
        _decide_or_raise(self, _tool_input_of(args, kwargs), client, observe)
        return original(self, *args, **kwargs)

    wrapper.__qualname__ = original.__qualname__
    wrapper.__qortara_wrapped__ = True  # type: ignore[attr-defined]
    # No __qortara_original__ handle is exposed on the wrapper (GAP-SEC-07): the
    # original is held only in the returned `originals` dict for unpatch().
    return wrapper


def _make_async_wrapper(
    original: _OriginalMethod, client: SidecarClient, observe: bool = False
) -> _OriginalMethod:
    async def wrapper(self: object, *args: Any, **kwargs: Any) -> Any:
        tool_input = _tool_input_of(args, kwargs)
        if getattr(client, "blocking_io", True):
            # Sidecar (blocking httpx) — run off the event loop so the decision
            # doesn't stall the loop. asyncio.to_thread propagates contextvars,
            # so get_context() still resolves in the worker thread.
            await asyncio.to_thread(_decide_or_raise, self, tool_input, client, observe)
        else:
            _decide_or_raise(self, tool_input, client, observe)
        return await original(self, *args, **kwargs)

    wrapper.__qualname__ = original.__qualname__
    wrapper.__qortara_wrapped__ = True  # type: ignore[attr-defined]
    # No __qortara_original__ handle is exposed on the wrapper (GAP-SEC-07): the
    # original is held only in the returned `originals` dict for unpatch().
    return wrapper


def apply(client: SidecarClient, observe: bool = False) -> dict[str, _OriginalMethod]:
    """Install BaseTool.run/arun patches (the dispatch funnel). Returns originals.

    invoke()/ainvoke() reach policy *through* run/arun, and a direct run/arun call
    is governed too (GAP-SEC-08). One decision per dispatch — no double-enforcement.
    """
    from langchain_core.tools import BaseTool

    if getattr(BaseTool.run, "__qortara_wrapped__", False):
        raise RuntimeError(
            "BaseTool.run is already wrapped by Qortara - refusing to "
            "double-install. Call tool_patches.unpatch(originals) before "
            "re-installing."
        )
    if getattr(BaseTool.arun, "__qortara_wrapped__", False):
        raise RuntimeError(
            "BaseTool.arun is already wrapped by Qortara - refusing to "
            "double-install. Call tool_patches.unpatch(originals) before "
            "re-installing."
        )
    originals: dict[str, _OriginalMethod] = {
        "run": BaseTool.run,
        "arun": BaseTool.arun,
    }
    BaseTool.run = _make_sync_wrapper(BaseTool.run, client, observe)  # type: ignore[method-assign]
    BaseTool.arun = _make_async_wrapper(BaseTool.arun, client, observe)  # type: ignore[method-assign]
    return originals


def unpatch(originals: dict[str, _OriginalMethod]) -> None:
    """Restore BaseTool.run/arun to byte-identical originals."""
    from langchain_core.tools import BaseTool

    BaseTool.run = originals["run"]  # type: ignore[method-assign]
    BaseTool.arun = originals["arun"]  # type: ignore[method-assign]


class LangChainToolAdapter:
    """FrameworkAdapter wrapping BaseTool.invoke / BaseTool.ainvoke patches."""

    name: str = "langchain-basetool"
    framework_module: str = "langchain_core.tools"
    contract_version: str = CONTRACT_VERSION

    def __init__(self, observe: bool = False) -> None:
        self._observe = observe

    def apply(self, client: SidecarClient) -> AdapterState:
        """Install patches and return an AdapterState snapshot of the originals."""
        originals = apply(client, self._observe)
        return AdapterState(
            adapter_name=self.name,
            originals=MappingProxyType(dict(originals)),
        )

    def unpatch(self, state: AdapterState) -> None:
        """Restore BaseTool methods from the snapshot in `state`."""
        unpatch(dict(state.originals))
