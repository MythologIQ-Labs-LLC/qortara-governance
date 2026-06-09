"""Runtime __version__ must equal the installed package metadata version.

Guards against the drift fixed in D1 (runtime lagged packaging at 0.2.0 vs 0.2.1).
Invokes both lookups and asserts equality, so any future divergence fails CI.
"""

from __future__ import annotations

from importlib.metadata import version

import qortara_governance


def test_runtime_version_matches_package_metadata() -> None:
    metadata_version = version("qortara-governance-langchain")
    assert qortara_governance.__version__ == metadata_version
