"""qortara-governance-langchain — LangChain + LangGraph governance SDK.

Public API:
    init(tenant_key=..., ...) -> None
    unpatch_all() -> None  # test teardown only
    QortaraCallbackHandler (for manual registration on Chain/Agent)
    qortara_exempt (decorator marking tools to skip enforcement)
    QortaraPolicyDenied / QortaraApprovalRequired / QortaraSidecarUnavailable
"""

from __future__ import annotations

from dataclasses import dataclass

from qortara_governance import contract
from qortara_governance.agt_engine import AgtDecisionClient, AgtPolicyAdapter
from qortara_governance.callback import QortaraCallbackHandler
from qortara_governance.client import SidecarClient
from qortara_governance.config import Config, PolicyMode, load_config
from qortara_governance.context import AgentContext, get_context, set_context
from qortara_governance.decorators import is_exempt, qortara_exempt
from qortara_governance.exceptions import (
    QortaraApprovalRequired,
    QortaraError,
    QortaraInsecureTransportWarning,
    QortaraPolicyDenied,
    QortaraProtocolMismatch,
    QortaraSidecarUnavailable,
    QortaraUngovernedDispatchWarning,
)
from qortara_governance.launcher import launch
from qortara_governance.patches import apply_patches, unpatch_all
from qortara_governance.protocol_version import (
    PROTOCOL_VERSION,
    require_compatible_protocol,
)

__version__ = "0.2.1"

__all__ = [
    "PROTOCOL_VERSION",
    "AgentContext",
    "AgtDecisionClient",
    "AgtPolicyAdapter",
    "Config",
    "PolicyMode",
    "QortaraApprovalRequired",
    "QortaraCallbackHandler",
    "QortaraError",
    "QortaraInsecureTransportWarning",
    "QortaraPolicyDenied",
    "QortaraProtocolMismatch",
    "QortaraSidecarUnavailable",
    "QortaraUngovernedDispatchWarning",
    "contract",
    "get_context",
    "init",
    "init_agt",
    "is_exempt",
    "qortara_exempt",
    "require_compatible_protocol",
    "set_context",
    "unpatch_all",
]


@dataclass(frozen=True)
class _InitFingerprint:
    endpoint: str | None
    tenant_key: str | None
    policy_mode: PolicyMode


_FINGERPRINT: _InitFingerprint | None = None


def _fingerprint_of(config: Config) -> _InitFingerprint:
    return _InitFingerprint(
        endpoint=config.sidecar_endpoint,
        tenant_key=config.tenant_key,
        policy_mode=config.policy_mode,
    )


def _is_observe(mode: PolicyMode) -> bool:
    return mode is PolicyMode.OBSERVE


def init(
    *,
    tenant_key: str | None = None,
    sidecar_endpoint: str | None = None,
    policy_mode: str | PolicyMode | None = None,
) -> None:
    """Initialize Qortara Governance for this process.

    Calling twice with the same args is a no-op. Calling twice with different
    args raises RuntimeError — call unpatch_all() first if reconfiguring.

    `policy_mode` defaults to `enforce` (deny decisions raise). `observe` is a
    shadow/dry-run mode: policy is still evaluated and every would-be block is
    logged at WARNING via the `qortara_governance` logger, but nothing is raised.

    On first call:
    - Resolves config (env > kwarg > default)
    - Launches sidecar subprocess (if no QORTARA_SIDECAR_ENDPOINT)
    - Verifies sidecar reachability
    - Installs BaseTool.invoke / ToolNode.invoke patches
    """
    global _FINGERPRINT

    config = load_config(
        sidecar_endpoint=sidecar_endpoint,
        tenant_key=tenant_key,
        policy_mode=policy_mode,
    )
    new_fp = _fingerprint_of(config)

    if _FINGERPRINT is not None:
        if _FINGERPRINT == new_fp:
            return
        raise RuntimeError(
            "qortara_governance.init() already called with different arguments. "
            "Call qortara_governance.unpatch_all() before re-initializing."
        )

    launch_result = launch(existing_endpoint=config.sidecar_endpoint)
    client = SidecarClient(launch_result.endpoint, config.tenant_key)
    client.require_reachable()
    apply_patches(client, observe=_is_observe(config.policy_mode))
    _FINGERPRINT = new_fp


def init_agt(
    agent_id: str,
    allowed_tools: list[str],
    *,
    capability_aliases: dict[str, str] | None = None,
    policy_mode: str | PolicyMode = PolicyMode.ENFORCE,
) -> AgtPolicyAdapter:
    """Initialize in-process enforcement backed by Microsoft AGT (ADR-0001).

    Installs the dispatch patch with an AGT-backed decision source — no sidecar
    needed locally (this is also the supported air-gapped / offline path). `agent_id`
    is the AGT policy role; `allowed_tools` is its allow-list (default-deny for
    everything else). `capability_aliases` maps your tool names onto AGT-recognized
    capability names (e.g. {"sql_db_query": "database_query"}) so AGT's
    argument-level checks reach them. `policy_mode=observe` runs shadow/dry-run
    (log would-be blocks, never raise). Returns the adapter so the caller can grant
    further roles. Set an AgentContext(agent_id=...) so the patch enforces on this
    agent's dispatches.
    """
    mode = (
        policy_mode if isinstance(policy_mode, PolicyMode) else PolicyMode(policy_mode)
    )
    adapter = AgtPolicyAdapter(capability_aliases=capability_aliases).allow(
        agent_id, allowed_tools
    )
    # AgtDecisionClient is a structural drop-in for SidecarClient (same .decide
    # contract); apply_patches is nominally typed to SidecarClient.
    apply_patches(AgtDecisionClient(adapter), observe=_is_observe(mode))  # type: ignore[arg-type]
    return adapter


# Keep direct exports for test teardown reach-through.
_unpatch_all_original = unpatch_all


def _unpatch_and_reset() -> None:
    global _FINGERPRINT
    _unpatch_all_original()
    _FINGERPRINT = None


# Override the exported name so tests / users get fingerprint reset too.
unpatch_all = _unpatch_and_reset  # type: ignore[assignment]
