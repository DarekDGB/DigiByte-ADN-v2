from __future__ import annotations

from enum import Enum


class ReasonCode(str, Enum):
    # success / neutral
    ADN_OK = "ADN_OK"

    # indicates "valid request produced a defensive signal" (contract-facing, minimal)
    ADN_V2_SIGNAL = "ADN_V2_SIGNAL"

    # fail-closed contract errors
    ADN_ERROR_INVALID_REQUEST = "ADN_ERROR_INVALID_REQUEST"
    ADN_ERROR_SCHEMA_VERSION = "ADN_ERROR_SCHEMA_VERSION"
    ADN_ERROR_UNKNOWN_KEY = "ADN_ERROR_UNKNOWN_KEY"
    ADN_ERROR_BAD_NUMBER = "ADN_ERROR_BAD_NUMBER"

    # event-level schema hardening
    ADN_ERROR_EVENT_UNKNOWN_KEY = "ADN_ERROR_EVENT_UNKNOWN_KEY"

    # oversize / abuse prevention
    ADN_ERROR_OVERSIZE = "ADN_ERROR_OVERSIZE"
