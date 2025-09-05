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

    email = serializers.EmailField()
    source_url = serializers.URLField(
        required=False,
        allow_blank=True,
        help_text="Source URL for tracking registration (e.g., https://dashboard.unrealon.com)",
    )

    def validate_email(self, value):
        """Validate email format."""
        if not value:
            raise serializers.ValidationError("Email is required.")
        return value.lower()

    def validate_source_url(self, value):
        """Validate source URL format."""
        if not value or not value.strip():
            return None
        return value


class OTPVerifySerializer(serializers.Serializer):
    """Serializer for OTP verification."""

    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6, min_length=6)
    source_url = serializers.URLField(
        required=False,
        allow_blank=True,
        help_text="Source URL for tracking login (e.g., https://dashboard.unrealon.com)",
    )

    def validate_email(self, value):
        """Validate email format."""
        if not value:
            raise serializers.ValidationError("Email is required.")
        return value.lower()

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
    """OTP verification response."""

    refresh = serializers.CharField(help_text="JWT refresh token")
    access = serializers.CharField(help_text="JWT access token")
    user = UserSerializer(help_text="User information")


class OTPRequestResponseSerializer(serializers.Serializer):
    """OTP request response."""

    message = serializers.CharField(help_text="Success message")


class OTPErrorResponseSerializer(serializers.Serializer):
    """Error response for OTP operations."""

    error = serializers.CharField(help_text="Error message")
