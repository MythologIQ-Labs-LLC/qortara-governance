"""qortara-governance doctor diagnostics (W3)."""

from __future__ import annotations

import json
from typing import Any

import pytest

import qortara_governance
from qortara_governance.client import SidecarClient
from qortara_governance.context import AgentContext, set_context
from qortara_governance.doctor import collect_status, format_report, main
from qortara_governance.patches import apply_patches
from qortara_protocol import EvidenceRecord


@pytest.fixture(autouse=True)
def _reset() -> None:
    yield
    # The exported unpatch_all also clears the init fingerprint + registry state.
    qortara_governance.unpatch_all()


class _Sink:
    def submit_evidence(
        self, records: list[EvidenceRecord]
    ) -> None:  # pragma: no cover
        pass


def test_doctor_reports_not_active() -> None:
    status = collect_status()
    assert status.patched is False
    assert status.policy_mode == "n/a"
    assert any("NOT active" in w for w in status.warnings)
    assert main([]) == 1  # non-zero exit when governance is off


def test_doctor_reports_enforce_agt() -> None:
    qortara_governance.init_agt("agent-x", ["lookup"])
    status = collect_status()
    assert status.patched is True
    assert "Agt" in status.client_kind  # AgtDecisionClient
    assert status.policy_mode == "enforce"
    assert "BaseTool.run" in status.wrapped_methods
    assert main([]) == 0  # active => zero exit


def test_doctor_reports_observe_mode() -> None:
    qortara_governance.init_agt("agent-x", ["lookup"], policy_mode="observe")
    status = collect_status()
    assert status.policy_mode == "observe"
    assert any(
        "not enforced" in w.lower() or "observe" in w.lower() for w in status.warnings
    )


def test_doctor_warns_when_no_context() -> None:
    qortara_governance.init_agt("agent-x", ["lookup"])  # no set_context
    status = collect_status()
    assert status.context_set is False
    assert any("AgentContext" in w for w in status.warnings)


def test_doctor_no_warning_when_context_set() -> None:
    qortara_governance.init_agt("agent-x", ["lookup"], evidence_sink=_Sink())
    set_context(AgentContext(tenant_id="t", agent_id="agent-x", session_id="s"))
    status = collect_status()
    assert status.context_set is True
    assert status.evidence_sink == "_Sink"
    # enforce + context + sink => no warnings
    assert status.warnings == []


def test_doctor_redacts_tenant_key() -> None:
    apply_patches(SidecarClient("https://api.example.com", "SUPER-SECRET-KEY"))
    status = collect_status()
    assert status.tenant_key_configured is True
    report = format_report(status)
    blob = report + json.dumps({"endpoint": status.endpoint})
    assert "SUPER-SECRET-KEY" not in blob  # value never surfaced


def test_doctor_json_output(capsys: Any) -> None:
    qortara_governance.init_agt("agent-x", ["lookup"])
    rc = main(["--json"])
    out = capsys.readouterr().out
    data = json.loads(out)
    assert data["patched"] is True
    assert data["policy_mode"] == "enforce"
    assert rc == 0
