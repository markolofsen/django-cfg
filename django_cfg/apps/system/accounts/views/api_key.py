"""
API Key management views.

Provides endpoints for retrieving and regenerating the user's API key.
"""

from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import serializers, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from django_cfg.mixins import ClientAPIMixin

from ..models.api_key import UserAPIKey


class APIKeySerializer(serializers.Serializer):
    """Serializer for API key response (masked)."""

    key = serializers.CharField(help_text="Masked API key")
    reissued_at = serializers.DateTimeField(
        allow_null=True, help_text="When the key was last regenerated"
    )
    created_at = serializers.DateTimeField(help_text="When the key was created")


class APIKeyRegenerateSerializer(serializers.Serializer):
    """Serializer for API key regeneration response (full key shown once)."""

    key = serializers.CharField(help_text="New API key (shown only once)")
    reissued_at = serializers.DateTimeField(help_text="When the key was regenerated")


class APIKeyTestSerializer(serializers.Serializer):
    """Serializer for testing an API key."""

    key = serializers.CharField(help_text="API key to test")


class APIKeyTestResultSerializer(serializers.Serializer):
    """Serializer for API key test result."""

    valid = serializers.BooleanField(help_text="Whether the key is valid")
    user_id = serializers.CharField(
        allow_null=True, help_text="User ID if valid, null otherwise"
    )


class APIKeyViewSet(ClientAPIMixin, viewsets.GenericViewSet):
    """
    API Key management.

    Endpoints:
    - GET /cfg/accounts/api-key/ — retrieve masked key details
    - POST /cfg/accounts/api-key/regenerate/ — generate new key
    - POST /cfg/accounts/api-key/test/ — test an API key
    """

    serializer_class = APIKeySerializer
    queryset = UserAPIKey.objects.none()

    @extend_schema(
        tags=["cfg_accounts_api_key"],
        summary="Get API key details",
        description="Retrieve the current user's API key (masked) and metadata.",
        responses={
            200: APIKeySerializer,
            401: {"description": "Authentication credentials were not provided."},
        },
    )
    @action(detail=False, methods=["get"], url_path="", url_name="detail")
    def retrieve_key(self, request):
        """Return masked API key details for the current user."""
        api_key = self._get_or_create_key(request.user)
        serializer = APIKeySerializer(
            {
                "key": api_key.masked_key,
                "reissued_at": api_key.reissued_at,
                "created_at": api_key.created_at,
            }
        )
        return Response(serializer.data)

    @extend_schema(
        tags=["cfg_accounts_api_key"],
        summary="Regenerate API key",
        description="Generate a new API key. The full key is returned only once.",
        responses={
            200: APIKeyRegenerateSerializer,
            401: {"description": "Authentication credentials were not provided."},
        },
        examples=[
            OpenApiExample(
                "Regenerate Response",
                value={
                    "key": "d0b45e78-1234-5678-9abc-def012345678",
                    "reissued_at": "2024-01-15T10:30:00Z",
                },
                response_only=True,
                status_codes=["200"],
            )
        ],
    )
    @action(detail=False, methods=["post"], url_path="regenerate")
    def regenerate(self, request):
        """Regenerate API key and return the new full key."""
        api_key = self._get_or_create_key(request.user)
        api_key.regenerate()

        serializer = APIKeyRegenerateSerializer(
            {
                "key": str(api_key.key),
                "reissued_at": api_key.reissued_at,
            }
        )
        return Response(serializer.data)

    @extend_schema(
        tags=["cfg_accounts_api_key"],
        summary="Test API key",
        description="Test whether an API key is valid without consuming it.",
        request=APIKeyTestSerializer,
        responses={
            200: APIKeyTestResultSerializer,
        },
        examples=[
            OpenApiExample(
                "Valid Key",
                value={"valid": True, "user_id": "42"},
                response_only=True,
                status_codes=["200"],
            ),
            OpenApiExample(
                "Invalid Key",
                value={"valid": False, "user_id": None},
                response_only=True,
                status_codes=["200"],
            ),
        ],
    )
    @action(detail=False, methods=["post"], url_path="test")
    def test_key(self, request):
        """Test an API key and return whether it is valid."""
        serializer = APIKeyTestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        key = serializer.validated_data["key"]

        try:
            api_key = UserAPIKey.objects.select_related("user").get(key=key)
            result = {"valid": True, "user_id": str(api_key.user_id)}
        except UserAPIKey.DoesNotExist:
            result = {"valid": False, "user_id": None}

        return Response(APIKeyTestResultSerializer(result).data)

    def _get_or_create_key(self, user) -> UserAPIKey:
        """Get or auto-create API key for user."""
        api_key, _ = UserAPIKey.objects.get_or_create(user=user)
        return api_key
