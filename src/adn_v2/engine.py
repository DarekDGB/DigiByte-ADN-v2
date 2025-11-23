from __future__ import annotations

import logging
from typing import Optional

from .config import ADNConfig
from .models import (
    ActionPlan,
    ChainTelemetry,
    SentinelSignal,
    WalletSignal,
)
from .policy import PolicyEngine

logger = logging.getLogger(__name__)


class ADNEngine:
    """
    High-level orchestration engine for ADN v2.

    It connects:
      - chain telemetry
      - Sentinel AI v2 signals
      - optional Wallet Guardian signals

    and produces an ActionPlan that can be executed by node operators.
    """

    def __init__(self, config: Optional[ADNConfig] = None) -> None:
        self.config = config or ADNConfig()
        self.policy = PolicyEngine(self.config)

    def evaluate(
        self,
        telemetry: ChainTelemetry,
        sentinel: SentinelSignal,
        wallet: Optional[WalletSignal] = None,
    ) -> ActionPlan:
        logger.debug(
            "Evaluating ADN v2 state",
            extra={
                "height": telemetry.height,
                "sentinel_score": sentinel.risk_score,
                "wallet_state": getattr(wallet, "aggregated_state", None),
            },
        )
        return self.policy.evaluate(telemetry, sentinel, wallet)
