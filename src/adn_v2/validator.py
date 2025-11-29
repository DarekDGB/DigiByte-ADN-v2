from __future__ import annotations

from typing import List

from .models import (
    RiskSignal,
    TelemetryPacket,
    RiskLevel,
)


class RiskValidator:
    """
    Minimal v2 RiskValidator.

    Converts TelemetryPacket → list[RiskSignal]

    This keeps the engine pipeline functional without introducing
    advanced scoring logic yet. Perfect for v2 tests.
    """

    def derive_signals(self, packet: TelemetryPacket) -> List[RiskSignal]:
        signals: List[RiskSignal] = []

        # --- Simple heuristics for v2 ---
        # More peers = safer, fewer peers = mild risk
        if packet.peer_count < 2:
            signals.append(
                RiskSignal(
                    source="telemetry",
                    level=RiskLevel.ELEVATED,
                    score=0.6,
                    details={"reason": "low_peer_count"},
                )
            )

        # Large mempool spike could signal congestion or attack pattern
        if packet.mempool_size > 20000:
            signals.append(
                RiskSignal(
                    source="telemetry",
                    level=RiskLevel.HIGH,
                    score=0.8,
                    details={"reason": "mempool_spike"},
                )
            )

        # If no obvious risk → emit NORMAL
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
