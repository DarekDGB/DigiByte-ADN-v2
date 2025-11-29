from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class RiskLevel(str, Enum):
    NORMAL = "normal"
    ELEVATED = "elevated"
    HIGH = "high"
    CRITICAL = "critical"


class RiskState(RiskLevel):
    """
    Backwards-compatible alias for RiskLevel.

    Older ADN v2 modules (e.g. validator) import RiskState, but the new
    defense logic standardises on RiskLevel. We subclass here so those
    imports continue to work without changing behaviour.
    """
    pass


@dataclass
class RiskSignal:
    source: str
    level: RiskLevel
    score: float
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TelemetryPacket:
    node_id: str
    height: int
    mempool_size: int
    peer_count: int
    timestamp: float
    extra: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PolicyDecision:
    level: RiskLevel
    score: float
    reason: str
    actions: List[str] = field(default_factory=list)


@dataclass
class NodeState:
    node_id: str
    hardened_mode: bool = False
    last_decision: Optional[PolicyDecision] = None


@dataclass
class ActionResult:
    name: str
    success: bool
    detail: str = ""


# --- v2 defense-layer models (lockdown + actions) ---

class LockdownState(str, Enum):
    NONE = "NONE"
    PARTIAL = "PARTIAL"   # e.g. RPC throttling, withdrawal cool-downs
    FULL = "FULL"         # e.g. full RPC lockdown / isolate node


@dataclass
class DefenseEvent:
    """
    Single security-related event observed by ADN.
    Example types:
      - 'rpc_abuse'
      - 'withdrawal_spike'
      - 'sentinel_alert'
      - 'dqsn_critical'
    """
    event_type: str
    severity: float          # 0.0 – 1.0
    source: str              # local, sentinel, dqsn, wallet_guard, etc.
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class NodeDefenseConfig:
    """
    Configuration knobs for ADN behaviour.
    """
    lockdown_threshold: float = 0.75
    partial_lock_threshold: float = 0.5
    max_withdrawals_per_min: int = 50
    rpc_rate_limit: int = 1000  # requests per minute


@dataclass
class DefenseAction:
    """
    Action ADN decides to take.
    Examples:
      - 'ENTER_PARTIAL_LOCKDOWN'
      - 'ENTER_FULL_LOCKDOWN'
      - 'LIFT_LOCKDOWN'
      - 'THROTTLE_RPC'
    """
    action_type: str
    reason: str
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class NodeDefenseState:
    """
    Current ADN view of the node at the defense layer.
    """
    risk_level: RiskLevel = RiskLevel.NORMAL
    lockdown_state: LockdownState = LockdownState.NONE
    active_events: List[DefenseEvent] = field(default_factory=list)
    last_actions: List[DefenseAction] = field(default_factory=list)
