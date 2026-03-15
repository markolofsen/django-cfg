"""
Telegram Message Queue with Rate Limiting.

Singleton priority queue for rate-limited Telegram message delivery.
"""

import itertools
import queue
import threading
import time

from ..django_logging import get_logger

logger = get_logger("django_cfg.telegram.queue")


class MessagePriority:
    """Message priority levels for Telegram queue."""

    CRITICAL = 1  # Security alerts, critical errors
    HIGH = 2      # Errors, important warnings
    NORMAL = 3    # Info, success messages
    LOW = 4       # Debug, non-urgent notifications


class TelegramMessageQueue:
    """
    Global singleton queue for all Telegram messages with rate limiting and auto-cleanup.

    Ensures we don't hit Telegram API limits:
    - 30 messages/sec to different chats
    - 1 message/sec to same chat

    We use conservative 20 msg/sec (0.05s delay) to be safe.

    Queue protection:
    - Max queue size: 1000 messages
    - Auto-cleanup: drops LOW priority messages when > 800
    - Emergency cleanup: drops NORMAL when > 900
    - Critical always kept
    """

    _instance = None
    _lock = threading.Lock()

    # Queue size limits
    MAX_QUEUE_SIZE = 1000
    WARNING_THRESHOLD = 800  # Start dropping LOW priority
    CRITICAL_THRESHOLD = 900  # Start dropping NORMAL priority

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._initialized = True
        self._queue = queue.PriorityQueue()  # Priority queue for message ordering
        self._counter = itertools.count()  # Tie-breaker for same-priority items
        self._worker = threading.Thread(
            target=self._process_queue,
            daemon=True,
            name="TelegramQueueWorker",
        )
        self._dropped_count = 0  # Track dropped messages
        self._last_cleanup_warning = 0  # Timestamp of last warning
        self._worker.start()
        logger.info(
            f"Telegram priority queue started: "
            f"rate_limit=20msg/sec, max_size={self.MAX_QUEUE_SIZE}, "
            f"auto_cleanup_at={self.WARNING_THRESHOLD}"
        )

    def _process_queue(self):
        """Worker thread that processes queued messages with rate limiting."""
        while True:
            try:
                # PriorityQueue returns (priority, count, item)
                priority, _count, (func, args, kwargs) = self._queue.get(timeout=1)

                try:
                    func(*args, **kwargs)
                    logger.debug(f"Processed telegram message with priority {priority}")
                except Exception as e:
                    logger.error(f"Telegram queue processing error: {e}")
                finally:
                    self._queue.task_done()
                    # Rate limit: 20 messages per second (0.05s delay)
                    time.sleep(0.05)

            except queue.Empty:
                # No messages, continue waiting
                continue
            except Exception as e:
                logger.error(f"Telegram queue worker error: {e}")
                time.sleep(1)  # Back off on errors

    def enqueue(self, func, priority=MessagePriority.NORMAL, *args, **kwargs):
        """
        Add a message to the queue with priority and smart cleanup.

        Args:
            func: Function to execute
            priority: Message priority (1=CRITICAL, 2=HIGH, 3=NORMAL, 4=LOW)
            *args: Positional arguments for func
            **kwargs: Keyword arguments for func
        """
        current_size = self._queue.qsize()

        # Check if we need to drop this message
        if current_size >= self.MAX_QUEUE_SIZE:
            # Queue is full - drop everything except CRITICAL
            if priority > MessagePriority.CRITICAL:
                self._dropped_count += 1
                logger.warning(
                    f"Queue FULL ({current_size}/{self.MAX_QUEUE_SIZE}): "
                    f"Dropped priority={priority} message. Total dropped: {self._dropped_count}"
                )
                return
            else:
                logger.critical(
                    f"Queue FULL but CRITICAL message queued anyway: "
                    f"{current_size}/{self.MAX_QUEUE_SIZE}"
                )

        elif current_size >= self.CRITICAL_THRESHOLD:
            # Emergency mode: drop NORMAL and LOW
            if priority >= MessagePriority.NORMAL:
                self._dropped_count += 1
                if time.time() - self._last_cleanup_warning > 60:  # Warn once per minute
                    logger.warning(
                        f"Queue CRITICAL ({current_size}/{self.MAX_QUEUE_SIZE}): "
                        f"Dropping NORMAL/LOW priority messages. Dropped: {self._dropped_count}"
                    )
                    self._last_cleanup_warning = time.time()
                return

        elif current_size >= self.WARNING_THRESHOLD:
            # Warning mode: drop only LOW priority
            if priority == MessagePriority.LOW:
                self._dropped_count += 1
                if time.time() - self._last_cleanup_warning > 60:  # Warn once per minute
                    logger.warning(
                        f"Queue WARNING ({current_size}/{self.MAX_QUEUE_SIZE}): "
                        f"Dropping LOW priority messages. Dropped: {self._dropped_count}"
                    )
                    self._last_cleanup_warning = time.time()
                return

        # Queue the message with counter for tie-breaking (avoids comparing functions)
        count = next(self._counter)
        self._queue.put((priority, count, (func, args, kwargs)))
        logger.debug(
            f"Telegram message queued with priority {priority} "
            f"(size: {current_size + 1}/{self.MAX_QUEUE_SIZE})"
        )

    def size(self) -> int:
        """Get current queue size."""
        return self._queue.qsize()

    def flush(self, timeout: float = 10.0) -> bool:
        """
        Wait for all queued messages to be sent.

        Use this before exiting a short-lived script (e.g., management command)
        to ensure all messages are delivered.

        Args:
            timeout: Maximum seconds to wait

        Returns:
            True if queue was flushed, False if timeout
        """
        if self._queue.qsize() == 0:
            return True

        logger.info(f"Flushing telegram queue ({self._queue.qsize()} messages)...")

        # Wait for queue to be empty
        start = time.time()
        while self._queue.qsize() > 0:
            if time.time() - start > timeout:
                logger.warning(f"Queue flush timeout ({self._queue.qsize()} messages remaining)")
                return False
            time.sleep(0.1)

        # Extra wait for last message to be processed
        time.sleep(0.1)
        logger.info("Telegram queue flushed")
        return True

    def get_stats(self) -> dict:
        """Get queue statistics."""
        current_size = self._queue.qsize()
        return {
            "queue_size": current_size,
            "max_size": self.MAX_QUEUE_SIZE,
            "usage_percent": round((current_size / self.MAX_QUEUE_SIZE) * 100, 1),
            "dropped_total": self._dropped_count,
            "warning_threshold": self.WARNING_THRESHOLD,
            "critical_threshold": self.CRITICAL_THRESHOLD,
            "status": (
                "FULL" if current_size >= self.MAX_QUEUE_SIZE
                else "CRITICAL" if current_size >= self.CRITICAL_THRESHOLD
                else "WARNING" if current_size >= self.WARNING_THRESHOLD
                else "OK"
            ),
        }


# Global singleton instance
telegram_queue = TelegramMessageQueue()


__all__ = [
    "MessagePriority",
    "TelegramMessageQueue",
    "telegram_queue",
]
