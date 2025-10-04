"""
WebSocket Message Router.

Routes incoming WebSocket messages to appropriate handlers.

File size: ~450 lines
"""

import json
import time
from typing import Dict, Any, Optional, Callable, Awaitable
from uuid import UUID
from pydantic import BaseModel, Field, ValidationError

from ..models import (
    RPCErrorCode,
    RPCError,
    RPCValidationError,
    ValidationErrorDetail,
)
from ..logger import RPCLogger, LoggerConfig
from .connection_manager import ConnectionManager, ActiveConnection


class IncomingMessage(BaseModel):
    """
    Incoming WebSocket message.

    All WebSocket messages must follow this structure.

    Example:
        >>> msg = IncomingMessage(
        ...     type="rpc",
        ...     method="send_notification",
        ...     params={"user_id": "123", "message": "Hello"},
        ... )
    """

    type: str = Field(
        description="Message type (rpc, subscribe, unsubscribe, ping, etc.)",
    )

    method: Optional[str] = Field(
        default=None,
        description="Method name (for RPC messages)",
    )

    params: Dict[str, Any] = Field(
        default_factory=dict,
        description="Method parameters",
    )

    correlation_id: Optional[str] = Field(
        default=None,
        description="Correlation ID for request/response matching",
    )


class OutgoingMessage(BaseModel):
    """
    Outgoing WebSocket message.

    Example:
        >>> msg = OutgoingMessage(
        ...     type="response",
        ...     correlation_id="abc-123",
        ...     result={"status": "ok"},
        ... )
    """

    type: str = Field(
        description="Message type (response, notification, error, etc.)",
    )

    correlation_id: Optional[str] = Field(
        default=None,
        description="Correlation ID matching request",
    )

    result: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Success result",
    )

    error: Optional[Any] = Field(
        default=None,
        description="Error details (RPCError or subclass)",
    )


# Handler type: async function taking ActiveConnection, params, and returning result
HandlerFunc = Callable[[ActiveConnection, Dict[str, Any]], Awaitable[Dict[str, Any]]]


class MessageRouter:
    """
    Routes incoming WebSocket messages to handlers.

    Provides message validation, method dispatch, and error handling.

    Example:
        >>> router = MessageRouter(connection_manager)
        >>>
        >>> # Register handler
        >>> @router.register("send_notification")
        ... async def handle_notification(conn: ActiveConnection, params: dict):
        ...     user_id = params["user_id"]
        ...     message = params["message"]
        ...     # ... send notification
        ...     return {"status": "sent"}
        >>>
        >>> # Process message
        >>> response = await router.process_message(connection_info, raw_message)
    """

    def __init__(
        self,
        connection_manager: ConnectionManager,
        logger: Optional[RPCLogger] = None,
        logger_config: Optional[LoggerConfig] = None,
    ):
        """
        Initialize message router.

        Args:
            connection_manager: ConnectionManager instance
            logger: RPCLogger instance (creates default if None)
            logger_config: LoggerConfig for creating logger (if logger not provided)
        """
        self.connection_manager = connection_manager

        # Setup logger
        if logger is None:
            self.logger = RPCLogger(
                config=logger_config or LoggerConfig(),
                name="message_router",
            )
        else:
            self.logger = logger

        # Handler registry: method_name -> handler_function
        self._handlers: Dict[str, HandlerFunc] = {}

        # Type handlers: message_type -> handler_function
        self._type_handlers: Dict[str, HandlerFunc] = {}

    def register(self, method: str) -> Callable:
        """
        Decorator to register RPC method handler.

        Args:
            method: Method name to handle

        Returns:
            Decorator function

        Example:
            >>> @router.register("echo")
            ... async def handle_echo(conn: ActiveConnection, params: dict):
            ...     return params
        """

        def decorator(func: HandlerFunc) -> HandlerFunc:
            if method in self._handlers:
                self.logger.warning(f"Overwriting handler for method: {method}")

            self._handlers[method] = func
            self.logger.debug(f"Registered handler for method: {method}")
            return func

        return decorator

    def register_type(self, message_type: str) -> Callable:
        """
        Decorator to register message type handler.

        Args:
            message_type: Message type to handle (ping, subscribe, etc.)

        Returns:
            Decorator function

        Example:
            >>> @router.register_type("ping")
            ... async def handle_ping(conn: ActiveConnection, params: dict):
            ...     return {"pong": True}
        """

        def decorator(func: HandlerFunc) -> HandlerFunc:
            if message_type in self._type_handlers:
                self.logger.warning(f"Overwriting handler for type: {message_type}")

            self._type_handlers[message_type] = func
            self.logger.debug(f"Registered handler for type: {message_type}")
            return func

        return decorator

    async def process_message(
        self,
        conn_info: ActiveConnection,
        raw_message: str,
    ) -> Optional[str]:
        """
        Process incoming WebSocket message.

        Args:
            conn_info: Connection information
            raw_message: Raw message string (JSON)

        Returns:
            Response JSON string or None
        """
        correlation_id = None

        try:
            # Parse JSON
            try:
                data = json.loads(raw_message)
            except json.JSONDecodeError as e:
                self.logger.warning(
                    f"Invalid JSON from {conn_info.connection_id}: {e}",
                    connection_id=str(conn_info.connection_id),
                )
                return self._format_error_response(
                    correlation_id=None,
                    error=RPCError(
                        code=RPCErrorCode.INVALID_PARAMS,
                        message=f"Invalid JSON: {str(e)}",
                    ),
                )

            # Validate message structure
            try:
                message = IncomingMessage.model_validate(data)
                correlation_id = message.correlation_id
            except ValidationError as e:
                self.logger.warning(
                    f"Invalid message structure from {conn_info.connection_id}: {e}",
                    connection_id=str(conn_info.connection_id),
                )
                return self._format_error_response(
                    correlation_id=data.get("correlation_id"),
                    error=self._validation_error_to_rpc_error(e),
                )

            # Update activity
            conn_info.update_activity()

            # Route by message type
            if message.type == "rpc":
                return await self._handle_rpc(conn_info, message)
            else:
                # Use type handlers
                handler = self._type_handlers.get(message.type)
                if handler:
                    result = await handler(conn_info, message.params)
                    return self._format_success_response(correlation_id, result)
                else:
                    self.logger.warning(
                        f"Unknown message type: {message.type}",
                        connection_id=str(conn_info.connection_id),
                    )
                    return self._format_error_response(
                        correlation_id=correlation_id,
                        error=RPCError(
                            code=RPCErrorCode.METHOD_NOT_FOUND,
                            message=f"Unknown message type: {message.type}",
                        ),
                    )

        except Exception as e:
            self.logger.error(
                f"Error processing message from {conn_info.connection_id}: {e}",
                exc_info=True,
                connection_id=str(conn_info.connection_id),
                correlation_id=correlation_id,
            )
            return self._format_error_response(
                correlation_id=correlation_id,
                error=RPCError(
                    code=RPCErrorCode.INTERNAL_ERROR,
                    message=f"Internal error: {str(e)}",
                ),
            )

    async def _handle_rpc(
        self,
        conn_info: ActiveConnection,
        message: IncomingMessage,
    ) -> str:
        """
        Handle RPC method call with full logging.

        Args:
            conn_info: Connection information
            message: Validated incoming message

        Returns:
            Response JSON string
        """
        if not message.method:
            return self._format_error_response(
                correlation_id=message.correlation_id,
                error=RPCError(
                    code=RPCErrorCode.INVALID_PARAMS,
                    message="RPC message missing 'method' field",
                ),
            )

        # Find handler
        handler = self._handlers.get(message.method)
        if not handler:
            self.logger.warning(
                f"Method not found: {message.method}",
                method=message.method,
                correlation_id=message.correlation_id,
            )
            return self._format_error_response(
                correlation_id=message.correlation_id,
                error=RPCError(
                    code=RPCErrorCode.METHOD_NOT_FOUND,
                    message=f"Method not found: {message.method}",
                ),
            )

        # Log RPC request
        self.logger.log_rpc_request(
            method=message.method,
            params=message.params,
            correlation_id=message.correlation_id or "unknown",
            user_id=getattr(conn_info, "user_id", None),
            connection_id=conn_info.connection_id,
        )

        # Execute handler with timing
        start_time = time.perf_counter()
        success = True
        error_code = None
        result = None

        try:
            result = await handler(conn_info, message.params)

            # Log successful response
            duration_ms = (time.perf_counter() - start_time) * 1000
            self.logger.log_rpc_response(
                method=message.method,
                result=result,
                correlation_id=message.correlation_id or "unknown",
                duration_ms=duration_ms,
                success=True,
            )

            return self._format_success_response(message.correlation_id, result)

        except ValidationError as e:
            duration_ms = (time.perf_counter() - start_time) * 1000

            self.logger.warning(
                f"Validation error in {message.method}: {e}",
                method=message.method,
                correlation_id=message.correlation_id,
            )

            self.logger.log_rpc_response(
                method=message.method,
                result=None,
                correlation_id=message.correlation_id or "unknown",
                duration_ms=duration_ms,
                success=False,
                error_code="VALIDATION_ERROR",
            )

            return self._format_error_response(
                correlation_id=message.correlation_id,
                error=self._validation_error_to_rpc_error(e),
            )

        except Exception as e:
            duration_ms = (time.perf_counter() - start_time) * 1000
            error_code = type(e).__name__

            self.logger.error(
                f"Handler error in {message.method}: {e}",
                exc_info=True,
                method=message.method,
                correlation_id=message.correlation_id,
                connection_id=str(conn_info.connection_id),
            )

            self.logger.log_rpc_response(
                method=message.method,
                result=None,
                correlation_id=message.correlation_id or "unknown",
                duration_ms=duration_ms,
                success=False,
                error_code=error_code,
            )

            return self._format_error_response(
                correlation_id=message.correlation_id,
                error=RPCError(
                    code=RPCErrorCode.INTERNAL_ERROR,
                    message=f"Handler error: {str(e)}",
                ),
            )

    def _format_success_response(
        self,
        correlation_id: Optional[str],
        result: Dict[str, Any],
    ) -> str:
        """
        Format success response.

        Args:
            correlation_id: Correlation ID from request
            result: Result data

        Returns:
            JSON string
        """
        response = OutgoingMessage(
            type="response",
            correlation_id=correlation_id,
            result=result,
        )
        return response.model_dump_json()

    def _format_error_response(
        self,
        correlation_id: Optional[str],
        error: RPCError,
    ) -> str:
        """
        Format error response.

        Args:
            correlation_id: Correlation ID from request
            error: Error details

        Returns:
            JSON string
        """
        response = OutgoingMessage(
            type="error",
            correlation_id=correlation_id,
            error=error,
        )
        return response.model_dump_json()

    def _validation_error_to_rpc_error(self, error: ValidationError) -> RPCValidationError:
        """
        Convert Pydantic ValidationError to RPCValidationError.

        Args:
            error: Pydantic ValidationError

        Returns:
            RPCValidationError
        """
        details = [
            ValidationErrorDetail(
                field=".".join(str(loc) for loc in err["loc"]),
                error=err["msg"],
                input_value=err.get("input"),
            )
            for err in error.errors()
        ]

        return RPCValidationError(
            code=RPCErrorCode.VALIDATION_ERROR,
            message="Validation failed",
            validation_errors=details,
        )

    def list_handlers(self) -> Dict[str, list]:
        """
        List all registered handlers.

        Returns:
            Dict with 'methods' and 'types' keys containing handler names
        """
        return {
            "methods": sorted(self._handlers.keys()),
            "types": sorted(self._type_handlers.keys()),
        }

    def has_handler(self, method: str) -> bool:
        """
        Check if handler exists for method.

        Args:
            method: Method name

        Returns:
            True if handler exists
        """
        return method in self._handlers

    def has_type_handler(self, message_type: str) -> bool:
        """
        Check if handler exists for message type.

        Args:
            message_type: Message type

        Returns:
            True if handler exists
        """
        return message_type in self._type_handlers


__all__ = [
    "IncomingMessage",
    "OutgoingMessage",
    "HandlerFunc",
    "MessageRouter",
]
