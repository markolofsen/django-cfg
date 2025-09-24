from typing import Literal, cast

OTPRequestRequestChannel = Literal["email", "phone"]

OTP_REQUEST_REQUEST_CHANNEL_VALUES: set[OTPRequestRequestChannel] = {
    "email",
    "phone",
}


def check_otp_request_request_channel(value: str) -> OTPRequestRequestChannel:
    if value in OTP_REQUEST_REQUEST_CHANNEL_VALUES:
        return cast(OTPRequestRequestChannel, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {OTP_REQUEST_REQUEST_CHANNEL_VALUES!r}")
