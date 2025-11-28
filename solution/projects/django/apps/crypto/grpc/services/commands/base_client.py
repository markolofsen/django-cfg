"""Crypto Client Streaming Command Client - thin adapter for crypto clients."""

import logging

from django_cfg.apps.integrations.grpc.services.commands.base import (
    StreamingCommandClient,
    CommandError,
    CommandTimeoutError,
    ClientNotConnectedError,
)
from ..generated import crypto_streaming_pb2 as pb2
from ..generated import crypto_streaming_pb2_grpc as pb2_grpc


logger = logging.getLogger(__name__)


class CryptoStreamingCommandClient(StreamingCommandClient[pb2.DjangoCommand]):
    """
    Crypto client-specific command client - declares gRPC service details.

    Ultra-minimal adapter: only declares class attributes for gRPC service.
    All logic (channel creation, stub, request, error handling) in base class.

    Class Attributes:
        stub_class: CryptoStreamingServiceStub
        request_class: SendCommandRequest
        rpc_method_name: "SendCommandToClient" (for async fire-and-forget)
        client_id_field: "client_id"
    """

    # gRPC service configuration (used by base class for async commands)
    stub_class = pb2_grpc.CryptoStreamingServiceStub
    request_class = pb2.SendCommandRequest
    rpc_method_name = "SendCommandToClient"
    client_id_field = "client_id"

    # Cross-process sync RPC configuration
    _sync_rpc_method_name = "ExecuteCommandSync"

    def __init__(self, client_id: str, model=None, **kwargs):
        super().__init__(client_id=client_id, **kwargs)
        self.client = self.model = model
        self.client_id = self.client_id  # Alias for consistency

    async def send_command_and_wait(
        self,
        command: pb2.DjangoCommand,
        timeout: float = 5.0
    ) -> pb2.CommandAck:
        """
        Send command and wait for CommandAck response synchronously.

        Auto-detects mode:
        - Same-process: Uses response_registry with Future
        - Cross-process: Uses ExecuteCommandSync RPC

        Args:
            command: DjangoCommand protobuf to send
            timeout: Timeout in seconds to wait for response (default: 5.0)

        Returns:
            CommandAck protobuf with execution result

        Raises:
            ClientNotConnectedError: If client is not connected
            CommandTimeoutError: If response not received within timeout
            CommandError: If command sending failed

        Example:
            >>> from django_cfg.apps.integrations.grpc.services.commands.helpers import CommandBuilder
            >>> from ..proto.converters import ProtobufConverter
            >>>
            >>> client = CryptoStreamingCommandClient(client_id, client_model)
            >>> command = CommandBuilder.create(pb2.DjangoCommand, ProtobufConverter)
            >>> command.pause.CopyFrom(pb2.PauseClientCommand(reason="Testing"))
            >>>
            >>> ack = await client.send_command_and_wait(command, timeout=10.0)
            >>> print(f"Success: {ack.success}, Message: {ack.message}")
        """
        # Check if cross-process mode (no streaming_service available)
        logger.debug(f"send_command_and_wait called: client={self.client_id[:8]}..., timeout={timeout}")

        if not self._is_same_process:
            # Cross-process mode: Use ExecuteCommandSync RPC
            logger.debug("Using cross-process mode (ExecuteCommandSync RPC)")
            return await self._execute_command_sync_via_grpc(command, timeout)

        # Same-process mode: Delegate to base class (uses response_registry)
        logger.debug("Using same-process mode (response_registry)")
        return await super().send_command_and_wait(
            command=command,
            timeout=timeout,
            command_id_field="command_id"
        )

    async def _execute_command_sync_via_grpc(
        self,
        command: pb2.DjangoCommand,
        timeout: float
    ) -> pb2.CommandAck:
        """
        Execute command synchronously via gRPC RPC (cross-process mode).

        Calls ExecuteCommandSync RPC which:
        1. Registers Future in gRPC server's response_registry
        2. Sends command to client via streaming
        3. Waits for CommandAck
        4. Returns CommandAck as RPC response

        Args:
            command: Command to execute
            timeout: Timeout in seconds

        Returns:
            CommandAck from client

        Raises:
            ClientNotConnectedError: If client not connected
            CommandTimeoutError: If timeout exceeded
            CommandError: If RPC failed
        """
        import grpc

        grpc_address = self.get_grpc_address()

        logger.debug(
            f"Cross-process ExecuteCommandSync: client={self.client_id[:8]}..., "
            f"command_id={command.command_id}, grpc_address={grpc_address}"
        )

        try:
            # Create gRPC channel
            async with grpc.aio.insecure_channel(
                grpc_address,
                options=[
                    ('grpc.keepalive_time_ms', 10000),
                    ('grpc.keepalive_timeout_ms', 5000),
                    ('grpc.max_receive_message_length', 100 * 1024 * 1024),
                ]
            ) as channel:
                # Create stub
                stub = self.stub_class(channel)

                # Build request
                request = self.request_class(
                    client_id=self.client_id,
                    command=command
                )

                # Call ExecuteCommandSync RPC
                # CRITICAL FIX: Client timeout must be > server timeout (15s)
                # to prevent premature RPC cancellation
                client_timeout = max(timeout * 3, 20.0)  # At least 20s
                ack = await stub.ExecuteCommandSync(request, timeout=client_timeout)

                # Check if command succeeded
                if not ack.success:
                    error = ack.error if ack.error else "Unknown error"

                    if error == "CLIENT_NOT_CONNECTED":
                        raise ClientNotConnectedError(
                            f"Client {self.client_id} not connected"
                        )
                    elif error == "COMMAND_TIMEOUT":
                        raise CommandTimeoutError(
                            f"Command {command.command_id} timeout after {timeout}s"
                        )
                    else:
                        raise CommandError(
                            f"Command failed: {ack.message} (error={error})"
                        )

                logger.info(
                    f"Cross-process ExecuteCommandSync succeeded: {ack.message}"
                )
                return ack

        except (ClientNotConnectedError, CommandTimeoutError, CommandError):
            # Re-raise expected exceptions
            raise

        except grpc.RpcError as e:
            logger.error(
                f"gRPC error in ExecuteCommandSync: {e.code()} - {e.details()}",
                exc_info=True
            )
            raise CommandError(f"gRPC error: {e.details()}") from e

        except Exception as e:
            logger.error(
                f"Unexpected error in ExecuteCommandSync: {e}",
                exc_info=True
            )
            raise CommandError(f"Failed to execute command: {e}") from e


__all__ = ['CryptoStreamingCommandClient']
