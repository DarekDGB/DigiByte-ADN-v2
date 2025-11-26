from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Any, Callable, Dict, Optional

from .decisions import Decision  # existing ADN enum


ADN_LAYER_NAME = "ADN_v2"


@dataclass
class AdaptiveEvent:
    """
    Generic adaptive event emitted by ADN v2.

    This structure is designed to be compatible with the
    DigiByte-Quantum-Adaptive-Core RiskEvent model.
    """

    event_id: str
    layer: str
    decision: str
    fingerprint: str
    severity: float
    created_at: datetime
    feedback: str = "unknown"
    metadata: Dict[str, Any] = None

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        # datetime → ISO string for JSON / logging
        d["created_at"] = self.created_at.isoformat()
        return d


def build_adaptive_event_from_adn(
    *,
    event_id: str,
    decision: Decision,
    severity: float,
    fingerprint: str,
    node_id: Optional[str] = None,
    reason: Optional[str] = None,
    extra_meta: Optional[Dict[str, Any]] = None,
) -> AdaptiveEvent:
    """
    Create an AdaptiveEvent instance from an ADN v2 decision.

    - event_id    – unique id in your system (tx id, internal uuid, etc.)
    - decision    – ADN v2 Decision enum (ALLOW / WARN / DELAY / BLOCK / ...)
    - severity    – numeric signal 0.0–1.0
    - fingerprint – hash / identifier of the underlying situation
    - node_id     – optional identifier of this ADN node
    - reason      – optional human-readable reason from ADN engine
    - extra_meta  – any additional fields you want to send
    """
    meta: Dict[str, Any] = {}
    if node_id is not None:
        meta["node_id"] = node_id
    if reason is not None:
        meta["reason"] = reason
    if extra_meta:
        meta.update(extra_meta)

    return AdaptiveEvent(
        event_id=event_id,
        layer=ADN_LAYER_NAME,
        decision=decision.value,
        fingerprint=fingerprint,
        severity=max(0.0, min(1.0, float(severity))),
        created_at=datetime.utcnow(),
        metadata=meta,
    )


# --------------------------------------------------------------------------- #
# Optional: simple helper to send events into Adaptive Core
# --------------------------------------------------------------------------- #

AdaptiveSink = Callable[[AdaptiveEvent], None]


def emit_adaptive_event(
    sink: Optional[AdaptiveSink],
    *,
    event_id: str,
    decision: Decision,
    severity: float,
    fingerprint: str,
    node_id: Optional[str] = None,
    reason: Optional[str] = None,
    extra_meta: Optional[Dict[str, Any]] = None,
) -> Optional[AdaptiveEvent]:
    """
    Convenience helper for ADN:

    If `sink` is provided, build an AdaptiveEvent and send it there.
    If `sink` is None → do nothing and return None.

    Example usage from ADN engine / policies:

        emit_adaptive_event(
            adaptive_sink,
            event_id=request_id,
            decision=decision,
            severity=risk_score,
            fingerprint=primary_fingerprint,
            node_id=node_id,
            reason=reason,
        )
    """
    if sink is None:
        return None

    event = build_adaptive_event_from_adn(
        event_id=event_id,
        decision=decision,
        severity=severity,
        fingerprint=fingerprint,
        node_id=node_id,
        reason=reason,
        extra_meta=extra_meta,
    )
    sink(event)
    return event
