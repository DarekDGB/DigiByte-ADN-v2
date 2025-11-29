from adn_v2.models import (
    DefenseEvent,
    NodeDefenseConfig,
    LockdownState,
    RiskLevel,
)
from adn_v2.engine import evaluate_defense
from adn_v2.actions import build_rpc_policy_from_state


def test_defense_flow_partial_lockdown():
    events = [
        DefenseEvent(event_type="rpc_abuse", severity=0.6, source="local"),
        DefenseEvent(event_type="sentinel_alert", severity=0.5, source="sentinel"),
    ]

    state = evaluate_defense(events, NodeDefenseConfig())
    policy = build_rpc_policy_from_state(state)

    # Risk level & lockdown mode
    assert state.risk_level in {RiskLevel.ELEVATED, RiskLevel.HIGH, RiskLevel.CRITICAL}
    assert state.lockdown_state in {LockdownState.PARTIAL, LockdownState.FULL}

    # Policy should at least throttle RPC in non-normal mode
    assert policy["rpc_enabled"] is True
    assert policy["rpc_rate_limit"] is not None
    assert "LOCKDOWN" in "".join(policy["notes"]).upper()


def test_defense_flow_full_lockdown():
    events = [
        DefenseEvent(event_type="dqsn_critical", severity=0.9, source="dqsn"),
        DefenseEvent(event_type="rpc_abuse", severity=0.85, source="local"),
    ]

    state = evaluate_defense(events, NodeDefenseConfig())
    policy = build_rpc_policy_from_state(state)

    # For very high severity we expect the strongest reaction
    assert state.risk_level in {RiskLevel.CRITICAL, RiskLevel.HIGH}
    assert state.lockdown_state == LockdownState.FULL
    assert policy["rpc_enabled"] is False
