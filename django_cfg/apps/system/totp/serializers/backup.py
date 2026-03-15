"""Serializers for backup recovery codes."""

from rest_framework import serializers


class BackupCodesStatusSerializer(serializers.Serializer):
    """Serializer for backup codes status."""

    remaining_count = serializers.IntegerField(
        help_text="Number of unused backup codes"
    )
    total_generated = serializers.IntegerField(
        help_text="Total number of codes generated"
    )
    warning = serializers.CharField(
        required=False,
        allow_null=True,
        help_text="Warning if running low on codes",
    )


class BackupCodesRegenerateSerializer(serializers.Serializer):
    """Serializer for regenerating backup codes."""

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


class BackupCodesRegenerateResponseSerializer(serializers.Serializer):
    """Response serializer for backup codes regeneration."""

    backup_codes = serializers.ListField(
        child=serializers.CharField(),
        help_text="List of new backup codes (save these!)",
    )
    warning = serializers.CharField(
        help_text="Warning about previous codes being invalidated"
    )




