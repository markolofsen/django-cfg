"""Enumeration types re-exported from generated API.

All enums used across the API client.
"""

from ..generated.cfg.enums import (
    CfgRqTestingScheduleDemoCreateRequestScheduleType,
    DeviceListStatus,
    OAuthConnectionProvider,
    OTPRequestRequestChannel,
    RunDemoRequestRequestScenario,
    StressTestRequestRequestScenario,
)

__all__ = [
    # TOTP / Device
    "DeviceListStatus",
    # OAuth
    "OAuthConnectionProvider",
    # OTP
    "OTPRequestRequestChannel",
    # RQ Testing
    "RunDemoRequestRequestScenario",
    "StressTestRequestRequestScenario",
    "CfgRqTestingScheduleDemoCreateRequestScheduleType",
]
