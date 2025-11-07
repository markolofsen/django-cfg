"""
Example: Wrapper Client Class

This demonstrates Pattern 3: wrapping command functions in a convenient client class.

The wrapper pattern provides:
- Clean API: client.start() instead of start_client(client, ...)
- Encapsulation: Commands bundled with client state
- Convenience: Methods can access self.model, self.client_id automatically

Usage:
    from your_app.grpc.commands.client import CommandClient

    # Create client
    client = CommandClient(client_id="123", model=instance, grpc_port=50051)

    # Use convenient methods
    await client.start(reason="User request")
    await client.update_config()
    await client.stop(graceful=True)
"""

import logging
from typing import Optional, List, Any

from django_cfg.apps.integrations.grpc.services.commands.examples.base_client import (
    ExampleCommandClient,
)

# Import command functions
from . import start, stop, config

logger = logging.getLogger(__name__)


class CommandClient(ExampleCommandClient):
    """
    Wrapper client class that provides convenient methods for all commands.

    This wraps the command functions (start.py, stop.py, config.py) into
    class methods for a cleaner API.

    Example:
        # Cross-process mode (from REST API, signals, tasks)
        from your_app.grpc.commands.client import CommandClient

        client = CommandClient(
            client_id="bot-123",
            model=bot_instance,
            grpc_port=50051
        )
        await client.start(reason="API request")

        # Same-process mode (from management commands)
        from your_app.grpc.services.commands.registry import get_streaming_service

        service = get_streaming_service("bots")
        client = CommandClient(
            client_id="bot-123",
            model=bot_instance,
            streaming_service=service
        )
        await client.start()  # Much faster (same-process)
    """

    async def start(self, reason: Optional[str] = None) -> bool:
        """
        Start the client.

        Args:
            reason: Optional reason for starting

        Returns:
            True if command sent successfully

        Example:
            success = await client.start(reason="User requested start")
        """
        if not self.model:
            logger.error(f"Cannot start {self.client_id}: model not provided")
            return False

        return await start.start_client(
            client=self,
            model=self.model,
            reason=reason
        )

    async def stop(
        self,
        reason: Optional[str] = None,
        graceful: bool = True
    ) -> bool:
        """
        Stop the client.

        Args:
            reason: Optional reason for stopping
            graceful: If True, allow client to finish current work

        Returns:
            True if command sent successfully

        Example:
            # Graceful stop
            success = await client.stop(reason="Maintenance", graceful=True)

            # Force stop
            success = await client.stop(reason="Emergency", graceful=False)
        """
        if not self.model:
            logger.error(f"Cannot stop {self.client_id}: model not provided")
            return False

        return await stop.stop_client(
            client=self,
            model=self.model,
            reason=reason,
            graceful=graceful
        )

    async def update_config(self, fields: Optional[List[str]] = None) -> bool:
        """
        Push config update to client.

        Args:
            fields: If specified, only update these fields (partial update)

        Returns:
            True if command sent successfully

        Example:
            # Full config update
            success = await client.update_config()

            # Partial update
            success = await client.update_config(fields=['timeout', 'max_retries'])
        """
        if not self.model:
            logger.error(f"Cannot update config for {self.client_id}: model not provided")
            return False

        return await config.update_config(
            client=self,
            model=self.model,
            fields=fields
        )

    async def restart(
        self,
        reason: Optional[str] = None,
        graceful: bool = True
    ) -> bool:
        """
        Restart the client (stop then start).

        Args:
            reason: Optional reason for restart
            graceful: If True, allow graceful stop

        Returns:
            True if both stop and start succeeded

        Example:
            success = await client.restart(reason="Config changed")
        """
        # Stop
        stop_success = await self.stop(
            reason=reason or "Restart",
            graceful=graceful
        )

        if not stop_success:
            logger.warning(f"Restart of {self.client_id} failed at stop phase")
            return False

        # Wait a moment for client to stop
        import asyncio
        await asyncio.sleep(1)

        # Start
        start_success = await self.start(
            reason=reason or "Restart"
        )

        if start_success:
            logger.info(f"✅ Restart of {self.client_id} complete")
        else:
            logger.error(f"❌ Restart of {self.client_id} failed at start phase")

        return start_success


# ============================================================================
# Batch Operations
# ============================================================================

async def batch_start(
    clients: List[CommandClient],
    reason: Optional[str] = None
) -> dict:
    """
    Start multiple clients in parallel.

    Args:
        clients: List of CommandClient instances
        reason: Optional reason for starting

    Returns:
        Dict with 'success': count, 'failed': count

    Example:
        from your_app.grpc.services.commands.registry import get_streaming_service

        service = get_streaming_service("bots")
        client_ids = ["bot-1", "bot-2", "bot-3"]

        clients = [
            CommandClient(client_id=cid, model=await Bot.objects.aget(id=cid), streaming_service=service)
            for cid in client_ids
        ]

        results = await batch_start(clients, reason="Batch start")
        print(f"Started {results['success']}/{len(clients)} clients")
    """
    import asyncio

    tasks = [client.start(reason=reason) for client in clients]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    success_count = sum(1 for r in results if r is True)
    failed_count = len(results) - success_count

    logger.info(f"Batch start: {success_count} succeeded, {failed_count} failed")

    return {'success': success_count, 'failed': failed_count}


async def batch_stop(
    clients: List[CommandClient],
    reason: Optional[str] = None,
    graceful: bool = True
) -> dict:
    """
    Stop multiple clients in parallel.

    Args:
        clients: List of CommandClient instances
        reason: Optional reason for stopping
        graceful: If True, allow graceful shutdown

    Returns:
        Dict with 'success': count, 'failed': count
    """
    import asyncio

    tasks = [client.stop(reason=reason, graceful=graceful) for client in clients]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    success_count = sum(1 for r in results if r is True)
    failed_count = len(results) - success_count

    logger.info(f"Batch stop: {success_count} succeeded, {failed_count} failed")

    return {'success': success_count, 'failed': failed_count}


__all__ = [
    'CommandClient',
    'batch_start',
    'batch_stop',
]
