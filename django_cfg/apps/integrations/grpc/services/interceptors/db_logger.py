"""
Database logging for gRPC requests.

Handles creation and updating of GRPCRequestLog entries.
"""

import logging
from typing import Optional, Any

import grpc.aio

from .utils import extract_ip_from_peer, get_grpc_code, serialize_message

logger = logging.getLogger(__name__)


class RequestLogger:
    """Handles database logging for gRPC requests."""

    def __init__(self, log_request_data: bool = False, log_response_data: bool = False):
        self.log_request_data = log_request_data
        self.log_response_data = log_response_data

    async def create_log_entry(
        self,
        request_id: str,
        service_name: str,
        method_name: str,
        full_method: str,
        peer: str,
        user_agent: str,
        context: grpc.aio.ServicerContext,
        request: Any = None,
    ) -> Optional[Any]:
        """Create log entry in database."""
        try:
            from ...models import GRPCRequestLog
            from ...auth import get_current_grpc_user, get_current_grpc_api_key

            user = get_current_grpc_user()
            api_key = get_current_grpc_api_key()
            client_ip = extract_ip_from_peer(peer)

            log_entry = await GRPCRequestLog.objects.acreate(
                request_id=request_id,
                service_name=service_name,
                method_name=method_name,
                full_method=full_method,
                user=user if user else None,
                api_key=api_key,
                is_authenticated=user is not None,
                client_ip=client_ip,
            )
            return log_entry

        except Exception as e:
            logger.error(f"Failed to create log entry: {e}", exc_info=True)
            return None

    async def mark_success(
        self,
        log_entry: Any,
        duration_ms: int,
        response: Any = None,
        request_data: dict = None,
        response_data: dict = None,
    ):
        """Mark log entry as successful."""
        if log_entry is None:
            return

        try:
            from ...models import GRPCRequestLog

            if response and self.log_response_data:
                response_data = serialize_message(response)

            await GRPCRequestLog.objects.amark_success(
                log_entry,
                duration_ms=duration_ms,
                response_data=response_data,
            )
        except Exception as e:
            logger.error(f"Failed to mark log success: {e}", exc_info=True)

    async def mark_error(
        self,
        log_entry: Any,
        error: Exception,
        context: grpc.aio.ServicerContext,
        duration_ms: int,
    ):
        """Mark log entry as error."""
        if log_entry is None:
            return

        try:
            from ...models import GRPCRequestLog

            grpc_code = get_grpc_code(error, context)

            await GRPCRequestLog.objects.amark_error(
                log_entry,
                grpc_status_code=grpc_code,
                error_message=str(error),
                error_details={"type": type(error).__name__},
                duration_ms=duration_ms,
            )
        except Exception as e:
            logger.error(f"Failed to mark log error: {e}", exc_info=True)


__all__ = ["RequestLogger"]
