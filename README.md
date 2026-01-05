# ⚔️ ADN v3 — Active Defence Network
### *Deterministic Local Defence Engine of the DigiByte Quantum Shield*
**Architecture by @DarekDGB — MIT Licensed**

---

## 🚀 Purpose

**ADN v3 (Active Defence Network)** is the **deterministic local defence engine**
of the DigiByte Quantum Shield.

It represents the evolution from *tactical advisory concepts* (v2)
into a **codified, testable, policy‑driven defence runtime**.

Where:

- **DQSN v2** observes network‑wide entropy and health
- **Sentinel AI v2** detects anomalies and produces threat signals

**ADN v3** enforces **local defensive decisions** in a strict, deterministic flow.

ADN v3 remains **consensus‑neutral**:
it never modifies DigiByte protocol rules and never signs transactions.
It only governs **local node and wallet behaviour**.

---

# 🛡️ Position in the DigiByte Quantum Shield

```
 ┌───────────────────────────────────────────────┐
 │           Guardian Wallet v2                  │
 │  User‑side policy enforcement                 │
 └───────────────────────────────────────────────┘
                     ▲
                     │   (defence constraints)
 ┌───────────────────────────────────────────────┐
 │        Quantum Wallet Guard (QWG)             │
 │  Runtime tx / key safety                      │
 └───────────────────────────────────────────────┘
                     ▲
                     │   (execution gating)
 ┌───────────────────────────────────────────────┐
 │                ADN v3                         │
 │  Deterministic defence engine                 │
 │  Policy → Lockdown → Enforcement              │
 └───────────────────────────────────────────────┘
                     ▲
                     │   (risk signals)
 ┌───────────────────────────────────────────────┐
 │            Sentinel AI v2                     │
 │  Anomaly & threat detection                   │
 └───────────────────────────────────────────────┘
                     ▲
                     │   (raw telemetry)
 ┌───────────────────────────────────────────────┐
 │               DQSN v2                         │
 │  Network entropy & health                     │
 └───────────────────────────────────────────────┘
```

---

# 🎯 Core Mission (v3)

### ✓ Deterministic Defence Decisions
ADN v3 converts telemetry and threat signals into **repeatable,
test‑verified defence outcomes**.

Same inputs → same decisions → same actions.

### ✓ Enforced Defence States
ADN v3 produces explicit, machine‑readable states:

- `RiskLevel`
- `LockdownState`
- `DefenseAction`

These states can be consumed by:
- nodes
- RPC gateways
- wallet guards
- orchestration tooling

### ✓ Local Autonomy, Global Awareness
Each ADN v3 instance acts **locally**,
while remaining compatible with network‑level intelligence
from Sentinel AI and DQSN.

### ✓ Zero Consensus Risk
ADN v3:
- does not alter consensus
- does not mint, sign, or validate transactions
- does not introduce governance rules

---

# 🧠 Defence Model (v3)

ADN v3 reasons using **explicit state machines**, not heuristics alone.

## Inputs
- Telemetry packets (node metrics, RPC behaviour)
- Sentinel AI events
- DQSN advisories
- Wallet‑side defence events

## Core State
- **RiskLevel**: `NORMAL`, `ELEVATED`, `HIGH`, `CRITICAL`
- **LockdownState**: `NONE`, `PARTIAL`, `FULL`

## Outputs
- Defence actions (`ENTER_PARTIAL_LOCKDOWN`, `ENTER_FULL_LOCKDOWN`, `LIFT_LOCKDOWN`)
- RPC policy constraints
- Structured defence events

---

# 🧩 Internal Architecture (v3 Reference)

```
src/adn_v3/
│
├── models.py        # Risk, defence & state models
├── telemetry.py     # Telemetry adapters
├── validator.py     # Telemetry → RiskSignal
├── policy.py        # RiskSignal → PolicyDecision
├── engine.py        # Deterministic runtime orchestration
├── actions.py       # Lockdown & enforcement helpers
└── tests/           # Deterministic regression tests
```

v3 removes speculative routing/playbook concepts and replaces them with
**explicit, enforceable invariants**.

---

# 📡 Defence Flow (v3)

```
Raw Telemetry / Events
        │
        ▼
TelemetryAdapter
        │
        ▼
RiskValidator
        │
        ▼
RiskSignal[]
        │
        ▼
PolicyEngine
        │
        ▼
PolicyDecision
        │
        ▼
Defense Engine
        │
        ▼
NodeDefenseState
        │
        ▼
RPC / Wallet / Node Enforcement
```

---

# 🛡️ Design Principles (v3)

1. **Determinism First**
2. **Fail‑Closed by Default**
3. **No Bypass Paths**
4. **Explicit State Machines**
5. **Local Enforcement Only**
6. **Test‑Locked Behaviour**

---

# ⚙️ Code Status

ADN v3 is a **locked reference defence engine**:

- deterministic execution paths
- invariant‑driven design
- regression‑tested lockdown logic
- safe for study, extension, and downstream integration

---

# 🧪 Tests

Tests guarantee:

- no signing or execution bypass
- correct lockdown transitions
- deterministic outcomes
- enforcement invariants remain intact

---

# 🤝 Contribution Policy

See `CONTRIBUTING.md`.

- Security‑first changes only
- No weakening of invariants
- No consensus‑touching logic
- Deterministic tests required

---

# 📜 License

MIT License  
© 2026 **DarekDGB**
