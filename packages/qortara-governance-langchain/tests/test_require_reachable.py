"""require_reachable distinguishes auth / timeout / unreachable (B2-followup)."""

from __future__ import annotations

from typing import Callable

import httpx
import pytest

from qortara_governance.client import SidecarClient
from qortara_governance.exceptions import (
    QortaraAuthenticationError,
    QortaraSidecarUnavailable,
    QortaraTimeout,
)


def _client(handler: Callable[[httpx.Request], httpx.Response]) -> SidecarClient:
    c = SidecarClient("http://fake", None)
    c._client = httpx.Client(
        base_url="http://fake", transport=httpx.MockTransport(handler)
    )
    return c


@pytest.mark.parametrize("status", [401, 403])
def test_auth_failure_raises_auth_error(status: int) -> None:
    c = _client(lambda r: httpx.Response(status))
    with pytest.raises(QortaraAuthenticationError):
        c.require_reachable()


def test_timeout_raises_timeout() -> None:
    def handler(r: httpx.Request) -> httpx.Response:
        raise httpx.TimeoutException("timed out")

    with pytest.raises(QortaraTimeout):
        _client(handler).require_reachable()


def test_timeout_is_sidecar_unavailable_subclass() -> None:
    # Back-compat: existing `except QortaraSidecarUnavailable` still catches a timeout.
    assert issubclass(QortaraTimeout, QortaraSidecarUnavailable)


def test_connection_error_is_unavailable_not_timeout() -> None:
    def handler(r: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("connection refused")

    with pytest.raises(QortaraSidecarUnavailable) as exc:
        _client(handler).require_reachable()
    assert not isinstance(exc.value, QortaraTimeout)  # distinct from a timeout


def test_5xx_raises_unavailable() -> None:
    with pytest.raises(QortaraSidecarUnavailable):
        _client(lambda r: httpx.Response(503)).require_reachable()


def test_healthy_2xx_does_not_raise() -> None:
    _client(lambda r: httpx.Response(200)).require_reachable()
