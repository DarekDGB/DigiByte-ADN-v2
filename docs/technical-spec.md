# DigiByte Active Defense Network v2 – Technical Specification

## 1. Overview

**Active Defense Network v2 (ADN v2)** is the upgraded Layer‑3 engine of the DigiByte quantum‑resistant security stack.  
It runs alongside a DigiByte full node and performs three core functions:

1. **Ingest telemetry** from:
   - local node (mempool, peers, chain reorgs, resource usage)
   - Sentinel AI v2 + DQSN (global quantum / anomaly scores)
   - optional Wallet Guardian and other local modules
2. **Evaluate policies** against this telemetry to derive a current **risk state**.
3. **Execute actions** (locally and across a mesh of ADN v2 instances) when threat thresholds are crossed.

ADN v2 is designed as a **reference implementation** – node operators can adopt it as‑is or integrate selected modules into their own infrastructure.

> **Legacy note:** Earlier drafts expanded ADN as “Autonomous Defense Node”.  
> The canonical and correct name is **Active Defense Network**.

## 2. Objectives

- Provide a **deterministic policy engine** for node‑level defense decisions.
- Allow **risk‑scored, real‑time reactions** to emerging quantum or network threats.
- Support **mesh coordination** between many ADN v2 nodes without centralization.
- Keep the implementation **simple, auditable and MIT‑licensed**.

## 3. Repository Layout

This specification targets the following repository structure:

```text
DigiByte-ADN-v2/
├─ README.md
├─ LICENSE
├─ docs/
│  ├─ technical-spec-adn-v2.md
│  └─ adn-v2-whitepaper.md
└─ src/
   └─ adn_v2/
      ├─ __init__.py
      ├─ actions.py
      ├─ cli.py
      ├─ client.py
      ├─ config.py
      ├─ engine.py
      ├─ main.py
      ├─ models.py
      ├─ policy.py
      ├─ server.py
      ├─ telemetry.py
      └─ validator.py
```

Each module is documented in detail below.

## 4. Core Data Models (`models.py`)

### 4.1 RiskLevel

An `Enum` describing the normalized risk buckets used across the engine:

- `NORMAL`
- `ELEVATED`
- `HIGH`
- `CRITICAL`

These levels are derived from policy evaluation and/or Sentinel AI v2 scores.

### 4.2 TelemetryPacket

A dataclass representing a single observation used for policy evaluation:

- `source`: textual identifier (e.g. `"node"`, `"sentinel"`, `"wallet_guardian"`).
- `timestamp`: UTC ISO‑8601 string or integer epoch.
- `metrics`: `Dict[str, float | int | str]` – arbitrary key/value metrics.
- `tags`: optional `Set[str]` – labels such as `"reorg"`, `"mempool_spike"`.

### 4.3 PolicyContext

Represents the current decision context:

- `risk_level`: current `RiskLevel` for this node.
- `score`: numeric score in `[0, 100]` summarising cumulative risk.
- `history`: rolling window of recent `TelemetryPacket` instances.
- `meta`: optional dictionary for implementation‑specific flags.

### 4.4 ActionRequest / ActionResult

Abstractions used between the policy engine and the action engine:

- `ActionRequest`:
  - `name`: canonical action name (e.g. `"enter_hardened_mode"`).
  - `params`: dictionary of action‑specific parameters.
  - `reason`: short human‑readable explanation.
- `ActionResult`:
  - `success`: boolean outcome.
  - `details`: optional free‑form diagnostic information.

### 4.5 MeshMessage

Represent messages exchanged between ADN v2 instances:

- `message_type`: `"PING"`, `"STATUS"`, `"ALERT"`, `"POLICY_UPDATE"`, etc.
- `payload`: JSON‑serialisable object.
- `signature`: optional field for future authenticated messaging.

## 5. Configuration Layer (`config.py`)

`config.py` exposes a `Config`/`ADNConfig` dataclass and helpers to load configuration from environment variables, JSON/YAML config files, or explicit dictionaries.

Key groups:

- **Risk thresholds**:
  - `score_elevated`
  - `score_high`
  - `score_critical`
- **Telemetry**:
  - `telemetry_window_seconds`
  - `max_packets_in_window`
- **Server / mesh**:
  - `listen_host`, `listen_port`
  - ` peers`: list of peer ADN v2 node addresses.
- **Integration**:
  - `sentinel_endpoint`
  - `dqsn_endpoint`
  - optional wallet guardian endpoint or IPC path.
- **Logging**:
  - log level, file path, rotation options.

All modules receive a shared config instance so behavior is reproducible.

## 6. Telemetry Ingestion (`telemetry.py`)

The telemetry module is responsible for collecting raw signals and emitting normalized `TelemetryPacket` instances to the engine.

Typical sources:

- **DigiByte node metrics** – RPC / CLI / log scraping:
  - mempool size / growth
  - peer count, bans, connection churn
  - orphan blocks, reorg depth
- **Sentinel AI v2**:
  - quantum risk scores
  - anomaly category identifiers
- **DQSN**:
  - global consensus on chain‑wide threat level
- **Local system**:
  - CPU, memory, disk I/O, process restarts

The module exports a `TelemetryCollector` class with methods such as:

- `collect_once() -> list[TelemetryPacket]`
- `stream(callback: Callable[[TelemetryPacket], None])`

The engine determines how often to pull telemetry and how to batch it.

## 7. Validation Layer (`validator.py`)

The validator module performs fast sanity checks before telemetry reaches the policy engine:

- type validation and bounds checking
- deduplication of obviously repeated packets
- dropping packets older than the configured window
- enforcing maximum packet sizes

It exposes at minimum:

- `validate_packet(packet: TelemetryPacket) -> bool`
- `normalise_packet(packet: TelemetryPacket) -> TelemetryPacket`

Packets failing validation are logged and discarded.

## 8. Policy Engine (`policy.py`)

The policy engine is the deterministic heart of ADN v2. It maps telemetry into **risk scores** and **action requests**.

Responsibilities:

- Maintain a rolling `PolicyContext` state.
- Aggregate metrics into a scalar risk `score` in `[0, 100]`.
- Map `score` to `RiskLevel` via configured thresholds.
- Generate `ActionRequest` instances when:
  - entering a higher‑risk state
  - specific policy rules are triggered (e.g. deep reorg, mempool flood).

Example policy classes:

- `ReorgDepthPolicy`
- `MempoolAnomalyPolicy`
- `EntropyCollapsePolicy` (input from Sentinel/DQSN)
- `PeerInstabilityPolicy`

Policy evaluation flow:

1. New telemetry packet is ingested and validated.
2. Packet is appended to the rolling history.
3. Each policy computes a partial contribution to the risk score.
4. Contributions are combined (e.g. weighted sum, capped at 100).
5. Final `RiskLevel` is computed using threshold cut‑offs.
6. Actions are suggested via `ActionRequest` objects.

## 9. Action Engine (`actions.py`)

The action engine receives `ActionRequest` objects from the policy engine and maps them to concrete local operations.

Typical actions:

- **Hardened node mode**:
  - restrict RPC access
  - freeze non‑essential automation
  - require manual operator confirmation for certain operations
- **Peer filtering**:
  - disconnect or deprioritise suspicious peers
  - rate‑limit incoming connections
- **Fee / mempool controls**:
  - tighten local mempool acceptance policies
  - adjust relay / rebroadcast behaviour
- **Alerting**:
  - log high‑risk events
  - send notifications to operators (e‑mail / webhook)

The engine exposes:

- `execute(action_request: ActionRequest) -> ActionResult`

All side‑effects are confined to the local node environment; protocol‑level changes remain the responsibility of the underlying DigiByte implementation.

## 10. Core Engine (`engine.py`)

The core engine orchestrates telemetry collection, validation, policy evaluation and action execution.

Key responsibilities:

- Maintain the current `PolicyContext`.
- Schedule telemetry pulls.
- Send packets through `validator`, `policy` and `actions` modules.
- Stream status updates to the mesh server and to local observers.

Main interface:

- `ADNEngine.run_forever()` – blocking loop.
- `ADNEngine.step()` – single iteration (useful for tests).
- `ADNEngine.get_status() -> PolicyContext`.

The engine is designed to be **pure Python**, single‑process and easily testable.

## 11. Server & Mesh Layer (`server.py`)

The server module exposes a lightweight HTTP/WebSocket or TCP JSON API for:

- health checks (`/health`)
- current status (`/status`)
- peer messages (`/mesh/*`)

Responsibilities:

- accept incoming `MeshMessage` instances from other ADN v2 nodes
- optionally broadcast local risk state when transitions occur
- support simple future extensions (e.g. signed status messages)

The exact transport details are implementation‑specific; this reference keeps the protocol minimal and text‑based.

## 12. Client Integrations (`client.py`)

The client module centralises outbound communication:

- sending risk updates to DQSN / Sentinel AI v2
- notifying local management tools or dashboards
- sending `MeshMessage` packets to peer ADN v2 nodes

It exposes convenience helpers such as:

- `publish_status(context: PolicyContext)`
- `send_alert(message: MeshMessage)`

## 13. Command‑Line Interface (`cli.py`)

The CLI module defines a `main()` function with subcommands such as:

- `adn-v2 run` – start the engine + server.
- `adn-v2 status` – query local or remote ADN v2 instance.
- `adn-v2 dump-policy` – print effective configuration and thresholds.

The CLI is intentionally thin; it delegates to `engine`, `client` and `config`.

## 14. Entry Point (`main.py`)

`main.py` is a small bootstrap module which:

- parses configuration
- initialises telemetry, policy, actions, server and client components
- starts the main event loop

This file is the reference example for how to embed ADN v2 in external tooling.

## 15. Risk State Model

ADN v2 uses both **discrete levels** and a **continuous score**:

- Score `0–24`: `RiskLevel.NORMAL`
- Score `25–49`: `RiskLevel.ELEVATED`
- Score `50–79`: `RiskLevel.HIGH`
- Score `80–100`: `RiskLevel.CRITICAL`

Threshold values are configurable and can be tuned by operators.

## 16. Logging, Metrics and Observability

All modules share a common logging setup:

- structured logs with timestamps and module names
- clear markers on state transitions (e.g. `NORMAL -> HIGH`)
- diagnostic logs for rejected telemetry and failed actions

Optional metrics endpoints (Prometheus‑friendly) can be exposed via the server module for external dashboards.

## 17. Security and Hardening Considerations

- ADN v2 must never be treated as a **trusted oracle** for protocol changes; it is one advisory signal among many.
- All network endpoints must be access‑controlled and, in production, protected by TLS and authentication.
- Operator‑facing actions (e.g. node shutdown) should include explicit confirmation or multi‑step workflows.
- The mesh layer is designed to be compatible with future **signed messages**, but signature schemes are intentionally out of scope for this v0.1 reference.

## 18. Extensibility

ADN v2 is designed to be extended via:

- new policy classes that plug into the policy engine
- additional telemetry sources (new collectors)
- custom action handlers for operator‑specific workflows

All extension points rely on clear dataclasses and enums defined in `models.py`, keeping the overall design simple and composable.
