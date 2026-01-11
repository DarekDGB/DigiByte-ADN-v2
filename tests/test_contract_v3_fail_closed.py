import pytest

from adn_v2.config import ADNConfig
from adn_v3 import ADNv3
from adn_v3.contracts.v3_reason_codes import ReasonCode


def test_contract_v3_invalid_version_fails_closed():
    """
    Archangel Michael invariant:
    Any request that is not contract_version == 3 MUST fail closed.
    """
    v3 = ADNv3(config=ADNConfig())

    request = {
        "contract_version": 2,  # invalid on purpose
        "request_id": "test",
        "component": "adn",
        "events": [],
    }

    response = v3.evaluate(request)

    assert response["decision"] == "ERROR"
    assert response["meta"]["fail_closed"] is True
    assert ReasonCode.ADN_ERROR_SCHEMA_VERSION.value in response["reason_codes"]
