# ⚔️ ADN v3 — Active Defence Network
### *Deterministic Local Defence Engine • Policy → Lockdown → Enforcement*
**Architecture by @DarekDGB — MIT Licensed**

---

## 🚀 Purpose

**ADN v3 (Active Defence Network)** is the **deterministic local defence engine** of the DigiByte Quantum Shield.

Where:

- **DQSN v3** observes network‑wide entropy & health  
- **Sentinel AI v3** detects anomalies and produces threat signals  

**ADN v3** decides **what the local node / gateway / wallet runtime is allowed to do** — in a strict, testable flow.

It does this by:

- ingesting telemetry + external risk signals  
- deriving structured risk signals (deterministic)  
- applying policy decisions  
- producing **lockdown / RPC policies** and other local enforcement outputs

ADN is **consensus‑neutral** — it **does not modify DigiByte protocol rules** and **does not sign transactions**.  
It governs **local behaviour** only (node wrapper / RPC gateway / wallet runtime integration).

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
 │        Quantum Wallet Guard (QWG)             │
 │   Runtime tx / key safety enforcement         │
 └───────────────────────────────────────────────┘
                     ▲
                     │   (execution authority)
 ┌───────────────────────────────────────────────┐
 │                 ADN v3                        │
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
 │               DQSN v3                         │
 │   Network entropy & health                    │
 └───────────────────────────────────────────────┘
```

---

## 🎯 Core Mission (v3)

### ✓ Deterministic risk → decision
- Convert telemetry / alerts into structured **RiskSignal** objects
- Produce a deterministic **PolicyDecision** (same inputs → same outputs)

### ✓ Lockdown & enforcement outputs
- Convert decisions into **NodeDefenseState**
- Generate **RPC policy objects** (throttle / disable / notes)
- Emit structured defence events for upstream layers

### ✓ Replaceable pieces
- Validators, policy scoring, and enforcement mapping are modular
- Operators can swap components without rewriting the whole engine

---

## ✅ What “v3” means in this repo

This repository is `DigiByte-ADN` and the **current v3 runtime lives inside the Python package path**:

- `src/adn_v2/v3.py` (v3 entry / logic wiring)
- `src/adn_v2/contracts/` (`v3_types.py`, `v3_reason_codes.py`, `v3_hash.py`)

The package is still named `adn_v2/` for compatibility with the original v2 layout, but the **docs and implementation here include v3 concepts**.

---

## 🧩 Repository Layout (as it exists)

```
DigiByte-ADN/
├─ README.md
├─ LICENSE
├─ CONTRIBUTING.md
├─ docs/
│  ├─ v2/                  # legacy / reference docs
│  └─ v3/                  # current v3 docs (INDEX, ARCHITECTURE, CONTRACT)
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
      ├─ v3.py             # v3 runtime entry / orchestrator glue
      └─ contracts/
         ├─ __init__.py
         ├─ v3_hash.py
         ├─ v3_reason_codes.py
         └─ v3_types.py
```

---

## 📚 Docs

- **v3 docs:** `docs/v3/INDEX.md` (start here)
- **v2 docs (legacy):** `docs/v2/` (reference / history)

---

## 🧪 Tests

Tests verify:

- module imports
- deterministic behaviour under mock inputs
- defence/lockdown logic (where applicable)

---

## 🤝 Contribution Policy

See `CONTRIBUTING.md`.

- Improvements welcome
- Do not introduce consensus‑touching behaviour
- Keep policy outputs deterministic and test‑backed

---

## 📜 License

MIT License  
© 2025 **DarekDGB**
