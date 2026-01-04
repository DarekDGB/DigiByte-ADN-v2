from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import time

from .models import DefenseEvent, NodeDefenseConfig, NodeDefenseState, RiskLevel, LockdownState
from .engine import evaluate_defense

from .contracts.v3_hash import canonical_sha256
from .contracts.v3_reason_codes import ReasonCode
from .contracts.v3_types import ADNv3Request


@dataclass(frozen=True)
class ADNv3:
    """
    Shield Contract v3 gate for ADN.

    v3 responsibilities:
    - strict request parsing (deny unknown top-level keys)
    - fail-closed semantics
    - deterministic decision outputs (context_hash stable)
    - calls the existing v2 engine for decisions (no behavior expansion)
    """
    config: Optional[NodeDefenseConfig] = None

    COMPONENT: str = "adn"
    CONTRACT_VERSION: int = 3

    def evaluate(self, request: Dict[str, Any]) -> Dict[str, Any]:
        start = time.time()

        # Strict contract parsing (fail-closed)
        try:
            req = ADNv3Request.from_dict(request)
        except ValueError as e:
            reason = str(e) or ReasonCode.ADN_ERROR_INVALID_REQUEST.value
            return self._error_response(
                request_id=request.get("request_id", "unknown") if isinstance(request, dict) else "unknown",
                reason_code=reason,
                details={"error": reason},
                latency_ms=self._latency_ms(start),
            )
        except Exception:
            return self._error_response(
                request_id=request.get("request_id", "unknown") if isinstance(request, dict) else "unknown",
                reason_code=ReasonCode.ADN_ERROR_INVALID_REQUEST.value,
                details={"error": "invalid request"},
                latency_ms=self._latency_ms(start),
            )

        # Version hard check
        if req.contract_version != self.CONTRACT_VERSION:
            return self._error_response(
                request_id=req.request_id,
                reason_code=ReasonCode.ADN_ERROR_SCHEMA_VERSION.value,
                details={"error": "contract_version must be 3"},
                latency_ms=self._latency_ms(start),
            )

        # Component hard check
        if req.component != self.COMPONENT:
            return self._error_response(
                request_id=req.request_id,
                reason_code=ReasonCode.ADN_ERROR_INVALID_REQUEST.value,
                details={"error": "component mismatch"},
                latency_ms=self._latency_ms(start),
            )

        # Map v3 events → v2 DefenseEvent objects (fail-closed)
        try:
            events: List[DefenseEvent] = self._parse_events(req.events)
        except ValueError as e:
            reason = str(e) or ReasonCode.ADN_ERROR_INVALID_REQUEST.value
            return self._error_response(
                request_id=req.request_id,
                reason_code=reason,
                details={"error": reason},
                latency_ms=self._latency_ms(start),
            )

        cfg = self.config or NodeDefenseConfig()
        state_in = NodeDefenseState()

        # Existing v2 engine (authoritative behavior for now)
        state_out = evaluate_defense(events=events, config=cfg, state=state_in)

        decision = self._decision_from_state(state_out)
        reason_codes = self._reason_codes_from_state(state_out)

        # Deterministic context hash (do NOT include latency_ms or timestamps)
        context_hash = canonical_sha256(
            {
                "component": self.COMPONENT,
                "contract_version": self.CONTRACT_VERSION,
                "request_id": req.request_id,
                "events": req.events,  # original request form (stable after contract parsing)
                "node_defense_config": self._config_fingerprint(cfg),
                "decision": decision,
                "risk_level": state_out.risk_level.value,
                "lockdown_state": state_out.lockdown_state.value,
                "actions": [self._action_to_dict(a) for a in (state_out.last_actions or [])],
                "reason_codes": reason_codes,
            }
        )

        return {
            "contract_version": self.CONTRACT_VERSION,
            "component": self.COMPONENT,
            "request_id": req.request_id,
            "context_hash": context_hash,
            "decision": decision,
            "risk": {
                "level": state_out.risk_level.value,
                "lockdown_state": state_out.lockdown_state.value,
            },
            "actions": [self._action_to_dict(a) for a in (state_out.last_actions or [])],
            "reason_codes": reason_codes,
            "evidence": {
                # Keep evidence minimal and contract-facing (avoid leaking internals)
                "active_events_count": len(state_out.active_events or []),
            },
            "meta": {
                "latency_ms": self._latency_ms(start),
                "fail_closed": True,
            },
        }

    # -------------------------
    # Parsing / mapping helpers
    # -------------------------

    @staticmethod
    def _parse_events(raw_events: List[Dict[str, Any]]) -> List[DefenseEvent]:
        events: List[DefenseEvent] = []
        allowed_event_keys = {"event_type", "severity", "source", "metadata"}

        for e in raw_events:
            if not isinstance(e, dict):
                raise ValueError(ReasonCode.ADN_ERROR_INVALID_REQUEST.value)

            # Event-level unknown key rejection (fail-closed)
            unknown = set(e.keys()) - allowed_event_keys
            if unknown:
                raise ValueError(ReasonCode.ADN_ERROR_EVENT_UNKNOWN_KEY.value)

            # Minimal required schema for v3 events (strict enough to be audit-friendly)
            event_type = e.get("event_type")
            severity = e.get("severity")
            source = e.get("source")
            metadata = e.get("metadata", {})

            if not isinstance(event_type, str) or not event_type.strip():
                raise ValueError(ReasonCode.ADN_ERROR_INVALID_REQUEST.value)
            if not (isinstance(severity, (int, float)) and 0.0 <= float(severity) <= 1.0):
                raise ValueError(ReasonCode.ADN_ERROR_INVALID_REQUEST.value)
            if not isinstance(source, str) or not source.strip():
                raise ValueError(ReasonCode.ADN_ERROR_INVALID_REQUEST.value)
            if metadata is None:
                metadata = {}
            if not isinstance(metadata, dict):
                raise ValueError(ReasonCode.ADN_ERROR_INVALID_REQUEST.value)

            events.append(
                DefenseEvent(
                    event_type=event_type.strip(),
                    severity=float(severity),
                    source=source.strip(),
                    metadata=metadata,
                )
            )

        return events

    @staticmethod
    def _action_to_dict(a: Any) -> Dict[str, Any]:
        # DefenseAction is a dataclass; keep it stable
        return {
            "action_type": getattr(a, "action_type", ""),
            "reason": getattr(a, "reason", ""),
            "metadata": getattr(a, "metadata", None),
        }

    @staticmethod
    def _decision_from_state(state: NodeDefenseState) -> str:
        # Deny-by-default mapping
        if state.lockdown_state == LockdownState.FULL:
            return "BLOCK"
        if state.lockdown_state == LockdownState.PARTIAL:
            return "WARN"

        # No lockdown: map by risk level
        if state.risk_level in {RiskLevel.NORMAL}:
            return "ALLOW"
        if state.risk_level in {RiskLevel.ELEVATED}:
            return "WARN"
        if state.risk_level in {RiskLevel.HIGH, RiskLevel.CRITICAL}:
            return "BLOCK"
        return "BLOCK"

    @staticmethod
    def _reason_codes_from_state(state: NodeDefenseState) -> List[str]:
        # Minimal, contract-facing
        if state.risk_level == RiskLevel.NORMAL and state.lockdown_state == LockdownState.NONE:
            return [ReasonCode.ADN_OK.value]
        return [ReasonCode.ADN_V2_SIGNAL.value]

    @staticmethod
    def _config_fingerprint(cfg: NodeDefenseConfig) -> Dict[str, Any]:
        try:
            return dict(vars(cfg))
        except Exception:
            return {"_": "unavailable"}

    # -------------------------
    # Error response
    # -------------------------

    @staticmethod
    def _latency_ms(start: float) -> int:
        return int((time.time() - start) * 1000)

    def _error_response(self, request_id: str, reason_code: str, details: Dict[str, Any], latency_ms: int) -> Dict[str, Any]:
        context_hash = canonical_sha256(
            {
                "component": self.COMPONENT,
                "contract_version": self.CONTRACT_VERSION,
                "request_id": str(request_id),
                "reason_code": reason_code,
            }
        )
        return {
            "contract_version": self.CONTRACT_VERSION,
            "component": self.COMPONENT,
            "request_id": str(request_id),
            "context_hash": context_hash,
            "decision": "ERROR",
            "risk": {"level": "unknown", "lockdown_state": "unknown"},
            "actions": [],
            "reason_codes": [reason_code],
            "evidence": {"details": details},
            "meta": {"latency_ms": int(latency_ms), "fail_closed": True},
        }
