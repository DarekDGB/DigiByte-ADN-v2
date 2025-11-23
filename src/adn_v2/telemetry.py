from __future__ import annotations

import time
from typing import Any, Dict

from .models import TelemetryPacket


class TelemetryAdapter:
    """
    Thin adapter that converts raw node / Sentinel / DQSN data into
    TelemetryPacket objects understood by ADN v2.
    """

    def from_raw(self, node_id: str, raw: Dict[str, Any]) -> TelemetryPacket:
        return TelemetryPacket(
            node_id=node_id,
            height=int(raw.get("height", 0)),
            mempool_size=int(raw.get("mempool_size", 0)),
            peer_count=int(raw.get("peer_count", 0)),
            timestamp=float(raw.get("timestamp", time.time())),
            extra={k: v for k, v in raw.items() if k not in {"height", "mempool_size", "peer_count", "timestamp"}},
        )
