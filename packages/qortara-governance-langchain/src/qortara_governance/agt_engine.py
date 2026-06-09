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
    """Thin wrapper over AGT's in-process PolicyEngine (default-deny allow-list).

    AGT's argument-level checks (SQL/code/path/endpoint) only fire for tool names
    AGT recognizes (e.g. `run_command`, `database_query`, `write_file`). For other
    tool names, enforcement is role + tool allow-listing only. `capability_aliases`
    maps your tool names onto AGT-recognized capability names so arg-checks reach
    them too (e.g. `{"sql_db_query": "database_query"}`).
    """

    def __init__(
        self,
        engine: PolicyEngine | None = None,
        capability_aliases: dict[str, str] | None = None,
    ) -> None:
        self._engine = engine or PolicyEngine()
        self._aliases = dict(capability_aliases or {})

    def allow(self, role: str, tools: list[str]) -> "AgtPolicyAdapter":
        """Grant `role` permission to use `tools` (AGT allow-list).

        Aliased capability names are also allow-listed so the alias arg-check pass
        in `check()` passes the role gate and reaches AGT's argument inspection.
        """
        constraint = list(tools)
        constraint += [self._aliases[t] for t in tools if t in self._aliases]
        self._engine.add_constraint(role, constraint)
        return self

    def check(self, role: str, tool_name: str, args: dict[str, Any]) -> str | None:
        """Return None if allowed, else AGT's violation string.

        Runs the allow-list + (incidental) arg-check under the real tool name,
        then — if the tool is aliased — a second arg-check pass under the
        AGT-recognized capability name so argument inspection actually fires.
        """
        violation = self._engine.check_violation(role, tool_name, args)
        if violation is not None:
            return violation
        alias = self._aliases.get(tool_name)
        if alias is not None:
            return self._engine.check_violation(role, alias, args)
        return None


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
        try:
            violation = self._adapter.check(
                request.agent_id, request.target_resource, args
            )
        except Exception as exc:
            # Fail closed: any error evaluating policy denies, never allows.
            return self._decision(
                DecisionKind.DENY,
                f"AGT policy evaluation error (fail-closed): {type(exc).__name__}",
            )
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
