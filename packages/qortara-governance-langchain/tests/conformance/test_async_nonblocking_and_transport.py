"""Conformance: async decisions don't block the event loop + cleartext-credential warning.

Closes deferred red-team MED items:
  - blocking httpx in the async dispatch wrapper (decision now runs off the loop
    for blocking_io clients; inline for in-process clients);
  - tenant_key sent over plaintext http to a non-loopback host now warns.
"""

from __future__ import annotations

import asyncio
import threading
import time

import pytest
from langchain_core.tools import BaseTool
from pydantic import PrivateAttr

from qortara_governance.client import SidecarClient
from qortara_governance.context import AgentContext
from qortara_governance.exceptions import (
    QortaraInsecureTransportWarning,
    QortaraPolicyDenied,
)
from qortara_governance.patches import apply_patches
from qortara_protocol import ActionDecision, ActionRequest, DecisionKind


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


class _RecordingClient:
    """Minimal decision client (duck-typed for the patch wrappers) that records
    the thread its decide() ran on."""

    def __init__(self, kind: DecisionKind, *, blocking_io: bool) -> None:
        self.blocking_io = blocking_io
        self._kind = kind
        self.decide_thread: int | None = None

    def decide(
        self, request: ActionRequest, tool_input: object = None
    ) -> ActionDecision:
        self.decide_thread = threading.get_ident()
        return ActionDecision(
            decision_kind=self._kind,
            policy_version_sha256="x",
            rationale="r",
            policy_pack_id="p",
            ts=time.time(),
        )

    def close(self) -> None:
        pass


# --- async non-blocking decision placement ---


def test_async_blocking_client_decides_off_loop_thread(ctx: AgentContext) -> None:
    client = _RecordingClient(DecisionKind.ALLOW, blocking_io=True)
    apply_patches(client)  # type: ignore[arg-type]
    tool = RecordingTool()
    loop_thread: dict[str, int] = {}

    async def _run() -> str:
        loop_thread["id"] = threading.get_ident()
        return await tool.arun("x")

    result = asyncio.run(_run())
    assert result == "aran:x"
    # decide ran on a worker thread, not the event-loop thread (non-blocking).
    assert client.decide_thread is not None
    assert client.decide_thread != loop_thread["id"]


def test_async_inprocess_client_decides_on_loop_thread(ctx: AgentContext) -> None:
    client = _RecordingClient(DecisionKind.ALLOW, blocking_io=False)
    apply_patches(client)  # type: ignore[arg-type]
    tool = RecordingTool()
    loop_thread: dict[str, int] = {}

    async def _run() -> str:
        loop_thread["id"] = threading.get_ident()
        return await tool.arun("x")

    asyncio.run(_run())
    # In-process client: decide runs inline on the loop thread (no gratuitous hop).
    assert client.decide_thread == loop_thread["id"]


def test_async_deny_still_blocks_via_thread(ctx: AgentContext) -> None:
    client = _RecordingClient(DecisionKind.DENY, blocking_io=True)
    apply_patches(client)  # type: ignore[arg-type]
    tool = RecordingTool()

    async def _run() -> None:
        with pytest.raises(QortaraPolicyDenied):
            await tool.arun("x")

    asyncio.run(_run())
    assert tool._ran is False  # body never ran despite the threaded decision


# --- cleartext-credential warning (tenant_key over non-TLS, non-loopback) ---


def test_tenant_key_http_nonloopback_warns() -> None:
    with pytest.warns(QortaraInsecureTransportWarning):
        with SidecarClient("http://api.example.com:8080", "secret-key"):
            pass


@pytest.mark.parametrize(
    "endpoint,key",
    [
        ("https://api.example.com", "secret-key"),  # TLS
        ("http://127.0.0.1:9000", "secret-key"),  # loopback
        ("http://localhost:9000", "secret-key"),  # loopback
        ("http://api.example.com", None),  # no credential
    ],
)
def test_no_insecure_transport_warning(
    endpoint: str, key: str | None, recwarn: pytest.WarningsRecorder
) -> None:
    with SidecarClient(endpoint, key):
        pass
    assert not any(
        isinstance(w.message, QortaraInsecureTransportWarning) for w in recwarn
    )
