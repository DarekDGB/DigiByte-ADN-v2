# DigiByte ADN v2 — Telemetry Flow (Telemetry → Risk → Policy)

This document explains the **telemetry pipeline** inside ADN v2:
how raw data becomes structured telemetry, how it is validated,
and how the system produces **RiskSignals** for the policy engine.

This is the first stage of the ADN v2 node defense pipeline.

---

# 1. Purpose of the Telemetry Flow

The telemetry pipeline performs three jobs:

1. **Normalise raw data** coming from:
   - DigiByte nodes (RPC, metrics, logs)
   - Sentinel AI v2 (Layer 1 signals)
   - Node wrappers or monitoring agents
   - Light clients / sidecar daemons

2. **Derive structured risk indicators** (`RiskSignal` objects).

3. **Feed the policy engine** which produces a `PolicyDecision`.

This keeps the rest of ADN v2 **independent from how data is collected**.

---

# 2. Components

Telemetry flow uses three modules:

### 2.1 TelemetryAdapter (`telemetry.py`)

Converts raw dictionaries into a **TelemetryPacket** dataclass.

Example raw telemetry:

```python
raw = {
    "height": 1200450,
    "mempool_size": 15000,
    "peer_count": 4,
    "cpu_usage": 0.70,
    "timestamp": 1732888000,
}
```

Example packet:

```python
packet = TelemetryPacket(
    node_id="node-a",
    height=1200450,
    mempool_size=15000,
    peer_count=4,
    timestamp=1732888000,
    extra={"cpu_usage": 0.70}
)
```

Anything not explicitly mapped is preserved in `extra`.

---

### 2.2 RiskValidator (`validator.py`)

Consumes `TelemetryPacket` → produces a list of `RiskSignal` objects.

The v2 reference implementation uses **simple heuristics**:

- low peer count → `ELEVATED`
- mempool spike → `HIGH`
- no issues → `NORMAL` baseline

Examples:

```python
RiskSignal(source="telemetry", level=RiskLevel.ELEVATED, ...)
RiskSignal(source="telemetry", level=RiskLevel.HIGH, ...)
RiskSignal(source="telemetry", level=RiskLevel.NORMAL, ...)
```

ADN v2 allows replacing `RiskValidator` with more advanced logic in
future versions (ML detection, anomaly classifiers, etc.).

---

### 2.3 PolicyEngine (`policy.py`)

Takes **all RiskSignals** and computes:

- final `RiskLevel`
- numeric severity score
- reason text
- suggested actions

Example:

```python
decision = PolicyDecision(
    level=RiskLevel.ELEVATED,
    score=0.45,
    reason="Mempool spike + low peers",
    actions=["enter_cooldown"]
)
```

This decision is then handed to:

- `ActionExecutor`
- `NodeState` tracker
- optional RPC policy generation

---

# 3. End-to-End Telemetry Flow

Below is the full pipeline from raw data to actionable defense logic.

```
       Raw Telemetry (dict)
                │
                ▼
       TelemetryAdapter
                │
                ▼
       TelemetryPacket (structured)
                │
                ▼
       RiskValidator
                │
                ├── RiskSignal(level=NORMAL)
                ├── RiskSignal(level=ELEVATED)
                └── RiskSignal(level=HIGH)
                ▼
       PolicyEngine
                │
                ▼
       PolicyDecision(level=..., score=..., reason=...)
                │
                ▼
       ActionExecutor
                │
                ▼
       NodeState(hardened_mode? last_decision?)
```

This is the **core loop** of ADN v2 and represents the majority of
operations in a running node defense instance.

---

# 4. Example: Full Telemetry Evaluation

Example script (included in ADN v2 under `examples/`):

```python
from adn_v2.engine import ADNEngine

engine = ADNEngine(node_id="dgb-node-1")

raw = {
    "height": 1_234_567,
    "mempool_size": 25_000,  # mempool spike
    "peer_count": 1,         # low peers
}

decision = engine.process_raw_telemetry(raw)

print(decision.level)   # CRITICAL or ELEVATED depending on config
print(decision.reason)
print(decision.actions)
```

This demonstrates how the telemetry pipeline reacts to signs of:

- poor connectivity  
- mempool congestion  
- possible attack syndrome  

---

# 5. Integration with Other Shield Layers

Telemetry flow is designed to be compatible with inputs from the full
DigiByte Quantum Shield:

### Layer 1 — Sentinel AI v2
- anomaly flags
- reorg detection
- entropy drop alerts

### Layer 2 — DQSN v2
- global advisory levels
- aggregated ecosystem drift

### Layer 3 — ADN v2 (this repo)
- telemetry → signals → policy
- defense/lockdown logic

### Layer 4 — Guardian Wallet v2
- wallet risk scoring
- withdrawal patterns

### Layer 5 — Quantum Wallet Guard
- advanced wallet protection

### Adaptive Core
- collects TelemetryPacket + RiskSignal history
- learns to refine thresholds over time

Telemetry is the **starting point** for the entire immune system pipeline.

---

# 6. Key Design Goals

- **Separation of concerns** — telemetry separate from validation  
- **Transparency** — simple heuristics easy to review  
- **Modularity** — validators/policies can be replaced  
- **Future-proof** — ML/AI detection can be added without changing API  

---

Author: **DarekDGB**
