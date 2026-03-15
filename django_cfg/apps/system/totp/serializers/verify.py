"""Serializers for 2FA verification during login."""

from rest_framework import serializers

from django_cfg.apps.system.accounts.serializers import UserSerializer


# Simplified user serializer without centrifugo to avoid Swift type conflicts
class TotpVerifyUserSerializer(UserSerializer):
    """User data returned after 2FA verification."""

    class Meta(UserSerializer.Meta):
        fields = [f for f in UserSerializer.Meta.fields if f != "centrifugo"]


class VerifySerializer(serializers.Serializer):
    """Serializer for TOTP code verification during login."""

    session_id = serializers.UUIDField(
        help_text="2FA session ID from login response"
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


class VerifyBackupSerializer(serializers.Serializer):
    """Serializer for backup code verification during login."""

    session_id = serializers.UUIDField(
        help_text="2FA session ID from login response"
    )
    backup_code = serializers.CharField(
        min_length=8,
        max_length=8,
        help_text="8-character backup recovery code",
    )

    def validate_backup_code(self, value):
        """Validate backup code format."""
        cleaned = value.strip().lower()
        if len(cleaned) != 8:
            raise serializers.ValidationError("Backup code must be 8 characters")
        return cleaned


class VerifyResponseSerializer(serializers.Serializer):
    """Response serializer for successful 2FA verification."""

    message = serializers.CharField()
    access_token = serializers.CharField(
        help_text="JWT access token"
    )
    refresh_token = serializers.CharField(
        help_text="JWT refresh token"
    )
    user = TotpVerifyUserSerializer(
        help_text="User profile data"
    )
    remaining_backup_codes = serializers.IntegerField(
        required=False,
        help_text="Number of remaining backup codes (if backup code was used)",
    )
    warning = serializers.CharField(
        required=False,
        help_text="Warning message (e.g., low backup codes)",
    )




