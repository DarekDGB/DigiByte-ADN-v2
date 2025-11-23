from __future__ import annotations

from typing import Any, Dict, Optional

from .config import ADNConfig
from .engine import ADNEngine
from .models import (
    ActionPlan,
    ChainTelemetry,
    SentinelSignal,
    WalletSignal,
)
from .telemetry import normalise_chain_telemetry


class ADNClient:
    """
    Convenience wrapper for applications that want a single entry-point.

    Typical flow:
        client = ADNClient()
        plan = client.evaluate(raw_chain_metrics, sentinel_payload, wallet_payload)
    """

    def __init__(self, config: Optional[ADNConfig] = None) -> None:
        self.config = config or ADNConfig()
        self.engine = ADNEngine(self.config)

    def evaluate(
        self,
        chain_metrics: Dict[str, Any],
        sentinel_payload: Dict[str, Any],
        wallet_payload: Optional[Dict[str, Any]] = None,
    ) -> ActionPlan:
        telemetry = normalise_chain_telemetry(chain_metrics)

        sentinel = SentinelSignal(
            risk_state=sentinel_payload.get("risk_state"),
            risk_score=float(sentinel_payload.get("risk_score", 0.0)),
            details=sentinel_payload.get("details", {}),
        )

        wallet: Optional[WalletSignal] = None
        if wallet_payload is not None:
            wallet = WalletSignal(
                aggregated_state=wallet_payload.get("aggregated_state"),
                wallet_ids=list(wallet_payload.get("wallet_ids", [])),
                details=wallet_payload.get("details", {}),
            )

        return self.engine.evaluate(telemetry, sentinel, wallet)
