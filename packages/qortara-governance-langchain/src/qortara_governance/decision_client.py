"""DecisionClient — the structural contract the dispatch patches depend on.

Both the remote `SidecarClient` (HTTP) and the in-process `AgtDecisionClient`
(Microsoft AGT) satisfy this Protocol structurally. The patch layer, registry,
and framework adapters are typed against `DecisionClient` rather than a concrete
class, so the two implementations can't drift apart silently and `init_agt` no
longer needs a `# type: ignore` to pass its AGT client through (GAP-C-2 from the
e2e review).
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from qortara_protocol import ActionDecision, ActionRequest, EvidenceRecord


@runtime_checkable
class DecisionClient(Protocol):
    """A policy-decision source usable by the LangChain/LangGraph dispatch patches."""

    # True if decide() performs blocking IO (network); async wrappers run it off
    # the event loop. In-process clients set this False.
    blocking_io: bool

    def decide(
        self, request: ActionRequest, tool_input: object = None
    ) -> ActionDecision:
        """Return a policy decision for an action request (fail-closed on error)."""
        ...

    def require_reachable(self) -> None:
        """Raise if the decision source is not reachable (no-op for in-process)."""
        ...

    def submit_evidence(self, records: list[EvidenceRecord]) -> None:
        """Best-effort evidence submission (never raises into the caller)."""
        ...

    def health(self) -> bool:
        """Return True if the decision source is healthy."""
        ...

    def close(self) -> None:
        """Release any resources held by the client."""
        ...
