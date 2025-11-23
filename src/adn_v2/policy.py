from __future__ import annotations

from typing import Optional

from .config import ADNConfig
from .models import (
    ActionPlan,
    ChainTelemetry,
    PolicyDecision,
    RiskState,
    SentinelSignal,
    WalletSignal,
)


def _merge_risk_state(
    sentinel_state: RiskState,
    wallet_state: Optional[RiskState],
) -> RiskState:
    """
    Combine Sentinel + wallet states, taking the worst case.
    """

    if wallet_state is None:
        return sentinel_state

    order = [RiskState.NORMAL, RiskState.ELEVATED, RiskState.HIGH, RiskState.CRITICAL]
    return max(sentinel_state, wallet_state, key=lambda s: order.index(s))


class PolicyEngine:
    """
    Stateless policy evaluator.

    Given:
      - config
      - chain telemetry
      - Sentinel AI v2 signal
      - optional wallet-guardian signal

    it produces:
      - PolicyDecision
      - ActionPlan (derived from the decision)
    """

    def __init__(self, config: ADNConfig) -> None:
        self.config = config

    # ---------- Public API ----------

    def evaluate(
        self,
        telemetry: ChainTelemetry,
        sentinel: SentinelSignal,
        wallet: Optional[WalletSignal] = None,
    ) -> ActionPlan:
        decision = self._evaluate_policy(telemetry, sentinel, wallet)
        return self._build_action_plan(decision, telemetry, sentinel, wallet)

    # ---------- Internals ----------

    def _evaluate_policy(
        self,
        telemetry: ChainTelemetry,
        sentinel: SentinelSignal,
        wallet: Optional[WalletSignal],
    ) -> PolicyDecision:
        # Decide effective risk state from Sentinel score + wallet state.
        risk_state = self._score_to_state(sentinel.risk_score)
        risk_state = _merge_risk_state(
            risk_state, wallet.aggregated_state if wallet else None
        )

        decision = PolicyDecision(effective_state=risk_state)

        if risk_state == RiskState.ELEVATED:
            decision.fee_multiplier = self.config.elevated_fee_multiplier
            decision.notes = "Elevated risk – modest fee increase."

        elif risk_state == RiskState.HIGH:
            decision.fee_multiplier = self.config.high_fee_multiplier
            decision.hardened_mode = self.config.enable_hardened_on_high
            decision.pqc_enforced = self.config.enable_pqc_on_high
            decision.notes = "High risk – hardened mode + PQC (if enabled)."

        elif risk_state == RiskState.CRITICAL:
            decision.fee_multiplier = self.config.critical_fee_multiplier
            decision.hardened_mode = self.config.enable_hardened_on_critical
            decision.pqc_enforced = self.config.enable_pqc_on_critical
            if self.config.global_lock_on_critical:
                decision.notes = "Critical risk – global defensive posture."
            else:
                decision.notes = "Critical risk – mitigations without full lock."

        else:
            decision.fee_multiplier = self.config.normal_fee_multiplier
            decision.notes = "Normal conditions."

        return decision

    def _score_to_state(self, score: float) -> RiskState:
        """
        Translate Sentinel risk_score into a coarse-grained state.
        """

        if score >= self.config.critical_threshold:
            return RiskState.CRITICAL
        if score >= self.config.high_threshold:
            return RiskState.HIGH
        if score >= self.config.elevated_threshold:
            return RiskState.ELEVATED
        return RiskState.NORMAL

    def _build_action_plan(
        self,
        decision: PolicyDecision,
        telemetry: ChainTelemetry,
        sentinel: SentinelSignal,
        wallet: Optional[WalletSignal],
    ) -> ActionPlan:
        """
        Convert a PolicyDecision into a concrete action plan.
        """

        plan = ActionPlan(
            decision=decision,
            enable_pqc=decision.pqc_enforced,
            enable_hardened_mode=decision.hardened_mode,
        )

        # Simple fee logic – integrators can extend this.
        base_min_fee = 1.0  # sat/byte – placeholder, to be replaced by integrators
        plan.set_min_fee_rate = base_min_fee * decision.fee_multiplier

        # Example advisory message (for logs / UI / monitoring).
        plan.broadcast_advisory = decision.notes

        # Attach some context as metadata (non-consensus).
        plan.metadata.update(
            {
                "telemetry_height": telemetry.height,
                "telemetry_mempool": telemetry.mempool_size,
                "sentinel_state": sentinel.risk_state.value,
                "sentinel_score": sentinel.risk_score,
                "wallet_state": wallet.aggregated_state.value
                if wallet
                else None,
            }
        )

        return plan
