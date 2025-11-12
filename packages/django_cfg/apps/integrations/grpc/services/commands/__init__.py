"""
Universal Streaming Commands

Provides reusable command client architecture for bidirectional gRPC streaming services.

Quick Start:
    1. Create your command client:
        from django_cfg.apps.integrations.grpc.services.commands.base import StreamingCommandClient
        from your_app.grpc import service_pb2 as pb2

        class MyCommandClient(StreamingCommandClient[pb2.Command]):
            async def _send_via_grpc(self, command):
                # Implement gRPC call
                async with grpc.aio.insecure_channel(self.get_grpc_address()) as channel:
                    stub = service_pb2_grpc.YourServiceStub(channel)
                    request = pb2.SendCommandRequest(client_id=self.client_id, command=command)
                    response = await stub.SendCommandToClient(request)
                    return response.success

    2. Register your streaming service:
        from django_cfg.apps.integrations.grpc.services.commands.registry import register_streaming_service

        def grpc_handlers(server):
            servicer = YourService()
            register_streaming_service("your_service", servicer._streaming_service)
            # ...

    3. Use the client:
        # Cross-process mode
        client = MyCommandClient(client_id="123", grpc_port=50051)
        await client.send_command(command)

        # Same-process mode
        from django_cfg.apps.integrations.grpc.services.commands.registry import get_streaming_service
        service = get_streaming_service("your_service")
        client = MyCommandClient(client_id="123", streaming_service=service)
        await client.send_command(command)

Documentation:
    See @commands/ directory for complete documentation:
    - README.md: Overview and quick start
    - ARCHITECTURE.md: System design
    - EXAMPLES.md: Code examples
    - INDEX.md: Navigation hub

Version: 1.0.0
"""

from .base import (
    StreamingCommandClient,
    CommandClientConfig,
    CommandError,
    CommandTimeoutError,
    ClientNotConnectedError,
    TCommand,
)
from .registry import (
    register_streaming_service,
    get_streaming_service,
    unregister_streaming_service,
    list_streaming_services,
    is_registered,
    clear_registry,
    set_streaming_service,
)
from .helpers import (
    CommandBuilder,
    command,
    command_with_timestamps,
    HasStatus,
    HasConfig,
    HasTimestamps,
    HasStatusAndTimestamps,
)

__version__ = "1.0.0"

__all__ = [
    # Base classes
    'StreamingCommandClient',
    'CommandClientConfig',

    # Exceptions
    'CommandError',
    'CommandTimeoutError',
    'ClientNotConnectedError',

    # Registry functions
    'register_streaming_service',
    'get_streaming_service',
    'unregister_streaming_service',
    'list_streaming_services',
    'is_registered',
    'clear_registry',
    'set_streaming_service',

    # Helpers - reduce boilerplate (NEW!)
    'CommandBuilder',
    'command',
    'command_with_timestamps',
    'HasStatus',
    'HasConfig',
    'HasTimestamps',
    'HasStatusAndTimestamps',

    # Type variables
    'TCommand',

    # Version
    '__version__',
]
