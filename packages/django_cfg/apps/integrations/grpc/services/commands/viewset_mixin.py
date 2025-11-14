"""
DRF ViewSet mixin for streaming command execution.

Provides helper method for executing synchronous streaming commands
from Django REST Framework views with proper error handling.

Usage:
    from django_cfg.apps.integrations.grpc.services.commands.viewset_mixin import (
        StreamingCommandViewSetMixin
    )

    class MyViewSet(StreamingCommandViewSetMixin, viewsets.ModelViewSet):
        # Define command client class
        command_client_class = MyStreamingCommandClient

        # Define client_id field on model (default: "id")
        client_id_field = "id"

        @action(detail=True, methods=['post'])
        def start(self, request, pk=None):
            instance = self.get_object()
            success, result = self.exec_sync_command(
                instance,
                'start_sync',
                timeout=5.0
            )

            if not success:
                return result  # Error response (503/504)

            # Update model and return success
            instance.status = 'RUNNING'
            instance.save()

            return Response({
                **MySerializer(instance).data,
                'command_result': self.format_command_response(result)
            })

Created: 2025-11-12
Status: %%PRODUCTION%%
"""

import logging
from typing import Any, Type, Optional, Tuple

logger = logging.getLogger(__name__)


class StreamingCommandViewSetMixin:
    """
    DRF ViewSet mixin for executing streaming commands synchronously.

    Provides exec_sync_command() helper that:
    - Creates command client with model instance
    - Executes command method with timeout
    - Handles ClientNotConnectedError (503) and CommandTimeoutError (504)
    - Returns tuple: (success: bool, result: response or error Response)

    Subclass Requirements:
        - command_client_class: StreamingCommandClient subclass
        - client_id_field: Field name on model for client_id (default: "id")

    Optional Customization:
        - get_client_id(instance): Override to customize client_id extraction
        - format_command_response(response): Override to customize response format
    """

    # Subclass must define this
    command_client_class: Optional[Type] = None

    # Field name on model instance for client_id (default: "id")
    client_id_field: str = "id"

    # gRPC connection settings for cross-process mode (optional)
    grpc_host: Optional[str] = None
    grpc_port: Optional[int] = None

    def get_client_id(self, instance) -> str:
        """
        Extract client_id from model instance.

        Override this method to customize client_id extraction.

        Args:
            instance: Model instance

        Returns:
            Client ID string

        Example:
            def get_client_id(self, instance):
                return f"{instance.user_id}:{instance.id}"
        """
        return str(getattr(instance, self.client_id_field))

    def format_command_response(self, response) -> dict:
        """
        Format command response for API output.

        Override this method to customize response format.
        Default implementation handles protobuf CommandAck with success/message/status fields.

        Args:
            response: Command response (typically protobuf message)

        Returns:
            Dictionary with formatted response

        Example:
            def format_command_response(self, response):
                return {
                    'success': response.success,
                    'message': response.message,
                    'timestamp': response.timestamp,
                    'custom_field': response.custom_field,
                }
        """
        # Default format for CommandAck-style responses
        result = {}

        if hasattr(response, 'success'):
            result['success'] = response.success
        if hasattr(response, 'message'):
            result['message'] = response.message
        if hasattr(response, 'current_status'):
            result['status'] = response.current_status

        return result

    def exec_sync_command(
        self,
        instance,
        command_method: str,
        timeout: float = 5.0,
        **kwargs
    ) -> Tuple[bool, Any]:
        """
        Execute synchronous streaming command.

        This method:
        1. Creates command client with instance
        2. Calls command_method on client
        3. Waits for response with timeout
        4. Returns (success, result) tuple

        Args:
            instance: Model instance (must have client_id field)
            command_method: Command method name to call on client
                           (e.g., 'start_bot_sync', 'stop_bot_sync')
            timeout: Command timeout in seconds (default: 5.0)
            **kwargs: Additional arguments to pass to command method
                     (e.g., reason='Manual stop', force=True)

        Returns:
            tuple: (success: bool, result: response or DRF Response)

            On success:
                (True, command_response)  # command_response = protobuf/object

            On error:
                (False, Response)  # DRF Response with 503 or 504 status

        Raises:
            ValueError: If command_client_class not defined in subclass

        Example:
            success, result = self.exec_sync_command(
                bot,
                'start_bot_sync',
                timeout=10.0,
                reason='Manual start'
            )

            if not success:
                return result  # Return error Response (503/504)

            # result is CommandAck protobuf
            bot.status = 'RUNNING'
            bot.save()

            return Response({
                'bot': BotSerializer(bot).data,
                'command_result': self.format_command_response(result)
            })
        """
        # Lazy imports to avoid circular dependencies
        from asgiref.sync import async_to_sync
        from django_cfg.apps.integrations.grpc.services.commands.base import (
            ClientNotConnectedError,
            CommandTimeoutError,
        )

        # Check command_client_class is defined
        if self.command_client_class is None:
            raise ValueError(
                f"{self.__class__.__name__} must define 'command_client_class' attribute. "
                f"Set it to your StreamingCommandClient subclass."
            )

        # Extract client_id from instance
        client_id = self.get_client_id(instance)

        # Execute command in async context
        async def _exec():
            try:
                # Get streaming service from registry
                # Try to get from viewset attribute first, fallback to "default"
                from django_cfg.apps.integrations.grpc.services.commands.registry import get_streaming_service

                service_name = getattr(self, 'streaming_service_name', None)
                streaming_service = get_streaming_service(service_name) if service_name else None

                logger.debug(
                    f"🔍 ViewSet exec_sync_command: service_name={service_name}, "
                    f"streaming_service={streaming_service}, "
                    f"registry_id={id(streaming_service.response_registry) if streaming_service and hasattr(streaming_service, 'response_registry') else 'N/A'}"
                )

                # Create client with streaming_service for same-process communication
                # Or with grpc_host/grpc_port for cross-process communication
                client = self.command_client_class(
                    client_id,
                    instance,
                    streaming_service=streaming_service,
                    grpc_host=getattr(self, 'grpc_host', None),
                    grpc_port=getattr(self, 'grpc_port', None)
                )

                # Get command method
                if not hasattr(client, command_method):
                    raise AttributeError(
                        f"Command client {self.command_client_class.__name__} "
                        f"does not have method '{command_method}'"
                    )

                method = getattr(client, command_method)

                # Execute command
                logger.debug(
                    f"Executing {command_method} for client {client_id} "
                    f"(timeout={timeout}s, kwargs={kwargs})"
                )

                response = await method(timeout=timeout, **kwargs)

                logger.info(f"✅ {command_method} succeeded for client {client_id}")

                return {'success': True, 'response': response}

            except ClientNotConnectedError as e:
                logger.warning(f"⚠️  Client {client_id} not connected: {e}")
                return {'success': False, 'error': 'not_connected', 'exception': e}

            except CommandTimeoutError as e:
                logger.warning(f"⏱️  Command timeout for client {client_id}: {e}")
                return {'success': False, 'error': 'timeout', 'exception': e}

            except Exception as e:
                logger.error(
                    f"❌ Unexpected error executing {command_method} for client {client_id}: {e}",
                    exc_info=True
                )
                raise  # Re-raise unexpected errors

        # Execute async function in sync context
        result = async_to_sync(_exec)()

        # Handle errors
        if not result['success']:
            # Import DRF components lazily
            try:
                from rest_framework.response import Response
                from rest_framework import status
            except ImportError:
                raise ImportError(
                    "djangorestframework is required for StreamingCommandViewSetMixin. "
                    "Install with: pip install djangorestframework"
                )

            error_type = result['error']
            exception = result.get('exception')

            if error_type == 'not_connected':
                return False, Response(
                    {
                        "error": f"Client {client_id} not connected",
                        "detail": str(exception) if exception else None,
                        "code": "CLIENT_NOT_CONNECTED"
                    },
                    status=status.HTTP_503_SERVICE_UNAVAILABLE
                )

            else:  # timeout
                return False, Response(
                    {
                        "error": f"Timeout waiting for client {client_id}",
                        "timeout": timeout,
                        "detail": str(exception) if exception else None,
                        "code": "COMMAND_TIMEOUT"
                    },
                    status=status.HTTP_504_GATEWAY_TIMEOUT
                )

        # Success - return response
        return True, result['response']


__all__ = [
    'StreamingCommandViewSetMixin',
]
