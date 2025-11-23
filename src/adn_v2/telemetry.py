from __future__ import annotations

from typing import Any, Dict

from .models import ChainTelemetry


def normalise_chain_telemetry(raw: Dict[str, Any]) -> ChainTelemetry:
    """
    Convert a raw dict (from node RPC / metrics) into ChainTelemetry.

    The goal is to keep this function simple, deterministic and safe.
    Missing values fall back to conservative defaults.
    """

    return ChainTelemetry(
        height=int(raw.get("height", 0)),
        difficulty=float(raw.get("difficulty", 0.0)),
        mempool_size=int(raw.get("mempool_size", 0)),
        avg_block_interval_sec=float(raw.get("avg_block_interval_sec", 15.0)),
        reorg_depth=int(raw.get("reorg_depth", 0)),
        extra={k: v for k, v in raw.items() if k not in _CORE_KEYS},
    )


_CORE_KEYS = {
    "height",
    "difficulty",
    "mempool_size",
    "avg_block_interval_sec",
    "reorg_depth",
}
