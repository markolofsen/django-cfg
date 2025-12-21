"""Serializers for TOTP device setup flow."""

from rest_framework import serializers

from ..models import TOTPDevice


class SetupSerializer(serializers.Serializer):
    """Serializer for starting 2FA setup."""

    device_name = serializers.CharField(
        max_length=100,
        required=False,
        default="Authenticator",
        help_text="Device name for identification (e.g., 'My iPhone')",
    )


class SetupResponseSerializer(serializers.Serializer):
    """Response serializer for setup initiation."""

    device_id = serializers.UUIDField(
        help_text="Device ID to use for confirmation"
    )
    secret = serializers.CharField(
        help_text="Base32-encoded TOTP secret (for manual entry)"
    )
    provisioning_uri = serializers.CharField(
        help_text="otpauth:// URI for QR code generation"
    )
    qr_code_base64 = serializers.CharField(
        help_text="Base64-encoded QR code image (data URI)"
    )
    expires_in = serializers.IntegerField(
        help_text="Seconds until setup expires (typically 600 = 10 minutes)"
    )


class ConfirmSetupSerializer(serializers.Serializer):
    """Serializer for confirming 2FA setup with first code."""

    device_id = serializers.UUIDField(
        help_text="Device ID from setup response"
    )
    code = serializers.CharField(
        min_length=6,
        max_length=6,
        help_text="6-digit TOTP code from authenticator app",
    )

    def validate_code(self, value):
        """Validate code is 6 digits."""
        if not value.isdigit():
            raise serializers.ValidationError("Code must be 6 digits")
        return value


class ConfirmSetupResponseSerializer(serializers.Serializer):
    """Response serializer for setup confirmation."""

    message = serializers.CharField()
    backup_codes = serializers.ListField(
        child=serializers.CharField(),
        help_text="List of backup recovery codes (save these!)",
    )
    backup_codes_warning = serializers.CharField(
        help_text="Warning message about backup codes"
    )




