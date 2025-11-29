from adn_v2.models import DefenseEvent, NodeDefenseConfig
from adn_v2.engine import evaluate_defense
from adn_v2.actions import build_rpc_policy_from_state

signals = [
    DefenseEvent(event_type="rpc_abuse", severity=0.7, source="local"),
    DefenseEvent(event_type="sentinel_alert", severity=0.6, source="sentinel"),
]

config = NodeDefenseConfig()
state = evaluate_defense(signals, config)

policy = build_rpc_policy_from_state(state)

print("ADN Defense State:", state)
print("Suggested RPC Policy:", policy)
