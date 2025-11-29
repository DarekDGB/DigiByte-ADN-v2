# DigiByte Autonomous Defense Node v2 (ADN v2)
## Architecture & Flow

> **Layer 3 – Autonomous Defense Node in the DigiByte Quantum Shield**  
> Repository: `DigiByte-ADN-v2`  
> Status: **v2 experimental, reference-only**

This document explains how ADN v2 is structured internally and how the main
components work together to provide **local, automated defense** for DigiByte
nodes and connected infrastructure.

---

## 1. High-Level Responsibilities

ADN v2 is a **local defense brain** that sits next to a DigiByte node.

It has three main jobs:

1. **Ingest telemetry & alerts**  
   - from the local node (RPC / logs / metrics)
   - from Sentinel AI v2 (Layer 1 detection)
   - from DQSN v2 (Layer 2 network advisory)
   - from wallet-side guardians (withdrawal patterns, UTXO risk, etc.)

2. **Decide appropriate defense posture**  
   - derive **RiskSignal** entries from telemetry  
   - compute a **PolicyDecision** (is the node at risk?)  
   - update **NodeDefenseState** with `RiskLevel` + `LockdownState`

3. **Apply safe, local actions**  
   - suggest **RPC throttling / lockdown policies**  
   - mark the node as “hardened” under critical conditions  
   - emit **DefenseEvent** objects that can be consumed by DQSN v2
     and the Adaptive Core (Layer 6, immune system).

ADN v2 does **not** touch consensus or private keys. It is purely a
**defense automation and signalling layer**.

---

## 2. Core Modules

ADN v2 is implemented under `src/adn_v2/` and is split into small,
testable modules.

### 2.1 Models (`models.py`)

Defines all core dataclasses and enums used across the engine:

- `RiskLevel` – coarse risk classification used everywhere:
  - `NORMAL`, `ELEVATED`, `HIGH`, `CRITICAL`
- `RiskState` – backwards-compatible alias for `RiskLevel`
- `RiskSignal` – a single risk observation:
  - `source`, `level`, `score`, `details`
- `TelemetryPacket` – normalised node telemetry:
  - `node_id`, `height`, `mempool_size`, `peer_count`, `timestamp`, `extra`
- `PolicyDecision` – output of the risk → policy pipeline:
  - `level`, `score`, `reason`, `actions`
- `NodeState` – minimal running state for the ADN engine:
  - `node_id`, `hardened_mode`, `last_decision`
- `ActionResult` – placeholder for future side-effect reporting

Defense-layer models:

- `LockdownState` – local defense posture:
  - `NONE`, `PARTIAL`, `FULL`
- `DefenseEvent` – high-level defense signal:
  - `event_type`, `severity`, `source`, `metadata`
- `NodeDefenseConfig` – tuning knobs for defense behaviour:
  - `lockdown_threshold`, `partial_lock_threshold` etc.
- `DefenseAction` – proposed defense step, such as:
  - `ENTER_PARTIAL_LOCKDOWN`, `ENTER_FULL_LOCKDOWN`, `LIFT_LOCKDOWN`
- `NodeDefenseState` – defense view of the node:
  - `risk_level`, `lockdown_state`, `active_events`, `last_actions`

These models are intentionally small so they can be reused in other
implementations or extended by downstream projects.

---

### 2.2 Telemetry Adapter (`telemetry.py`)

**Class:** `TelemetryAdapter`

Responsibility: convert a **raw dict** of metrics into a
`TelemetryPacket`:

```python
packet = TelemetryAdapter().from_raw(node_id, raw_metrics)
```

Typical raw metrics might include:

- `height`
- `mempool_size`
- `peer_count`
- optional extras (latency, CPU usage, RPC stats, etc.)

Any unknown keys are stored in `TelemetryPacket.extra` so that future
validators or adaptive logic can still inspect them.

This keeps the engine independent from *how* the data was collected
(Prometheus, direct RPC, log-scraping, etc.).

---

### 2.3 Risk Validator (`validator.py`)

**Class:** `RiskValidator`

Responsibility: inspect a `TelemetryPacket` and emit one or more
`RiskSignal` entries.

The v2 reference implementation is deliberately simple:

- low peer count → `RiskLevel.ELEVATED`
- large mempool spike → `RiskLevel.HIGH`
- otherwise → `RiskLevel.NORMAL`

Projects embedding ADN v2 can replace `RiskValidator` with a more
sophisticated implementation (machine learning, heuristics, etc.)
without changing the rest of the pipeline.

---

### 2.4 Policy Engine (`policy.py`)

**Class:** `PolicyEngine`

Responsibility: convert `List[RiskSignal]` into a `PolicyDecision`.

The v2 engine performs a minimal reduction over all signals:

- combines severity into a simple numeric score  
- determines a final `RiskLevel`  
- records a human-readable `reason` and optional `actions` list

The exact scoring logic is intentionally light so that other chains
or operators can specialise it for their own risk appetite.

---

### 2.5 Actions & RPC Policy (`actions.py`)

**Key pieces:**

- `ActionExecutor` – attaches the `PolicyDecision` into the runtime
  context and marks a node as **“hardened”** when risk is critical.
- `build_rpc_policy_from_state(NodeDefenseState)` – converts a defense
  state into a JSON-style RPC policy object:

```jsonc
{
  "rpc_enabled": true | false,
  "rpc_rate_limit": 100,   // or None for normal
  "notes": ["PARTIAL_LOCKDOWN"]
}
```

This helper is meant for:

- gateways
- orchestrators
- node wrappers

It lets them implement **RPC throttling / lockdown** without needing
to understand the full defense model.

---

### 2.6 Engine (`engine.py`)

**Class:** `ADNEngine`

This is the **runtime orchestrator**:

1. Accepts raw telemetry via `process_raw_telemetry(...)`
2. Uses `TelemetryAdapter` to build a `TelemetryPacket`
3. Feeds the packet into `RiskValidator` → `List[RiskSignal]`
4. Runs `PolicyEngine.decide(...)` → `PolicyDecision`
5. Passes the decision into `ActionExecutor.execute(...)`
6. Updates internal `NodeState`:
   - `hardened_mode` flag
   - `last_decision` snapshot

The engine is intentionally small and composable: each dependency
(validator, policy_engine, action_executor, telemetry_adapter) can
be swapped out in integration tests or production deployments.

---

### 2.7 Defense Decision Engine (`evaluate_defense` in `engine.py`)

In addition to the main pipeline, ADN v2 exposes a dedicated
**defense engine**:

```python
from adn_v2.engine import evaluate_defense

state = evaluate_defense(events, config, state)
```

- Input: `List[DefenseEvent]` + optional `NodeDefenseConfig` and
  existing `NodeDefenseState`.
- Output: updated `NodeDefenseState` with:
  - new `risk_level`
  - updated `lockdown_state`
  - appended `active_events`
  - fresh `last_actions` list

The v2 logic is simple but expressive:

- **Average severity** across events is computed.
- If it crosses `lockdown_threshold` → `CRITICAL` + `FULL` lockdown.
- If it crosses `partial_lock_threshold` → `ELEVATED` + `PARTIAL` lockdown.
- If it drops back to normal → lockdown is lifted.

This function is the main bridge into:

- **guardian wallets / RPC gateways** (via `build_rpc_policy_from_state`)  
- **DQSN v2** and the **Adaptive Core**, which can consume `DefenseEvent`
  streams for higher-level learning.

---

## 3. End-to-End Flow

Below is a simplified ADN v2 lifecycle for a single node.

### 3.1 Telemetry → Policy

```text
[raw metrics] ──▶ TelemetryAdapter ──▶ TelemetryPacket
                             │
                             ▼
                     RiskValidator
                             │
                             ▼
                       RiskSignal[*]
                             │
                             ▼
                       PolicyEngine
                             │
                             ▼
                      PolicyDecision
                             │
                             ▼
                      ActionExecutor
                             │
                             ▼
                        NodeState
```

### 3.2 Defense Events → Lockdown

```text
[DefenseEvent[*]] ──▶ evaluate_defense(...) ──▶ NodeDefenseState
                                                  │
                                                  ▼
                                 build_rpc_policy_from_state(...)
                                                  │
                                                  ▼
                                          RPC / gateway layer
```

Sentinel AI v2, DQSN v2, guardian wallets and the Adaptive Core can
all be sources of `DefenseEvent` objects, allowing a **shared local
language** for “what is going wrong and how severe it is”.

---

## 4. Position in the Quantum Shield

Within the **5-layer DigiByte Quantum Shield** (plus Adaptive Core),
ADN v2 plays the **Layer 3** role:

1. **Layer 1 – Sentinel AI v2**  
   - detects anomalies at node / chain level.

2. **Layer 2 – DQSN v2**  
   - aggregates risk signals across many nodes and infra sources.

3. **Layer 3 – ADN v2 (this repo)**  
   - applies **local defense logic** at each node:
     - decides lockdown / throttling  
     - emits structured DefenseEvents
     - marks nodes as hardened when needed

4. **Layer 4 – Guardian Wallet v2**  
   - enforces wallet-side protections built on top of ADN decisions.

5. **Layer 5 – Quantum Wallet Guard**  
   - future-facing wallet protection against advanced / quantum threats.

6. **Adaptive Core (immune system)**  
   - learns from all layers over time and refines rules, thresholds,
     and policies.

ADN v2 is intentionally **modular and replaceable**: networks can adopt
only the pieces they want, or use this repo as a starting point to build
their own chain-specific defense automation.

---

## 5. Testing & CI Integration

ADN v2 includes a small but meaningful test suite under `tests/`:

- `test_imports.py` – basic sanity imports for the package.
- `basic_policy.py` – legacy policy tests kept for reference.
- `test_defense_engine.py` – v2 functional tests:
  - partial lockdown scenario
  - full lockdown scenario

GitHub Actions run `pytest -v` on every push to `main`, so contributors
can see immediately if a change breaks the v2 reference behaviour.

---

## 6. Design Principles

ADN v2 follows a few guiding principles:

- **Separation of concerns** – telemetry, validation, policy, actions,
  and defense events are split into distinct, focused modules.
- **Replaceable pieces** – operators can plug in their own validator,
  policy engine, or action executor without touching the rest.
- **Explainability** – risk, decisions and actions are surfaced via
  small, clear dataclasses that can be logged or exported.
- **Non-invasive** – ADN v2 does not touch consensus or private keys; it
  only suggests node / RPC behaviour and emits defense signals.

This makes ADN v2 a safe **experimental sandbox** for building local
defense automation around DigiByte and other UTXO-based chains.
