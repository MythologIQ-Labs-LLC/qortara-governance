"""PROTOCOL_VERSION drives client endpoints; protocol mismatch fails closed.

Beta contract (B2): the SDK speaks one wire-protocol version and refuses an
incompatible peer; the public exception set is frozen.
"""

from __future__ import annotations

import time

import httpx
import pytest

from qortara_governance import (
    PROTOCOL_VERSION,
    QortaraError,
    QortaraProtocolMismatch,
    require_compatible_protocol,
)
from qortara_governance.client import SidecarClient
from qortara_protocol import ActionRequest, ActionType, Framework


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


def test_client_request_path_uses_protocol_version() -> None:
    seen: dict[str, str] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["path"] = request.url.path
        return httpx.Response(
            200,
            json={
                "decision_kind": "allow",
                "policy_version_sha256": "x",
                "rationale": "ok",
                "policy_pack_id": "p",
                "ts": time.time(),
            },
        )

    client = SidecarClient("http://fake", None)
    client._client = httpx.Client(
        base_url="http://fake", transport=httpx.MockTransport(handler)
    )
    client.decide(_req())
    assert seen["path"] == f"/{PROTOCOL_VERSION}/decisions"


def test_require_compatible_protocol_accepts_same_major() -> None:
    require_compatible_protocol(PROTOCOL_VERSION)  # must not raise


def test_require_compatible_protocol_rejects_different_major() -> None:
    with pytest.raises(QortaraProtocolMismatch) as exc_info:
        require_compatible_protocol("v9.0")
    assert exc_info.value.expected == PROTOCOL_VERSION
    assert exc_info.value.received == "v9.0"


def test_protocol_mismatch_is_qortara_error() -> None:
    assert issubclass(QortaraProtocolMismatch, QortaraError)
