"""
Minimal HTTP interface skeleton for ADN v2.

This keeps dependencies optional – real deployments can swap this
for FastAPI, gRPC, or direct node integration.
"""

from __future__ import annotations


def run_demo_server() -> None:
    # Intentionally tiny placeholder – we do NOT ship a real server here.
    print("ADN v2 demo server stub – replace with real HTTP/gRPC implementation.")


if __name__ == "__main__":
    run_demo_server()
