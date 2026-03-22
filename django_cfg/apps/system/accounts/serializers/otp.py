from rest_framework import serializers

from ..models import CustomUser, OTPSecret
from ..services.email_validator import validate_email_address, EmailValidationError
from .profile import UserSerializer


class OTPSerializer(serializers.ModelSerializer):
    """Serializer for OTP operations."""

    class Meta:
        model = OTPSecret
        fields = ["email", "secret"]
        read_only_fields = ["secret"]


class OTPRequestSerializer(serializers.Serializer):
    """Serializer for OTP request."""

    identifier = serializers.CharField(
        help_text="Email address for OTP delivery"
    )
    source_url = serializers.URLField(
        required=False,
        allow_blank=True,
        help_text="Source URL for tracking registration (e.g., https://my.djangocfg.com)",
    )

    def validate_identifier(self, value):
        """Validate and normalize email address."""
        try:
            # Syntax + suspicious patterns + disposable blocklist.
            # MX check disabled here (sync serializer) — DNS is checked in OTPService
            # on first OTP request so invalid domains are caught before user creation.
            return validate_email_address(value)
        except EmailValidationError as exc:
            raise serializers.ValidationError(str(exc)) from exc

    def validate_source_url(self, value):
        if not value or not value.strip():
            return None
        return value


class OTPVerifySerializer(serializers.Serializer):
    """Serializer for OTP verification."""

    identifier = serializers.CharField(
        help_text="Email address used for OTP request"
    )
    otp = serializers.CharField(max_length=6, min_length=6)
    source_url = serializers.URLField(
        required=False,
        allow_blank=True,
        help_text="Source URL for tracking login (e.g., https://my.djangocfg.com)",
    )

    def validate_identifier(self, value):
        """Validate and normalize email address."""
        try:
            return validate_email_address(value)
        except EmailValidationError as exc:
            raise serializers.ValidationError(str(exc)) from exc

    def validate_otp(self, value):
        """Normalize and validate OTP code."""
        value = value.strip()
        if not value.isdigit():
            raise serializers.ValidationError("OTP must contain only digits.")
        return value

    def validate_source_url(self, value):
        if not value or not value.strip():
            return None
        return value


class OTPVerifyResponseSerializer(serializers.Serializer):
    """
    OTP verification response.

    When 2FA is required:
    - requires_2fa: True
    - session_id: UUID of 2FA verification session
    - refresh/access/user: null

    When 2FA is not required:
    - requires_2fa: False
    - session_id: null
    - refresh/access/user: populated
    """

    requires_2fa = serializers.BooleanField(
        default=False,
        help_text="Whether 2FA verification is required"
    )
    session_id = serializers.UUIDField(
        required=False,
        allow_null=True,
        help_text="2FA session ID (if requires_2fa is True)"
    )
    refresh = serializers.CharField(
        required=False,
        allow_null=True,
        help_text="JWT refresh token (if requires_2fa is False)"
    )
    access = serializers.CharField(
        required=False,
        allow_null=True,
        help_text="JWT access token (if requires_2fa is False)"
    )
    user = UserSerializer(
        required=False,
        allow_null=True,
        help_text="User information (if requires_2fa is False)"
    )
    should_prompt_2fa = serializers.BooleanField(
        required=False,
        help_text="Whether user should be prompted to enable 2FA"
    )


class OTPRequestResponseSerializer(serializers.Serializer):
    """OTP request response."""

    message = serializers.CharField(help_text="Success message")


class OTPErrorResponseSerializer(serializers.Serializer):
    """
    Typed error response for OTP operations.

    error_code values:
      - invalid_identifier   — malformed email
      - cooldown             — too soon after last request (retry_after = seconds)
      - hourly_limit         — hourly quota exceeded   (retry_after = seconds until reset)
      - daily_limit          — daily quota exceeded    (retry_after = seconds until reset)
      - rate_limited         — IP-level rate limit hit (no retry_after)
      - user_creation_failed — internal error creating account
      - send_failed          — transport error (email / SMS)
      - internal_error       — unexpected server error
    """

    error = serializers.CharField(
        help_text="Human-readable error message"
    )
    error_code = serializers.CharField(
        help_text="Machine-readable error code",
        required=False,
        allow_null=True,
    )
    retry_after = serializers.IntegerField(
        help_text="Seconds until the client may retry (present only for rate-limit errors)",
        required=False,
        allow_null=True,
    )
