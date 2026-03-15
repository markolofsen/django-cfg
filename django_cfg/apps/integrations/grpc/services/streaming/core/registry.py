"""
Response registry for synchronous command execution.

Manages Future objects for commands that expect responses (CommandAck).
Enables synchronous-style RPC execution over bidirectional streams.

Created: 2025-11-14
Status: %%PRODUCTION%%
Phase: Phase 1 - Universal Components (Refactored)
"""

import asyncio
import logging
from typing import Dict, Optional, Any
from google.protobuf.message import Message

# Logger will be configured by BidirectionalStreamingService via setup_streaming_logger
logger = logging.getLogger("grpc_streaming.registry")


class CommandFuture:
    """
    Wrapper around asyncio.Future for command responses.

    Stores metadata about the command and provides timeout support.
    """

    def __init__(
        self,
        command_id: str,
        timeout: float,
        loop: Optional[asyncio.AbstractEventLoop] = None
    ):
        """
        Initialize command future.

        Args:
            command_id: Unique command UUID
            timeout: Timeout in seconds
            loop: Event loop (uses current if None)
        """
        self.command_id = command_id
        self.timeout = timeout
        self.loop = loop or asyncio.get_event_loop()
        self.future: asyncio.Future = self.loop.create_future()
        self.timeout_handle: Optional[asyncio.TimerHandle] = None

    def set_result(self, result: Any) -> None:
        """
        Set future result.

        Args:
            result: Command result (usually CommandAck protobuf)
        """
        if not self.future.done():
            self.future.set_result(result)
            self._cancel_timeout()

    def set_exception(self, exc: Exception) -> None:
        """
        Set future exception.

        Args:
            exc: Exception to set
        """
        if not self.future.done():
            self.future.set_exception(exc)
            self._cancel_timeout()

    def cancel(self, reason: str = "Cancelled") -> None:
        """
        Cancel future.

        Args:
            reason: Cancellation reason
        """
        if not self.future.done():
            self.future.cancel()
            self._cancel_timeout()
            logger.debug(f"Command {self.command_id} cancelled: {reason}")

    def _cancel_timeout(self) -> None:
        """Cancel timeout handler if set."""
        if self.timeout_handle and not self.timeout_handle.cancelled():
            self.timeout_handle.cancel()

    def is_done(self) -> bool:
        """Check if future is done."""
        return self.future.done()

    async def wait(self) -> Any:
        """
        Wait for result with timeout.

        Returns:
            Command result

        Raises:
            asyncio.TimeoutError: If timeout exceeded
            asyncio.CancelledError: If cancelled
        """
        try:
            return await asyncio.wait_for(self.future, timeout=self.timeout)
        except asyncio.TimeoutError:
            logger.warning(
                f"⏱️  Command {self.command_id} timeout after {self.timeout}s"
            )
            raise


class ResponseRegistry:
    """
    Registry for command responses.

    Maps command_id -> Future for synchronous command execution.
    Used by ExecuteCommandSync RPC to wait for CommandAck responses.

    **How it works**:
    1. ExecuteCommandSync registers Future with command_id
    2. Sends command to bot via streaming connection
    3. Bot processes command and sends CommandAck back
    4. handle_command_ack resolves Future with CommandAck
    5. ExecuteCommandSync returns CommandAck as RPC response

    Thread-safe for asyncio single event loop.
    """

    def __init__(self):
        """Initialize empty registry."""
        self._futures: Dict[str, CommandFuture] = {}

    async def register_command(
        self,
        command_id: str,
        timeout: float = 30.0
    ) -> asyncio.Future:
        """
        Register command and create Future.

        Args:
            command_id: Unique command UUID
            timeout: Timeout in seconds (default: 30s)

        Returns:
            Future that will be resolved when CommandAck arrives

        Raises:
            ValueError: If command_id already registered
        """
        if command_id in self._futures:
            logger.warning(
                f"⚠️  Command {command_id} already registered, replacing"
            )
            # Cancel old future
            self._futures[command_id].cancel("Replaced by new command")

        cmd_future = CommandFuture(command_id, timeout)
        self._futures[command_id] = cmd_future

        logger.debug(
            f"📝 Registered command {command_id} "
            f"(timeout={timeout}s, registry_size={len(self._futures)})"
        )

        return cmd_future.future

    async def resolve_command(
        self,
        command_id: str,
        result: Message
    ) -> bool:
        """
        Resolve command with result.

        Called when CommandAck arrives from client.

        Args:
            command_id: Command UUID
            result: CommandAck protobuf message

        Returns:
            True if command was registered and resolved
        """
        cmd_future = self._futures.pop(command_id, None)

        if cmd_future is None:
            logger.warning(
                f"⚠️  Received CommandAck for unknown command: {command_id}"
            )
            return False

        if cmd_future.is_done():
            logger.warning(
                f"⚠️  Command {command_id} future already done"
            )
            return False

        cmd_future.set_result(result)

        logger.info(
            f"✅ Resolved command {command_id} "
            f"(registry_size={len(self._futures)})"
        )

        return True

    async def cancel_command(
        self,
        command_id: str,
        reason: str = "Cancelled"
    ) -> bool:
        """
        Cancel command.

        Args:
            command_id: Command UUID
            reason: Cancellation reason

        Returns:
            True if command was found and cancelled
        """
        cmd_future = self._futures.pop(command_id, None)

        if cmd_future is None:
            logger.debug(f"Command {command_id} not in registry (already resolved or never registered)")
            return False

        cmd_future.cancel(reason)

        logger.debug(
            f"🚫 Cancelled command {command_id}: {reason} "
            f"(registry_size={len(self._futures)})"
        )

        return True

    def is_registered(self, command_id: str) -> bool:
        """
        Check if command is registered.

        Args:
            command_id: Command UUID

        Returns:
            True if command is waiting for response
        """
        return command_id in self._futures

    def count(self) -> int:
        """
        Get count of pending commands.

        Returns:
            Number of commands waiting for responses
        """
        return len(self._futures)

    def get_pending_commands(self) -> list:
        """
        Get list of pending command IDs.

        Returns:
            List of command UUIDs waiting for responses
        """
        return list(self._futures.keys())

    def cleanup_all(self, reason: str = "Cleanup") -> int:
        """
        Cancel all pending commands.

        Useful on shutdown or connection loss.

        Args:
            reason: Cancellation reason

        Returns:
            Number of commands cancelled
        """
        count = len(self._futures)

        for cmd_future in self._futures.values():
            cmd_future.cancel(reason)

        self._futures.clear()

        if count > 0:
            logger.info(f"🧹 Cleaned up {count} pending commands: {reason}")

        return count


# ============================================================================
# Exports
# ============================================================================

__all__ = [
    'CommandFuture',
    'ResponseRegistry',
]
