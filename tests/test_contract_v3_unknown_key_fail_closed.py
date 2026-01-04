from adn_v2.config import ADNConfig
from adn_v2.v3 import ADNv3
from adn_v2.contracts.v3_reason_codes import ReasonCode


def test_contract_v3_unknown_top_level_key_fails_closed():
    v3 = ADNv3(config=ADNConfig())

    request = {
        "contract_version": 3,
        "request_id": "test",
        "component": "adn",
        "events": [],
        "hacker_key": "nope",  # unknown key on purpose
    }

    response = v3.evaluate(request)

    assert response["decision"] == "ERROR"
    assert response["meta"]["fail_closed"] is True
    assert ReasonCode.ADN_ERROR_UNKNOWN_KEY.value in response["reason_codes"]
