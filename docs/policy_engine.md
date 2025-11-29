# DigiByte ADN v2 — Policy Engine (Risk → Decision Layer)

The **Policy Engine** is the core logic that converts a list of
`RiskSignal` objects into a structured `PolicyDecision`.  
This is the heart of the *Risk → Action* reasoning inside ADN v2.

It sits directly between:

- **RiskValidator** (which produces structured signals)  
- **ActionExecutor** (which applies the chosen decision)  

The Policy Engine does **not** perform any actions itself.  
It decides *what the node SHOULD do*, not *how it does it*.

---

# 1. Purpose of the Policy Engine

The Policy Engine answers one question:

> “Given the current signals, what risk state is the node in,  
>  and what should it do next?”

It evaluates:

- all incoming `RiskSignal` objects  
- their severity scores  
- their source (telemetry, sentinel, dqsn, wallet_guard, etc.)  
- their types (baseline, anomaly, congestion, stall, etc.)

And produces a final **PolicyDecision**, which includes:

### Decision Fields
- **RiskLevel** (`NORMAL`, `ELEVATED`, `HIGH`, `CRITICAL`)
- **Final score** (0.0 → 1.0)
- **Reason string** (developer readable)
- **Suggested actions** (optional list of strings)

This output feeds directly into:

- the `ActionExecutor`
- the `NodeState`
- the defense/lockdown engine (Layer 3)
- eventual RPC lockdown policies

---

# 2. Input: RiskSignal Objects

The Policy Engine receives signals like:

```python
RiskSignal(
    source="telemetry",
    level=RiskLevel.ELEVATED,
    score=0.6,
    details={"reason": "low_peer_count"},
)
```

Each signal carries:

- a **risk level**
- a **score** (severity)
- optional **details** (reason metadata)

In ADN v2 these signals come from:

- TelemetryAdapter + RiskValidator  
- Sentinel AI v2  
- DQSN v2  
- Wallet Guard v2  
- Node-side heuristics  

---

# 3. How the Policy Engine Works

The v2 reference implementation uses a **simple reduction model**:

### Step 1 — Combine severity scores
```python
total_score = sum(signal.score for signal in signals)
final_score = total_score / len(signals)
```

### Step 2 — Determine final RiskLevel
Based on the final_score:

- `< 0.3` → NORMAL  
- `< 0.6` → ELEVATED  
- `< 0.8` → HIGH  
- `>= 0.8` → CRITICAL  

These values are intentionally conservative and can be replaced by
node operators or future v3 modules.

### Step 3 — Build a human-readable reason
The Policy Engine concatenates all “reason” fields from signals:

Example:
```
Reasons:
- low_peer_count
- mempool_spike
```

Final reason string:
```
"low_peer_count | mempool_spike"
```

### Step 4 — Suggest actions
Actions are NOT applied here — only suggested.

Example actions:
- `"enter_cooldown"`
- `"enable_logging"`
- `"lockdown_trigger"`

These string values are meaningful to:
- node wrappers  
- orchestrators  
- RPC gateways  
- higher layers in the shield  

---

# 4. Output: PolicyDecision

Example:

```python
PolicyDecision(
    level=RiskLevel.HIGH,
    score=0.72,
    reason="low_peer_count | mempool_spike",
    actions=["enter_cooldown"],
)
```

The decision is then handed to the `ActionExecutor`:

```python
action_executor.execute(decision, context)
```

The node’s `NodeState` is updated automatically.

---

# 5. Visual Flow Diagram

```
      RiskSignal[*]
            │
            ▼
      ┌──────────────┐
      │ PolicyEngine │
      └──────────────┘
            │
            ▼
  ┌──────────────────────┐
  │   PolicyDecision     │
  │   level = CRITICAL   │
  │   score = 0.81       │
  │   reason = "... ..." │
  └──────────────────────┘
            │
            ▼
     ActionExecutor
            │
            ▼
       NodeState
```

---

# 6. Integration with Defense Engine

The Policy Engine handles **risk logic**, while the defense engine handles
**lockdown logic**.

Flow:

```
Telemetry → RiskSignals → PolicyEngine → Decision → NodeState
                                             │
                                             ▼
                            DefenseEvent(source="adn_policy")
                                             │
                                             ▼
                             evaluate_defense(events)
```

This allows PolicyEngine to supply **early defensive signals** to the
lockdown engine (PARTIAL / FULL).

---

# 7. Extensibility

The Policy Engine was designed to be replaced easily.

You can plug in:

- machine-learning anomaly classifiers  
- advanced multi-source scoring  
- cost/benefit risk models  
- time-based hysteresis logic  
- economic sensitivity scoring  
- DQSN + Adaptive Core weighted overlays  

as long as the new engine returns a:

```python
PolicyDecision
```

with the same fields.

---

# 8. Minimal Example

```python
from adn_v2.policy import PolicyEngine
from adn_v2.models import RiskSignal, RiskLevel

signals = [
    RiskSignal("telemetry", RiskLevel.ELEVATED, 0.6, {"reason": "low_peers"}),
    RiskSignal("telemetry", RiskLevel.HIGH,     0.8, {"reason": "mempool_spike"}),
]

engine = PolicyEngine()
decision = engine.decide(signals)

print(decision.level)     # CRITICAL
print(decision.reason)    # "low_peers | mempool_spike"
print(decision.actions)   # ["enter_cooldown"]
```

---

Author: **DarekDGB**
