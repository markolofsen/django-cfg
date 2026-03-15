"""Serializers for TOTP device management."""

from rest_framework import serializers

from ..models import DeviceStatus, TOTPDevice


class DeviceListSerializer(serializers.ModelSerializer):
    """Serializer for listing TOTP devices."""

    class Meta:
        model = TOTPDevice
        fields = [
            "id",
            "name",
            "is_primary",
            "status",
            "created_at",
            "confirmed_at",
            "last_used_at",
        ]
        read_only_fields = fields


class DeviceDeleteSerializer(serializers.Serializer):
    """Serializer for device deletion (requires verification code)."""

    code = serializers.CharField(
        min_length=6,
        max_length=6,
        required=False,
        help_text="TOTP code for verification (required for last/primary device)",
    )

    def validate_code(self, value):
        """Validate code is 6 digits if provided."""
        if value and not value.isdigit():
            raise serializers.ValidationError("Code must be 6 digits")
        return value


class DisableSerializer(serializers.Serializer):
    """Serializer for completely disabling 2FA."""

    code = serializers.CharField(
        min_length=6,
        max_length=6,
        help_text="TOTP code for verification",
    )

    def validate_code(self, value):
        """Validate code is 6 digits."""
        if not value.isdigit():
            raise serializers.ValidationError("Code must be 6 digits")
        return value


class DeviceListResponseSerializer(serializers.Serializer):
    """Response serializer for device list endpoint."""

    devices = DeviceListSerializer(many=True)
    has_2fa_enabled = serializers.BooleanField()




