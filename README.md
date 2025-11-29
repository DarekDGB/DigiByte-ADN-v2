# 🛡 DigiByte Autonomous Defense Node v2 (ADN v2)

Status: **v2 reference implementation – experimental**

### *Layer 3 — Node-Level Reflex & Lockdown Engine*

## 1. Project Intent

ADN v2 is **not** a consensus or wallet implementation.  
It is a **node-side defense layer** that sits *next to* a DigiByte full node
and makes **local protection decisions** based on telemetry and security
signals.

Where Sentinel AI v2 and DQSN v2 focus on *detection* and *network-wide scoring*,
**ADN v2 is the reflex system**:

- receives signals about abnormal behaviour (RPC abuse, Sentinel alerts, DQSN critical events, wallet spikes)  
- evaluates local risk  
- decides how hard the node should defend itself  
- suggests a concrete **RPC lockdown / throttling policy**

All upgrades to DigiByte consensus, mining rules, and cryptography remain the
responsibility of **DigiByte Core (C++)** and the wider community.  
ADN v2 is an **external defense controller**, not a hard fork.

---

## 2. High-Level Architecture (v2)

ADN v2 is built as a simple, testable pipeline:

1. **Telemetry Adapter**
   - converts raw node stats into a `TelemetryPacket`
   - fields like: height, mempool size, peer count, timestamp, extra

2. **Risk Validator (v2)**
   - converts `TelemetryPacket` → one or more `RiskSignal` objects  
   - very simple heuristics in v2 (low peers, large mempool = higher risk)  
   - designed to be extended with more advanced logic later

3. **Policy Engine**
   - reads the list of `RiskSignal` instances  
   - chooses a `PolicyDecision` (risk level, score, actions)  
   - v2 focuses on mapping risk → lockdown choices

4. **Action Executor**
   - turns `PolicyDecision` into side effects  
   - in this reference repo it *only* updates in-memory state and returns a dict  
   - production implementations could wire this to:
     - RPC access control
     - firewall rules
     - withdrawal throttling
     - admin alerts / dashboards

5. **Defense Engine (v2)**
   - a focused path used by the new tests:
     - list of `DefenseEvent` → updated `NodeDefenseState`
     - state carries:
       - `risk_level`
       - `lockdown_state`
       - `active_events`
       - `last_actions`

---

## 3. v2 Defense Models

Key dataclasses and enums for the new defense flow:

- `RiskLevel` — `NORMAL`, `ELEVATED`, `HIGH`, `CRITICAL`
- `LockdownState` — `NONE`, `PARTIAL`, `FULL`
- `DefenseEvent` — single event like:
  - `rpc_abuse`
  - `sentinel_alert`
  - `dqsn_critical`
- `NodeDefenseConfig` — thresholds and knobs:
  - `partial_lock_threshold`
  - `lockdown_threshold`
  - RPC rate limit hints
- `DefenseAction` — what ADN *decides* to do:
  - `ENTER_PARTIAL_LOCKDOWN`
  - `ENTER_FULL_LOCKDOWN`
  - `LIFT_LOCKDOWN`
- `NodeDefenseState` — current view of the node:
  - `risk_level`
  - `lockdown_state`
  - `active_events`
  - `last_actions`

Older code that imported `RiskState` is kept working via a small compatibility
alias inside `models.py`.

---

## 4. Defense Engine Flow

The main v2 helper is:

```python
from adn_v2.engine import evaluate_defense
```

Usage pattern:

1. Collect security events from local logic, Sentinel AI v2, DQSN v2, or wallet guardians.
2. Build a list of `DefenseEvent` objects.
3. Call `evaluate_defense(events, config, state)`.

The function:

- merges events into `state.active_events`
- computes an average severity
- maps that to a `RiskLevel`
- sets `lockdown_state` according to thresholds
- produces `DefenseAction` entries in `state.last_actions`

Example thresholds:

- severity ≥ `lockdown_threshold` → `CRITICAL` + `FULL` lockdown
- severity ≥ `partial_lock_threshold` → `ELEVATED` + `PARTIAL` lockdown
- else → `NORMAL` + no lockdown

---

## 5. RPC Policy Builder

ADN v2 exposes a small helper to convert defense state into a simple policy dict:

```python
from adn_v2.actions import build_rpc_policy_from_state
```

The returned dict is **intentionally minimal**:

```python
{
    "rpc_enabled": bool,
    "rpc_rate_limit": Optional[int],
    "notes": List[str],
}
```

Example mapping:

- `LockdownState.NONE`
  - `rpc_enabled = True`
  - `rpc_rate_limit = None`
  - `notes = ["NORMAL"]`

- `LockdownState.PARTIAL`
  - `rpc_enabled = True`
  - `rpc_rate_limit = 100`
  - `notes = ["PARTIAL_LOCKDOWN"]`

- `LockdownState.FULL`
  - `rpc_enabled = False`
  - `rpc_rate_limit = 0`
  - `notes = ["FULL_LOCKDOWN"]`

This makes it easy for node operators, dashboards, or wrapper scripts to apply
the right RPC constraints based on ADN’s decision.

---

## 6. Functional Testing (v2)

To answer the “Where is the functional testing?” question — ADN v2 now includes:

- ✅ unit tests for import layout (`tests/test_imports.py`)
- ✅ unit tests for basic policy logic (`tests/basic_policy.py`)
- ✅ **new functional defense test** (`tests/test_defense_engine.py`)

The functional test covers:

- partial lockdown scenario (Sentinel + local RPC abuse)
- full lockdown scenario (DQSN critical + local abuse)
- expectations on:
  - `risk_level`
  - `lockdown_state`
  - resulting RPC policy (`rpc_enabled`, `rpc_rate_limit`, `"LOCKDOWN"` markers)

Tests are run automatically in CI on every push via GitHub Actions.

---

## 7. Example: Minimal Defense Flow

The following example shows how to wire a simple defense flow:

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

You can place this as `examples/example_adn_flow.py` or adapt it into your own
node orchestration scripts.

---

## 8. Role Inside the 5-Layer Quantum Shield

ADN v2 is **Layer 3** of the DigiByte Quantum Shield:

1. **Sentinel AI v2** — detects anomalies at node level.
2. **DQSN v2** — aggregates risk across many nodes and chains.
3. **ADN v2** — this repo; applies node-level defense and lockdown.
4. **Guardian Wallet v2** — applies protections on withdrawals and UTXOs.
5. **Quantum Wallet Guard** — future hardening for wallet key use.

ADN v2 listens “upwards” to Sentinel + DQSN and pushes decisions “downwards”
toward the wallet and RPC layer.

It is deliberately **modular** so other UTXO chains can reuse or adapt the same
patterns for their own defense logic.

---

## 9. Non‑Goals & Limitations

ADN v2 does **not**:

- modify DigiByte consensus rules
- change mining difficulty or algorithms
- sign transactions or hold private keys
- guarantee perfect security

It is a **reference defense controller** and a **blueprint** for how a node
could react to different threat levels, not a finished production product.

---

## 10. License & Attribution

This repository is released under the **MIT License** (see `LICENSE` file).

Core architecture, defense flow, and documentation were designed and authored by:

- **DarekDGB**

Contributions, forks, and adaptations for other PoW chains are welcome, as long
as the MIT terms are respected and attribution is preserved where appropriate.
