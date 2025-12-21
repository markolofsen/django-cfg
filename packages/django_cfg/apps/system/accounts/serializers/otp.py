from rest_framework import serializers

from ..models import OTPSecret
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
        help_text="Email address or phone number for OTP delivery"
    )
    channel = serializers.ChoiceField(
        choices=[('email', 'Email'), ('phone', 'Phone')],
        required=False,
        help_text="Delivery channel: 'email' or 'phone'. Auto-detected if not provided."
    )
    source_url = serializers.URLField(
        required=False,
        allow_blank=True,
        help_text="Source URL for tracking registration (e.g., https://my.djangocfg.com)",
    )

    def validate_identifier(self, value):
        """Validate identifier format."""
        if not value:
            raise serializers.ValidationError("Identifier is required.")

        value = value.strip()
        if not value:
            raise serializers.ValidationError("Identifier cannot be empty.")

        # Auto-detect if it's email or phone
        if '@' in value:
            # Basic email validation
            if not value.count('@') == 1:
                raise serializers.ValidationError("Invalid email format.")
            return value.lower()
        else:
            # Assume it's a phone number - basic validation
            # Remove common phone number characters for validation
            clean_phone = ''.join(c for c in value if c.isdigit() or c in '+')
            if len(clean_phone) < 10:
                raise serializers.ValidationError("Phone number must be at least 10 digits.")
            return value

    def validate_source_url(self, value):
        """Validate source URL format."""
        if not value or not value.strip():
            return None
        return value


class OTPVerifySerializer(serializers.Serializer):
    """Serializer for OTP verification."""

    identifier = serializers.CharField(
        help_text="Email address or phone number used for OTP request"
    )
    otp = serializers.CharField(max_length=6, min_length=6)
    channel = serializers.ChoiceField(
        choices=[('email', 'Email'), ('phone', 'Phone')],
        required=False,
        help_text="Delivery channel: 'email' or 'phone'. Auto-detected if not provided."
    )
    source_url = serializers.URLField(
        required=False,
        allow_blank=True,
        help_text="Source URL for tracking login (e.g., https://my.djangocfg.com)",
    )

    def validate_identifier(self, value):
        """Validate identifier format."""
        if not value:
            raise serializers.ValidationError("Identifier is required.")

        value = value.strip()
        if not value:
            raise serializers.ValidationError("Identifier cannot be empty.")

        # Auto-detect if it's email or phone
        if '@' in value:
            # Basic email validation
            if not value.count('@') == 1:
                raise serializers.ValidationError("Invalid email format.")
            return value.lower()
        else:
            # Assume it's a phone number - basic validation
            # Remove common phone number characters for validation
            clean_phone = ''.join(c for c in value if c.isdigit() or c in '+')
            if len(clean_phone) < 10:
                raise serializers.ValidationError("Phone number must be at least 10 digits.")
            return value

    def validate_otp(self, value):
        """Validate OTP format."""
        if not value.isdigit():
            raise serializers.ValidationError("OTP must contain only digits.")
        return value

    def validate_source_url(self, value):
        """Validate source URL format."""
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
    """Error response for OTP operations."""

    error = serializers.CharField(help_text="Error message")
