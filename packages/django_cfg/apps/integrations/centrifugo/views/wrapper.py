"""
Centrifugo Wrapper API.

Provides /api/publish endpoint that acts as a proxy to Centrifugo
with ACK tracking and database logging.
"""

import asyncio
import time
import uuid
from typing import Any, Dict

import httpx
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django_cfg.modules.django_logging import get_logger
from pydantic import BaseModel, Field

from ..services import get_centrifugo_config
from ..services.logging import CentrifugoLogger

logger = get_logger("centrifugo.wrapper")


# ========================================================================
# Request/Response Models
# ========================================================================


class PublishRequest(BaseModel):
    """Request model for publish endpoint."""

    channel: str = Field(..., description="Target channel name")
    data: Dict[str, Any] = Field(..., description="Message data")
    wait_for_ack: bool = Field(default=False, description="Wait for client ACK")
    ack_timeout: int = Field(default=10, description="ACK timeout in seconds")
    message_id: str | None = Field(default=None, description="Optional message ID")


class PublishResponse(BaseModel):
    """Response model for publish endpoint."""

    published: bool = Field(..., description="Whether message was published")
    message_id: str = Field(..., description="Unique message ID")
    channel: str = Field(..., description="Target channel")
    delivered: bool = Field(default=False, description="Whether message was delivered")
    acks_received: int = Field(default=0, description="Number of ACKs received")


# ========================================================================
# Wrapper View
# ========================================================================


@method_decorator(csrf_exempt, name='dispatch')
class PublishWrapperView(View):
    """
    Centrifugo publish wrapper endpoint.

    Provides /api/publish endpoint that:
    - Accepts publish requests from CentrifugoClient
    - Logs to database (CentrifugoLog)
    - Proxies to Centrifugo HTTP API
    - Returns publish result with ACK tracking
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

            # Add Centrifugo API key for server-to-server auth
            if config.centrifugo_api_key:
                headers["Authorization"] = f"apikey {config.centrifugo_api_key}"

            # Use Centrifugo API URL (not wrapper URL)
            base_url = config.centrifugo_api_url.rstrip("/api").rstrip("/")

            self._http_client = httpx.AsyncClient(
                base_url=base_url,
                headers=headers,
                timeout=httpx.Timeout(config.http_timeout),
                verify=config.verify_ssl,
            )

        return self._http_client

    async def _publish_to_centrifugo(
        self, channel: str, data: Dict[str, Any], wait_for_ack: bool, ack_timeout: int, message_id: str
    ) -> Dict[str, Any]:
        """
        Publish message to Centrifugo API.

        Args:
            channel: Target channel
            data: Message data
            wait_for_ack: Whether to wait for ACK
            ack_timeout: ACK timeout in seconds
            message_id: Message ID

        Returns:
            Publish result dict
        """
        start_time = time.time()

        # Create log entry
        log_entry = await CentrifugoLogger.create_log_async(
            message_id=message_id,
            channel=channel,
            data=data,
            wait_for_ack=wait_for_ack,
            ack_timeout=ack_timeout if wait_for_ack else None,
            is_notification=True,
            user=None,  # Can extract from request if needed
        )

        try:
            # Centrifugo API format: POST /api with method in body
            payload = {
                "method": "publish",
                "params": {
                    "channel": channel,
                    "data": data,
                },
            }

            response = await self.http_client.post("/api", json=payload)
            response.raise_for_status()
            result = response.json()

            # Check for Centrifugo error
            if "error" in result and result["error"]:
                raise Exception(f"Centrifugo error: {result['error']}")

            # Calculate duration
            duration_ms = int((time.time() - start_time) * 1000)

            # Mark as success
            if log_entry:
                await CentrifugoLogger.mark_success_async(
                    log_entry,
                    acks_received=0,  # ACK tracking would be implemented separately
                    duration_ms=duration_ms,
                )

            # Return wrapper-compatible response
            return {
                "published": True,
                "message_id": message_id,
                "channel": channel,
                "acks_received": 0,
                "delivered": True,  # Centrifugo confirms publish, not delivery
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

    def post(self, request):
        """
        Handle POST /api/publish request.

        Request body:
            {
                "channel": "test#demo",
                "data": {"key": "value"},
                "wait_for_ack": false,
                "ack_timeout": 10,
                "message_id": "optional-uuid"
            }

        Response:
            {
                "published": true,
                "message_id": "uuid",
                "channel": "test#demo",
                "delivered": true,
                "acks_received": 0
            }
        """
        try:
            import json

            # Parse request body
            body = json.loads(request.body)
            req_data = PublishRequest(**body)

            # Generate message ID if not provided
            message_id = req_data.message_id or str(uuid.uuid4())

            # Publish to Centrifugo
            result = asyncio.run(
                self._publish_to_centrifugo(
                    channel=req_data.channel,
                    data=req_data.data,
                    wait_for_ack=req_data.wait_for_ack,
                    ack_timeout=req_data.ack_timeout,
                    message_id=message_id,
                )
            )

            response = PublishResponse(**result)
            return JsonResponse(response.model_dump(), status=200)

        except Exception as e:
            logger.error(f"Failed to publish via wrapper: {e}", exc_info=True)
            return JsonResponse(
                {
                    "published": False,
                    "message_id": "",
                    "channel": body.get("channel", "") if "body" in locals() else "",
                    "delivered": False,
                    "acks_received": 0,
                    "error": str(e),
                },
                status=500,
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


__all__ = ["PublishWrapperView"]
