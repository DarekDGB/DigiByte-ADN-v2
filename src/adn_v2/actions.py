from __future__ import annotations

from typing import Dict, Any

from .models import (
    DefenseAction,
    NodeDefenseState,
)


def build_rpc_policy_from_state(state: NodeDefenseState) -> Dict[str, Any]:
    """
    Convert a NodeDefenseState into a JSON-friendly RPC policy.

    This helper is designed for gateways or config templates: it exposes
    simple flags such as:
        - rpc_enabled
        - rpc_rate_limit
        - notes (why lockdown is active)

    The tests depend on this function returning clean + predictable output.
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
            "rpc_rate_limit": 100,  # simple throttle
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
    Executes concrete side-effects for ADN decisions.

    The reference implementation is intentionally minimal — it only marks
    in-memory state (e.g., hardened=True). In production, node operators
    could subclass this to integrate firewalls, RPC gateways, or external
    orchestration systems.
    """

    def __init__(self, node_id: str) -> None:
        self.node_id = node_id

    def execute(self, decision, context: Dict[str, Any]) -> None:
        """
        Apply a PolicyDecision to node_state context.

        For v2 tests:
        - If decision.level == CRITICAL → hardened_mode is set.
        No real RPC calls, no external effects.
        """
        node_state: Dict[str, Any] = context.get("node_state", {})

        if decision.level.name in ("CRITICAL",):
            node_state["hardened"] = True

        context["node_state"] = node_state
