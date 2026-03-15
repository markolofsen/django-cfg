"""
Cross-process command routing for gRPC services.

This module provides automatic routing between direct calls (same process)
and gRPC calls (cross-process) for Django multi-process architecture.

**Problem**:
Django typically runs multiple processes:
- `runserver` - HTTP server process
- `rungrpc` - gRPC server process (with active WebSocket connections)

When code in `runserver` needs to send a command to a connected gRPC client,
it must use gRPC to communicate with `rungrpc` process.

**Solution**:
CrossProcessCommandRouter automatically detects the current process and routes commands:
1. **Same process (rungrpc)**: Direct method call (fast, no network)
2. **Different process (runserver)**: gRPC call to localhost (cross-process)

**Architecture**:
```
┌─────────────────────────────────────────────────────────────┐
│  runserver process                                           │
│                                                              │
│  Django View/Command                                         │
│         │                                                    │
│         ▼                                                    │
│  CrossProcessCommandRouter                                   │
│         │                                                    │
│         │ (service_instance is None)                         │
│         │                                                    │
│         ▼                                                    │
│  gRPC call to localhost:50051 ────────────────────┐         │
└───────────────────────────────────────────────────│─────────┘
                                                     │
                                                     │ gRPC
                                                     │
┌────────────────────────────────────────────────────┼─────────┐
│  rungrpc process                                   │         │
│                                                    ▼         │
│                          RPC Handler (SendCommandToClient)   │
│                                    │                         │
│                                    ▼                         │
│                          service_instance.send_to_client()   │
│                                    │                         │
│                                    ▼                         │
│                          Active WebSocket connection         │
└──────────────────────────────────────────────────────────────┘
```

**Usage Example**:
```python
from .router import CrossProcessCommandRouter, CrossProcessConfig

# 1. Configure router
config = CrossProcessConfig(
    grpc_host="localhost",
    grpc_port=50051,
    rpc_method_name="SendCommandToClient",
    timeout=5.0,
)

router = CrossProcessCommandRouter(
    config=config,
    get_service_instance=lambda: get_streaming_service(),
)

# 2. Register with service (in rungrpc process)
streaming_service = BotStreamingService()
router.register_service(streaming_service)

# 3. Route commands (works from any process)
success = await router.send_command(
    client_id="bot_123",
    command=my_command_protobuf,
)
```

Created: 2025-11-07
Status: %%PRODUCTION%%
Phase: Phase 1 - Universal Components
"""

from typing import Generic, Optional, Callable, Any, TypeVar
import logging

import grpc

from .config import CrossProcessConfig


logger = logging.getLogger(__name__)


# ============================================================================
# Type Variables
# ============================================================================

TCommand = TypeVar('TCommand')
"""Generic type for command messages (protobuf)"""

TService = TypeVar('TService')
"""Generic type for service instance"""

TRequest = TypeVar('TRequest')
"""Generic type for gRPC request"""

TResponse = TypeVar('TResponse')
"""Generic type for gRPC response"""


# ============================================================================
# Router
# ============================================================================

class CrossProcessCommandRouter(Generic[TCommand, TService]):
    """
    Routes commands between direct calls and cross-process gRPC calls.

    This router automatically detects whether the service instance is available
    locally (same process) or requires cross-process communication via gRPC.

    **Type Parameters**:
        TCommand: Type of command to route (protobuf message)
        TService: Type of service instance

    **Parameters**:
        config: CrossProcessConfig with gRPC connection details
        get_service_instance: Callable that returns local service instance (or None)
        stub_factory: Factory function to create gRPC stub from channel
        request_factory: Factory function to create gRPC request
        extract_success: Function to extract success bool from response

    **Example - Full Setup**:
    ```python
    # 1. Define factories
    def create_stub(channel):
        return BotStreamingServiceStub(channel)

    def create_request(client_id, command):
        return SendCommandRequest(
            client_id=client_id,
            command=command,
        )

    def is_success(response):
        return response.success

    # 2. Create router
    router = CrossProcessCommandRouter(
        config=config,
        get_service_instance=lambda: _streaming_service_instance,
        stub_factory=create_stub,
        request_factory=create_request,
        extract_success=is_success,
    )

    # 3. Use anywhere (automatically routes correctly)
    success = await router.send_command("bot_123", command_pb)
    ```
    """

    def __init__(
        self,
        config: CrossProcessConfig,
        get_service_instance: Callable[[], Optional[TService]],
        stub_factory: Callable[[grpc.aio.Channel], Any],
        request_factory: Callable[[str, TCommand], Any],
        extract_success: Callable[[Any], bool],
        extract_message: Optional[Callable[[Any], str]] = None,
    ):
        """
        Initialize cross-process command router.

        Args:
            config: Pydantic configuration
            get_service_instance: Returns local service instance or None
            stub_factory: Creates gRPC stub from channel
            request_factory: Creates gRPC request from (client_id, command)
            extract_success: Extracts success bool from gRPC response
            extract_message: Optional - extracts error message from response
        """
        self.config = config
        self.get_service_instance = get_service_instance
        self.stub_factory = stub_factory
        self.request_factory = request_factory
        self.extract_success = extract_success
        self.extract_message = extract_message or (lambda r: getattr(r, 'message', ''))

        if self.config.enable_logging:
            logger.info(
                f"CrossProcessCommandRouter initialized: {self.config.grpc_address}, "
                f"method={self.config.rpc_method_name}"
            )

    # ------------------------------------------------------------------------
    # Main Routing Method
    # ------------------------------------------------------------------------

    async def send_command(
        self,
        client_id: str,
        command: TCommand,
    ) -> bool:
        """
        Send command to client (automatically routes).

        **Routing Logic**:
        1. Check if service instance is available locally
        2. If yes -> direct call (fast, same process)
        3. If no -> gRPC call to localhost (cross-process)

        Args:
            client_id: Target client identifier
            command: Command to send (protobuf message)

        Returns:
            True if command sent successfully, False otherwise

        Example:
        ```python
        # Works from any process!
        command = BotCommand(action="START")
        success = await router.send_command("bot_123", command)
        ```
        """
        # Try direct call first (same process)
        service = self.get_service_instance()

        if service is not None:
            return await self._send_direct(service, client_id, command)

        # Fallback to cross-process call
        return await self._send_cross_process(client_id, command)

    # ------------------------------------------------------------------------
    # Direct Call (Same Process)
    # ------------------------------------------------------------------------

    async def _send_direct(
        self,
        service: TService,
        client_id: str,
        command: TCommand,
    ) -> bool:
        """
        Send command via direct method call (same process).

        Args:
            service: Local service instance
            client_id: Target client ID
            command: Command to send

        Returns:
            True if sent successfully
        """
        if self.config.enable_logging:
            logger.debug(f"📞 Direct call for client {client_id}")

        try:
            # Assumes service has send_to_client method
            # (from BidirectionalStreamingService)
            success = await service.send_to_client(client_id, command)

            if self.config.enable_logging:
                if success:
                    logger.info(f"✅ Direct call succeeded for {client_id}")
                else:
                    logger.warning(f"⚠️  Direct call failed for {client_id} (client not connected)")

            return success

        except Exception as e:
            if self.config.enable_logging:
                logger.error(f"❌ Direct call error for {client_id}: {e}", exc_info=True)
            return False

    # ------------------------------------------------------------------------
    # Cross-Process Call (gRPC)
    # ------------------------------------------------------------------------

    async def _send_cross_process(
        self,
        client_id: str,
        command: TCommand,
    ) -> bool:
        """
        Send command via gRPC call to localhost (cross-process).

        Args:
            client_id: Target client ID
            command: Command to send

        Returns:
            True if sent successfully
        """
        if self.config.enable_logging:
            logger.debug(
                f"📡 Cross-process gRPC call for client {client_id} to {self.config.grpc_address}"
            )

        try:
            # Create gRPC channel to local server
            async with grpc.aio.insecure_channel(self.config.grpc_address) as channel:
                # Create stub
                stub = self.stub_factory(channel)

                # Get RPC method dynamically
                rpc_method = getattr(stub, self.config.rpc_method_name)

                # Create request
                request = self.request_factory(client_id, command)

                # Call RPC with timeout
                response = await rpc_method(
                    request,
                    timeout=self.config.timeout,
                )

                # Extract success
                success = self.extract_success(response)

                if self.config.enable_logging:
                    if success:
                        logger.info(f"✅ Cross-process RPC succeeded for {client_id}")
                    else:
                        message = self.extract_message(response)
                        logger.warning(f"⚠️  Cross-process RPC failed for {client_id}: {message}")

                return success

        except grpc.RpcError as e:
            if self.config.enable_logging:
                logger.error(
                    f"❌ gRPC error for {client_id}: {e.code()} - {e.details()}",
                    exc_info=True,
                )
            return False

        except Exception as e:
            if self.config.enable_logging:
                logger.error(f"❌ Cross-process call error for {client_id}: {e}", exc_info=True)
            return False

    # ------------------------------------------------------------------------
    # Broadcast
    # ------------------------------------------------------------------------

    async def broadcast_command(
        self,
        command: TCommand,
        client_ids: Optional[list[str]] = None,
    ) -> dict[str, bool]:
        """
        Broadcast command to multiple clients.

        Args:
            command: Command to broadcast
            client_ids: Optional list of client IDs (None = all connected)

        Returns:
            Dict mapping client_id -> success bool

        Example:
        ```python
        results = await router.broadcast_command(
            command=shutdown_command,
            client_ids=["bot_1", "bot_2", "bot_3"],
        )
        # {"bot_1": True, "bot_2": False, "bot_3": True}
        ```
        """
        results = {}

        # If no client_ids provided, try to get all from service
        if client_ids is None:
            service = self.get_service_instance()
            if service is not None and hasattr(service, 'get_active_connections'):
                client_ids = list(service.get_active_connections().keys())
            else:
                if self.config.enable_logging:
                    logger.warning("Cannot broadcast: no client_ids and service unavailable")
                return {}

        # Send to each client
        for client_id in client_ids:
            success = await self.send_command(client_id, command)
            results[client_id] = success

        if self.config.enable_logging:
            success_count = sum(results.values())
            total_count = len(results)
            logger.info(f"Broadcast completed: {success_count}/{total_count} succeeded")

        return results

    # ------------------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------------------

    def is_same_process(self) -> bool:
        """
        Check if running in same process as gRPC server.

        Returns:
            True if service instance is available (same process)
        """
        return self.get_service_instance() is not None

    def get_process_mode(self) -> str:
        """
        Get current process mode.

        Returns:
            "direct" if same process, "cross-process" otherwise
        """
        return "direct" if self.is_same_process() else "cross-process"


# ============================================================================
# Exports
# ============================================================================

__all__ = [
    # Config
    'CrossProcessConfig',

    # Router
    'CrossProcessCommandRouter',
]
