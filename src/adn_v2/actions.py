from __future__ import annotations

from dataclasses import asdict
from typing import Dict, Any

from .models import ActionPlan


class ActionExecutor:
    """
    Reference "executor" that simply turns ActionPlan into a dict.

    Real node integrators can map this dict into RPC calls, config
    changes, or signalling inside DigiByte Core.
    """

    def to_dict(self, plan: ActionPlan) -> Dict[str, Any]:
        """
        Convert ActionPlan into a serialisable dict.
        """
        data = asdict(plan)
        # You can customise / redact fields here if needed.
        return data
