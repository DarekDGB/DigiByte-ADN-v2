from __future__ import annotations

import json
from dataclasses import asdict
from typing import Any, Dict, Optional
from urllib.request import Request, urlopen

from .models import PolicyDecision


class ADNClient:
    """
    Lightweight HTTP client used by ADN nodes to talk to a central ADN service,
    DQSN, Sentinel AI v2, or Wallet Guardian endpoints.

    Uses only the Python standard library (urllib).
    """

    def __init__(self, base_url: str) -> None:
        self.base_url = base_url.rstrip("/")

    def _post(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        data = json.dumps(payload).encode("utf-8")
        req = Request(
            f"{self.base_url}{path}",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urlopen(req) as resp:  # noqa: S310
            raw = resp.read().decode("utf-8")
        return json.loads(raw)

    def send_telemetry(self, telemetry: Dict[str, Any]) -> PolicyDecision:
        response = self._post("/telemetry", {"type": "telemetry", "data": telemetry})
        return PolicyDecision(
            level=response["level"],
            score=response["score"],
            reason=response.get("reason", ""),
            actions=response.get("actions", []),
        )

    def notify_dqsn(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return self._post("/dqsn", message)

    def notify_sentinel(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return self._post("/sentinel", message)
