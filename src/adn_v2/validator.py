from __future__ import annotations

from typing import List

from .config import ADNConfig
from .models import RiskState, PolicyDecision


class ADNValidator:
    """
    Validation layer for ADN v2 decisions.

    This module makes sure that:
    - risk states are internally consistent
    - policy decisions respect configured rules
    - hardened / PQC modes are only triggered when allowed
    """

    def __init__(self, config: ADNConfig | None = None) -> None:
        self.config = config or ADNConfig.default()

    # -----------------------------
    # Public helpers
    # -----------------------------

    def validate_risk_state(self, state: RiskState) -> List[str]:
        """
        Validate a RiskState produced by Sentinel AI v2 or local heuristics.
        Returns a list of human-readable error strings.
        Empty list == valid.
        """
        errors: List[str] = []

        if not (0.0 <= state.risk_score <= 1.0):
            errors.append(f"risk_score out of range: {state.risk_score}")

        if state.status not in self.config.allowed_statuses:
            errors.append(f"invalid status: {state.status}")

        if state.source not in {"sentinel_v2", "local_heuristic", "manual_override"}:
            errors.append(f"unknown risk source: {state.source}")

        # sanity: critical should never have zero triggers
        if state.status == "CRITICAL" and not state.triggers:
            errors.append("CRITICAL state must contain at least one trigger")

        # sanity: NORMAL should not contain hard circuit-breaker triggers
        if state.status == "NORMAL":
            hard = [t for t in state.triggers if t.startswith("cb_")]
            if hard:
                errors.append(
                    f"NORMAL state contains circuit-breaker triggers: {hard}"
                )

        return errors

    def validate_policy_decision(
        self, decision: PolicyDecision, state: RiskState
    ) -> List[str]:
        """
        Validate that a PolicyDecision is compatible with the current RiskState
        and high-level config rules.
        """
        errors: List[str] = []

        # hardened mode allowed only for HIGH / CRITICAL
        if decision.hardened_mode and state.status not in {"HIGH", "CRITICAL"}:
            errors.append(
                f"hardened_mode enabled for non-high state: {state.status}"
            )

        # pqc_enforced only allowed when quantum flag is present
        if decision.pqc_enforced and "quantum_suspect" not in state.flags:
            errors.append("pqc_enforced without quantum_suspect flag in state")

        # peer quarantine should only happen from ELEVATED+
        if decision.quarantined_peers and state.status == "NORMAL":
            errors.append(
                "quarantined_peers set while state is NORMAL"
            )

        # fee escalations must be non-negative
        if decision.fee_multiplier < 1.0:
            errors.append(
                f"fee_multiplier below 1.0: {decision.fee_multiplier}"
            )

        # check against config hard limits
        if decision.fee_multiplier > self.config.max_fee_multiplier:
            errors.append(
                f"fee_multiplier {decision.fee_multiplier} "
                f"exceeds configured max {self.config.max_fee_multiplier}"
            )

        if decision.broadcast_paused and not self.config.allow_broadcast_pause:
            errors.append("broadcast_paused but config forbids pausing broadcast")

        return errors

    def is_safe(self, decision: PolicyDecision, state: RiskState) -> bool:
        """
        Convenience helper: True if both risk state and decision validate.
        """
        return not (self.validate_risk_state(state) or
                    self.validate_policy_decision(decision, state))
