"""@qortara_exempt: tool marked exempt skips sidecar roundtrip."""

from __future__ import annotations

from langchain_core.tools import BaseTool

from qortara_governance.decorators import is_exempt, qortara_exempt
from qortara_governance.patches.tool_patches import apply as tool_apply
from qortara_governance.patches.tool_patches import unpatch as tool_unpatch
from qortara_protocol import DecisionKind


class NormalTool(BaseTool):
    name: str = "normal"
    description: str = "normal"

    def _run(self, q: str) -> str:  # type: ignore[override]
        return q


@qortara_exempt
class ExemptTool(BaseTool):
    name: str = "exempt"
    description: str = "exempt from policy"

    def _run(self, q: str) -> str:  # type: ignore[override]
        return f"exempt: {q}"


def test_is_exempt_sentinel_detects_class_mark() -> None:
    assert is_exempt(ExemptTool())
    assert is_exempt(ExemptTool)
    assert not is_exempt(NormalTool())


def test_raw_truthy_attr_does_not_exempt() -> None:
    # GAP-SEC-07 defense-in-depth: a stray/injected truthy attribute must NOT
    # exempt — only the decorator (which sets the identity sentinel) does.
    tool = NormalTool()
    tool.__qortara_exempt__ = True  # type: ignore[attr-defined]
    assert is_exempt(tool) is False
    tool.__qortara_exempt__ = "yes"  # type: ignore[attr-defined]
    assert is_exempt(tool) is False


def test_raw_truthy_attr_tool_is_still_governed(fake_client, ctx) -> None:  # noqa: ANN001
    # End-to-end: a tool wearing a fake exempt bool is still denied under policy.
    import pytest

    from qortara_governance.exceptions import QortaraPolicyDenied

    fake_client.scripted_decisions = [DecisionKind.DENY]
    originals = tool_apply(fake_client)
    try:
        tool = NormalTool()
        tool.__qortara_exempt__ = True  # type: ignore[attr-defined]
        with pytest.raises(QortaraPolicyDenied):
            tool.invoke("hello")
    finally:
        tool_unpatch(originals)


def test_exempt_tool_skips_sidecar_and_runs(fake_client, ctx) -> None:  # noqa: ANN001
    fake_client.scripted_decisions = [DecisionKind.DENY]  # would block if it reached
    originals = tool_apply(fake_client)
    try:
        # Exempt tool runs despite scripted-deny — never hits sidecar.
        result = ExemptTool().invoke("hello")
        assert result == "exempt: hello"
        assert len(fake_client.decisions) == 0  # No decision requested
    finally:
        tool_unpatch(originals)


def test_non_exempt_still_governed(fake_client, ctx) -> None:  # noqa: ANN001
    import pytest

    from qortara_governance.exceptions import QortaraPolicyDenied

    fake_client.scripted_decisions = [DecisionKind.DENY]
    originals = tool_apply(fake_client)
    try:
        with pytest.raises(QortaraPolicyDenied):
            NormalTool().invoke("hello")
    finally:
        tool_unpatch(originals)
