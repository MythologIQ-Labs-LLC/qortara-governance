"""EvidenceSink — where dispatch-path evidence goes (opt-in; B5 emission).

Emitting evidence from the enforcement dispatch path is opt-in: pass an
``evidence_sink`` to ``init()`` / ``init_agt()``. With no sink (the default),
nothing is emitted and the hot path is unchanged.

The sink contract is the existing best-effort, never-raises shape already used by
``SidecarClient.submit_evidence`` — so a sidecar deployment can serve as its own
sink. ``safe_emit`` guarantees a sink failure never propagates into the governed
call (evidence loss must never weaken enforcement).
"""

from __future__ import annotations

import logging
from typing import Protocol, runtime_checkable

from qortara_governance.otel import tag_evidence_id
from qortara_protocol import EvidenceRecord

_log = logging.getLogger("qortara_governance")


@runtime_checkable
class EvidenceSink(Protocol):
    """A destination for governance evidence records (best-effort, never raises)."""

    def submit_evidence(self, records: list[EvidenceRecord]) -> None:
        """Persist/forward evidence. MUST NOT raise into the caller."""
        ...


def safe_emit(sink: EvidenceSink, record: EvidenceRecord) -> None:
    """Emit one record best-effort. A sink failure is logged, never raised.

    This is the guarantee that makes dispatch-path emission safe: evidence loss
    must never break a governed call or alter a policy decision.
    """
    try:
        sink.submit_evidence([record])
    except Exception:  # noqa: BLE001 — emission must never raise into the caller
        _log.debug("qortara: evidence sink failed; record dropped", exc_info=True)


class OTelEvidenceSink:
    """Built-in sink that surfaces evidence on the current OpenTelemetry span.

    Tags the active span with ``qortara.evidence_id`` and adds a span event with
    the decision kind + execution result. A no-op when OpenTelemetry is not
    installed or no span is recording (``otel.py`` is import-guarded).
    """

    def submit_evidence(self, records: list[EvidenceRecord]) -> None:
        try:
            from opentelemetry import trace
        except ImportError:  # pragma: no cover — OTel optional
            return
        span = trace.get_current_span()
        recording = span.is_recording()
        for record in records:
            tag_evidence_id(record.evidence_id)
            if recording:
                span.add_event(
                    "qortara.evidence",
                    {
                        "qortara.evidence_id": record.evidence_id,
                        "qortara.decision_kind": record.decision.decision_kind.value,
                        "qortara.execution_result": record.execution_result.value,
                        "qortara.duration_ms": record.duration_ms,
                    },
                )
