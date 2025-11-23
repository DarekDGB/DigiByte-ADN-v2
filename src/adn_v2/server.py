"""
Placeholder HTTP server wiring for ADN v2.

This file intentionally avoids binding to a specific web framework.
Integrators can adapt the pattern below to FastAPI, Flask, etc.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from .client import ADNClient
from .config import ADNConfig


class ADNService:
    """
    Minimal, framework-agnostic service wrapper.

    You can call ADNService.handle_request(...) from any HTTP handler.
    """

    def __init__(self, config: Optional[ADNConfig] = None) -> None:
        self.client = ADNClient(config=config)

    def handle_request(
        self,
        chain_metrics: Dict[str, Any],
        sentinel_payload: Dict[str, Any],
        wallet_payload: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Evaluate inputs and return an action plan as a dict.
        """
        plan = self.client.evaluate(chain_metrics, sentinel_payload, wallet_payload)
        # Use ActionExecutor if you want a more opinionated mapping.
        from .actions import ActionExecutor

        return ActionExecutor().to_dict(plan)
