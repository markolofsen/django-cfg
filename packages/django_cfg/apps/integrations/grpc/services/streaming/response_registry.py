"""
Command Response Registry for synchronous command execution.

Provides a registry to track pending commands and resolve them when
CommandAck responses arrive from bots.

Architecture:
    1. API sends command → register Future with command_id
    2. Bot processes → sends CommandAck back through stream
    3. handle_command_ack → resolves Future with CommandAck data
    4. API receives response → returns to user

Usage:
    # In command sender (API)
    from .response_registry import response_registry

    future = response_registry.register_command(command_id, timeout=5.0)
    await send_command_to_bot(command)
    ack = await asyncio.wait_for(future, timeout=5.0)

    # In command_ack handler
    response_registry.resolve_command(command_ack.command_id, command_ack)
"""
import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta


logger = logging.getLogger(__name__)


class CommandResponseRegistry:
    """
    Registry for tracking pending commands and their responses.

    Thread-safe registry that stores futures for commands awaiting responses.
    When CommandAck arrives, the future is resolved with the response data.
    """

    def __init__(self):
        """Initialize empty registry."""
        self._pending: Dict[str, dict] = {}  # {command_id: {'future': Future, 'ready': bool}}
        self._timeouts: Dict[str, datetime] = {}
        self._lock = asyncio.Lock()

    async def register_command(
        self,
        command_id: str,
        timeout: float = 5.0
    ) -> asyncio.Future:
        """
        Register a command and create Future for awaiting response.

        Args:
            command_id: Unique command identifier
            timeout: Timeout in seconds (for tracking only, actual timeout in caller)

        Returns:
            asyncio.Future that will be resolved with CommandAck

        Raises:
            ValueError: If command_id already registered
        """
        async with self._lock:
            if command_id in self._pending:
                logger.warning(f"Command {command_id} already registered, overwriting")

            future = asyncio.get_event_loop().create_future()

            # SIMPLIFIED APPROACH 1 from ARCHITECTURE_ANALYSIS.md:
            # Set ready=True immediately - no two-phase registration needed.
            # The client timeout fix prevents RPC cancellation, so this is safe.
            self._pending[command_id] = {
                'future': future,
                'ready': True,  # Always ready immediately (Approach 1: Atomic Single-Phase)
                'pending_data': None  # Not used when ready=True
            }
            self._timeouts[command_id] = datetime.now() + timedelta(seconds=timeout)

            logger.info(f"📝 Registered command {command_id} in registry {id(self)} (timeout: {timeout}s)")

        # Mark as ready OUTSIDE the lock, after returning from this function
        # The caller will mark it as ready after they start waiting
        return future

    async def resolve_command(
        self,
        command_id: str,
        response_data: Any
    ) -> bool:
        """
        Resolve pending command with response data.

        Args:
            command_id: Command identifier
            response_data: CommandAck protobuf or dict with response

        Returns:
            True if command was found and resolved, False if not found
        """
        async with self._lock:
            print(f"🔥 resolve_command: Acquired lock for {command_id}")
            print(f"🔥 resolve_command: Pending commands = {list(self._pending.keys())}")

            if command_id not in self._pending:
                print(f"⚠️  Command {command_id} not found in registry {id(self)} (already resolved or timeout)")
                print(f"⚠️  Available commands: {list(self._pending.keys())}")
                logger.warning(f"⚠️  Command {command_id} not found in registry {id(self)} (already resolved or timeout)")
                return False

            entry = self._pending[command_id]
            future = entry['future']
            ready = entry['ready']

            print(f"🔥 resolve_command: Found entry, ready={ready}")

            # If not ready yet, store the data for later
            if not ready:
                print(f"📨 Command {command_id} arrived early, storing data for later")
                logger.info(f"📨 Command {command_id} arrived early, storing data for later")
                entry['pending_data'] = response_data
                return True  # Return True - we'll process it when ready

            # Don't check future.done() or future.cancelled() here!
            # These checks create race conditions because Future state can change
            # between the check and set_result() call.
            # Instead, let set_result() handle it with InvalidStateError.

            # Resolve future with response
            try:
                print(f"🔥 About to call future.set_result() for command {command_id}")
                future.set_result(response_data)
                print(f"🔥 future.set_result() completed successfully for command {command_id}")
            except asyncio.InvalidStateError as e:
                # Future was already resolved/cancelled before we could set result
                # This is normal if:
                # - Multiple CommandAck arrive (bot sends twice)
                # - Future was cancelled by timeout
                # - Future was resolved by another handler
                logger.warning(f"⚠️  Command {command_id} InvalidStateError: {e} (Future already done)")
                del self._pending[command_id]
                if command_id in self._timeouts:
                    del self._timeouts[command_id]
                return False

            # Cleanup
            print(f"🔥 resolve_command: DELETING command {command_id} from registry after set_result()")
            del self._pending[command_id]
            del self._timeouts[command_id]
            print(f"🔥 resolve_command: Successfully deleted command {command_id}")

            logger.debug(f"✅ Resolved command {command_id}")
            return True

    async def mark_ready(self, command_id: str) -> bool:
        """
        Mark command as ready to receive responses.

        This should be called AFTER the caller starts waiting on the Future.
        If response data arrived early (before ready), it will be processed now.

        Args:
            command_id: Command identifier

        Returns:
            True if marked ready successfully
        """
        # NO LOCK! Dict operations are atomic in Python, and we only set a flag
        # Lock would cause DEADLOCK when bot responds instantly
        print(f"🔥 mark_ready: checking command {command_id} in registry {id(self)}")
        print(f"🔥 mark_ready: pending commands = {list(self._pending.keys())}")

        if command_id not in self._pending:
            print(f"⚠️  mark_ready: Command {command_id} NOT FOUND in registry!")
            logger.warning(f"⚠️  Cannot mark ready: Command {command_id} not in registry")
            return False

        print(f"🔥 mark_ready: Found command {command_id}")
        entry = self._pending[command_id]
        entry['ready'] = True
        print(f"🔥 mark_ready: Set ready=True for command {command_id}")

        # Check if data arrived early while we were not ready
        pending_data = entry['pending_data']
        print(f"🔥 mark_ready: pending_data = {pending_data is not None}")

        if pending_data is not None:
            print(f"📦 mark_ready: Processing early-arrived data for command {command_id}")
            logger.info(f"📦 Processing early-arrived data for command {command_id}")
            future = entry['future']

            try:
                future.set_result(pending_data)
                # Cleanup
                del self._pending[command_id]
                del self._timeouts[command_id]
                print(f"✅ mark_ready: Deleted command {command_id} from registry (early data)")
                logger.debug(f"✅ Resolved command {command_id} with early data")
            except asyncio.InvalidStateError as e:
                logger.warning(f"⚠️  Command {command_id} InvalidStateError on early data: {e}")
                del self._pending[command_id]
                del self._timeouts[command_id]

        print(f"🔥 mark_ready: Returning True for command {command_id}")
        return True

    async def cancel_command(self, command_id: str, reason: str = "Cancelled") -> bool:
        """
        Cancel pending command.

        Args:
            command_id: Command identifier
            reason: Cancellation reason

        Returns:
            True if command was found and cancelled
        """
        async with self._lock:
            if command_id not in self._pending:
                return False

            entry = self._pending[command_id]
            future = entry['future']

            if not future.done():
                future.cancel()

            del self._pending[command_id]
            del self._timeouts[command_id]

            logger.debug(f"❌ Cancelled command {command_id}: {reason}")
            return True

    def get_pending_count(self) -> int:
        """Get number of pending commands."""
        return len(self._pending)

    def get_pending_commands(self) -> list[str]:
        """Get list of pending command IDs."""
        return list(self._pending.keys())

    async def cleanup_expired(self) -> int:
        """
        Cleanup expired commands (timeout exceeded).

        Returns:
            Number of commands cleaned up
        """
        now = datetime.now()
        expired = []

        async with self._lock:
            for command_id, timeout_at in self._timeouts.items():
                if now > timeout_at:
                    expired.append(command_id)

            for command_id in expired:
                entry = self._pending.get(command_id)
                if entry:
                    future = entry['future']
                    if not future.done():
                        future.cancel()

                del self._pending[command_id]
                del self._timeouts[command_id]

        if expired:
            logger.warning(f"🧹 Cleaned up {len(expired)} expired commands: {expired}")

        return len(expired)


# Global singleton instance
response_registry = CommandResponseRegistry()


__all__ = ['response_registry', 'CommandResponseRegistry']
