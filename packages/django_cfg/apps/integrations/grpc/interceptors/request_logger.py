"""
Request Logger Interceptor for gRPC.

Automatically logs all gRPC requests to the database for monitoring.
"""

from __future__ import annotations

import asyncio
import logging
import time
import uuid
from typing import Callable

import grpc
import grpc.aio

logger = logging.getLogger(__name__)


class RequestLoggerInterceptor(grpc.aio.ServerInterceptor):
    """
    gRPC interceptor for request logging to database (async).

    Features:
    - Logs all requests to GRPCRequestLog model
    - Captures timing, status, and error information
    - Links requests to authenticated users
    - Captures client metadata
    - Tracks request/response sizes

    Example:
        ```python
        # In Django settings (auto-configured)
        GRPC_FRAMEWORK = {
            "SERVER_INTERCEPTORS": [
                "django_cfg.apps.integrations.grpc.interceptors.RequestLoggerInterceptor",
            ]
        }
        ```

    Database Schema:
        All requests are logged to GRPCRequestLog model.
        Use admin interface or REST API to view logs.
    """

    def __init__(self, log_request_data: bool = False, log_response_data: bool = False):
        """
        Initialize request logger.

        Args:
            log_request_data: Whether to log request data (default: False)
            log_response_data: Whether to log response data (default: False)
        """
        self.log_request_data = log_request_data
        self.log_response_data = log_response_data

    async def intercept_service(
        self,
        continuation: Callable,
        handler_call_details: grpc.HandlerCallDetails,
    ) -> grpc.RpcMethodHandler:
        """
        Intercept gRPC service call for logging (async).

        Args:
            continuation: Function to invoke the next interceptor or handler
            handler_call_details: Details about the RPC call

        Returns:
            RPC method handler with logging
        """
        # Generate unique request ID
        request_id = str(uuid.uuid4())

        # Extract method info
        full_method = handler_call_details.method
        service_name, method_name = self._parse_method(full_method)

        # Extract client metadata
        metadata_dict = dict(handler_call_details.invocation_metadata)
        peer = metadata_dict.get("peer", "unknown")
        user_agent = metadata_dict.get("user-agent", None)

        # Get handler and wrap it (await for async)
        handler = await continuation(handler_call_details)

        if handler is None:
            logger.warning(f"[gRPC Logger] No handler found for {full_method}")
            return None

        # Wrap handler methods to log to database
        return self._wrap_handler(
            handler,
            request_id,
            service_name,
            method_name,
            full_method,
            peer,
            user_agent,
        )

    def _wrap_handler(
        self,
        handler: grpc.RpcMethodHandler,
        request_id: str,
        service_name: str,
        method_name: str,
        full_method: str,
        peer: str,
        user_agent: str,
    ) -> grpc.RpcMethodHandler:
        """
        Wrap handler to add database logging.

        Args:
            handler: Original RPC method handler
            request_id: Unique request ID
            service_name: Service name
            method_name: Method name
            full_method: Full method path
            peer: Client peer
            user_agent: User agent

        Returns:
            Wrapped RPC method handler
        """
        def wrap_unary_unary(behavior):
            async def wrapper(request, context):
                start_time = time.time()

                # Create log entry (async)
                log_entry = await self._create_log_entry_async(
                    request_id=request_id,
                    service_name=service_name,
                    method_name=method_name,
                    full_method=full_method,
                    peer=peer,
                    user_agent=user_agent,
                    context=context,
                    request=request if self.log_request_data else None,
                )

                try:
                    response = await behavior(request, context)
                    duration_ms = int((time.time() - start_time) * 1000)

                    # Mark as successful (async)
                    await self._mark_success_async(
                        log_entry,
                        duration_ms=duration_ms,
                        response=response if self.log_response_data else None,
                    )

                    return response
                except Exception as e:
                    duration_ms = int((time.time() - start_time) * 1000)

                    # Mark as error (async)
                    await self._mark_error_async(
                        log_entry,
                        error=e,
                        context=context,
                        duration_ms=duration_ms,
                    )

                    raise

            return wrapper

        def wrap_unary_stream(behavior):
            async def wrapper(request, context):
                start_time = time.time()

                # Create log entry (async)
                log_entry = await self._create_log_entry_async(
                    request_id=request_id,
                    service_name=service_name,
                    method_name=method_name,
                    full_method=full_method,
                    peer=peer,
                    user_agent=user_agent,
                    context=context,
                    request=request if self.log_request_data else None,
                )

                try:
                    response_count = 0
                    async for response in behavior(request, context):
                        response_count += 1
                        yield response

                    duration_ms = int((time.time() - start_time) * 1000)

                    # Mark as successful (async)
                    await self._mark_success_async(
                        log_entry,
                        duration_ms=duration_ms,
                        response_data={"message_count": response_count} if not self.log_response_data else None,
                    )

                except Exception as e:
                    duration_ms = int((time.time() - start_time) * 1000)

                    # Mark as error (async)
                    await self._mark_error_async(
                        log_entry,
                        error=e,
                        context=context,
                        duration_ms=duration_ms,
                    )

                    raise

            return wrapper

        def wrap_stream_unary(behavior):
            async def wrapper(request_iterator, context):
                start_time = time.time()

                # Create log entry (async)
                log_entry = await self._create_log_entry_async(
                    request_id=request_id,
                    service_name=service_name,
                    method_name=method_name,
                    full_method=full_method,
                    peer=peer,
                    user_agent=user_agent,
                    context=context,
                )

                try:
                    # Count requests (async for)
                    requests = []
                    request_count = 0
                    async for req in request_iterator:
                        request_count += 1
                        requests.append(req)

                    # Process (create async generator)
                    async def async_iter():
                        for r in requests:
                            yield r

                    response = await behavior(async_iter(), context)
                    duration_ms = int((time.time() - start_time) * 1000)

                    # Mark as successful (async)
                    await self._mark_success_async(
                        log_entry,
                        duration_ms=duration_ms,
                        request_data={"message_count": request_count} if not self.log_request_data else None,
                        response=response if self.log_response_data else None,
                    )

                    return response
                except Exception as e:
                    duration_ms = int((time.time() - start_time) * 1000)

                    # Mark as error (async)
                    await self._mark_error_async(
                        log_entry,
                        error=e,
                        context=context,
                        duration_ms=duration_ms,
                    )

                    raise

            return wrapper

        def wrap_stream_stream(behavior):
            async def wrapper(request_iterator, context):
                start_time = time.time()

                # Create log entry (async)
                log_entry = await self._create_log_entry_async(
                    request_id=request_id,
                    service_name=service_name,
                    method_name=method_name,
                    full_method=full_method,
                    peer=peer,
                    user_agent=user_agent,
                    context=context,
                )

                try:
                    # Count requests (async for)
                    requests = []
                    request_count = 0
                    async for req in request_iterator:
                        request_count += 1
                        requests.append(req)

                    # Process and count responses (async for)
                    async def async_iter():
                        for r in requests:
                            yield r

                    response_count = 0
                    async for response in behavior(async_iter(), context):
                        response_count += 1
                        yield response

                    duration_ms = int((time.time() - start_time) * 1000)

                    # Mark as successful (async)
                    await self._mark_success_async(
                        log_entry,
                        duration_ms=duration_ms,
                        response_data={"request_count": request_count, "response_count": response_count} if not self.log_response_data else None,
                    )

                except Exception as e:
                    duration_ms = int((time.time() - start_time) * 1000)

                    # Mark as error (async)
                    await self._mark_error_async(
                        log_entry,
                        error=e,
                        context=context,
                        duration_ms=duration_ms,
                    )

                    raise

            return wrapper

        # Return wrapped handler based on type
        if handler.unary_unary:
            return grpc.unary_unary_rpc_method_handler(
                wrap_unary_unary(handler.unary_unary),
                request_deserializer=handler.request_deserializer,
                response_serializer=handler.response_serializer,
            )
        elif handler.unary_stream:
            return grpc.unary_stream_rpc_method_handler(
                wrap_unary_stream(handler.unary_stream),
                request_deserializer=handler.request_deserializer,
                response_serializer=handler.response_serializer,
            )
        elif handler.stream_unary:
            return grpc.stream_unary_rpc_method_handler(
                wrap_stream_unary(handler.stream_unary),
                request_deserializer=handler.request_deserializer,
                response_serializer=handler.response_serializer,
            )
        elif handler.stream_stream:
            return grpc.stream_stream_rpc_method_handler(
                wrap_stream_stream(handler.stream_stream),
                request_deserializer=handler.request_deserializer,
                response_serializer=handler.response_serializer,
            )
        else:
            return handler

    async def _create_log_entry_async(
        self,
        request_id: str,
        service_name: str,
        method_name: str,
        full_method: str,
        peer: str,
        user_agent: str,
        context: grpc.aio.ServicerContext,
        request=None,
    ):
        """Create initial log entry in database (async)."""
        try:
            from ..models import GRPCRequestLog
            from ..auth import get_current_grpc_user, get_current_grpc_api_key

            # Get user and api_key from contextvars (set by ApiKeyAuthInterceptor)
            user = get_current_grpc_user()
            api_key = get_current_grpc_api_key()
            is_authenticated = user is not None

            logger.info(f"[RequestLogger] Got contextvar api_key = {api_key} (user={user}, authenticated={is_authenticated})")

            # Extract client IP from peer
            client_ip = self._extract_ip_from_peer(peer)

            # Create log entry (wrap Django ORM in asyncio.to_thread)
            log_entry = await asyncio.to_thread(
                GRPCRequestLog.objects.create,
                request_id=request_id,
                service_name=service_name,
                method_name=method_name,
                full_method=full_method,
                user=user if is_authenticated else None,
                api_key=api_key,
                is_authenticated=is_authenticated,
                client_ip=client_ip,
                user_agent=user_agent,
                peer=peer,
                request_data=self._serialize_message(request) if request else None,
                status="pending",
            )

            return log_entry

        except Exception as e:
            logger.error(f"Failed to create log entry: {e}", exc_info=True)
            return None

    async def _mark_success_async(
        self,
        log_entry,
        duration_ms: int,
        response=None,
        request_data: dict = None,
        response_data: dict = None,
    ):
        """Mark log entry as successful (async)."""
        if log_entry is None:
            return

        try:
            from ..models import GRPCRequestLog

            # Prepare response data
            if response:
                response_data = self._serialize_message(response)

            # Wrap Django ORM in asyncio.to_thread
            await asyncio.to_thread(
                GRPCRequestLog.objects.mark_success,
                log_entry,
                duration_ms=duration_ms,
                response_data=response_data,
            )

        except Exception as e:
            logger.error(f"Failed to mark success: {e}", exc_info=True)

    async def _mark_error_async(
        self,
        log_entry,
        error: Exception,
        context: grpc.aio.ServicerContext,
        duration_ms: int,
    ):
        """Mark log entry as error (async)."""
        if log_entry is None:
            return

        try:
            from ..models import GRPCRequestLog

            # Get gRPC status code
            grpc_code = self._get_grpc_code(error, context)

            # Wrap Django ORM in asyncio.to_thread
            await asyncio.to_thread(
                GRPCRequestLog.objects.mark_error,
                log_entry,
                grpc_status_code=grpc_code,
                error_message=str(error),
                error_details={"type": type(error).__name__},
                duration_ms=duration_ms,
            )

        except Exception as e:
            logger.error(f"Failed to mark error: {e}", exc_info=True)

    def _parse_method(self, full_method: str) -> tuple[str, str]:
        """
        Parse full method path into service and method names.

        Args:
            full_method: Full method path (e.g., /myapp.UserService/GetUser)

        Returns:
            (service_name, method_name) tuple
        """
        try:
            parts = full_method.strip("/").split("/")
            if len(parts) >= 2:
                return parts[0], parts[1]
            else:
                return full_method, "unknown"
        except Exception:
            return full_method, "unknown"

    def _extract_ip_from_peer(self, peer: str) -> str | None:
        """
        Extract IP address from peer string.

        Args:
            peer: Peer string (e.g., ipv4:127.0.0.1:12345)

        Returns:
            IP address or None
        """
        try:
            if ":" in peer:
                parts = peer.split(":")
                # Handle ipv4:x.x.x.x:port format
                if len(parts) >= 3 and parts[0] in ["ipv4", "ipv6"]:
                    return parts[1]
                # Handle x.x.x.x:port format
                elif len(parts) == 2:
                    return parts[0]
        except Exception:
            pass
        return None

    def _get_grpc_code(self, error: Exception, context: grpc.aio.ServicerContext) -> str:
        """Get gRPC status code from error."""
        try:
            # Check if error is a gRPC error
            if hasattr(error, "code"):
                return error.code().name

            # Try to get from context
            if hasattr(context, "_state") and hasattr(context._state, "code"):
                return context._state.code.name

            # Default to UNKNOWN
            return "UNKNOWN"
        except Exception:
            return "UNKNOWN"

    def _serialize_message(self, message) -> dict | None:
        """Serialize protobuf message to dict."""
        try:
            # Try to use MessageToDict from google.protobuf
            from google.protobuf.json_format import MessageToDict
            return MessageToDict(message)
        except Exception as e:
            logger.debug(f"Failed to serialize message: {e}")
            return None


__all__ = ["RequestLoggerInterceptor"]
