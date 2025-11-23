from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass
class TelemetryBundle:
    """
    Normalised incoming data from DQSN + Sentinel + Wallet Guardian.

    This allows different implementations to feed ADN v2 without
    depending on their internal structures.
    """

    chain_snapshot: Dict[str, int | float]
    sentinel_payload: Dict[str, float]
    guardians_payload: Dict[str, float]
