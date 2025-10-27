from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from ..enums import OTPRequestRequestChannel, OTPVerifyRequestChannel


class OTPRequestResponse(BaseModel):
    """
    OTP request response.

    Response model (includes read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="allow",
        frozen=False,
    )

    message: str = Field(description='Success message')



class OTPErrorResponse(BaseModel):
    """
    Error response for OTP operations.

    Response model (includes read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="allow",
        frozen=False,
    )

    error: str = Field(description='Error message')



class OTPVerifyResponse(BaseModel):
    """
    OTP verification response.

    Response model (includes read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="allow",
        frozen=False,
    )

    refresh: str = Field(description='JWT refresh token')
    access: str = Field(description='JWT access token')
    user: Any = ...



class OTPRequestRequest(BaseModel):
    """
    Serializer for OTP request.

    Request model (no read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="allow",
        frozen=False,
    )

    identifier: str = Field(description='Email address or phone number for OTP delivery', min_length=1)
    channel: OTPRequestRequestChannel = Field(None, description="Delivery channel: 'email' or 'phone'. Auto-detected if not provided.\n\n* `email` - Email\n* `phone` - Phone")
    source_url: str = Field(None, description='Source URL for tracking registration (e.g., https://dashboard.unrealon.com)')



class OTPVerifyRequest(BaseModel):
    """
    Serializer for OTP verification.

    Request model (no read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="allow",
        frozen=False,
    )

    identifier: str = Field(description='Email address or phone number used for OTP request', min_length=1)
    otp: str = Field(min_length=6, max_length=6)
    channel: OTPVerifyRequestChannel = Field(None, description="Delivery channel: 'email' or 'phone'. Auto-detected if not provided.\n\n* `email` - Email\n* `phone` - Phone")
    source_url: str = Field(None, description='Source URL for tracking login (e.g., https://dashboard.unrealon.com)')



