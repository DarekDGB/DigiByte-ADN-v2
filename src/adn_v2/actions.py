from __future__ import annotations

from typing import Dict, Any

from .models import (
    DefenseAction,
    NodeDefenseState,
)


def build_rpc_policy_from_state(state: NodeDefenseState) -> Dict[str, Any]:
    """
    Convert NodeDefenseState → RPC policy dict.

    Used by tests and by ADN v2 to apply lockdown / throttling.
    """
    # NORMAL mode
    if state.lockdown_state == "NONE" or state.lockdown_state.name == "NONE":
        return {
            "rpc_enabled": True,
            "rpc_rate_limit": None,
            "notes": ["NORMAL"],
        }

    # PARTIAL lockdown → throttled, but RPC still enabled
    if state.lockdown_state.name == "PARTIAL":
        return {
            "rpc_enabled": True,
            "rpc_rate_limit": 100,   # simple throttle
            "notes": ["PARTIAL_LOCKDOWN"],
        }

    # FULL lockdown → RPC disabled
    if state.lockdown_state.name == "FULL":
        return {
            "rpc_enabled": False,
            "rpc_rate_limit": 0,
            "notes": ["FULL_LOCKDOWN"],
        }

    # fallback (should never happen)
    return {
        "rpc_enabled": True,
        "rpc_rate_limit": None,
        "notes": ["UNKNOWN_STATE"],
    }


class ActionExecutor:
    """
    v2 minimal executor — used only to flag state changes.

    No real RPC calls, no side effects.
    """

    def __init__(self, node_id: str) -> None:
        self.node_id = node_id

    def execute(self, decision, context: Dict[str, Any]) -> None:
        """
        Attach decision → node_state context dict.

        In v2 tests, we only mark hardened_mode for FULL lockdown.
        """
        node_state: Dict[str, Any] = context.get("node_state", {})

        if decision.level.name in ("CRITICAL",):
            node_state["hardened"] = True

        context["node_state"] = node_state
