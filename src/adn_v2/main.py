from .config import CONFIG
from .validator import RiskValidator
from .policy import PolicyEngine
from .actions import ActionExecutor
from .telemetry import TelemetryClient
from .server import ADNServer


class AutonomousDefenseNodeV2:
    def __init__(self):
        self.validator = RiskValidator(CONFIG)
        self.policy = PolicyEngine(CONFIG)
        self.actions = ActionExecutor(CONFIG)
        self.telemetry = TelemetryClient(CONFIG)
        self.server = ADNServer(self.validator, self.policy)

    def run(self):
        self.telemetry.log_system_event("ADN_v2_startup")

        state = self.server.snapshot_network_state()
        score = self.validator.evaluate(state)
        decision = self.policy.decide(score)

        self.telemetry.log_risk(score, decision)
        self.actions.execute(decision)

        return {
            "state": state,
            "score": score,
            "decision": decision
        }


def main():
    node = AutonomousDefenseNodeV2()
    result = node.run()
    print("ADN v2 executed:", result)


if __name__ == "__main__":
    main()
