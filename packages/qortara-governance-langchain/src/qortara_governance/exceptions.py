"""Public exceptions (and warning categories) raised by Qortara Governance SDK.

`__all__` is the frozen Beta contract: consumers may catch/filter any of these
names and rely on the inheritance shape. Every *error* name derives from
QortaraError; every *warning* category (suffix ``Warning``) derives from the
builtin ``UserWarning`` so it composes with the stdlib ``warnings`` machinery
(it is NOT a QortaraError, because a warning is not a raised error by default).
Additions are minor-version compatible; removals/renames are breaking.
"""

from __future__ import annotations

__all__ = [
    "QortaraError",
    "QortaraPolicyDenied",
    "QortaraApprovalRequired",
    "QortaraSidecarUnavailable",
    "QortaraProtocolMismatch",
    "QortaraUngovernedDispatchWarning",
]


class QortaraError(Exception):
    """Base for all SDK-raised errors."""


class QortaraPolicyDenied(QortaraError):
    """Sidecar returned decision_kind=deny for the attempted action."""

    def __init__(
        self, rationale: str, policy_pack_id: str, policy_version_sha256: str
    ) -> None:
        self.rationale = rationale
        self.policy_pack_id = policy_pack_id
        self.policy_version_sha256 = policy_version_sha256
        super().__init__(f"[{policy_pack_id}] {rationale}")


class QortaraApprovalRequired(QortaraError):
    """Sidecar returned decision_kind=require_approval; caller must obtain approval."""

    def __init__(
        self, rationale: str, approval_url: str | None, policy_pack_id: str
    ) -> None:
        self.rationale = rationale
        self.approval_url = approval_url
        self.policy_pack_id = policy_pack_id
        super().__init__(f"[{policy_pack_id}] approval required: {rationale}")


class QortaraSidecarUnavailable(QortaraError):
    """Sidecar unreachable and circuit breaker has tripped."""


class QortaraProtocolMismatch(QortaraError):
    """SDK and sidecar speak incompatible wire-protocol major versions."""

    def __init__(self, expected: str, received: str) -> None:
        self.expected = expected
        self.received = received
        super().__init__(
            f"incompatible protocol version: expected {expected}, received {received}"
        )


class QortaraUngovernedDispatchWarning(UserWarning):
    """A patched tool dispatched with no AgentContext set, so policy did not run.

    After ``init()``/``init_agt()`` the tool-dispatch methods are patched
    process-wide, but a dispatch off any code path that never set an
    ``AgentContext`` is enforced against nothing — it runs UNGOVERNED. The SDK
    emits this warning rather than failing closed by default, because patched
    methods are global and non-agent call paths legitimately run uncontextualized.

    To make ungoverned dispatch fail closed, escalate this category to an error::

        import warnings
        from qortara_governance import QortaraUngovernedDispatchWarning
        warnings.filterwarnings("error", category=QortaraUngovernedDispatchWarning)
    """
