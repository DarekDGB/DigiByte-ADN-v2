"""
DigiByte Autonomous Defense Node v2 (ADN v2)

Layer-3 execution engine in the DigiByte quantum-resilient shield:

    DQSN → Sentinel AI v2 → ADN v2 → Wallet Guardian

This package exposes a small, clean surface for:
- ingesting chain / Sentinel / wallet signals
- applying policy rules
- producing machine-readable action plans
"""

from .models import (
    RiskState,
    SentinelSignal,
    WalletSignal,
    ChainTelemetry,
    PolicyDecision,
    ActionPlan,
)
from .config import ADNConfig
from .engine import ADNEngine

__all__ = [
    "RiskState",
    "SentinelSignal",
    "WalletSignal",
    "ChainTelemetry",
    "PolicyDecision",
    "ActionPlan",
    "ADNConfig",
    "ADNEngine",
]

__version__ = "0.1.0"
