"""
Centrifugo Token API

Provides endpoint for generating Centrifugo JWT tokens with user permissions.
"""

import logging

from drf_spectacular.utils import extend_schema
from pydantic import BaseModel, Field
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from ..services import generate_centrifugo_token

logger = logging.getLogger(__name__)


# ========================================================================
# Response Models
# ========================================================================


class ConnectionTokenResponse(BaseModel):
    """Response model for Centrifugo connection token."""

    token: str = Field(..., description="JWT token for Centrifugo connection")
    centrifugo_url: str = Field(..., description="Centrifugo WebSocket URL")
    expires_at: str = Field(..., description="Token expiration time (ISO 8601)")
    channels: list[str] = Field(..., description="List of allowed channels")


class CentrifugoTokenViewSet(viewsets.ViewSet):
    """
    Centrifugo Token API ViewSet.

    Provides endpoint for authenticated users to get Centrifugo JWT token
    with their allowed channels based on permissions.
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Centrifugo Auth"],
        summary="Get Centrifugo connection token",
        description=(
            "Generate JWT token for WebSocket connection to Centrifugo. "
            "Token includes user's allowed channels based on their permissions. "
            "Requires authentication."
        ),
        responses={
            200: ConnectionTokenResponse,
            401: {"description": "Unauthorized - authentication required"},
            500: {"description": "Server error"},
        },
    )
    @action(detail=False, methods=["get"], url_path="token")
    def get_token(self, request):
        """
        Get Centrifugo connection token for authenticated user.

        Returns JWT token with user's allowed channels that can be used
        to connect to Centrifugo WebSocket.
        """
        try:
            user = request.user

            # Generate token with user's channels
            token_data = generate_centrifugo_token(user)

            logger.debug(
                f"Generated Centrifugo token for user {user.email} (ID: {user.id}) "
                f"with {len(token_data['channels'])} channels: {token_data['channels']}"
            )

            # Format expires_at as ISO 8601 string
            return Response({
                "token": token_data["token"],
                "centrifugo_url": token_data["centrifugo_url"],
                "expires_at": token_data["expires_at"].isoformat() + "Z",
                "channels": token_data["channels"],
            })

        except ValueError as e:
            # Centrifugo not configured or disabled
            logger.warning(f"Centrifugo token generation failed: {e}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        except Exception as e:
            logger.error(f"Failed to generate Centrifugo token: {e}", exc_info=True)
            return Response(
                {"error": "Failed to generate token"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


__all__ = ["CentrifugoTokenViewSet"]
