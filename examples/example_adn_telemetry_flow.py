"""
Example: full ADN v2 telemetry → risk → policy flow.

This script shows how a DigiByte node (or monitoring agent) can:
  1. Build a raw telemetry dict.
  2. Feed it into ADNEngine.process_raw_telemetry(...).
  3. Inspect the resulting PolicyDecision and node hardened state.
"""

from adn_v2.engine import ADNEngine


def main() -> None:
    # 1. Create an engine instance for a single node
    engine = ADNEngine(node_id="dgb-node-1")

    # 2. Simulate a raw telemetry snapshot from the node
    raw_telemetry = {
        "height": 1_234_567,
        "mempool_size": 25_000,   # large mempool => potential congestion / attack
        "peer_count": 1,          # very low peers => connectivity risk
        # extra fields are passed through in TelemetryPacket.extra
        "cpu_usage": 0.85,
        "disk_usage": 0.70,
    }

    # 3. Let ADN v2 derive RiskSignal entries and a PolicyDecision
    decision = engine.process_raw_telemetry(raw_telemetry)

    # 4. Inspect results
    print("=== ADN v2 Telemetry Flow Example ===")
    print("Node ID:              ", engine.state.node_id)
    print("Risk level:           ", decision.level.name)
    print("Risk score:           ", decision.score)
    print("Decision reason:      ", decision.reason)
    print("Suggested actions:    ", decision.actions)
    print("Node hardened mode?:  ", engine.state.hardened_mode)


if __name__ == "__main__":
    main()
