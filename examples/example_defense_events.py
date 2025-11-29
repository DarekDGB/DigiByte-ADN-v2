"""
Example: DefenseEvent → NodeDefenseState → RPC policy.

This script uses the v2 defense engine directly:
  - builds a list of DefenseEvent objects
  - evaluates lockdown state with evaluate_defense(...)
  - converts the result into an RPC policy dict
"""

from adn_v2.models import DefenseEvent, NodeDefenseConfig
from adn_v2.engine import evaluate_defense
from adn_v2.actions import build_rpc_policy_from_state


def main() -> None:
    # 1. Simulate multiple high-severity events
    events = [
        DefenseEvent(
            event_type="dqsn_critical",
            severity=0.9,
            source="dqsn",
            metadata={"advisory": "CRITICAL_GLOBAL"},
        ),
        DefenseEvent(
            event_type="rpc_abuse",
            severity=0.85,
            source="local",
            metadata={"ip": "203.0.113.42"},
        ),
    ]

    config = NodeDefenseConfig()

    # 2. Evaluate defense state for this batch of events
    state = evaluate_defense(events, config=config)

    # 3. Build an RPC policy from the resulting NodeDefenseState
    policy = build_rpc_policy_from_state(state)

    print("=== ADN v2 DefenseEvent Flow Example ===")
    print("Risk level:           ", state.risk_level.name)
    print("Lockdown state:       ", state.lockdown_state.name)
    print("Last actions:         ", [a.action_type for a in state.last_actions])
    print("RPC policy:           ", policy)


if __name__ == "__main__":
    main()
