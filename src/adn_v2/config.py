from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class PQCOptions:
    """Configuration for post-quantum defense behaviour."""

    enable_pqc_switch: bool = True
    preferred_algorithms: List[str] = field(
        default_factory=lambda: ["XMSS", "SPHINCS+", "Dilithium"]
    )
    # How aggressively to push PQC even on weak signals
    sensitivity: float = 0.7  # 0.0–1.0


@dataclass
class HardenedModeOptions:
    """Settings for 'hardened mode' during HIGH/CRITICAL risk."""

    min_confirmations: int = 18
    fee_multiplier: float = 3.0
    block_relay_restriction: bool = True
    disconnect_suspicious_peers: bool = True


@dataclass
class ADNConfig:
    """Top-level ADN v2 configuration object."""

    network: str = "digibyte-mainnet"
    # How deep a reorg we tolerate before auto-escalation
    max_safe_reorg_depth: int = 6
    # If Sentinel / Guardian disagree, how much we trust Sentinel
    sentinel_weight: float = 0.65  # remainder goes to wallet signals
    # When combined risk >= this, we enter hardened mode
    hardened_threshold: float = 0.6
    # When combined risk >= this, we trigger emergency PQC switch
    pqc_threshold: float = 0.85

    pqc: PQCOptions = field(default_factory=PQCOptions)
    hardened: HardenedModeOptions = field(default_factory=HardenedModeOptions)


def load_default_config() -> ADNConfig:
    """
    Convenience helper for simple setups.

    In a real node this would load from `adn_v2.yaml` or similar.
    """
    return ADNConfig()
