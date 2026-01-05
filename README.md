# ⚔️ ADN v3 — Active Defence Network
### *Deterministic Local Defence Engine • Policy → Decision → Local Enforcement*
**Architecture by @DarekDGB — MIT Licensed**

---

## 🚀 Purpose

**ADN v3 (Active Defence Network)** is the **deterministic local defence decision engine** of the DigiByte Quantum Shield.

Where:
- **Sentinel AI v3** detects anomalies and produces structured threat signals  
- **DQSN v3** validates, deduplicates, and transports those signals deterministically  

**ADN v3** decides **what the local environment is allowed to do** — node wrapper, RPC gateway, or wallet runtime — using a strict, testable, fail‑closed flow.

ADN does this by:
- ingesting aggregated risk signals from DQSN  
- evaluating them against explicit defence policies  
- producing deterministic **PolicyDecision** objects  
- emitting **local enforcement intents** (lockdown states, RPC policies, advisory outputs)

ADN is **consensus‑neutral**:
- it does **not** modify DigiByte protocol rules  
- it does **not** sign transactions  

It governs **local behaviour only**.

---

## 🛡️ Position in the DigiByte Quantum Shield (v3)

```
 ┌───────────────────────────────────────────────┐
 │            Guardian Wallet                    │
 │   User-side defence rules & policies          │
 └───────────────────────────────────────────────┘
                     ▲
                     │   (policy recommendations)
 ┌───────────────────────────────────────────────┐
 │        Quantum Wallet Guard (QWG)             │
 │   Runtime tx / key safety enforcement         │
 └───────────────────────────────────────────────┘
                     ▲
                     │   (execution authority)
 ┌───────────────────────────────────────────────┐
 │                 ADN v3                        │
 │   Deterministic defence decision engine       │
 │   Risk → Policy → Enforcement intent          │
 └───────────────────────────────────────────────┘
                     ▲
                     │   (aggregated signals)
 ┌───────────────────────────────────────────────┐
 │               DQSN v3                         │
 │   Deterministic signal aggregation & transport│
 └───────────────────────────────────────────────┘
                     ▲
                     │   (raw threat signals)
 ┌───────────────────────────────────────────────┐
 │            Sentinel AI v3                     │
 │   Anomaly & threat detection                  │
 └───────────────────────────────────────────────┘
```

ADN is the **decision authority** for local defence actions — not the source of signals and not the executor of cryptography.

---

## 🎯 Core Mission (v3)

### ✓ Deterministic risk → decision
- Convert aggregated signals into structured **RiskSignal** objects
- Produce deterministic **PolicyDecision** outputs  
  *(same inputs → same decisions)*

### ✓ Local enforcement intent
- Map decisions into **NodeDefenseState**
- Generate **RPC policy outputs** (throttle / restrict / annotate)
- Emit structured defence events for upstream or user‑facing layers

### ✓ Modular policy engine
- Validators, scoring logic, and enforcement mapping are modular
- Components can be swapped without changing the contract surface

---

## ✅ What “v3” means in this repository

This repository is **DigiByte‑ADN**.

The **v3 runtime is implemented inside the existing package layout** for backward compatibility:

- `src/adn_v2/v3.py` — v3 orchestration entry point  
- `src/adn_v2/contracts/` — Shield Contract v3 primitives  
  - `v3_types.py`
  - `v3_reason_codes.py`
  - `v3_hash.py`

The folder name `adn_v2/` is **historical**.  
The **logic and contracts implemented here are v3**, and documentation reflects that reality.

---

## 🧩 Repository Layout (as it exists)

```
DigiByte-ADN/
├─ README.md
├─ LICENSE
├─ CONTRIBUTING.md
├─ docs/
│  ├─ v2/                  # legacy reference docs
│  └─ v3/                  # authoritative v3 docs
└─ src/
   └─ adn_v2/
      ├─ __init__.py
      ├─ actions.py
      ├─ adaptive_bridge.py
      ├─ cli.py
      ├─ client.py
      ├─ config.py
      ├─ engine.py
      ├─ main.py
      ├─ models.py
      ├─ policy.py
      ├─ server.py
      ├─ telemetry.py
      ├─ validator.py
      ├─ v3.py             # v3 runtime entry
      └─ contracts/
         ├─ __init__.py
         ├─ v3_hash.py
         ├─ v3_reason_codes.py
         └─ v3_types.py
```

The v3 contract surface is **explicit, isolated, and deterministic**.

---

## 📚 Documentation

- **Authoritative v3 docs:** `docs/v3/INDEX.md` (start here)
- **Legacy v2 docs:** `docs/v2/` (historical reference)

---

## 🧪 Tests

Tests verify:
- deterministic behaviour under fixed inputs
- correct policy classification
- stable enforcement outputs

Fail‑closed behaviour is a **design invariant**.

---

## 🤝 Contribution Policy

See `CONTRIBUTING.md`.

Rules:
- Do not introduce consensus‑touching behaviour
- Keep decisions deterministic
- Enforcement outputs must be explicit and testable

---

## 📜 License

MIT License  
© 2026 **DarekDGB**
