"""
Centrifugo Testing API.

Provides endpoints for live testing of Centrifugo integration from dashboard.
Includes connection tokens, publish proxying, and ACK management.
"""

import asyncio
import time
from datetime import datetime, timedelta
from typing import Any, Dict

import httpx
import jwt
from django.conf import settings
from django_cfg.modules.django_logging import get_logger
from drf_spectacular.utils import extend_schema
from pydantic import BaseModel, Field
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from django_cfg.mixins import AdminAPIMixin
from ..services import get_centrifugo_config
from ..services.client import CentrifugoClient

logger = get_logger("centrifugo.testing_api")


# ========================================================================
# Request/Response Models
# ========================================================================


class ConnectionTokenRequest(BaseModel):
    """Request model for connection token generation."""

    user_id: str = Field(..., description="User ID for the connection")
    channels: list[str] = Field(
        default_factory=list, description="List of channels to authorize"
    )


class ConnectionTokenResponse(BaseModel):
    """Response model for connection token."""

    token: str = Field(..., description="JWT token for WebSocket connection")
    centrifugo_url: str = Field(..., description="Centrifugo WebSocket URL")
    expires_at: str = Field(..., description="Token expiration time (ISO 8601)")


class PublishTestRequest(BaseModel):
    """Request model for test message publishing."""

    channel: str = Field(..., description="Target channel name")
    data: Dict[str, Any] = Field(..., description="Message data (any JSON object)")
    wait_for_ack: bool = Field(
        default=False, description="Wait for client acknowledgment"
    )
    ack_timeout: int = Field(
        default=10, ge=1, le=60, description="ACK timeout in seconds"
    )


class PublishTestResponse(BaseModel):
    """Response model for test message publishing."""

    success: bool = Field(..., description="Whether publish succeeded")
    message_id: str = Field(..., description="Unique message ID")
    channel: str = Field(..., description="Target channel")
    acks_received: int = Field(default=0, description="Number of ACKs received")
    delivered: bool = Field(default=False, description="Whether message was delivered")
    error: str | None = Field(default=None, description="Error message if failed")


class ManualAckRequest(BaseModel):
    """Request model for manual ACK sending."""

    message_id: str = Field(..., description="Message ID to acknowledge")
    client_id: str = Field(..., description="Client ID sending the ACK")


class ManualAckResponse(BaseModel):
    """Response model for manual ACK."""

    success: bool = Field(..., description="Whether ACK was sent successfully")
    message_id: str = Field(..., description="Message ID that was acknowledged")
    error: str | None = Field(default=None, description="Error message if failed")


# ========================================================================
# Testing API ViewSet
# ========================================================================


class CentrifugoTestingAPIViewSet(AdminAPIMixin, viewsets.ViewSet):
    """
    Centrifugo Testing API ViewSet.

    Provides endpoints for interactive testing of Centrifugo integration
    from the dashboard. Includes connection token generation, test message
    publishing, and manual ACK management.
    Requires admin authentication (JWT, Session, or Basic Auth).
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._http_client = None

    @property
    def http_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client for wrapper API calls."""
        if self._http_client is None:
            config = get_centrifugo_config()
            if not config:
                raise ValueError("Centrifugo not configured")

            headers = {"Content-Type": "application/json"}
            # Use centrifugo_api_key for direct Centrifugo API calls
            if config.centrifugo_api_key:
                headers["X-API-Key"] = config.centrifugo_api_key

            # Use wrapper URL as base (which points to Centrifugo in local setup)
            base_url = config.wrapper_url.rstrip("/")

            self._http_client = httpx.AsyncClient(
                base_url=base_url,
                headers=headers,
                timeout=httpx.Timeout(30.0),
                verify=False,  # Allow self-signed certificates
            )

        return self._http_client

    @extend_schema(
        tags=["Centrifugo Testing"],
        summary="Generate connection token",
        description="Generate JWT token for WebSocket connection to Centrifugo.",
        request=ConnectionTokenRequest,
        responses={
            200: ConnectionTokenResponse,
            400: {"description": "Invalid request"},
            500: {"description": "Server error"},
        },
    )
    @action(detail=False, methods=["post"], url_path="connection-token")
    def connection_token(self, request):
        """
        Generate JWT token for WebSocket connection.

        Returns token that can be used to connect to Centrifugo from browser.
        """
        try:
            config = get_centrifugo_config()
            if not config:
                return Response(
                    {"error": "Centrifugo not configured"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            # Parse request
            req_data = ConnectionTokenRequest(**request.data)

            # Generate JWT token
            now = int(time.time())
            exp = now + 3600  # 1 hour

            payload = {
                "sub": req_data.user_id,
                "exp": exp,
                "iat": now,
            }

            # Add channels if provided
            if req_data.channels:
                payload["channels"] = req_data.channels

            # Use HMAC secret from config or Django SECRET_KEY
            secret = config.centrifugo_token_hmac_secret or settings.SECRET_KEY

            token = jwt.encode(payload, secret, algorithm="HS256")

            response = ConnectionTokenResponse(
                token=token,
                centrifugo_url=config.centrifugo_url,
                expires_at=datetime.utcfromtimestamp(exp).isoformat() + "Z",
            )

            return Response(response.model_dump())

        except Exception as e:
            logger.error(f"Failed to generate connection token: {e}", exc_info=True)
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @extend_schema(
        tags=["Centrifugo Testing"],
        summary="Publish test message",
        description="Publish test message to Centrifugo via wrapper with optional ACK tracking.",
        request=PublishTestRequest,
        responses={
            200: PublishTestResponse,
            400: {"description": "Invalid request"},
            500: {"description": "Server error"},
        },
    )
    @action(detail=False, methods=["post"], url_path="publish-test")
    def publish_test(self, request):
        """
        Publish test message via wrapper.

        Proxies request to Centrifugo wrapper with ACK tracking support.
        """
        try:
            req_data = PublishTestRequest(**request.data)

            # Call wrapper API
            result = asyncio.run(
                self._publish_to_wrapper(
                    channel=req_data.channel,
                    data=req_data.data,
                    wait_for_ack=req_data.wait_for_ack,
                    ack_timeout=req_data.ack_timeout,
                )
            )

            response = PublishTestResponse(
                success=result.get("published", False),
                message_id=result.get("message_id", ""),
                channel=result.get("channel", req_data.channel),
                acks_received=result.get("acks_received", 0),
                delivered=result.get("delivered", False),
            )

            return Response(response.model_dump())

        except Exception as e:
            logger.error(f"Failed to publish test message: {e}", exc_info=True)
            return Response(
                PublishTestResponse(
                    success=False,
                    message_id="",
                    channel=request.data.get("channel", ""),
                    error=str(e),
                ).model_dump(),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @extend_schema(
        tags=["Centrifugo Testing"],
        summary="Send manual ACK",
        description="Manually send ACK for a message to the wrapper. Pass message_id in request body.",
        request=ManualAckRequest,
        responses={
            200: ManualAckResponse,
            400: {"description": "Invalid request"},
            500: {"description": "Server error"},
        },
    )
    @action(detail=False, methods=["post"], url_path="send-ack")
    def send_ack(self, request):
        """
        Send manual ACK for message.

        Proxies ACK to wrapper for testing ACK flow.
        """
        try:
            req_data = ManualAckRequest(**request.data)

            # Send ACK to wrapper
            result = asyncio.run(
                self._send_ack_to_wrapper(
                    message_id=req_data.message_id, client_id=req_data.client_id
                )
            )

            response = ManualAckResponse(
                success=result.get("status") == "ok",
                message_id=req_data.message_id,
                error=result.get("message") if result.get("status") != "ok" else None,
            )

            return Response(response.model_dump())

        except Exception as e:
            logger.error(f"Failed to send ACK: {e}", exc_info=True)
            return Response(
                ManualAckResponse(
                    success=False,
                    message_id=request.data.get("message_id", ""),
                    error=str(e)
                ).model_dump(),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    async def _publish_to_wrapper(
        self, channel: str, data: Dict[str, Any], wait_for_ack: bool, ack_timeout: int
    ) -> Dict[str, Any]:
        """
        Publish message to Centrifugo API.

        Args:
            channel: Target channel
            data: Message data
            wait_for_ack: Whether to wait for ACK
            ack_timeout: ACK timeout in seconds

        Returns:
            Centrifugo API response formatted for wrapper compatibility
        """
        import uuid
        import time
        from ..services.logging import CentrifugoLogger

        # Generate unique message ID
        message_id = str(uuid.uuid4())
        start_time = time.time()

        # Create log entry
        log_entry = await CentrifugoLogger.create_log_async(
            message_id=message_id,
            channel=channel,
            data=data,
            wait_for_ack=wait_for_ack,
            ack_timeout=ack_timeout if wait_for_ack else None,
            is_notification=True,
            user=self.request.user if self.request and self.request.user.is_authenticated else None,
        )

        try:
            # Centrifugo API format: POST /api with method in body
            payload = {
                "method": "publish",
                "params": {
                    "channel": channel,
                    "data": data,
                }
            }

            response = await self.http_client.post("/api", json=payload)
            response.raise_for_status()
            result = response.json()

            # Calculate duration
            duration_ms = int((time.time() - start_time) * 1000)

            # Mark as success
            if log_entry:
                await CentrifugoLogger.mark_success_async(
                    log_entry,
                    acks_received=0,
                    duration_ms=duration_ms,
                )

            # Transform Centrifugo response to match wrapper API format
            return {
                "published": True,
                "message_id": message_id,
                "channel": channel,
                "acks_received": 0,
                "delivered": True,
            }

        except Exception as e:
            # Calculate duration
            duration_ms = int((time.time() - start_time) * 1000)

            # Mark as failed
            if log_entry:
                from asgiref.sync import sync_to_async
                from ..models import CentrifugoLog

                await sync_to_async(CentrifugoLog.objects.mark_failed)(
                    log_instance=log_entry,
                    error_code=type(e).__name__,
                    error_message=str(e),
                    duration_ms=duration_ms,
                )

            raise

    async def _send_ack_to_wrapper(
        self, message_id: str, client_id: str
    ) -> Dict[str, Any]:
        """
        Send ACK to wrapper API.

        Args:
            message_id: Message ID to acknowledge
            client_id: Client ID sending the ACK

        Returns:
            Wrapper API response
        """
        payload = {"client_id": client_id}

        response = await self.http_client.post(
            f"/api/ack/{message_id}", json=payload
        )
        response.raise_for_status()
        return response.json()

    @extend_schema(
        tags=["Centrifugo Testing"],
        summary="Publish with database logging",
        description="Publish message using CentrifugoClient with database logging. This will create CentrifugoLog records.",
        request=PublishTestRequest,
        responses={
            200: PublishTestResponse,
            400: {"description": "Invalid request"},
            500: {"description": "Server error"},
        },
    )
    @action(detail=False, methods=["post"], url_path="publish-with-logging")
    def publish_with_logging(self, request):
        """
        Publish message using CentrifugoClient with database logging.

        This endpoint uses the production CentrifugoClient which logs all
        publishes to the database (CentrifugoLog model).
        """
        try:
            req_data = PublishTestRequest(**request.data)

            # Use CentrifugoClient for publishing
            client = CentrifugoClient()

            # Publish message
            result = asyncio.run(
                client.publish_with_ack(
                    channel=req_data.channel,
                    data=req_data.data,
                    ack_timeout=req_data.ack_timeout if req_data.wait_for_ack else None,
                    user=request.user if request.user.is_authenticated else None,
                    caller_ip=request.META.get("REMOTE_ADDR"),
                    user_agent=request.META.get("HTTP_USER_AGENT"),
                )
                if req_data.wait_for_ack
                else client.publish(
                    channel=req_data.channel,
                    data=req_data.data,
                    user=request.user if request.user.is_authenticated else None,
                    caller_ip=request.META.get("REMOTE_ADDR"),
                    user_agent=request.META.get("HTTP_USER_AGENT"),
                )
            )

            # Convert PublishResponse to dict
            response_data = {
                "success": result.published,
                "message_id": result.message_id,
                "channel": req_data.channel,
                "delivered": result.delivered if req_data.wait_for_ack else None,
                "acks_received": result.acks_received if req_data.wait_for_ack else 0,
                "logged_to_database": True,  # CentrifugoClient always logs
            }

            return Response(response_data)

        except Exception as e:
            logger.error(f"Failed to publish with logging: {e}", exc_info=True)
            return Response(
                {"success": False, "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def __del__(self):
        """Cleanup HTTP client on deletion."""
        if self._http_client:
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    loop.create_task(self._http_client.aclose())
                else:
                    loop.run_until_complete(self._http_client.aclose())
            except Exception:
                pass


__all__ = ["CentrifugoTestingAPIViewSet"]
