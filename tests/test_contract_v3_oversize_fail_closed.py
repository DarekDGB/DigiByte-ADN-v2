from adn_v2.config import ADNConfig
from adn_v2.v3 import ADNv3
from adn_v2.contracts.v3_reason_codes import ReasonCode


def test_contract_v3_too_many_events_fails_closed():
    v3 = ADNv3(config=ADNConfig())

    # 201 events (default cap will be 200)
    events = [
        {"event_type": "PING", "severity": 0.1, "source": "dqsn", "metadata": {}}
        for _ in range(201)
    ]

    request = {
        "contract_version": 3,
        "request_id": "test",
        "component": "adn",
        "events": events,
    }

    response = v3.evaluate(request)

    assert response["decision"] == "ERROR"
    assert response["meta"]["fail_closed"] is True
    assert ReasonCode.ADN_ERROR_OVERSIZE.value in response["reason_codes"]


def test_contract_v3_metadata_too_large_fails_closed():
    v3 = ADNv3(config=ADNConfig())

    big = "x" * (16_384 + 1)  # 16KB + 1

    request = {
        "contract_version": 3,
        "request_id": "test",
        "component": "adn",
        "events": [
            {"event_type": "REORG_WARNING", "severity": 0.6, "source": "dqsn", "metadata": {"blob": big}},
        ],
    }

    response = v3.evaluate(request)

    assert response["decision"] == "ERROR"
    assert response["meta"]["fail_closed"] is True
    assert ReasonCode.ADN_ERROR_OVERSIZE.value in response["reason_codes"]
