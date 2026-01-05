# 🔐 ADN — Shield Contract v3

**Component:** ADN (Active Defence Network)  
**Contract Version:** `3`  
**Repository:** DigiByte-ADN (formerly DigiByte-ADN-v2)  
**License:** MIT  
**Author:** DarekDGB

---

## Purpose

This document defines the **public, contract-facing interface** of ADN under **Shield Contract v3**.

The v3 contract exists to ensure that ADN is:
- **Fail-closed** (invalid input is rejected)
- **Deterministic** (same input → same output → same `context_hash`)
- **Auditable** (behavior is enforced by tests)
- **Non-consensus** (ADN does not modify DigiByte rules)
- **Read-only with respect to keys** (ADN never signs)

This contract is designed to survive review from skeptical engineers who only trust:
- schema
- tests
- deterministic output behavior

---

## Core Guarantees (v3)

### 1) Hard Version Gate
Any request where `contract_version != 3` **MUST fail closed**.

### 2) Fail-Closed by Default
Invalid requests **MUST** return:
- `decision: "ERROR"`
- `meta.fail_closed: true`
- a v3 reason code explaining the rejection

### 3) Strict Schema
- Unknown **top-level** keys are rejected.
- Unknown **event-level** keys are rejected.
- NaN / Infinity values are rejected.
- Oversized requests are rejected.

### 4) Deterministic Outputs
`context_hash` is computed from stable input fields and decision results.

**Never include**:
- timestamps
- latency values
- random identifiers
- host state

### 5) No Signing, No Execution
ADN:
- does **not** hold keys
- does **not** sign transactions
- does **not** execute wallet actions
- does **not** change chain consensus rules

ADN outputs **defensive decisions and recommended actions only**.

---

## Request Contract (v3)

### Top-Level Schema

```json
{
  "contract_version": 3,
  "component": "adn",
  "request_id": "string",
  "events": [ ... ]
}
```

### Field Requirements

- `contract_version` (int)
  - MUST equal `3`
- `component` (string)
  - MUST equal `"adn"`
- `request_id` (string)
  - REQUIRED
  - SHOULD be stable and caller-supplied
- `events` (array)
  - REQUIRED
  - MAY be empty (but still valid)
  - MUST not exceed **MAX_EVENTS** (default: 200)

### Unknown Key Rejection

- Any unknown top-level key → fail-closed
- Any unknown event-level key → fail-closed

---

## Event Schema (v3)

Each element in `events[]` MUST be a JSON object containing **only**:

```json
{
  "event_type": "string",
  "severity": 0.0,
  "source": "string",
  "metadata": {}
}
```

### Event Fields

- `event_type` (string, required)
  - non-empty
- `severity` (number, required)
  - range: `0.0 <= severity <= 1.0`
  - NaN/Infinity rejected
- `source` (string, required)
  - non-empty
- `metadata` (object, optional)
  - defaults to `{}` if missing or null
  - MUST be an object if present
  - serialized size MUST not exceed **MAX_METADATA_BYTES** (default: 16KB)

### Unknown Event Keys

Any extra keys (example: `"evil": "inject"`) **MUST fail closed**.

---

## Oversize / Abuse Protection

ADN v3 enforces:

- **MAX_EVENTS**: 200
- **MAX_METADATA_BYTES**: 16,384 bytes (16KB), per event

If exceeded, ADN MUST fail closed with:
- `decision: "ERROR"`
- reason code `ADN_ERROR_OVERSIZE`

---

## Response Contract (v3)

### Success Response (valid request)

```json
{
  "contract_version": 3,
  "component": "adn",
  "request_id": "string",
  "context_hash": "sha256_hex",
  "decision": "ALLOW | WARN | BLOCK",
  "risk": {
    "level": "normal | elevated | high | critical",
    "lockdown_state": "none | partial | full"
  },
  "actions": [
    {
      "action_type": "string",
      "reason": "string",
      "metadata": {}
    }
  ],
  "reason_codes": ["ADN_OK | ADN_V2_SIGNAL"],
  "evidence": {
    "active_events_count": 0
  },
  "meta": {
    "latency_ms": 0,
    "fail_closed": true
  }
}
```

### Error Response (fail-closed)

```json
{
  "contract_version": 3,
  "component": "adn",
  "request_id": "string",
  "context_hash": "sha256_hex",
  "decision": "ERROR",
  "risk": { "level": "unknown", "lockdown_state": "unknown" },
  "actions": [],
  "reason_codes": ["<REASON_CODE>"],
  "evidence": { "details": { "error": "<REASON_CODE>" } },
  "meta": { "latency_ms": 0, "fail_closed": true }
}
```

---

## Decision Semantics

ADN maps internal defense state into contract decisions using **deny-by-default** rules:

- `lockdown_state == full` → `BLOCK`
- `lockdown_state == partial` → `WARN`
- otherwise by `risk.level`:
  - normal → ALLOW
  - elevated → WARN
  - high/critical → BLOCK

If uncertain → **BLOCK** (deny-by-default).

---

## Reason Codes (Contract-Facing)

Minimal, stable v3 reason codes:

### Normal outcome
- `ADN_OK`  
- `ADN_V2_SIGNAL` (valid request produced a defensive signal)

### Fail-closed errors
- `ADN_ERROR_SCHEMA_VERSION`
- `ADN_ERROR_INVALID_REQUEST`
- `ADN_ERROR_UNKNOWN_KEY`
- `ADN_ERROR_BAD_NUMBER`
- `ADN_ERROR_EVENT_UNKNOWN_KEY`
- `ADN_ERROR_OVERSIZE`

---

## Context Hash Rules (Deterministic)

`context_hash` MUST be computed from stable fields only.

Allowed inputs:
- `component`
- `contract_version`
- `request_id`
- `events` (canonical request form)
- `node_defense_config` fingerprint
- `decision`, `risk`, `actions`, `reason_codes`

Forbidden inputs:
- timestamps
- latency values
- random data
- environment-dependent values

---

## Non-Goals / Explicit Forbidden Powers

ADN MUST NOT:
- sign anything
- generate keys
- transmit private material
- modify node consensus behavior
- interfere with block acceptance rules
- claim to “stop quantum attacks” by itself

ADN provides:
> **decisions + recommended defensive actions**  
not authority, not execution, not consensus.

---

## Test Enforcement

This contract is enforced by CI tests which prove:
- version gating fails closed
- unknown keys rejected (top-level and event-level)
- NaN/Infinity rejected
- oversize rejected (events and metadata)
- behavior remains consistent via v2→v3 no-drift regression locks

If tests fail, the contract is considered broken.

---
