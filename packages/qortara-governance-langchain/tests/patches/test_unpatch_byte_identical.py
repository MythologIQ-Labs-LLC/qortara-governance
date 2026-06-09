"""After unpatch_all(): BaseTool.run/arun is byte-identical to pre-patch.

The hook lives on run/arun (the dispatch funnel invoke/ainvoke pass through);
invoke/ainvoke are never replaced.
"""

from __future__ import annotations

from langchain_core.tools import BaseTool

from qortara_governance.patches.tool_patches import apply as tool_apply
from qortara_governance.patches.tool_patches import unpatch as tool_unpatch


def test_unpatch_restores_original_method_object(fake_client) -> None:  # noqa: ANN001
    original_run = BaseTool.run
    original_arun = BaseTool.arun
    original_invoke = BaseTool.invoke  # untouched throughout

    originals = tool_apply(fake_client)

    # While patched, run/arun differ from originals; invoke is left alone.
    assert BaseTool.run is not original_run
    assert getattr(BaseTool.run, "__qortara_wrapped__", False) is True
    assert getattr(BaseTool.arun, "__qortara_wrapped__", False) is True
    assert BaseTool.invoke is original_invoke
    assert not getattr(BaseTool.invoke, "__qortara_wrapped__", False)

    tool_unpatch(originals)

    # After unpatch, method objects must be byte-identical to originals.
    assert BaseTool.run is original_run
    assert BaseTool.arun is original_arun
    assert not getattr(BaseTool.run, "__qortara_wrapped__", False)
