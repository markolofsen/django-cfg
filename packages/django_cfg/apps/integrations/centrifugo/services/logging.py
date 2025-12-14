"""
Centrifugo Logging helper for tracking publish operations.

Provides async-safe logging of Centrifugo publishes to database.
Mirrors RPCLogger patterns from legacy WebSocket solution for easy migration.
"""

import time
from typing import Any, Optional

from django.utils import timezone
from django_cfg.utils import get_logger

logger = get_logger("centrifugo")


class CentrifugoLogger:
    """
    Helper class for logging Centrifugo publish operations to database.

    Mirrors RPCLogger interface for migration compatibility.

    Usage:
        >>> log_entry = CentrifugoLogger.create_log(
        ...     message_id="abc123",
        ...     channel="user#456",
        ...     data={"title": "Hello", "message": "World"},
        ...     wait_for_ack=True,
        ...     user=request.user if authenticated else None
        ... )
        >>> # ... publish message ...
        >>> CentrifugoLogger.mark_success(log_entry, acks_received=1, duration_ms=125)
    """

    @staticmethod
    def is_logging_enabled() -> bool:
        """
        Check if Centrifugo logging is enabled in django-cfg config.

        Returns:
            bool: True if logging is enabled
        """
        from .config_helper import get_centrifugo_config

        config = get_centrifugo_config()

        if not config:
            return False

        # If log_only_with_ack is True, only log ACK calls
        if config.log_only_with_ack:
            return True  # Will check wait_for_ack in create_log

        return config.log_all_calls

    @staticmethod
    async def create_log_async(
        message_id: str,
        channel: str,
        data: dict,
        wait_for_ack: bool = False,
        ack_timeout: int | None = None,
        acks_expected: int | None = None,
        is_notification: bool = True,
        user: Any = None,
        caller_ip: str | None = None,
        user_agent: str | None = None,
    ) -> Any | None:
        """
        Async version of create_log for use in async contexts.
        """
        logging_enabled = CentrifugoLogger.is_logging_enabled()
        logger.info(f"🔍 create_log_async called: message_id={message_id}, channel={channel}, logging_enabled={logging_enabled}")

        if not logging_enabled:
            logger.warning(f"❌ Logging disabled, skipping log creation for {message_id}")
            return None

        # If log_only_with_ack is enabled, skip non-ACK publishes
        from .config_helper import get_centrifugo_config

        config = get_centrifugo_config()
        logger.info(f"🔍 Config check: log_only_with_ack={config.log_only_with_ack if config else None}, wait_for_ack={wait_for_ack}")

        if config and config.log_only_with_ack and not wait_for_ack:
            logger.info(f"⏭️ Skipping non-ACK publish for {message_id}")
            return None

        logger.info(f"✅ Creating CentrifugoLog entry for {message_id} (async)")
        try:
            from ..models import CentrifugoLog

            # ✅ Use Django 5.2+ async ORM instead of sync_to_async
            # This prevents connection leaks from sync_to_async threads
            log_entry = await CentrifugoLog.objects.acreate(
                message_id=message_id,
                channel=channel,
                data=data,
                wait_for_ack=wait_for_ack,
                ack_timeout=ack_timeout,
                acks_expected=acks_expected,
                is_notification=is_notification,
                user=user,
                caller_ip=caller_ip,
                user_agent=user_agent,
                status=CentrifugoLog.StatusChoices.PENDING,
            )

            logger.debug(
                f"Created Centrifugo log entry: {message_id} on channel {channel}",
                extra={
                    "message_id": message_id,
                    "channel": channel,
                    "wait_for_ack": wait_for_ack,
                },
            )

            # Notify dashboard about new publish
            try:
                from .dashboard_notifier import DashboardNotifier
                await DashboardNotifier.notify_new_publish(log_entry)
            except Exception as e:
                logger.debug(f"Dashboard notification failed: {e}")

            return log_entry

        except Exception as e:
            logger.error(
                f"Failed to create Centrifugo log entry: {e}",
                extra={"message_id": message_id, "error": str(e)},
            )
            return None

    @staticmethod
    def create_log(
        message_id: str,
        channel: str,
        data: dict,
        wait_for_ack: bool = False,
        ack_timeout: int | None = None,
        acks_expected: int | None = None,
        is_notification: bool = True,
        user: Any = None,
        caller_ip: str | None = None,
        user_agent: str | None = None,
    ) -> Any | None:
        """
        Create log entry for Centrifugo publish operation.

        Args:
            message_id: Unique message identifier
            channel: Centrifugo channel
            data: Published data
            wait_for_ack: Whether this publish waits for ACK
            ack_timeout: ACK timeout in seconds
            acks_expected: Expected number of ACKs
            is_notification: Whether this is a notification
            user: Django User instance
            caller_ip: IP address of caller
            user_agent: User agent of caller

        Returns:
            CentrifugoLog instance or None if logging disabled
        """
        logging_enabled = CentrifugoLogger.is_logging_enabled()
        logger.info(f"🔍 create_log called: message_id={message_id}, channel={channel}, logging_enabled={logging_enabled}")

        if not logging_enabled:
            logger.warning(f"❌ Logging disabled, skipping log creation for {message_id}")
            return None

        # If log_only_with_ack is enabled, skip non-ACK publishes
        from .config_helper import get_centrifugo_config

        config = get_centrifugo_config()
        logger.info(f"🔍 Config check: log_only_with_ack={config.log_only_with_ack if config else None}, wait_for_ack={wait_for_ack}")

        if config and config.log_only_with_ack and not wait_for_ack:
            logger.info(f"⏭️ Skipping non-ACK publish for {message_id}")
            return None

        logger.info(f"✅ Creating CentrifugoLog entry for {message_id} (sync)")
        try:
            from ..models import CentrifugoLog

            # Direct synchronous call - will fail if called from async context
            # Use create_log_async() for async contexts instead
            log_entry = CentrifugoLog.objects.create(
                message_id=message_id,
                channel=channel,
                data=data,
                wait_for_ack=wait_for_ack,
                ack_timeout=ack_timeout,
                acks_expected=acks_expected,
                is_notification=is_notification,
                user=user,
                caller_ip=caller_ip,
                user_agent=user_agent,
                status=CentrifugoLog.StatusChoices.PENDING,
            )

            logger.debug(
                f"Created Centrifugo log entry: {message_id} on channel {channel}",
                extra={
                    "message_id": message_id,
                    "channel": channel,
                    "wait_for_ack": wait_for_ack,
                },
            )

            return log_entry

        except Exception as e:
            logger.error(
                f"Failed to create Centrifugo log entry: {e}",
                extra={"message_id": message_id, "error": str(e)},
            )
            return None

    @staticmethod
    async def mark_success_async(
        log_entry: Any,
        acks_received: int = 0,
        duration_ms: int | None = None,
    ) -> None:
        """
        Mark publish operation as successful (async version).

        Args:
            log_entry: CentrifugoLog instance
            acks_received: Number of ACKs received
            duration_ms: Duration in milliseconds
        """
        if log_entry is None:
            return

        try:
            from ..models import CentrifugoLog

            # ✅ Use Django 5.2+ async ORM instead of sync_to_async
            log_entry.status = CentrifugoLog.StatusChoices.SUCCESS
            log_entry.acks_received = acks_received
            log_entry.completed_at = timezone.now()

            if duration_ms is not None:
                log_entry.duration_ms = duration_ms

            await log_entry.asave(update_fields=["status", "acks_received", "completed_at", "duration_ms"])

            logger.info(
                f"Centrifugo publish successful: {log_entry.message_id}",
                extra={
                    "message_id": log_entry.message_id,
                    "channel": log_entry.channel,
                    "acks_received": acks_received,
                    "duration_ms": duration_ms,
                },
            )

            # Notify dashboard about status change
            try:
                from .dashboard_notifier import DashboardNotifier
                await DashboardNotifier.notify_status_change(log_entry, old_status="pending")
            except Exception as notify_error:
                logger.debug(f"Dashboard notification failed: {notify_error}")

        except Exception as e:
            logger.error(
                f"Failed to mark Centrifugo log as success: {e}",
                extra={"message_id": getattr(log_entry, "message_id", "unknown")},
            )

    @staticmethod
    def mark_success(
        log_entry: Any,
        acks_received: int = 0,
        duration_ms: int | None = None,
    ) -> None:
        """
        Mark publish operation as successful (sync version).

        Args:
            log_entry: CentrifugoLog instance
            acks_received: Number of ACKs received
            duration_ms: Duration in milliseconds
        """
        if log_entry is None:
            return

        try:
            from ..models import CentrifugoLog

            CentrifugoLog.objects.mark_success(
                log_instance=log_entry,
                acks_received=acks_received,
                duration_ms=duration_ms,
            )

            logger.info(
                f"Centrifugo publish successful: {log_entry.message_id}",
                extra={
                    "message_id": log_entry.message_id,
                    "channel": log_entry.channel,
                    "acks_received": acks_received,
                    "duration_ms": duration_ms,
                },
            )

        except Exception as e:
            logger.error(
                f"Failed to mark Centrifugo log as success: {e}",
                extra={"message_id": getattr(log_entry, "message_id", "unknown")},
            )

    @staticmethod
    def mark_partial(
        log_entry: Any,
        acks_received: int,
        acks_expected: int,
        duration_ms: int | None = None,
    ) -> None:
        """
        Mark publish operation as partially delivered.

        Args:
            log_entry: CentrifugoLog instance
            acks_received: Number of ACKs received
            acks_expected: Number of ACKs expected
            duration_ms: Duration in milliseconds
        """
        if log_entry is None:
            return

        try:
            from ..models import CentrifugoLog

            CentrifugoLog.objects.mark_partial(
                log_instance=log_entry,
                acks_received=acks_received,
                acks_expected=acks_expected,
                duration_ms=duration_ms,
            )

            logger.warning(
                f"Centrifugo publish partially delivered: {log_entry.message_id}",
                extra={
                    "message_id": log_entry.message_id,
                    "channel": log_entry.channel,
                    "acks_received": acks_received,
                    "acks_expected": acks_expected,
                    "duration_ms": duration_ms,
                },
            )

        except Exception as e:
            logger.error(
                f"Failed to mark Centrifugo log as partial: {e}",
                extra={"message_id": getattr(log_entry, "message_id", "unknown")},
            )

    @staticmethod
    def mark_failed(
        log_entry: Any,
        error_code: str,
        error_message: str,
        duration_ms: int | None = None,
    ) -> None:
        """
        Mark publish operation as failed.

        Args:
            log_entry: CentrifugoLog instance
            error_code: Error code
            error_message: Error message
            duration_ms: Duration in milliseconds
        """
        if log_entry is None:
            return

        try:
            from ..models import CentrifugoLog

            CentrifugoLog.objects.mark_failed(
                log_instance=log_entry,
                error_code=error_code,
                error_message=error_message,
                duration_ms=duration_ms,
            )

            logger.error(
                f"Centrifugo publish failed: {log_entry.message_id}",
                extra={
                    "message_id": log_entry.message_id,
                    "channel": log_entry.channel,
                    "error_code": error_code,
                    "error_message": error_message,
                    "duration_ms": duration_ms,
                },
            )

        except Exception as e:
            logger.error(
                f"Failed to mark Centrifugo log as failed: {e}",
                extra={"message_id": getattr(log_entry, "message_id", "unknown")},
            )

    @staticmethod
    async def mark_failed_async(
        log_entry: Any,
        error_code: str,
        error_message: str,
        duration_ms: int | None = None,
    ) -> None:
        """
        Mark publish operation as failed (async version).

        Args:
            log_entry: CentrifugoLog instance
            error_code: Error code
            error_message: Error message
            duration_ms: Duration in milliseconds
        """
        if log_entry is None:
            return

        try:
            from ..models import CentrifugoLog

            # ✅ Use Django 5.2+ async ORM instead of sync_to_async
            log_entry.status = CentrifugoLog.StatusChoices.FAILED
            log_entry.error_code = error_code
            log_entry.error_message = error_message
            log_entry.completed_at = timezone.now()

            if duration_ms is not None:
                log_entry.duration_ms = duration_ms

            await log_entry.asave(
                update_fields=[
                    "status",
                    "error_code",
                    "error_message",
                    "completed_at",
                    "duration_ms",
                ]
            )

            logger.error(
                f"Centrifugo publish failed: {log_entry.message_id}",
                extra={
                    "message_id": log_entry.message_id,
                    "channel": log_entry.channel,
                    "error_code": error_code,
                    "error_message": error_message,
                    "duration_ms": duration_ms,
                },
            )

        except Exception as e:
            logger.error(
                f"Failed to mark Centrifugo log as failed: {e}",
                extra={"message_id": getattr(log_entry, "message_id", "unknown")},
            )

    @staticmethod
    async def mark_timeout_async(
        log_entry: Any,
        acks_received: int = 0,
        duration_ms: int | None = None,
    ) -> None:
        """
        Mark publish operation as timed out (async version).

        Args:
            log_entry: CentrifugoLog instance
            acks_received: Number of ACKs received before timeout
            duration_ms: Duration in milliseconds
        """
        if log_entry is None:
            return

        try:
            from ..models import CentrifugoLog

            # ✅ Use Django 5.2+ async ORM instead of sync_to_async
            log_entry.status = CentrifugoLog.StatusChoices.TIMEOUT
            log_entry.acks_received = acks_received
            log_entry.error_code = "timeout"
            log_entry.error_message = f"Timeout after {log_entry.ack_timeout}s"
            log_entry.completed_at = timezone.now()

            if duration_ms is not None:
                log_entry.duration_ms = duration_ms

            await log_entry.asave(
                update_fields=[
                    "status",
                    "acks_received",
                    "error_code",
                    "error_message",
                    "completed_at",
                    "duration_ms",
                ]
            )

            logger.warning(
                f"Centrifugo publish timeout: {log_entry.message_id}",
                extra={
                    "message_id": log_entry.message_id,
                    "channel": log_entry.channel,
                    "acks_received": acks_received,
                    "ack_timeout": log_entry.ack_timeout,
                    "duration_ms": duration_ms,
                },
            )

        except Exception as e:
            logger.error(
                f"Failed to mark Centrifugo log as timeout: {e}",
                extra={"message_id": getattr(log_entry, "message_id", "unknown")},
            )

    @staticmethod
    def mark_timeout(
        log_entry: Any,
        acks_received: int = 0,
        duration_ms: int | None = None,
    ) -> None:
        """
        Mark publish operation as timed out (sync version).

        Args:
            log_entry: CentrifugoLog instance
            acks_received: Number of ACKs received before timeout
            duration_ms: Duration in milliseconds
        """
        if log_entry is None:
            return

        try:
            from ..models import CentrifugoLog

            CentrifugoLog.objects.mark_timeout(
                log_instance=log_entry,
                acks_received=acks_received,
                duration_ms=duration_ms,
            )

            logger.warning(
                f"Centrifugo publish timeout: {log_entry.message_id}",
                extra={
                    "message_id": log_entry.message_id,
                    "channel": log_entry.channel,
                    "acks_received": acks_received,
                    "ack_timeout": log_entry.ack_timeout,
                    "duration_ms": duration_ms,
                },
            )

        except Exception as e:
            logger.error(
                f"Failed to mark Centrifugo log as timeout: {e}",
                extra={"message_id": getattr(log_entry, "message_id", "unknown")},
            )


class CentrifugoLogContext:
    """
    Context manager for automatic Centrifugo publish logging.

    Mirrors RPCLogContext interface for migration compatibility.

    Usage:
        >>> with CentrifugoLogContext(
        ...     message_id="abc123",
        ...     channel="user#456",
        ...     data={"title": "Hello"},
        ...     wait_for_ack=True
        ... ) as log_ctx:
        ...     result = await client.publish_with_ack(...)
        ...     log_ctx.set_result(result.acks_received)
    """

    def __init__(
        self,
        message_id: str,
        channel: str,
        data: dict,
        wait_for_ack: bool = False,
        ack_timeout: int | None = None,
        acks_expected: int | None = None,
        is_notification: bool = True,
        user: Any = None,
        caller_ip: str | None = None,
        user_agent: str | None = None,
    ):
        """
        Initialize logging context.

        Args:
            message_id: Unique message identifier
            channel: Centrifugo channel
            data: Published data
            wait_for_ack: Whether this publish waits for ACK
            ack_timeout: ACK timeout in seconds
            acks_expected: Expected number of ACKs
            is_notification: Whether this is a notification
            user: Django User instance
            caller_ip: IP address of caller
            user_agent: User agent of caller
        """
        self.message_id = message_id
        self.channel = channel
        self.data = data
        self.wait_for_ack = wait_for_ack
        self.ack_timeout = ack_timeout
        self.acks_expected = acks_expected
        self.is_notification = is_notification
        self.user = user
        self.caller_ip = caller_ip
        self.user_agent = user_agent

        self.log_entry: Any = None
        self.start_time: float = 0
        self._result_set: bool = False

    def __enter__(self):
        """Enter context - create log entry."""
        self.start_time = time.time()

        self.log_entry = CentrifugoLogger.create_log(
            message_id=self.message_id,
            channel=self.channel,
            data=self.data,
            wait_for_ack=self.wait_for_ack,
            ack_timeout=self.ack_timeout,
            acks_expected=self.acks_expected,
            is_notification=self.is_notification,
            user=self.user,
            caller_ip=self.caller_ip,
            user_agent=self.user_agent,
        )

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context - mark result based on outcome."""
        duration_ms = int((time.time() - self.start_time) * 1000)

        # If result was explicitly set, don't override
        if self._result_set:
            return False

        # If exception occurred, mark as failed
        if exc_type is not None:
            error_code = exc_type.__name__ if exc_type else "unknown"
            error_message = str(exc_val) if exc_val else "Unknown error"
            CentrifugoLogger.mark_failed(
                self.log_entry,
                error_code=error_code,
                error_message=error_message,
                duration_ms=duration_ms,
            )
            return False

        # Otherwise mark as success with 0 ACKs (fire-and-forget)
        if not self.wait_for_ack:
            CentrifugoLogger.mark_success(
                self.log_entry,
                acks_received=0,
                duration_ms=duration_ms,
            )

        return False

    def set_result(self, acks_received: int) -> None:
        """
        Set successful result.

        Args:
            acks_received: Number of ACKs received
        """
        duration_ms = int((time.time() - self.start_time) * 1000)

        CentrifugoLogger.mark_success(
            self.log_entry,
            acks_received=acks_received,
            duration_ms=duration_ms,
        )

        self._result_set = True

    def set_timeout(self, acks_received: int = 0) -> None:
        """
        Set timeout result.

        Args:
            acks_received: Number of ACKs received before timeout
        """
        duration_ms = int((time.time() - self.start_time) * 1000)

        CentrifugoLogger.mark_timeout(
            self.log_entry,
            acks_received=acks_received,
            duration_ms=duration_ms,
        )

        self._result_set = True

    def set_partial(self, acks_received: int, acks_expected: int) -> None:
        """
        Set partial delivery result.

        Args:
            acks_received: Number of ACKs received
            acks_expected: Number of ACKs expected
        """
        duration_ms = int((time.time() - self.start_time) * 1000)

        CentrifugoLogger.mark_partial(
            self.log_entry,
            acks_received=acks_received,
            acks_expected=acks_expected,
            duration_ms=duration_ms,
        )

        self._result_set = True

    def set_error(self, error_code: str, error_message: str) -> None:
        """
        Set error result.

        Args:
            error_code: Error code
            error_message: Error message
        """
        duration_ms = int((time.time() - self.start_time) * 1000)

        CentrifugoLogger.mark_failed(
            self.log_entry,
            error_code=error_code,
            error_message=error_message,
            duration_ms=duration_ms,
        )

        self._result_set = True


__all__ = [
    "CentrifugoLogger",
    "CentrifugoLogContext",
    "logger",
]
