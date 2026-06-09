"""SDK↔sidecar wire protocol version — single source of truth.

`PROTOCOL_VERSION` is the version segment of every sidecar endpoint the SDK
calls (`/v0.1/decisions`, `/v0.1/evidence`, `/v0.1/health`). It is also the
version the SDK advertises during compatibility negotiation. Promote any wire
version change here; `client.py` builds its paths from this constant.
"""

from __future__ import annotations

from qortara_governance.exceptions import QortaraProtocolMismatch

PROTOCOL_VERSION = "v0.1"


def _major(version: str) -> str:
    """Return the major component of a `vMAJOR.MINOR` (or `MAJOR.MINOR`) string."""
    return version.lstrip("vV").split(".", 1)[0]


def require_compatible_protocol(peer_version: str) -> None:
    """Raise QortaraProtocolMismatch when the peer's major version differs from ours.

    Same-major versions are considered wire-compatible; a differing major is a
    breaking change and fails closed before any decision is trusted. A missing or
    empty peer version is itself a mismatch (fail-closed), not an opaque crash
    (GAP-M-3).
    """
    if not peer_version:
        raise QortaraProtocolMismatch(
            expected=PROTOCOL_VERSION, received=repr(peer_version)
        )
    if _major(peer_version) != _major(PROTOCOL_VERSION):
        raise QortaraProtocolMismatch(expected=PROTOCOL_VERSION, received=peer_version)
