"""
Queue management for bidirectional streaming.

Simple utilities for creating and managing asyncio queues.

Created: 2025-11-14
Status: %%PRODUCTION%%
Phase: Phase 1 - Universal Components (Refactored)
"""

import asyncio
import logging
from typing import TypeVar, Generic

# Logger will be configured by BidirectionalStreamingService via setup_streaming_logger
T = TypeVar('T')
logger = logging.getLogger("grpc_streaming.queue")


class QueueManager(Generic[T]):
    """
    Manager for asyncio queues.

    Provides utilities for queue creation and timeout-based operations.
    """

    @staticmethod
    def create_queue(maxsize: int = 0) -> asyncio.Queue[T]:
        """
        Create new asyncio queue.

        Args:
            maxsize: Maximum queue size (0 = unlimited)

        Returns:
            New asyncio.Queue instance
        """
        return asyncio.Queue(maxsize=maxsize)

    @staticmethod
    async def put_with_timeout(
        queue: asyncio.Queue[T],
        item: T,
        timeout: float = None
    ) -> bool:
        """
        Put item into queue with optional timeout.

        Args:
            queue: Target queue
            item: Item to enqueue
            timeout: Timeout in seconds (None = no timeout)

        Returns:
            True if successful, False if timeout

        Raises:
            asyncio.TimeoutError: If timeout exceeded
        """
        try:
            if timeout:
                await asyncio.wait_for(queue.put(item), timeout=timeout)
            else:
                await queue.put(item)
            return True
        except asyncio.TimeoutError:
            logger.warning(f"⏱️  Queue.put() timeout after {timeout}s")
            raise

    @staticmethod
    async def get_with_timeout(
        queue: asyncio.Queue[T],
        timeout: float = None
    ) -> T:
        """
        Get item from queue with optional timeout.

        Args:
            queue: Source queue
            timeout: Timeout in seconds (None = no timeout)

        Returns:
            Item from queue

        Raises:
            asyncio.TimeoutError: If timeout exceeded
        """
        try:
            if timeout:
                return await asyncio.wait_for(queue.get(), timeout=timeout)
            else:
                return await queue.get()
        except asyncio.TimeoutError:
            logger.warning(f"⏱️  Queue.get() timeout after {timeout}s")
            raise


# ============================================================================
# Exports
# ============================================================================

__all__ = [
    'QueueManager',
]
