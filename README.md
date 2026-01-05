# ⚔️ ADN v3 — Active Defence Network
### *Deterministic Defence & Enforcement Engine of the DigiByte Quantum Shield*
**Architecture by @DarekDGB — MIT Licensed**

---

## 🚀 Purpose

**ADN v3 (Active Defence Network)** is the **deterministic local defence engine** of the DigiByte Quantum Shield.

It represents the evolution from **advisory concepts (v2)** into a **codified, testable, policy‑driven defence runtime**.

Where:

- **DQSN v3** observes **network‑wide entropy, health, and systemic risk**
- **Sentinel AI v3** detects anomalies and produces **threat signals**

**ADN v3** enforces **local defensive decisions** in a **strict, deterministic flow**.

ADN v3 remains **consensus‑neutral**:
- it never modifies DigiByte protocol rules
- it never signs transactions
- it governs **local node and wallet behaviour only**

---

## 🛡️ Position in the DigiByte Quantum Shield (v3)

```
 ┌───────────────────────────────────────────────┐
 │            Guardian Wallet                    │
 │   User‑side defence rules & policies          │
 └───────────────────────────────────────────────┘
                     ▲
                     │   (defence recommendations)
 ┌───────────────────────────────────────────────┐
 │        Quantum Wallet Guard (QWG)              │
 │   Runtime tx / key safety enforcement         │
 └───────────────────────────────────────────────┘
                     ▲
                     │   (execution authority)
 ┌───────────────────────────────────────────────┐
 │                ADN v3                         │
 │   Deterministic defence engine                │
 │   Policy → Lockdown → Enforcement             │
 └───────────────────────────────────────────────┘
                     ▲
                     │   (risk signals)
 ┌───────────────────────────────────────────────┐
 │            Sentinel AI v3                     │
 │   Anomaly & threat detection                  │
 └───────────────────────────────────────────────┘
                     ▲
                     │   (raw telemetry)
 ┌───────────────────────────────────────────────┐
 │              DQSN v3                          │
 │   Network entropy & health                    │
 └───────────────────────────────────────────────┘
```

---

## 🎯 Core Mission (v3)

### ✓ Deterministic Defence Decisions
ADN v3 converts risk signals into **explicit, auditable decisions**:
- no heuristics hidden in runtime
- no implicit behaviour
- every outcome is explainable and testable

### ✓ Enforced Local Protection
ADN v3 governs:
- RPC availability and throttling
- node lockdown states
- wallet‑side execution permissions (via QWG / Guardian)

### ✓ Strict Execution Boundaries
ADN v3 **cannot be bypassed**:
- policy must pass
- lockdown rules must be satisfied
- enforcement is explicit and ordered

### ✓ Consensus Neutrality
ADN v3 is **not governance** and **not protocol logic**.
It is a **local enforcement layer**, not a chain‑wide authority.

---

## 🧠 Threat & Response Model (v3)

ADN v3 reasons in four dimensions:

1. **Threat Class**
   - reorg attempts
   - eclipse / partition attacks
   - hashrate dominance
   - mempool flooding / spam
   - timestamp manipulation
   - propagation instability

2. **Severity**
   - informational
   - low
   - medium
   - high
   - critical

3. **Context**
   - locality vs global scope
   - duration and recurrence
   - correlation with other anomalies

4. **Policy Outcome**
   - allow
   - restrict
   - partial lockdown
   - full lockdown

---

## 🧩 Internal Architecture (Reference)

```
adn_v3/
│
├── telemetry/
│     ├── dqsn_v3_stream.py
│     ├── sentinel_v3_stream.py
│     └── adapters.py
│
├── policy/
│     ├── classifiers.py
│     ├── evaluators.py
│     └── decisions.py
│
├── enforcement/
│     ├── lockdown.py
│     ├── rpc_policy.py
│     └── wallet_policy.py
│
├── runtime/
│     ├── orchestrator.py
│     ├── invariants.py
│     └── state.py
│
└── utils/
      ├── types.py
      ├── config.py
      └── logging.py
```

---

## 📡 Deterministic Data Flow

```
[DQSN v3 Telemetry]        [Sentinel AI v3 Signals]
          │                         │
          └──────────► [Telemetry Layer] ◄──────────┘
                               │
                         [Policy Engine]
                               │
                     [Decision & Risk State]
                               │
                        [Lockdown Engine]
                               │
                   [Enforcement / Execution]
                               │
              QWG • Guardian Wallet • Node Runtime
```

---

## 🛡️ Design Invariants

1. **Deny‑by‑default**
2. **Explicit permissions only**
3. **No silent fallbacks**
4. **Deterministic execution**
5. **Explainable decisions**
6. **Non‑bypassable enforcement**

If an invariant breaks, **security is broken**.

---

## ⚙️ Code Status

ADN v3 is an **active, evolving defence runtime**.

- v2 documents remain preserved under `docs/v2/`
- v3 defines the **authoritative direction**
- all new work targets **v3 invariants**

---

## 🧪 Testing

Tests enforce:
- deterministic outcomes
- invariant preservation
- non‑bypassable policy paths
- regression locks for security‑critical flows

---

## 🤝 Contribution Policy

See `CONTRIBUTING.md`.

- Security‑first changes only
- No consensus logic
- No implicit execution paths
- All behaviour must be testable

---

## 📜 License

MIT License  
© 2026 **DarekDGB**
