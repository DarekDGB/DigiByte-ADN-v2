from adn_v2.config import ADNConfig
from adn_v3 import ADNv3
from adn_v3.contracts.v3_reason_codes import ReasonCode


def test_contract_v3_unknown_key_inside_event_fails_closed():
    v3 = ADNv3(config=ADNConfig())

    request = {
        "contract_version": 3,
        "request_id": "test",
        "component": "adn",
        "events": [
            {
                "event_type": "REORG_WARNING",
                "severity": 0.6,
                "source": "dqsn",
                "metadata": {"depth": 2},
                "evil": "inject",  # unknown key on purpose
            }
        ],
    }

    response = v3.evaluate(request)

    assert response["decision"] == "ERROR"
    assert response["meta"]["fail_closed"] is True
    assert ReasonCode.ADN_ERROR_EVENT_UNKNOWN_KEY.value in response["reason_codes"]
