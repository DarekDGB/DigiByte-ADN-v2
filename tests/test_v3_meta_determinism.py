from adn_v2.v3 import ADNv3


def test_v3_meta_latency_is_deterministic_zero():
    v3 = ADNv3()

    req = {
        "contract_version": 3,
        "component": "adn",
        "request_id": "meta-determinism",
        "events": [],
    }

    r1 = v3.evaluate(req)
    r2 = v3.evaluate(req)

    assert r1["meta"]["latency_ms"] == 0
    assert r2["meta"]["latency_ms"] == 0
    assert r1["meta"]["fail_closed"] is True
    assert r2["meta"]["fail_closed"] is True
