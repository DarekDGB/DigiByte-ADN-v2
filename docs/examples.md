# DigiByte ADN v2 — Examples & Usage Guide

This document provides **complete working examples** that demonstrate how
to use the different components of ADN v2:

- Telemetry → Risk → Policy flow  
- DefenseEvent → Lockdown → RPC Policy flow  
- Combined scenarios  

All examples are real code taken from the `examples/` directory.

---

# 1. Telemetry → Policy Flow

This example shows how raw telemetry from a DigiByte node is processed
through the full ADN v2 pipeline.

```python
from adn_v2.engine import ADNEngine

engine = ADNEngine(node_id="dgb-node-1")

raw_telemetry = {
    "height": 1_234_567,
    "mempool_size": 25_000,   # large spike
    "peer_count": 1,          # low connectivity
    "cpu_usage": 0.85,
}

decision = engine.process_raw_telemetry(raw_telemetry)

print("Risk Level:", decision.level)
print("Reason:", decision.reason)
print("Actions:", decision.actions)
print("Hardened Mode:", engine.state.hardened_mode)
```

Expected output (depending on configuration):

```
Risk Level: CRITICAL
Reason: low_peer_count | mempool_spike
Actions: ['enter_cooldown']
Hardened Mode: True
```

---

# 2. Defense Events → Lockdown Flow

Example: combining multiple defense events into a full lockdown.

```python
from adn_v2.models import DefenseEvent, NodeDefenseConfig
from adn_v2.engine import evaluate_defense
from adn_v2.actions import build_rpc_policy_from_state

events = [
    DefenseEvent(event_type="dqsn_critical", severity=0.9, source="dqsn"),
    DefenseEvent(event_type="rpc_abuse", severity=0.85, source="local"),
]

config = NodeDefenseConfig()

state = evaluate_defense(events, config)
policy = build_rpc_policy_from_state(state)

print("Risk Level:", state.risk_level)
print("Lockdown State:", state.lockdown_state)
print("Actions:", [a.action_type for a in state.last_actions])
print("RPC Policy:", policy)
```

Expected output:

```
Risk Level: CRITICAL
Lockdown State: FULL
Actions: ['ENTER_FULL_LOCKDOWN']
RPC Policy: {'rpc_enabled': False, 'rpc_rate_limit': 0, 'notes': ['FULL_LOCKDOWN']}
```

---

# 3. Mixed Telemetry + Defense Scenario

Nodes will often mix both telemetry-based policies and defense events.

Example:

```python
from adn_v2.engine import ADNEngine, evaluate_defense
from adn_v2.models import DefenseEvent, NodeDefenseConfig
from adn_v2.actions import build_rpc_policy_from_state

engine = ADNEngine(node_id="node-x")

# Telemetry signals (moderate risk)
decision = engine.process_raw_telemetry({
    "height": 999999,
    "mempool_size": 22000,
    "peer_count": 2,
})

print("Telemetry Risk:", decision.level)

# Defense layer signals (stronger)
events = [
    DefenseEvent(event_type="sentinel_alert", severity=0.7, source="sentinel"),
    DefenseEvent(event_type="dqsn_critical", severity=0.95, source="dqsn"),
]

state = evaluate_defense(events, NodeDefenseConfig())
policy = build_rpc_policy_from_state(state)

print("Defense Risk:", state.risk_level)
print("Lockdown:", state.lockdown_state)
print("RPC Policy:", policy)
```

This simulates a normal → elevated → full lockdown escalation.

---

# 4. Minimal Example (Quick Start)

If a developer wants to test ADN v2 with just a few lines:

```python
from adn_v2.engine import ADNEngine

engine = ADNEngine("quick-node")

decision = engine.process_raw_telemetry({"peer_count": 1, "mempool_size": 30000})

print(decision)
```

This is the fastest way to evaluate the pipeline.

---

# 5. Using ADN v2 in a Real Node Wrapper

A real node wrapper may do:

```python
import time
from adn_v2.engine import ADNEngine

engine = ADNEngine("real-node-01")

while True:
    raw = collect_metrics_somehow()

    decision = engine.process_raw_telemetry(raw)

    if decision.level.name in ("HIGH", "CRITICAL"):
        log_alert(decision)

    apply_rpc_policy_if_needed(engine.state)

    time.sleep(5)
```

This is how exchanges or node operators integrate ADN v2.

---

Author: **DarekDGB**
