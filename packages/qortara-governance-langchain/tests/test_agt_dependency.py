"""The AGT foundation (agent-governance-toolkit) is installed and resolvable.

qortara extends AGT (ADR-0001); this guards that the dependency is actually
present so the extension seam in Increment B has a foundation to build on.
"""

from __future__ import annotations

from importlib.metadata import version

from qortara_governance.agt import agt_available, agt_version


def test_agt_is_available() -> None:
    assert agt_available() is True


def test_agt_version_resolves() -> None:
    v = agt_version()
    assert v
    assert v == version("agent-governance-toolkit-core")
