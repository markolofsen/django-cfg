from typing import Literal, cast

OTPVerifyRequestChannel = Literal["email", "phone"]

OTP_VERIFY_REQUEST_CHANNEL_VALUES: set[OTPVerifyRequestChannel] = {
    "email",
    "phone",
}


def check_otp_verify_request_channel(value: str) -> OTPVerifyRequestChannel:
    if value in OTP_VERIFY_REQUEST_CHANNEL_VALUES:
        return cast(OTPVerifyRequestChannel, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {OTP_VERIFY_REQUEST_CHANNEL_VALUES!r}")
