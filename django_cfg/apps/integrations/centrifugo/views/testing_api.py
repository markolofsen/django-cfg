"""
Centrifugo Testing API.

Provides endpoints for live testing of Centrifugo integration from dashboard.
Includes connection tokens, publish proxying, and ACK management.
"""

import time
from datetime import datetime, timedelta
from typing import Any, Dict

import httpx
import jwt
from django.conf import settings
from django.utils import timezone
from django_cfg.utils import get_logger
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
    async def publish_test(self, request):
        """
        Publish test message via wrapper (ASYNC).

        Proxies request to Centrifugo wrapper with ACK tracking support.
        """
        try:
            req_data = PublishTestRequest(**request.data)

            # Call wrapper API (ASYNC - no asyncio.run()!)
            result = await self._publish_to_wrapper(
                channel=req_data.channel,
                data=req_data.data,
                wait_for_ack=req_data.wait_for_ack,
                ack_timeout=req_data.ack_timeout,
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
    async def send_ack(self, request):
        """
        Send manual ACK for message (ASYNC).

        Proxies ACK to wrapper for testing ACK flow.
        """
        try:
            req_data = ManualAckRequest(**request.data)

            # Send ACK to wrapper (ASYNC - no asyncio.run()!)
            result = await self._send_ack_to_wrapper(
                message_id=req_data.message_id, client_id=req_data.client_id
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
                from ..models import CentrifugoLog

                # ✅ Use Django 5.2+ async ORM instead of sync_to_async
                log_entry.status = CentrifugoLog.StatusChoices.FAILED
                log_entry.error_code = type(e).__name__
                log_entry.error_message = str(e)
                log_entry.completed_at = timezone.now()
                log_entry.duration_ms = duration_ms

                await log_entry.asave(
                    update_fields=[
                        "status",
                        "error_code",
                        "error_message",
                        "completed_at",
                        "duration_ms",
                    ]
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
    async def publish_with_logging(self, request):
        """
        Publish message using CentrifugoClient with database logging (ASYNC).

        This endpoint uses the production CentrifugoClient which logs all
        publishes to the database (CentrifugoLog model).
        """
        try:
            req_data = PublishTestRequest(**request.data)

            # Use CentrifugoClient for publishing
            client = CentrifugoClient()

            # Publish message (ASYNC - no asyncio.run()!)
            if req_data.wait_for_ack:
                result = await client.publish_with_ack(
                    channel=req_data.channel,
                    data=req_data.data,
                    ack_timeout=req_data.ack_timeout,
                    user=request.user if request.user.is_authenticated else None,
                    caller_ip=request.META.get("REMOTE_ADDR"),
                    user_agent=request.META.get("HTTP_USER_AGENT"),
                )
            else:
                result = await client.publish(
                    channel=req_data.channel,
                    data=req_data.data,
                    user=request.user if request.user.is_authenticated else None,
                    caller_ip=request.META.get("REMOTE_ADDR"),
                    user_agent=request.META.get("HTTP_USER_AGENT"),
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


__all__ = ["CentrifugoTestingAPIViewSet"]
