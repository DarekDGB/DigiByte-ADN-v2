# DigiByte Active Defense Network v2 — Overview

The **Active Defense Network v2 (ADN v2)** is Layer 3 of the DigiByte Quantum Shield Network.  
Its purpose is to provide **local, autonomous, real-time defense** for DigiByte full nodes without modifying consensus.

> **Legacy note:** Earlier drafts expanded ADN as “Autonomous Defense Node”.  
> The canonical and correct name is **Active Defense Network**.

## 🚀 Purpose
ADN v2 acts as a **reflex system**:
- Detects abnormal behaviour
- Evaluates risk using defense events and telemetry
- Applies partial/full lockdown policies
- Communicates risk states to upper shield layers

## 🛡 Key Components
### 1. DefenseEvent  
Structured security signals from Sentinel AI, DQSN, Wallet Guard, RPC monitors.

### 2. NodeDefenseState  
Represents current:
- Risk level  
- Lockdown mode  
- Active events  
- Latest ADN actions  

### 3. Defense Decision Engine  
Implements `evaluate_defense(events, config)`:
- Aggregates severity  
- Determines risk  
- Chooses lockdown actions  

### 4. RPC Policy Layer  
Converts defense state → safe RPC policy for gateways.

### 5. Telemetry Flow  
Raw telemetry → TelemetryAdapter → RiskValidator → RiskSignals.

## 📁 Directory Structure
```
src/adn_v2/
    models.py
    engine.py
    actions.py
    telemetry.py
    validator.py
    policy.py
tests/
examples/
docs/
```

## 🔗 Related Documents
- `defense_flow.md` — lockdown logic internals
- `telemetry_flow.md` — telemetry → risk pipeline

Author: **DarekDGB**
