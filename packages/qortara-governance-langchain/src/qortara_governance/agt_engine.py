"""AGT-backed in-process enforcement (ADR-0001 Increment B).

qortara's dispatch patch calls `client.decide(ActionRequest) -> ActionDecision`.
`AgtDecisionClient` satisfies that contract using Microsoft AGT's in-process
`agent_control_plane.PolicyEngine` as the decision engine — no sidecar/HTTP for
local enforcement. It is a drop-in for `SidecarClient`, so the existing patch
(and its DENY -> QortaraPolicyDenied path) is used unchanged.

Mapping: AGT `check_violation(role, tool, args)` returns None on allow, or a
string describing the violation on deny. `build_tool_action` does not inline
args (privacy), so argument-level AGT checks are out of scope here (role + tool
allow-listing only); arg threading is a follow-up.
"""

from __future__ import annotations

import time
from typing import Any

from agent_control_plane.policy_engine import PolicyEngine
from qortara_protocol import ActionDecision, ActionRequest, DecisionKind

from qortara_governance.agt import agt_version


class AgtPolicyAdapter:
    """Thin wrapper over AGT's in-process PolicyEngine (default-deny allow-list)."""

    def __init__(self, engine: PolicyEngine | None = None) -> None:
        self._engine = engine or PolicyEngine()

    def allow(self, role: str, tools: list[str]) -> "AgtPolicyAdapter":
        """Grant `role` permission to use `tools` (AGT allow-list)."""
        self._engine.add_constraint(role, tools)
        return self

    def check(self, role: str, tool_name: str, args: dict[str, Any]) -> str | None:
        """Return None if allowed, else AGT's violation string."""
        return self._engine.check_violation(role, tool_name, args)


class AgtDecisionClient:
    """Decision source backed by AGT's PolicyEngine; drop-in for SidecarClient."""

    def __init__(self, adapter: AgtPolicyAdapter) -> None:
        self._adapter = adapter
        self._policy_id = f"agt-core:{agt_version() or 'unknown'}"

    def decide(
        self, request: ActionRequest, tool_input: object = None
    ) -> ActionDecision:
        """Map an AGT policy verdict onto an ActionDecision (fail-closed).

        `tool_input` is consumed in-process (no wire) so AGT's argument-level
        checks (SQL/code/path/endpoint) run on the real arguments when the input
        is a dict; otherwise no args are supplied.
        """
        args: dict[str, Any] = tool_input if isinstance(tool_input, dict) else {}
        violation = self._adapter.check(request.agent_id, request.target_resource, args)
        if violation is None:
            return self._decision(DecisionKind.ALLOW, "allowed by AGT policy")
        return self._decision(DecisionKind.DENY, violation)

    def _decision(self, kind: DecisionKind, rationale: str) -> ActionDecision:
        return ActionDecision(
            decision_kind=kind,
            policy_version_sha256=self._policy_id,
            rationale=rationale,
            policy_pack_id="agt",
            ts=time.time(),
        )

    # --- SidecarClient-compatible no-ops (in-process: nothing to reach/submit) ---
    def require_reachable(self) -> None:  # noqa: D102
        return None

    def submit_evidence(self, records: list[Any]) -> None:  # noqa: D102
        return None

    def health(self) -> bool:  # noqa: D102
        return True

    def close(self) -> None:  # noqa: D102
        return None
