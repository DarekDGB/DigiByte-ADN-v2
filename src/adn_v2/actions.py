from __future__ import annotations

import logging
from typing import Any, Dict, List

from .models import ActionResult, PolicyDecision

logger = logging.getLogger("adn_v2.actions")


class ActionExecutor:
    """
    Executes actions selected by the PolicyEngine.

    Real integrations can replace the body of these methods with concrete
    DigiByte node RPC calls, firewall controls, or wallet hooks.
    """

    def __init__(self, node_id: str) -> None:
        self.node_id = node_id

    def execute(self, decision: PolicyDecision, context: Dict[str, Any] | None = None) -> List[ActionResult]:
        context = context or {}
        results: List[ActionResult] = []

        for action_name in decision.actions:
            handler = getattr(self, f"_do_{action_name}", None)
            if handler is None:
                logger.warning("Unknown action '%s'", action_name)
                results.append(
                    ActionResult(
                        name=action_name,
                        success=False,
                        detail="unknown action",
                    )
                )
                continue

            try:
                detail = handler(decision, context)
                results.append(
                    ActionResult(
                        name=action_name,
                        success=True,
                        detail=detail or "",
                    )
                )
            except Exception as exc:  # noqa: BLE001
                logger.exception("Action '%s' failed", action_name)
                results.append(
                    ActionResult(
                        name=action_name,
                        success=False,
                        detail=str(exc),
                    )
                )

        return results

    def _do_log(self, decision: PolicyDecision, _: Dict[str, Any]) -> str:
        logger.info(
            "ADN decision on node %s: level=%s score=%.2f reason=%s",
            self.node_id,
            decision.level.value,
            decision.score,
            decision.reason,
        )
        return "logged decision"

    def _do_alert(self, decision: PolicyDecision, _: Dict[str, Any]) -> str:
        logger.warning(
            "ADN ALERT on node %s: level=%s score=%.2f",
            self.node_id,
            decision.level.value,
            decision.score,
        )
        return "operator alerted (log-level warning)"

    def _do_harden_node(self, _: PolicyDecision, context: Dict[str, Any]) -> str:
        context.setdefault("node_state", {})["hardened"] = True
        logger.info("Node %s switched to hardened mode", self.node_id)
        return "hardened mode on"

    def _do_isolate_peers(self, _: PolicyDecision, context: Dict[str, Any]) -> str:
        context.setdefault("node_state", {})["peer_filtering"] = "strict"
        logger.info("Node %s enabling strict peer filtering", self.node_id)
        return "strict peer filtering enabled"

    def _do_throttle_mempool(self, _: PolicyDecision, context: Dict[str, Any]) -> str:
        context.setdefault("node_state", {})["mempool_throttle"] = True
        logger.info("Node %s throttling mempool ingestion", self.node_id)
        return "mempool throttling enabled"

    def _do_notify_wallet_guardian(self, decision: PolicyDecision, _: Dict[str, Any]) -> str:
        logger.info(
            "Notifying Wallet Guardian from ADN: level=%s score=%.2f",
            decision.level.value,
            decision.score,
        )
        return "wallet guardian notified"

# --- v2 RPC / node-guard helpers -------------------------------------------

from typing import Dict
from .models import NodeDefenseState, LockdownState


def build_rpc_policy_from_state(state: NodeDefenseState) -> Dict[str, object]:
    """
    Translate the current NodeDefenseState into a simple RPC / node policy.

    This does NOT actually change any live node config. It just describes
    what a node operator or integration script *could* apply.
    """
    # default: everything open (normal mode)
    policy: Dict[str, object] = {
        "rpc_enabled": True,
        "allow_withdrawals": True,
        "rpc_rate_limit": None,   # None = unlimited
        "notes": [],
    }

    if state.lockdown_state is LockdownState.FULL:
        policy["rpc_enabled"] = False
        policy["allow_withdrawals"] = False
        policy["notes"].append("FULL_LOCKDOWN: disable RPC + withdrawals")

    elif state.lockdown_state is LockdownState.PARTIAL:
        policy["rpc_enabled"] = True
        policy["allow_withdrawals"] = True
        policy["rpc_rate_limit"] = 100  # example throttle; tune per-node
        policy["notes"].append("PARTIAL_LOCKDOWN: throttle RPC")

    else:
        policy["notes"].append("NORMAL: no ADN lockdown active")

    return policy
