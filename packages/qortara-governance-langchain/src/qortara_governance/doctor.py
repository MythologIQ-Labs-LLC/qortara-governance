"""qortara-governance doctor - operator diagnostics for governance state (W3).

Answers the question an operator actually needs before trusting a deployment:
**"is governance actually active, and in what mode?"** - patch state, the active
decision client, enforce vs observe, whether an evidence sink + an AgentContext
are configured, and the silent traps (no context, observe mode, no sink,
plaintext-credential transport).

Read-only: doctor diagnoses, it never changes configuration.

Run as::

    python - m qortara_governance.doctor [--json]

Exit code: 0 when governance is active (patched), 1 when it is not - suitable for
a startup healthcheck.
"""

from __future__ import annotations

import json
import sys
from dataclasses import asdict, dataclass

from qortara_governance.context import get_context
from qortara_governance.patches import (
    get_client,
    get_evidence_sink,
    get_observe,
    is_patched,
)

_TENANT_KEY_HEADER = "Ocp-Apim-Subscription-Key"


@dataclass(frozen=True)
class GovernanceStatus:
    """A snapshot of the process's governance configuration (no secrets)."""

    patched: bool
    wrapped_methods: list[str]
    client_kind: str
    policy_mode: str  # "enforce" | "observe" | "n/a"
    evidence_sink: str | None  # sink class name, or None
    context_set: bool
    endpoint: str | None  # SidecarClient endpoint URL (never a credential)
    tenant_key_configured: bool  # presence only - never the value
    warnings: list[str]


def _wrapped_methods() -> list[str]:
    """Which dispatch methods are currently Qortara-wrapped (best-effort)."""
    found: list[str] = []
    try:
        from langchain_core.tools import BaseTool

        for m in ("run", "arun"):
            if getattr(getattr(BaseTool, m, None), "__qortara_wrapped__", False):
                found.append(f"BaseTool.{m}")
    except Exception:  # noqa: BLE001 - diagnostics must never raise
        pass
    try:
        from langgraph.prebuilt import ToolNode

        for m in ("invoke", "ainvoke"):
            if getattr(getattr(ToolNode, m, None), "__qortara_wrapped__", False):
                found.append(f"ToolNode.{m}")
    except Exception:  # noqa: BLE001
        pass
    return found


def collect_status() -> GovernanceStatus:
    """Gather the current governance status. Never raises; never returns secrets."""
    patched = is_patched()
    client = get_client()
    client_kind = type(client).__name__ if client is not None else "none"
    observe = get_observe()
    policy_mode = ("observe" if observe else "enforce") if patched else "n/a"
    sink = get_evidence_sink()
    evidence_sink = type(sink).__name__ if sink is not None else None
    context_set = get_context() is not None

    endpoint = getattr(client, "_endpoint", None) if client is not None else None
    headers = getattr(client, "_headers", None) if client is not None else None
    tenant_key_configured = isinstance(headers, dict) and _TENANT_KEY_HEADER in headers

    warnings: list[str] = []
    if not patched:
        warnings.append("Governance is NOT active - call init() or init_agt() first.")
    else:
        if not context_set:
            warnings.append(
                "No AgentContext set in this process - dispatches here would be "
                "UNGOVERNED (a QortaraUngovernedDispatchWarning is emitted). Call "
                "set_context(...)."
            )
        if observe:
            warnings.append(
                "policy_mode=observe - policy is evaluated but NOT enforced; "
                "would-be blocks are logged, not raised."
            )
        if evidence_sink is None:
            warnings.append(
                "No evidence_sink configured - no audit trail is emitted from the "
                "dispatch path. Pass evidence_sink= to init()/init_agt() to enable."
            )
        if endpoint and str(endpoint).startswith("http://") and tenant_key_configured:
            warnings.append(
                "tenant_key configured over plaintext http - the credential may be "
                "sent in cleartext. Use https."
            )

    return GovernanceStatus(
        patched=patched,
        wrapped_methods=_wrapped_methods(),
        client_kind=client_kind,
        policy_mode=policy_mode,
        evidence_sink=evidence_sink,
        context_set=context_set,
        endpoint=endpoint,
        tenant_key_configured=tenant_key_configured,
        warnings=warnings,
    )


def format_report(status: GovernanceStatus) -> str:
    """Render a human-readable report."""
    lines = ["qortara-governance doctor", "=" * 26]
    lines.append(f"Governance:       {'ACTIVE' if status.patched else 'INACTIVE'}")
    lines.append(f"Decision client:  {status.client_kind}")
    lines.append(f"Policy mode:      {status.policy_mode}")
    lines.append(f"Wrapped methods:  {', '.join(status.wrapped_methods) or '(none)'}")
    lines.append(f"Evidence sink:    {status.evidence_sink or '(none)'}")
    lines.append(f"AgentContext set: {status.context_set}")
    if status.endpoint:
        lines.append(f"Sidecar endpoint: {status.endpoint}")
        lines.append(f"tenant_key set:   {status.tenant_key_configured}")
    lines.append("")
    if status.warnings:
        lines.append("Warnings:")
        lines.extend(f"  ! {w}" for w in status.warnings)
    else:
        lines.append("No warnings - governance is active and enforcing.")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    """CLI entry point. Returns 0 if governance is active, else 1."""
    args = sys.argv[1:] if argv is None else argv
    status = collect_status()
    if "--json" in args:
        print(json.dumps(asdict(status), indent=2))
    else:
        print(format_report(status))
    return 0 if status.patched else 1


if __name__ == "__main__":
    sys.exit(main())
