# ⚔️ ADN v2 — Active Defence Network
### *Tactical Response & Defence Orchestration Layer of the DigiByte Quantum Shield*
**Architecture by @DarekDGB — MIT Licensed**

---

## 🚀 Purpose

**ADN v2 (Active Defence Network)** is the **tactical brain** of the DigiByte Quantum Shield.

Where:

- **DQSN v2** measures the network’s health  
- **Sentinel AI v2** detects and scores threats  

**ADN v2** decides *how to respond*.

It does this by:

- fusing risk signals  
- mapping them to defence playbooks  
- emitting structured recommendations and alerts  
- coordinating responses across wallets, nodes, and infrastructure

ADN is **advisory only** — it **does not change DigiByte consensus**.  
It provides **tactical intelligence**, not protocol rules.

---

# 🛡️ Position in the 5-Layer DigiByte Quantum Shield

```
 ┌───────────────────────────────────────────────┐
 │           Guardian Wallet                     │
 │  User-side rules & defence policies           │
 └───────────────────────────────────────────────┘
                     ▲
                     │   (defence recommendations)
 ┌───────────────────────────────────────────────┐
 │       Quantum Wallet Guard (QWG)              │
 │  Tx vetting • PQC checks • runtime guard      │
 └───────────────────────────────────────────────┘
                     ▲
                     │   (playbook outputs)
 ┌───────────────────────────────────────────────┐
 │                ADN v2                         │
 │  Active Defence Network – tactics & routing   │
 └───────────────────────────────────────────────┘
                     ▲
                     │   (risk vectors & alerts)
 ┌───────────────────────────────────────────────┐
 │             Sentinel AI v2                    │
 │  Telemetry analytics & anomaly detection      │
 └───────────────────────────────────────────────┘
                     ▲
                     │   (raw health metrics)
 ┌───────────────────────────────────────────────┐
 │            DQSN v2                            │
 │  Network entropy & health telemetry           │
 └───────────────────────────────────────────────┘
```

---

# 🎯 Core Mission

### ✓ Fuse Threat Intelligence  
ADN ingests:

- network health metrics from **DQSN v2**
- anomaly and threat scores from **Sentinel AI v2**

and produces a **consolidated defence view**.

### ✓ Select Defence Playbooks  
Based on threat class and severity, ADN chooses:

- which playbook to activate  
- which targets (nodes / wallets / services) are relevant  
- which signals to emit

### ✓ Orchestrate Multi-Layer Responses  
ADN routes:

- alerts and hints to **QWG & Guardian Wallet**  
- infrastructure suggestions to node operators and tooling  
- monitoring hooks to dashboards and SIEMs

### ✓ Stay Consensus-Neutral  
ADN is **not a governance layer** and **never** modifies DigiByte rules.

---

# 🧠 Threat & Response Model

ADN reasons in terms of:

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
   - regional effects  
   - duration  
   - correlation with other anomalies  

4. **Playbook**  
   - which defence strategy applies  
   - which outputs to generate  
   - which layer should act (QWG / Guardian / Infra)

---

# 🧩 Internal Architecture (Reference)

```
adn_v2/
│
├── inputs/
│     ├── dqs_stream.py
│     ├── sentinel_stream.py
│     └── config_loader.py
│
├── fusion/
│     ├── risk_fusion.py
│     ├── context_builder.py
│     └── severity_classifier.py
│
├── playbooks/
│     ├── reorg_playbook.py
│     ├── eclipse_playbook.py
│     ├── hashrate_playbook.py
│     ├── mempool_playbook.py
│     └── generic_safe_mode.py
│
├── routing/
│     ├── qwg_router.py
│     ├── guardian_router.py
│     ├── infra_router.py
│     └── audit_log.py
│
└── utils/
      ├── types.py
      ├── config.py
      └── logging.py
```

---

# 📡 Data Flow Overview

```
[DQSN v2 Health Metrics]      [Sentinel AI v2 Alerts]
           │                         │
           └──────► [ADN Inputs] ◄───┘
                        │
                  [Risk Fusion]
                        │
             [Threat & Severity Model]
                        │
                 [Playbook Engine]
                        │
         ┌──────────────┼────────────────┐
         ▼              ▼                ▼
   [QWG Router]   [Guardian Router]   [Infra Router]
```

---

# 🛡️ Security & Design Principles

1. **Advisory, Not Authoritarian**  
2. **Explainability**  
3. **Minimal Assumptions**  
4. **Fail-Safe Behaviour**  
5. **Composable Playbooks**  
6. **Interoperable Outputs**

---

# ⚙️ Code Status

ADN v2 provides a structured, modular Python architecture designed for:

- extending defensive playbooks  
- orchestrating network responses  
- integrating with QWG & Guardian Wallet  
- threat simulation  
- safe community development  

---

# 🧪 Tests

Tests verify:

- module imports  
- data flow structure  
- deterministic behaviour under mock inputs  

---

# 🤝 Contribution Policy

See `CONTRIBUTING.md`.

- Improvements welcome  
- No architecture removal  
- ADN must **never** become a consensus layer  

---

# 📜 License

MIT License  
© 2025 **DarekDGB**
