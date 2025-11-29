# DigiByte ADN v2 — Defense Flow (Lockdown Engine)

This document explains how the **v2 defense engine** in ADN works:
how it consumes `DefenseEvent` objects, updates `NodeDefenseState`,
and produces lockdown actions and RPC policies.

It is focused on the function:

```python
from adn_v2.engine import evaluate_defense
```

and the helper:

```python
from adn_v2.actions import build_rpc_policy_from_state
```

---

## 1. Core Concepts

### 1.1 DefenseEvent

A `DefenseEvent` is a single piece of structured security context.

Examples:

- `event_type="rpc_abuse"` – local RPC is being hammered  
- `event_type="sentinel_alert"` – Sentinel AI flagged anomaly  
- `event_type="dqsn_critical"` – DQSN reports global critical state  

Each event carries:

- `event_type: str` – human-readable label for the incident
- `severity: float` (0.0 – 1.0) – how bad this looks
- `source: str` – where it came from (`local`, `sentinel`, `dqsn`, `wallet_guard`, etc.)
- `metadata: dict` – optional extra detail (IP, advisory text, etc.)

ADN v2 does **not** prescribe exact event types; projects can define
their own as long as they map to a severity score.

---

### 1.2 NodeDefenseConfig

Configuration knobs for the defense engine:

- `partial_lock_threshold: float`  
  - average severity at which PARTIAL lockdown begins

- `lockdown_threshold: float`  
  - average severity at which FULL lockdown is entered

- `max_withdrawals_per_min`, `rpc_rate_limit`, etc.  
  - future expansion for wallet / RPC behaviour

These defaults are intentionally conservative and illustrative; they
should be tuned by node operators and DigiByte devs based on real-world
data and risk appetite.

---

### 1.3 NodeDefenseState

The defense state tracks:

- `risk_level: RiskLevel`  
  - `NORMAL`, `ELEVATED`, `HIGH`, `CRITICAL`

- `lockdown_state: LockdownState`  
  - `NONE`, `PARTIAL`, `FULL`

- `active_events: List[DefenseEvent]`  
  - all events currently considered relevant

- `last_actions: List[DefenseAction]`  
  - actions produced by the last call to `evaluate_defense`

This makes the defense engine **stateful** but easy to reason about:
each call to `evaluate_defense` updates and returns a new state snapshot.

---

## 2. The `evaluate_defense` Function

Signature:

```python
def evaluate_defense(
    events: List[DefenseEvent],
    config: Optional[NodeDefenseConfig] = None,
    state: Optional[NodeDefenseState] = None,
) -> NodeDefenseState:
```

### 2.1 Inputs

- `events` – new DefenseEvent objects to process
- `config` – optional tuning parameters (uses defaults if `None`)
- `state` – existing NodeDefenseState (if `None`, a fresh one is created)

### 2.2 Behaviour (step-by-step)

1. **Initialise config and state**  
   - If no config is provided, `NodeDefenseConfig()` is used.  
   - If no state is provided, `NodeDefenseState()` is used.

2. **Handle empty events**  
   - If `events` is empty:
     - `state.last_actions` is cleared
     - the state is returned unchanged
   - This allows periodic “no-op” evaluations that keep the defense
     picture stable unless something new happens.

3. **Merge events**  
   - All incoming `events` are appended to `state.active_events`.
   - No deduplication is done by default; this is a **reference
     implementation**, and production code is expected to apply its
     own retention and cleanup logic.

4. **Compute aggregate severity**  
   - For all `state.active_events`, a simple average of `severity`
     is computed:
     ```python
     severities = [e.severity for e in state.active_events]
     avg_severity = sum(severities) / len(severities)
     ```

5. **Determine RiskLevel**  
   - If `avg_severity >= lockdown_threshold` → `RiskLevel.CRITICAL`
   - Else if `avg_severity >= partial_lock_threshold` → `RiskLevel.ELEVATED`
   - Else → `RiskLevel.NORMAL`

   (Note: `RiskLevel.HIGH` is kept for extension but not used in this
   minimal v2 reference flow.)

6. **Determine LockdownState and DefenseAction list**

   - If risk is `CRITICAL`:
     - If previous `lockdown_state` is not FULL:
       - set `lockdown_state=FULL`
       - append `DefenseAction("ENTER_FULL_LOCKDOWN", reason=...)`
   - If risk is `ELEVATED`:
     - If previous `lockdown_state` is NONE:
       - set `lockdown_state=PARTIAL`
       - append `DefenseAction("ENTER_PARTIAL_LOCKDOWN", reason=...)`
   - If risk is `NORMAL`:
     - If previous `lockdown_state` was PARTIAL or FULL:
       - append `DefenseAction("LIFT_LOCKDOWN", reason="risk back to NORMAL")`
       - set `lockdown_state=NONE`

7. **Return updated state**  
   - `state.last_actions` is set to the newly generated list.
   - The whole `NodeDefenseState` is returned.

---

## 3. RPC Policy Mapping

The defense engine itself does not directly manipulate RPC endpoints.
Instead, it provides a clean API for generating policies.

Helper function:

```python
from adn_v2.actions import build_rpc_policy_from_state

policy = build_rpc_policy_from_state(state)
```

### 3.1 Example Output

- For `LockdownState.NONE`:

```jsonc
{
  "rpc_enabled": true,
  "rpc_rate_limit": null,
  "notes": ["NORMAL"]
}
```

- For `LockdownState.PARTIAL`:

```jsonc
{
  "rpc_enabled": true,
  "rpc_rate_limit": 100,
  "notes": ["PARTIAL_LOCKDOWN"]
}
```

- For `LockdownState.FULL`:

```jsonc
{
  "rpc_enabled": false,
  "rpc_rate_limit": 0,
  "notes": ["FULL_LOCKDOWN"]
}
```

These policies are small, serialisable, and easy to apply in:

- JSON-based node configs
- sidecar daemons
- RPC gateways
- reverse proxies or firewalls

---

## 4. Example Flows

### 4.1 Partial Lockdown Scenario

**Events:**

- `rpc_abuse` from local (severity 0.6)
- `sentinel_alert` from Sentinel AI v2 (severity 0.5)

These are strong but not catastrophic signals.

Flow:

```python
events = [
    DefenseEvent(event_type="rpc_abuse", severity=0.6, source="local"),
    DefenseEvent(event_type="sentinel_alert", severity=0.5, source="sentinel"),
]

state = evaluate_defense(events, NodeDefenseConfig())
policy = build_rpc_policy_from_state(state)
```

Expected behavior:
- `risk_level` → `ELEVATED`
- `lockdown_state` → `PARTIAL`
- RPC still enabled, but throttled
- policy notes mention `"PARTIAL_LOCKDOWN"`

### 4.2 Full Lockdown Scenario

**Events:**

- `dqsn_critical` from DQSN (severity 0.9)
- `rpc_abuse` from local (severity 0.85)

Flow:

```python
events = [
    DefenseEvent(event_type="dqsn_critical", severity=0.9, source="dqsn"),
    DefenseEvent(event_type="rpc_abuse", severity=0.85, source="local"),
]

state = evaluate_defense(events, NodeDefenseConfig())
policy = build_rpc_policy_from_state(state)
```

Expected behavior:
- `risk_level` → `CRITICAL`
- `lockdown_state` → `FULL`
- `last_actions` includes `"ENTER_FULL_LOCKDOWN"`
- RPC disabled in resulting policy

---

## 5. Integration Points

Defense events can be generated by:

- Sentinel AI v2 (Layer 1)
- DQSN v2 (Layer 2)
- Guardian Wallet v2 (Layer 4)
- Quantum Wallet Guard (Layer 5)
- node-local logic (RPC logs, rate limits, etc.)

The defense engine is designed to be **chain-agnostic** and reusable.

Other UTXO chains can adopt this pattern by:

- defining their own `DefenseEvent` types
- tuning the thresholds in `NodeDefenseConfig`
- implementing chain-specific policy builders on top of
  `NodeDefenseState`.

---

Author: **DarekDGB**
