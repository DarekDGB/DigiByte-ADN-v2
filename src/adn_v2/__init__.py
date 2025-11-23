"""
DigiByte Autonomous Defense Node v2 (ADN v2)

Layer-3 defense engine in the DigiByte quantum-resistant stack:

    DQSN → Sentinel AI v2 → ADN v2 → Wallet Guardian

This package exposes a clean, testable API for:
- receiving signals from Sentinel AI v2 and Wallet Guardian
- evaluating chain + wallet risk
- deciding which network & node-level defenses to activate
"""

from .models import RiskLevel, SentinelSignal, GuardianSignal, DefenseDecision
from .client import ADNClient  # will be defined below

__all__ = [
    "RiskLevel",
    "SentinelSignal",
    "GuardianSignal",
    "DefenseDecision",
    "ADNClient",
]

__version__ = "0.1.0"
