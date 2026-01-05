# 🛡️ Active Defence Network (ADN) — Architecture v3
### *Shield Contract v3 • Deterministic • Fail-Closed Active Response Layer*
**Architecture by @DarekDGB — MIT Licensed**

---

## 1. Role in the DigiByte Quantum Shield

**ADN (Active Defence Network)** is the **decision and response layer** of the DigiByte Quantum Shield.

It sits **above Sentinel AI and DQSN**, consuming their signals and translating them into **defensive actions**
such as warnings, throttling, partial lockdowns, or full isolation recommendations.

ADN **does not modify consensus** and **does not execute blockchain actions directly**.

---

## 2. Position in the 5-Layer Shield

```
Guardian Wallet
        ▲
Quantum Wallet Guard (QWG)
        ▲
ADN v3  ← THIS LAYER
        ▲
Sentinel AI v3
        ▲
DQSN v3
```

---

## 3. Core Responsibilities

ADN v3 is responsible for:

- Consuming structured signals from Sentinel AI and other upstream systems
- Evaluating node defense state using deterministic rules
- Escalating or de-escalating risk levels
- Producing contract-stable decisions for downstream consumers
- Enforcing fail-closed behavior on invalid input

ADN **does not**:
- hold keys
- sign transactions
- modify consensus
- perform cryptography
- act autonomously without upstream signals

---

## 4. Shield Contract v3 Enforcement

ADN v3 is governed by **Shield Contract v3**.

Hard guarantees:

- contract_version == 3 required
- Unknown top-level keys → ERROR
- Unknown event schema → ERROR
- NaN / Infinity values → ERROR
- Deterministic outputs (stable context_hash)
- Deny-by-default decision mapping

No execution path bypasses the v3 gate.

---

## 5. High-Level Data Flow

```
[Sentinel AI v3 / Signals]
        ↓
Shield Contract v3 Gate
        ↓
Event Parsing (fail-closed)
        ↓
v2 Defense Engine (authoritative)
        ↓
NodeDefenseState
        ↓
Deterministic Decision Output
        ↓
[QWG / Guardian Wallet / Operators]
```

---

## 6. Internal Architecture (Reference)

```
src/adn_v2/
│
├── v3.py            # Shield Contract v3 gate (authoritative)
├── engine.py        # Defense evaluation logic (v2)
├── models.py        # DefenseEvent, NodeDefenseState
├── policies/        # Policy definitions
└── utils/           # Helpers
```

---

## 7. Determinism & Auditability

- Same input → same output
- No timestamps or randomness in decision hash
- Context hash binds inputs, config, decision, and reasons
- Designed for external review and reproducibility

---

## 8. Security Philosophy

1. Fail closed
2. Deterministic first
3. No silent acceptance
4. Signal, not authority
5. Human-overridable downstream
6. Defense-in-depth alignment

---

## 9. Status

ADN v3 architecture is **contract-complete** and **integration-ready**.
Behavior remains intentionally anchored to the proven v2 engine.

---

## 10. License

MIT License  
© 2026 DarekDGB
