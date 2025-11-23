from __future__ import annotations

import argparse
import json
from typing import List

from .client import ADNClient
from .models import ChainSnapshot, SentinelSignal, GuardianSignal, RiskLevel


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="adn-v2",
        description="Reference CLI for the DigiByte Autonomous Defense Node v2",
    )
    parser.add_argument(
        "--input",
        help="Path to a JSON file with chain/sentinel/guardian demo data",
        required=False,
    )

    args = parser.parse_args(argv)

    # Very simple demo wiring
    if not args.input:
        print("ADN v2 CLI skeleton – no input provided.")
        return 0

    with open(args.input, "r", encoding="utf-8") as f:
        payload = json.load(f)

    chain = ChainSnapshot(**payload["chain"])
    sentinel = SentinelSignal(
        risk_score=payload["sentinel"]["risk_score"],
        level=RiskLevel(payload["sentinel"]["level"]),
        details=payload["sentinel"]["details"],
    )
    guardians = [
        GuardianSignal(
            wallet_id=g["wallet_id"],
            level=RiskLevel(g["level"]),
            reasons=g["reasons"],
        )
        for g in payload.get("guardians", [])
    ]

    client = ADNClient()
    decision = client.evaluate(chain, sentinel, guardians)
    print("Final decision:", decision)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
