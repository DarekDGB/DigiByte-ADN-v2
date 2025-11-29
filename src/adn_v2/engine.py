from __future__ import annotations

from typing import Dict, List

from .actions import ActionExecutor
from .models import NodeState, PolicyDecision, RiskSignal, TelemetryPacket
from .policy import PolicyEngine
from .telemetry import TelemetryAdapter
from .validator import RiskValidator  # already created earlier


class ADNEngine:
    """
    Core ADN v2 engine.

    Pipeline:
      telemetry -> RiskValidator -> PolicyEngine -> ActionExecutor
    """

    def __init__(
        self,
        node_id: str,
        policy_engine: PolicyEngine | None = None,
        action_executor: ActionExecutor | None = None,
        validator: RiskValidator | None = None,
        telemetry_adapter: TelemetryAdapter | None = None,
    ) -> None:
        self.state = NodeState(node_id=node_id)
        self.policy_engine = policy_engine or PolicyEngine()
        self.action_executor = action_executor or ActionExecutor(node_id=node_id)
        self.validator = validator or RiskValidator()
        self.telemetry_adapter = telemetry_adapter or TelemetryAdapter()

    def process_raw_telemetry(self, raw: Dict[str, object]) -> PolicyDecision:
        packet = self.telemetry_adapter.from_raw(self.state.node_id, raw)
        return self.process_packet(packet)

    def process_packet(self, packet: TelemetryPacket) -> PolicyDecision:
        signals: List[RiskSignal] = self.validator.derive_signals(packet)
        decision = self.policy_engine.decide(signals)
        context: Dict[str, object] = {"packet": packet, "node_state": {}}
        self.action_executor.execute(decision, context)
        if context["node_state"].get("hardened"):
            self.state.hardened_mode = True
        self.state.last_decision = decision
        return decision

from typing import List, Optional

from .models import (
    DefenseEvent,
    DefenseAction,
    NodeDefenseConfig,
    NodeDefenseState,
    LockdownState,
    RiskLevel,
)


def evaluate_defense(
    events: List[DefenseEvent],
    config: Optional[NodeDefenseConfig] = None,
    state: Optional[NodeDefenseState] = None,
) -> NodeDefenseState:
    """
    v2 defense decision engine.

    Takes a list of DefenseEvent objects and returns an updated NodeDefenseState
    plus any DefenseActions that should be taken (stored in state.last_actions).
    """
    if config is None:
        config = NodeDefenseConfig()

    if state is None:
        state = NodeDefenseState()

    if not events:
        # Nothing new: keep existing state, clear last_actions
        state.last_actions = []
        return state

    # Merge new events into active list
    state.active_events.extend(events)

    # Compute a simple aggregate severity
    severities = [e.severity for e in state.active_events]
    avg_severity = sum(severities) / len(severities)

    actions: List[DefenseAction] = []

    # Decide risk level from average severity
    if avg_severity >= config.lockdown_threshold:
        state.risk_level = RiskLevel.CRITICAL
    elif avg_severity >= config.partial_lock_threshold:
        state.risk_level = RiskLevel.ELEVATED
    else:
        state.risk_level = RiskLevel.NORMAL

    # Decide lockdown state + actions
    if state.risk_level is RiskLevel.CRITICAL:
        if state.lockdown_state is not LockdownState.FULL:
            state.lockdown_state = LockdownState.FULL
            actions.append(
                DefenseAction(
                    action_type="ENTER_FULL_LOCKDOWN",
                    reason=f"avg_severity={avg_severity:.2f} >= {config.lockdown_threshold}",
                )
            )
    elif state.risk_level is RiskLevel.ELEVATED:
        if state.lockdown_state is LockdownState.NONE:
            state.lockdown_state = LockdownState.PARTIAL
            actions.append(
                DefenseAction(
                    action_type="ENTER_PARTIAL_LOCKDOWN",
                    reason=f"avg_severity={avg_severity:.2f} >= {config.partial_lock_threshold}",
                )
            )
    else:
        # NORMAL → lift lockdown if we were previously locked
        if state.lockdown_state is not LockdownState.NONE:
            actions.append(
                DefenseAction(
                    action_type="LIFT_LOCKDOWN",
                    reason="risk back to NORMAL",
                )
            )
        state.lockdown_state = LockdownState.NONE

    state.last_actions = actions
    return state
