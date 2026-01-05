# 📚 ADN Documentation Index

**Active Defence Network (ADN)** is a core component of the **DigiByte Quantum Shield**.
This repository now implements **Shield Contract v3** with strict, fail-closed semantics.

This document is the **authoritative entry point** for all ADN documentation.

---

## 🛡️ Current Status

- **Contract Version:** v3 (enforced in code and tests)
- **Mode:** External, non-consensus, read-only decision engine
- **Fail-Closed:** Yes
- **Deterministic Outputs:** Yes
- **Legacy v2 Docs:** Archived (preserved for historical context)

If you are reviewing ADN today, **only v3 documents are normative**.

---

## ✅ Authoritative v3 Documentation (Current)

These documents define how ADN works *now* and what integrators should rely on.

### 🔐 Shield Contract
- **`CONTRACT.md`**
  - Request schema (events)
  - Fail-closed guarantees
  - Deterministic output rules
  - What ADN is allowed to do — and what it must never do

### 🧱 Architecture
- **`ARCHITECTURE.md`**
  - ADN’s role inside the 5-layer Quantum Shield
  - How ADN consumes Sentinel AI + DQSN signals
  - How defensive actions are produced without signing or execution

### 🔄 Upgrade Notes
- **`upgrade/`**
  - Documents describing the transition from v2 → v3
  - Rationale for contract hardening and regression locks

---

## 🗄️ Legacy Documentation (Archived)

The following documents were written for **ADN v2**.
They remain available for reference and historical context, but **do not define current behavior**.

Location:
docs/legacy/

Includes:
- `architecture.md`
- `defense_flow.md`
- `examples.md`
- `overview.md`
- `policy_engine.md`
- `risk_validator.md`
- `technical-spec.md`
- `telemetry_flow.md`
- `whitepaper-adn-v2.md`

Legacy documents may describe concepts that still exist, but:
> **When in conflict with v3 contract or code, legacy docs are non-authoritative.**

---

## 🧭 How to Read This Repo (for Reviewers)

If you are:
- **Auditing security** → read `CONTRACT.md`, then tests  
- **Integrating ADN** → read `ARCHITECTURE.md`, then examples  
- **Reviewing evolution** → compare `legacy/` with v3 contract and tests  

ADN is designed to survive review from engineers who only trust:
- contracts  
- tests  
- deterministic behavior  

---

## 📜 Governance Note

ADN:
- does **not** modify consensus
- does **not** sign transactions
- does **not** hold keys
- does **not** execute wallet actions

It emits **defensive decisions and recommendations only**.

---

© 2026 **DarekDGB**  
MIT Licensed
