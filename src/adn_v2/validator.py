from __future__ import annotations

from typing import List

from .models import (
    RiskSignal,
    TelemetryPacket,
    RiskLevel,
)


"""
RiskValidator – ADN v2 reference validator

This module provides the minimal telemetry → risk translation used by
the Autonomous Defense Node (ADN) pipeline.

Projects depending on ADN v2 can subclass / replace this validator
to implement more sophisticated threat scoring without modifying the
core engine.
"""


class RiskValidator:
    """
    Minimal reference validator for ADN v2.

    It inspects TelemetryPacket fields and produces a list of
    RiskSignal entries. The logic is intentionally simple:
    - low peer count → elevated risk
    - large mempool spike → high risk
    - otherwise → normal baseline

    This keeps v2 tests and CI clean while providing a realistic
    entry point for future expansion.
    """

    def derive_signals(self, packet: TelemetryPacket) -> List[RiskSignal]:
        signals: List[RiskSignal] = []

        # ---------------------------
        # Simple heuristics for v2
        # ---------------------------

        # Very low peer connectivity → mild/elevated risk
        if packet.peer_count < 2:
            signals.append(
                RiskSignal(
                    source="telemetry",
                    level=RiskLevel.ELEVATED,
                    score=0.6,
                    details={"reason": "low_peer_count"},
                )
            )

        # Mempool spike → potential congestion / attack pattern
        if packet.mempool_size > 20000:
            signals.append(
                RiskSignal(
                    source="telemetry",
                    level=RiskLevel.HIGH,
                    score=0.8,
                    details={"reason": "mempool_spike"},
                )
            )

        # No notable anomalies → baseline “normal” signal
        if not signals:
            signals.append(
                RiskSignal(
                    source="telemetry",
                    level=RiskLevel.NORMAL,
                    score=0.1,
                    details={"reason": "baseline_telemetry"},
                )
            )

        return signals
