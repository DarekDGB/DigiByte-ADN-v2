# Autonomous Defense Node v2 (ADN v2) – Layer-3 Enforcement Engine for DigiByte

**ADN v2** is the upgraded enforcement layer in DigiByte’s quantum‑resistant 4‑layer shield:

> **DQSN → Sentinel AI v2 → ADN v2 → Wallet Guardian**

Its mission is simple but critical:

### **Take action when the chain is under threat.**
ADN v2 receives risk signals from Sentinel AI v2, verifies them, and executes automated defensive responses to protect the DigiByte network in real time.

---

## 🚀 Key Responsibilities

### **1. Threat Validation Layer**
ADN v2 double‑checks Sentinel’s risk state before taking action:
- verifies entropy drops
- confirms mempool anomalies
- checks peer behaviour patterns
- validates timestamp & difficulty manipulation signals
- rejects false positives & poisoned signals

### **2. Automated Chain Protection**
When a verified risk is detected, ADN v2 can activate:
- **Hardened Mode** (strict block validation)
- **Emergency Fee Mode** (anti‑spam)
- **Peer Eviction** (malicious peers removed)
- **Block Freeze Window** (during deep reorg threats)
- **PQC Activation** (post‑quantum signing paths)

### **3. Privacy‑Safe Wallet Coordination**
ADN v2 communicates with:
- **Wallet Guardian** (Layer‑4 wallet protection)

Using minimal, anonymous flags:
- CRITICAL → freeze signing
- HIGH → require additional confirmation
- ELEVATED → show warnings

### **4. Self‑Audit & Tamper Detection**
- signed configuration files
- hashed rule sets
- integrity check at startup
- threat replay protection
- adversarial drift‑proof logic

---

## 🧠 How It Works

**Sentinel AI v2 → ADN v2 → Node Actions**

1. Sentinel AI v2 evaluates network telemetry  
2. It produces a risk state (NORMAL → CRITICAL)  
3. ADN v2 verifies the threat using deterministic rules  
4. If valid, ADN v2 activates the appropriate response  

This keeps DigiByte running even under:
- rented hashrate attacks  
- timestamp manipulation  
- Sybil clustering  
- mempool floods  
- quantum‑assisted key extraction  
- deep reorg attempts  

---

## 📁 Repository Structure

```
DigiByte-ADN-v2/
├─ README.md
├─ LICENSE
├─ src/
│  └─ dgb_adn_v2/
│     ├─ __init__.py
│     ├─ config.py
│     ├─ policy_engine.py
│     ├─ validator.py
│     ├─ action_engine.py
│     ├─ api.py
│     └─ main.py
└─ docs/
   ├─ technical-spec-adn-v2.md
   └─ adn-v2-whitepaper.md
```

---

## 🛠 Early Milestone (v0.1)

- baseline policy engine  
- risk state validation  
- hardened mode activation  
- basic peer filtering  
- fee escalation logic  
- API for Sentinel v2 + Wallet Guardian testing  

---

## 📜 License (MIT)

```
MIT License

Copyright (c) 2025 
Darek (@Darek_DGB)
```

---

## 🌟 Vision

With ADN v2, DigiByte becomes a **self‑defending blockchain**, able to adapt, resist, and respond to both classical and quantum‑era attacks.

This is the next evolution of decentralized security.

