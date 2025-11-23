from __future__ import annotations

from typing import Iterable

from .config import ADNConfig, load_default_config
from .engine import ADNEngine
from .models import (
    ChainSnapshot,
    SentinelSignal,
    GuardianSignal,
    DefenseDecision,
)


class ADNClient:
    """
    High-level convenience wrapper for other projects.

    Example:

        from adn_v2 import ADNClient

        adn = ADNClient()
        decision = adn.evaluate(chain_snapshot, sentinel_signal, guardian_signals)
    """

    def __init__(self, config: ADNConfig | None = None) -> None:
        self.engine = ADNEngine(config or load_default_config())

    def evaluate(
        self,
        chain: ChainSnapshot,
        sentinel: SentinelSignal,
        guardians: Iterable[GuardianSignal],
    ) -> DefenseDecision:
        return self.engine.evaluate_and_apply(chain, sentinel, guardians)
