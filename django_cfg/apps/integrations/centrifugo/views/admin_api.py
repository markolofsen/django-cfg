"""
Centrifugo Admin API Proxy.

Proxies requests to Centrifugo server API with authentication and type safety.
Provides Django endpoints that map to Centrifugo HTTP API methods.
"""

import httpx
from django.http import JsonResponse
from django_cfg.utils import get_logger
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from django_cfg.mixins import AdminAPIMixin
from ..serializers import (
    CentrifugoInfoRequest,
    CentrifugoInfoResponse,
    CentrifugoChannelsRequest,
    CentrifugoChannelsResponse,
    CentrifugoPresenceRequest,
    CentrifugoPresenceResponse,
    CentrifugoPresenceStatsRequest,
    CentrifugoPresenceStatsResponse,
    CentrifugoHistoryRequest,
    CentrifugoHistoryResponse,
)
from ..services import get_centrifugo_config

logger = get_logger("centrifugo.admin_api")


class CentrifugoAdminAPIViewSet(AdminAPIMixin, viewsets.ViewSet):
    """
    Centrifugo Admin API Proxy ViewSet.

    Provides type-safe proxy endpoints to Centrifugo server API.
    All requests are authenticated via Django session/JWT and proxied to Centrifugo.
    Requires admin authentication (JWT, Session, or Basic Auth).
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._http_client = None

    @property
    def http_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client for Centrifugo API calls."""
        if self._http_client is None:
            config = get_centrifugo_config()
            if not config:
                raise ValueError("Centrifugo not configured")

            headers = {"Content-Type": "application/json"}
            if config.centrifugo_api_key:
                # Centrifugo expects "Authorization: apikey <key>" header
                headers["Authorization"] = f"apikey {config.centrifugo_api_key}"
                logger.debug(f"Using Centrifugo API key: {config.centrifugo_api_key[:10]}...")
            else:
                logger.warning("No Centrifugo API key configured!")

            # Use base URL without /api suffix since we'll add it in requests
            base_url = config.centrifugo_api_url.rstrip('/api').rstrip('/')
            logger.debug(f"Centrifugo API base URL: {base_url}")

            self._http_client = httpx.AsyncClient(
                base_url=base_url,
                headers=headers,
                timeout=httpx.Timeout(10.0),
                verify=False,  # Disable SSL verification for self-signed certs
            )

        return self._http_client

    async def _call_centrifugo_api(self, method: str, params: dict = None) -> dict:
        """
        Call Centrifugo API method.

        Args:
            method: API method name (e.g., "info", "channels", "presence")
            params: Method parameters (optional)

        Returns:
            API response data or error dict

        Raises:
            httpx.HTTPError: If API call fails
        """
        payload = {"method": method, "params": params or {}}

        try:
            response = await self.http_client.post("/api", json=payload)
            response.raise_for_status()
            result = response.json()

            # Return both error and result - let caller decide
            return result

        except httpx.HTTPError as e:
            logger.error(f"Centrifugo API HTTP error: {e}", exc_info=True)
            raise

    @extend_schema(
        tags=["Centrifugo Admin API"],
        summary="Get Centrifugo server info",
        description="Returns server information including node count, version, and uptime.",
        request=CentrifugoInfoRequest,
        responses={
            200: CentrifugoInfoResponse,
            500: {"description": "Server error"},
        },
    )
    @action(detail=False, methods=["post"], url_path="info")
    async def info(self, request):
        """Get Centrifugo server information (ASYNC)."""
        try:
            result = await self._call_centrifugo_api("info", params={})

            # Check for Centrifugo API error
            if "error" in result and result["error"]:
                return Response(
                    {"error": result["error"], "result": None},
                    status=status.HTTP_200_OK  # Not a server error, just API error
                )

            # Success response
            response = CentrifugoInfoResponse(error=None, result=result.get("result", {}))
            return Response(response.model_dump())

        except Exception as e:
            logger.error(f"Failed to get server info: {e}", exc_info=True)
            return Response(
                {"error": {"code": 102, "message": str(e)}},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @extend_schema(
        tags=["Centrifugo Admin API"],
        summary="List active channels",
        description="Returns list of active channels with optional pattern filter.",
        request=CentrifugoChannelsRequest,
        responses={
            200: CentrifugoChannelsResponse,
            500: {"description": "Server error"},
        },
    )
    @action(detail=False, methods=["post"], url_path="channels")
    async def channels(self, request):
        """List active channels (ASYNC)."""
        try:
            req_data = CentrifugoChannelsRequest(**request.data)
            result = await self._call_centrifugo_api(
                "channels", params=req_data.model_dump(exclude_none=True)
            )

            # Check for Centrifugo API error
            if "error" in result and result["error"]:
                return Response(
                    {"error": result["error"], "result": None},
                    status=status.HTTP_200_OK
                )

            response = CentrifugoChannelsResponse(error=None, result=result.get("result", {}))
            return Response(response.model_dump())

        except Exception as e:
            logger.error(f"Failed to list channels: {e}", exc_info=True)
            return Response(
                {"error": {"code": 102, "message": str(e)}},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @extend_schema(
        tags=["Centrifugo Admin API"],
        summary="Get channel presence",
        description="Returns list of clients currently subscribed to a channel.",
        request=CentrifugoPresenceRequest,
        responses={
            200: CentrifugoPresenceResponse,
            500: {"description": "Server error"},
        },
    )
    @action(detail=False, methods=["post"], url_path="presence")
    async def presence(self, request):
        """Get channel presence (active subscribers) (ASYNC)."""
        try:
            req_data = CentrifugoPresenceRequest(**request.data)
            result = await self._call_centrifugo_api(
                "presence", params=req_data.model_dump()
            )

            # Check for Centrifugo API error (e.g., code 108 "not available")
            if "error" in result and result["error"]:
                return Response(
                    {"error": result["error"], "result": None},
                    status=status.HTTP_200_OK
                )

            response = CentrifugoPresenceResponse(error=None, result=result.get("result", {}))
            return Response(response.model_dump())

        except Exception as e:
            logger.error(f"Failed to get presence: {e}", exc_info=True)
            return Response(
                {"error": {"code": 102, "message": str(e)}},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @extend_schema(
        tags=["Centrifugo Admin API"],
        summary="Get channel presence statistics",
        description="Returns quick statistics about channel presence (num_clients, num_users).",
        request=CentrifugoPresenceStatsRequest,
        responses={
            200: CentrifugoPresenceStatsResponse,
            500: {"description": "Server error"},
        },
    )
    @action(detail=False, methods=["post"], url_path="presence-stats")
    async def presence_stats(self, request):
        """Get channel presence statistics (ASYNC)."""
        try:
            req_data = CentrifugoPresenceStatsRequest(**request.data)
            result = await self._call_centrifugo_api(
                "presence_stats", params=req_data.model_dump()
            )

            # Check for Centrifugo API error (e.g., code 108 "not available")
            if "error" in result and result["error"]:
                return Response(
                    {"error": result["error"], "result": None},
                    status=status.HTTP_200_OK
                )

            response = CentrifugoPresenceStatsResponse(error=None, result=result.get("result", {}))
            return Response(response.model_dump())

        except Exception as e:
            logger.error(f"Failed to get presence stats: {e}", exc_info=True)
            return Response(
                {"error": {"code": 102, "message": str(e)}},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @extend_schema(
        tags=["Centrifugo Admin API"],
        summary="Get channel history",
        description="Returns message history for a channel.",
        request=CentrifugoHistoryRequest,
        responses={
            200: CentrifugoHistoryResponse,
            500: {"description": "Server error"},
        },
    )
    @action(detail=False, methods=["post"], url_path="history")
    async def history(self, request):
        """Get channel message history (ASYNC)."""
        try:
            req_data = CentrifugoHistoryRequest(**request.data)
            result = await self._call_centrifugo_api(
                "history", params=req_data.model_dump(exclude_none=True)
            )

            # Check for Centrifugo API error (e.g., code 108 "not available")
            if "error" in result and result["error"]:
                return Response(
                    {"error": result["error"], "result": None},
                    status=status.HTTP_200_OK
                )

            response = CentrifugoHistoryResponse(error=None, result=result.get("result", {}))
            return Response(response.model_dump())

        except Exception as e:
            logger.error(f"Failed to get history: {e}", exc_info=True)
            return Response(
                {"error": {"code": 102, "message": str(e)}},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @extend_schema(
        tags=["Centrifugo Admin API"],
        summary="Get connection token for dashboard",
        description="Returns JWT token and config for WebSocket connection to Centrifugo.",
        request=None,
        responses={
            200: {
                "type": "object",
                "properties": {
                    "token": {"type": "string"},
                    "config": {
                        "type": "object",
                        "properties": {
                            "centrifugo_url": {"type": "string"},
                            "expires_at": {"type": "string"},
                        }
                    }
                }
            },
            400: {"description": "Centrifugo not configured"},
            500: {"description": "Server error"},
        },
    )
    @action(detail=False, methods=["post"], url_path="auth/token")
    def auth_token(self, request):
        """
        Generate JWT token for dashboard WebSocket connection.

        Returns token that authenticates the current user to subscribe
        to the dashboard channel for real-time updates.
        """
        try:
            import jwt
            import time
            from datetime import datetime, timezone

            config = get_centrifugo_config()
            if not config:
                return Response(
                    {"error": "Centrifugo is not configured"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Generate JWT token for current user
            now = int(time.time())
            exp = now + 3600  # 1 hour

            payload = {
                "sub": str(request.user.id),  # User ID
                "exp": exp,  # Expiration
                "iat": now,  # Issued at
            }

            # Subscribe to dashboard channel
            payload["channels"] = ["centrifugo#dashboard"]

            # Use HMAC secret from config or Django SECRET_KEY
            secret = config.centrifugo_token_hmac_secret or ""
            if not secret:
                from django.conf import settings
                secret = settings.SECRET_KEY

            token = jwt.encode(payload, secret, algorithm="HS256")

            return Response({
                "token": token,
                "config": {
                    "centrifugo_url": config.centrifugo_url,
                    "expires_at": datetime.fromtimestamp(exp, tz=timezone.utc).isoformat(),
                }
            })

        except Exception as e:
            logger.error(f"Failed to generate auth token: {e}", exc_info=True)
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    async def cleanup(self):
        """
        Explicit async cleanup method for HTTP client.

        Note: Django handles ViewSet lifecycle automatically.
        This method is provided for explicit cleanup if needed,
        but httpx.AsyncClient will be garbage collected normally.
        """
        if self._http_client:
            await self._http_client.aclose()
            self._http_client = None


__all__ = ["CentrifugoAdminAPIViewSet"]
