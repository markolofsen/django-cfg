"""
Example: Base Command Client Implementation

This example shows how to extend StreamingCommandClient for a specific gRPC service.
It implements the _send_via_grpc method for cross-process communication.

Copy this pattern and adapt it to your service:
1. Update protobuf imports (your_service_pb2, your_service_pb2_grpc)
2. Update Command type to match your proto
3. Update stub class name
4. Update SendCommandRequest message structure
5. Optionally add model type hints using Protocol

Usage:
    # Import your extended client
    from your_app.grpc.commands.base_client import ExampleCommandClient

    # Cross-process mode
    client = ExampleCommandClient(client_id="123", grpc_port=50051)

    # Same-process mode
    from django_cfg.apps.integrations.grpc.services.commands.registry import get_streaming_service
    service = get_streaming_service("example")
    client = ExampleCommandClient(client_id="123", streaming_service=service)
"""

import logging
from typing import Any, Optional, Protocol, runtime_checkable

from django_cfg.apps.integrations.grpc.services.commands.base import (
    StreamingCommandClient,
    CommandClientConfig,
)

# IMPORTANT: Update these imports to match your protobuf files
# Example assumes you have:
# - your_service_pb2.py (generated from your_service.proto)
# - your_service_pb2_grpc.py (generated gRPC stub)
#
# from your_app.grpc.generated import your_service_pb2 as pb2
# from your_app.grpc.generated import your_service_pb2_grpc as pb2_grpc

logger = logging.getLogger(__name__)


# ============================================================================
# Protocol for Type-Safe Model Operations
# ============================================================================

@runtime_checkable
class HasStatus(Protocol):
    """
    Protocol for models that have a status field.

    This allows type-safe operations on Django models without tight coupling.
    Any model with these attributes/methods will pass type checking.

    Example Django model:
        class YourModel(models.Model):
            status = models.CharField(max_length=20)

            # Django 5.2+ async save
            async def asave(self, update_fields=None):
                ...
    """
    status: str

    async def asave(self, update_fields: Optional[list[str]] = None) -> None:
        """Django async save method (Django 5.2+)."""
        ...


@runtime_checkable
class HasConfig(Protocol):
    """
    Protocol for models that have configuration.

    Example Django model:
        class YourModel(models.Model):
            config = models.JSONField(default=dict)

            async def asave(self, update_fields=None):
                ...
    """
    config: dict

    async def asave(self, update_fields: Optional[list[str]] = None) -> None:
        """Django async save method."""
        ...


# ============================================================================
# Example Command Client
# ============================================================================

class ExampleCommandClient(StreamingCommandClient):  # [pb2.Command]
    """
    Example implementation of universal command client.

    This shows how to extend StreamingCommandClient with gRPC implementation.

    Type Parameters:
        TCommand: Should be your protobuf Command type (e.g., pb2.Command)

    Note: The type parameter is commented out because protobuf imports
    are not available in this example. In your implementation, use:

        class YourCommandClient(StreamingCommandClient[pb2.Command]):
            ...
    """

    def __init__(
        self,
        client_id: str,
        model: Optional[Any] = None,
        streaming_service: Optional[Any] = None,
        config: Optional[CommandClientConfig] = None,
        grpc_port: Optional[int] = None,
        grpc_host: Optional[str] = None,
    ):
        """
        Initialize example command client.

        Args:
            client_id: Unique identifier for the client
            model: Optional Django model instance (for callbacks)
            streaming_service: BidirectionalStreamingService for same-process mode
            config: Client configuration
            grpc_port: gRPC port for cross-process mode
            grpc_host: gRPC host for cross-process mode
        """
        super().__init__(
            client_id=client_id,
            streaming_service=streaming_service,
            config=config,
            grpc_port=grpc_port,
            grpc_host=grpc_host,
        )
        self.model = model

    async def _send_via_grpc(self, command) -> bool:  # command: pb2.Command
        """
        Send command via gRPC RPC (cross-process mode).

        This implements the abstract method from StreamingCommandClient.

        Args:
            command: Protobuf command message (pb2.Command)

        Returns:
            True if RPC succeeded, False otherwise

        Implementation guide:
            1. Import grpc and your stubs at the top of the file:
               import grpc
               from your_app.grpc.generated import your_service_pb2_grpc as pb2_grpc
               from your_app.grpc.generated import your_service_pb2 as pb2

            2. Create gRPC channel
            3. Create stub instance
            4. Create request message with client_id and command
            5. Call SendCommandToClient RPC
            6. Return response.success
        """
        # This is a template - you need to implement with your actual protobuf types

        logger.warning(
            "Example implementation: _send_via_grpc is not implemented. "
            "Please copy this file and implement with your actual protobuf types."
        )

        # Example implementation (uncomment and adapt):
        #
        # try:
        #     import grpc
        #
        #     async with grpc.aio.insecure_channel(
        #         self.get_grpc_address(),
        #         options=[
        #             ('grpc.keepalive_time_ms', 10000),
        #             ('grpc.keepalive_timeout_ms', 5000),
        #         ]
        #     ) as channel:
        #         stub = pb2_grpc.YourServiceStub(channel)
        #
        #         # Create request with your service's message structure
        #         request = pb2.SendCommandRequest(
        #             client_id=self.client_id,
        #             command=command,
        #         )
        #
        #         # Call your service's SendCommandToClient RPC
        #         response = await stub.SendCommandToClient(
        #             request,
        #             timeout=self.config.call_timeout
        #         )
        #
        #         if response.success:
        #             logger.debug(f"Command sent to {self.client_id} via gRPC")
        #             return True
        #         else:
        #             logger.warning(
        #                 f"Command failed for {self.client_id}: {response.message}"
        #             )
        #             return False
        #
        # except grpc.RpcError as e:
        #     logger.error(
        #         f"gRPC error sending command to {self.client_id}: "
        #         f"{e.code()} - {e.details()}",
        #         exc_info=True
        #     )
        #     return False
        # except Exception as e:
        #     logger.error(
        #         f"Error sending command to {self.client_id}: {e}",
        #         exc_info=True
        #     )
        #     return False

        return False


__all__ = [
    'ExampleCommandClient',
    'HasStatus',
    'HasConfig',
]
