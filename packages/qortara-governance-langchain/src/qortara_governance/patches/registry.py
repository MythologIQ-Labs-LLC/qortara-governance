"""Patch lifecycle registry — versioned FrameworkAdapter dispatch.

Holds an ordered dict of (adapter, AdapterState) entries. `apply` checks each
adapter's contract_version, attempts to import its target framework (skipping
with a `RuntimeWarning` on failure), and stores the returned state.
`unpatch_all` unwinds stored entries in LIFO order.

The module exposes a process-singleton `_REGISTRY` so the public entry point
`qortara_governance.init()` can remain a thin wrapper.
"""

from __future__ import annotations

import importlib.util
import threading
import warnings
from typing import Sequence

from qortara_governance.contract.protocol import FrameworkAdapter
from qortara_governance.decision_client import DecisionClient
from qortara_governance.contract.state import (
    CONTRACT_VERSION,
    AdapterState,
    IncompatibleAdapterVersion,
)


def _default_adapters(observe: bool = False) -> list[FrameworkAdapter]:
    """Return the default adapter list shipped with this SDK.

    `observe` (policy_mode=observe) is baked into each adapter so its dispatch
    wrappers log would-be blocks instead of raising (shadow/dry-run mode).
    """
    from qortara_governance.patches.langgraph_patches import LangGraphToolNodeAdapter
    from qortara_governance.patches.tool_patches import LangChainToolAdapter

    return [LangChainToolAdapter(observe), LangGraphToolNodeAdapter(observe)]


class AdapterRegistry:
    """Ordered registry of applied FrameworkAdapters and their AdapterStates."""

    def __init__(self) -> None:
        self._entries: dict[str, tuple[FrameworkAdapter, AdapterState]] = {}
        self._client: DecisionClient | None = None

    def apply(
        self,
        client: DecisionClient,
        adapters: Sequence[FrameworkAdapter],
    ) -> None:
        """Apply each adapter in order; skip those whose framework is unavailable."""
        for adapter in adapters:
            self._apply_one(client, adapter)
        self._client = client

    def _apply_one(self, client: DecisionClient, adapter: FrameworkAdapter) -> None:
        if adapter.contract_version != CONTRACT_VERSION:
            raise IncompatibleAdapterVersion(
                f"adapter {adapter.name!r} contract_version="
                f"{adapter.contract_version!r} does not match "
                f"CONTRACT_VERSION={CONTRACT_VERSION!r}"
            )
        try:
            spec = importlib.util.find_spec(adapter.framework_module)
        except (ImportError, ValueError):
            spec = None
        if spec is None:
            warnings.warn(
                f"skipping adapter {adapter.name!r}: framework module "
                f"{adapter.framework_module!r} is not importable",
                RuntimeWarning,
                stacklevel=3,
            )
            return
        try:
            state = adapter.apply(client)
        except ImportError as e:
            # Symmetric with the find_spec skip: if the adapter's internal
            # imports fail during apply (broken submodule, missing transitive
            # dep), treat it the same as the parent not being importable.
            warnings.warn(
                f"skipping adapter {adapter.name!r}: apply() raised ImportError: {e}",
                RuntimeWarning,
                stacklevel=3,
            )
            return
        self._entries[adapter.name] = (adapter, state)

    def unpatch_all(self) -> None:
        """Unwind stored adapters in LIFO order and close the client."""
        for adapter, state in reversed(list(self._entries.values())):
            adapter.unpatch(state)
        self._entries.clear()
        if self._client is not None:
            self._client.close()
        self._client = None

    def is_installed(self) -> bool:
        """Return True iff any adapters are currently applied."""
        return bool(self._entries)

    @property
    def client(self) -> DecisionClient | None:
        """Return the client passed to the most recent `apply`, if any."""
        return self._client


_REGISTRY = AdapterRegistry()
# Serialize patch install/uninstall — monkeypatching BaseTool/ToolNode is a
# process-global mutation; a lock makes the check-then-apply atomic against
# concurrent init() calls (GAP-H-1).
_PATCH_LOCK = threading.Lock()


def apply_patches(client: DecisionClient, *, observe: bool = False) -> None:
    """Install the default adapter set. Idempotent per identical client.

    `observe=True` (policy_mode=observe) installs shadow-mode wrappers that log
    would-be policy blocks instead of raising. Default is enforce.
    """
    with _PATCH_LOCK:
        if _REGISTRY.is_installed():
            if _REGISTRY.client is client:
                return
            raise RuntimeError(
                "Qortara patches already installed with a different client. "
                "Call qortara_governance.unpatch_all() first."
            )
        _REGISTRY.apply(client, _default_adapters(observe))


def unpatch_all() -> None:
    """Restore byte-identical originals. Required for test teardown."""
    with _PATCH_LOCK:
        _REGISTRY.unpatch_all()


def is_patched() -> bool:
    """Return True iff patches are currently applied."""
    return _REGISTRY.is_installed()


def get_client() -> DecisionClient | None:
    """Return the currently-installed client, or None."""
    return _REGISTRY.client
