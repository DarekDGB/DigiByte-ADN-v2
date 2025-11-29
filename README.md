# 🛡 DigiByte Autonomous Defense Node v2 (ADN v2)

Status: **v2 reference implementation – experimental**

### *Layer 3 — Node-Level Reflex & Lockdown Engine*

## 1. Project Intent

ADN v2 is **not** a consensus or wallet implementation.  
It is a **node-side defense layer** that sits *next to* a DigiByte full node and makes **local protection decisions** based on telemetry and security signals.

Where Sentinel AI v2 and DQSN v2 focus on *detection* and *network-wide scoring*,  
**ADN v2 is the reflex system**:

- receives signals about abnormal behaviour (RPC abuse, Sentinel alerts, DQSN critical events, wallet spikes)  
- evaluates local risk  
- decides how hard the node should defend itself  
- suggests a concrete **RPC lockdown / throttling policy**

All upgrades to DigiByte consensus, mining rules, and cryptography remain the responsibility of **DigiByte Core (C++)** and the wider community.  
ADN v2 is an **external defense controller**, not a hard fork.

---

## 2. High-Level Architecture (v2)

ADN v2 is built as a simple, testable pipeline:

### **1. Telemetry Adapter**
- Converts raw node stats into a `TelemetryPacket`
- Fields: height, mempool size, peer count, timestamp, extra

### **2. Risk Validator (v2)**
- Converts `TelemetryPacket` → list of `RiskSignal` objects  
- Simple v2 heuristics (low peers, large mempool = higher risk)

### **3. Policy Engine**
- Reads `RiskSignal` entries  
- Produces a `PolicyDecision` (risk level, score, actions)

### **4. Action Executor**
- Translates `PolicyDecision` into side effects  
- Reference repo: only updates in-memory state  
- Production examples: RPC firewall, cooldowns, alerts, dashboards

### **5. Defense Engine (v2)**
- Secure-event pipeline:
  - input: list of `DefenseEvent`
  - output: updated `NodeDefenseState`
  - state includes:
    - `risk_level`
    - `lockdown_state`
    - `active_events`
    - `last_actions`

---

## 3. v2 Defense Models

Core dataclasses and enums:

- **RiskLevel** — `NORMAL`, `ELEVATED`, `HIGH`, `CRITICAL`
- **LockdownState** — `NONE`, `PARTIAL`, `FULL`
- **DefenseEvent** — e.g. `rpc_abuse`, `sentinel_alert`, `dqsn_critical`
- **NodeDefenseConfig** — thresholds and knobs  
- **DefenseAction** — `ENTER_PARTIAL_LOCKDOWN`, `ENTER_FULL_LOCKDOWN`, `LIFT_LOCKDOWN`
- **NodeDefenseState** — node risk, lockdown mode, events, actions

Legacy `RiskState` remains supported through a compatibility alias.

---

## 4. Defense Engine Flow

Main function:

```python
from adn_v2.engine import evaluate_defense
```

Process:

1. Collect events
2. Evaluate with `evaluate_defense`
3. Update node defense state
4. Produce actions + lockdown mode

Severity → lockdown mapping:

- `>= lockdown_threshold` → `CRITICAL` + **FULL lockdown**
- `>= partial_lock_threshold` → `ELEVATED` + **PARTIAL lockdown**
- otherwise → `NORMAL`

---

## 5. RPC Policy Builder

Helper:

```python
from adn_v2.actions import build_rpc_policy_from_state
```

Returns:

```python
{
    "rpc_enabled": bool,
    "rpc_rate_limit": Optional[int],
    "notes": List[str],
}
```

Examples:

| Lockdown | rpc_enabled | rate_limit | notes |
|---------|-------------|------------|--------|
| NONE | True | None | NORMAL |
| PARTIAL | True | 100 | PARTIAL_LOCKDOWN |
| FULL | False | 0 | FULL_LOCKDOWN |

---

## 6. Functional Testing (v2)

CI includes:

- ✔ import tests  
- ✔ basic policy tests  
- ✔ **functional defense engine test**  
  - partial lockdown  
  - full lockdown  
  - policy correctness  

Runs automatically via GitHub Actions.

---

## 7. Example: Minimal Defense Flow

```python
from adn_v2.models import DefenseEvent, NodeDefenseConfig
from adn_v2.engine import evaluate_defense
from adn_v2.actions import build_rpc_policy_from_state

events = [
    DefenseEvent(event_type="rpc_abuse", severity=0.7, source="local"),
    DefenseEvent(event_type="sentinel_alert", severity=0.6, source="sentinel"),
]

config = NodeDefenseConfig()
state = evaluate_defense(events, config)

policy = build_rpc_policy_from_state(state)

print("ADN Defense State:", state)
print("Suggested RPC Policy:", policy)
```

---

## 8. Role Inside the 5-Layer Quantum Shield

ADN v2 = **Layer 3**:

1. Sentinel AI v2 — detection  
2. DQSN v2 — global scoring  
3. **ADN v2 — reflex & lockdown**  
4. Guardian Wallet v2 — withdrawal / UTXO protections  
5. Quantum Wallet Guard — future wallet hardening  

ADN v2 listens upward and defends downward.

---

## 9. Non‑Goals

ADN v2 does **not**:

- alter consensus
- change block validation rules
- manage private keys
- guarantee complete security

It is a **reference defense module** for nodes.

---

## 10. License & Attribution

Released under the **MIT License**.

**Author: DarekDGB**

Adaptations, forks, and downstream implementations for other blockchains are welcome under MIT terms.
