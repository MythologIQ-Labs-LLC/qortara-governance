"""Microsoft Agent Governance Toolkit (AGT) foundation probe.

qortara-governance extends AGT (ADR-0001): it depends on the full toolkit and
adds a bypass-proof dispatch hook on top. This module is the minimal seam that
confirms the foundation is present. Increment B wires the dispatch patch into
AGT's decision engine; until then this only reports availability/version.
"""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version

# We depend on the AGT *library* components (not the meta/CLI package); the core
# policy engine is the anchor distribution we probe for foundation presence.
_AGT_DIST = "agent-governance-toolkit-core"


def agt_version() -> str | None:
    """Return the installed AGT core distribution version, or None if absent."""
    try:
        return version(_AGT_DIST)
    except PackageNotFoundError:
        return None


def agt_available() -> bool:
    """True when the AGT foundation is installed in the current environment."""
    return agt_version() is not None
