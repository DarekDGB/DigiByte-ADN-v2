from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict
import time

from .config import ADNConfig
from .contracts.v3_hash import canonical_sha256
from .contracts.v3_reason_codes import ReasonCode
from .contracts.v3_types import ADNv3Request


@dataclass(frozen=True)
class ADNv3:
    """
    Shield Contract v3 gate for ADN.
    Minimal implementation: contract validation + fail-closed error responses.

    Next step will map validated events into v2 engine evaluation.
    """
    config: ADNConfig

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

        # v3 gate is valid.
        # Next step: map req.events into v2 engine and return real decision/actions.
        raise NotImplementedError("ADNv3 evaluation logic not wired to v2 engine yet")

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
            "actions": [],
            "reason_codes": [reason_code],
            "evidence": {"details": details},
            "meta": {"latency_ms": int(latency_ms), "fail_closed": True},
        }
