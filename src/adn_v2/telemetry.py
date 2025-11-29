from __future__ import annotations

import time
from typing import Any, Dict

from .models import TelemetryPacket


"""
Telemetry Adapter – Raw → Structured TelemetryPacket

Different execution environments (full nodes, lightweight nodes,
Sentinel AI, DQSN gateways, test harnesses) expose different raw
telemetry formats.

TelemetryAdapter standardises them into a single
TelemetryPacket object so that:

    • RiskValidator
    • PolicyEngine
    • ADNEngine

all receive consistent, predictable input regardless of origin.
"""


class TelemetryAdapter:
    """
    Adapter layer between raw node telemetry and the internal ADN v2
    TelemetryPacket model.

    The adapter reads whatever keys are present in `raw` and extracts
    the canonical metrics (height, mempool size, peer count, timestamp).
    All remaining keys are preserved under `extra` to avoid losing
    context — validators and advanced engines may use them later.
    """

    def from_raw(self, node_id: str, raw: Dict[str, Any]) -> TelemetryPacket:
        """
        Build a TelemetryPacket from a raw dictionary of metrics.

        Callers can include arbitrary extra fields; anything that is not
        explicitly mapped becomes part of the `extra` dictionary and is
        still available to validators, anomaly detectors, or future v3+
        modules.

        Parameters
        ----------
        node_id : str
            Identifier of the node emitting telemetry.
        raw : dict
            Raw telemetry payload coming from a node, gateway, or test.

        Returns
        -------
        TelemetryPacket
        """
        return TelemetryPacket(
            node_id=node_id,
            height=int(raw.get("height", 0)),
            mempool_size=int(raw.get("mempool_size", 0)),
            peer_count=int(raw.get("peer_count", 0)),
            timestamp=float(raw.get("timestamp", time.time())),
            extra={
                k: v
                for k, v in raw.items()
                if k not in {"height", "mempool_size", "peer_count", "timestamp"}
            },
        )
