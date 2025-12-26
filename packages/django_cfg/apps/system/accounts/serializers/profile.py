from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from ..models import CustomUser, RegistrationSource, UserRegistrationSource


class CentrifugoTokenSerializer(serializers.Serializer):
    """Nested serializer for Centrifugo WebSocket connection token."""

    token = serializers.CharField(
        help_text="JWT token for Centrifugo WebSocket connection"
    )
    centrifugo_url = serializers.URLField(
        help_text="Centrifugo WebSocket URL"
    )
    expires_at = serializers.DateTimeField(
        help_text="Token expiration time (ISO 8601)"
    )
    channels = serializers.ListField(
        child=serializers.CharField(),
        help_text="List of allowed channels for this user"
    )


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user details."""

    full_name = serializers.ReadOnlyField()
    initials = serializers.ReadOnlyField()
    display_username = serializers.ReadOnlyField()
    avatar = serializers.SerializerMethodField()
    centrifugo = serializers.SerializerMethodField()
    # Explicit nullable fields for proper OpenAPI schema generation
    last_login = serializers.DateTimeField(read_only=True, allow_null=True)
    unanswered_messages_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = CustomUser
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "full_name",
            "initials",
            "display_username",
            "company",
            "phone",
            "position",
            "avatar",
            "is_staff",
            "is_superuser",
            "date_joined",
            "last_login",
            "unanswered_messages_count",
            "centrifugo",
        ]
        read_only_fields = [
            "id",
            "email",
            "is_staff",
            "is_superuser",
            "date_joined",
            "last_login",
            "unanswered_messages_count",
        ]

    @extend_schema_field(serializers.URLField(allow_null=True))
    def get_avatar(self, obj):
        """
        Return avatar URL with fallback to OAuth provider avatar.

        Uses user.avatar_url property which handles:
        1. Local uploaded avatar
        2. GitHub/OAuth provider avatar
        3. None
        """
        avatar_url = obj.avatar_url
        if not avatar_url:
            return None

        # Build absolute URL for local avatars
        if obj.avatar and avatar_url == obj.avatar.url:
            request = self.context.get('request')
            if request is not None:
                return request.build_absolute_uri(avatar_url)

        return avatar_url

    @extend_schema_field(CentrifugoTokenSerializer(allow_null=True))
    def get_centrifugo(self, obj):
        """
        Generate Centrifugo WebSocket connection token if enabled.

        Returns None if Centrifugo is disabled in config.
        """
        try:
            # Import here to avoid circular imports
            from django_cfg.apps.integrations.centrifugo.services import generate_centrifugo_token

            # Generate token with user's channels
            token_data = generate_centrifugo_token(obj)
            return token_data

        except ValueError:
            # Centrifugo not configured or disabled
            return None
        except Exception:
            # If token generation fails, return None (don't break profile response)
            return None



class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile."""

    class Meta:
        model = CustomUser
        fields = ["first_name", "last_name", "company", "phone", "position"]

    def validate_first_name(self, value):
        """Validate first name."""
        if value and len(value.strip()) < 2:
            raise serializers.ValidationError(
                "First name must be at least 2 characters long."
            )
        return value.strip() if value else value

    def validate_last_name(self, value):
        """Validate last name."""
        if value and len(value.strip()) < 2:
            raise serializers.ValidationError(
                "Last name must be at least 2 characters long."
            )
        return value.strip() if value else value

    def validate_phone(self, value):
        """Validate phone number."""
        if (
            value
            and not value.replace("+", "")
            .replace("-", "")
            .replace(" ", "")
            .replace("(", "")
            .replace(")", "")
            .isdigit()
        ):
            raise serializers.ValidationError("Please enter a valid phone number.")
        return value


class AvatarUploadSerializer(serializers.ModelSerializer):
    """Serializer for avatar upload only."""

    class Meta:
        model = CustomUser
        fields = ["avatar"]

    def validate_avatar(self, value):
        """Validate avatar image."""
        if value:
            # Check file size (max 5MB)
            if value.size > 5 * 1024 * 1024:
                raise serializers.ValidationError(
                    "Avatar file size must be less than 5MB."
                )

            # Check file type
            allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
            if (
                hasattr(value, "content_type")
                and value.content_type not in allowed_types
            ):
                raise serializers.ValidationError(
                    "Avatar must be a valid image file (JPEG, PNG, GIF, or WebP)."
                )

        return value


class RegistrationSourceSerializer(serializers.ModelSerializer):
    """Serializer for RegistrationSource model."""

    class Meta:
        model = RegistrationSource
        fields = [
            "id",
            "url",
            "name",
            "description",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class UserRegistrationSourceSerializer(serializers.ModelSerializer):
    """Serializer for UserRegistrationSource model."""
    source = RegistrationSourceSerializer(read_only=True)

    class Meta:
        model = UserRegistrationSource
        fields = ["id", "user", "source", "first_registration", "registration_date"]
        read_only_fields = ["id", "registration_date"]


class UserWithSourcesSerializer(UserSerializer):
    """Extended user serializer with sources information."""
    sources = serializers.SerializerMethodField()
    primary_source = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ['sources', 'primary_source']

    def get_sources(self, obj):
        """Get all sources for the user."""
        user_sources = UserRegistrationSource.objects.filter(user=obj).select_related('source')
        return UserRegistrationSourceSerializer(user_sources, many=True).data

    def get_primary_source(self, obj):
        """Get the primary source for the user."""
        primary_source = obj.primary_source
        if primary_source:
            return RegistrationSourceSerializer(primary_source).data
        return None
