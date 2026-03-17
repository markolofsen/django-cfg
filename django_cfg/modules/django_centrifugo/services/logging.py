"""
Centrifugo Logging helper for tracking publish operations.

Rewritten from ORM to D1-backed append-only log.
Each status transition (pending → success/failed/timeout/partial)
inserts a new row — no UPDATE operations.

Interface is backward-compatible with the original CentrifugoLogger.
"""

from __future__ import annotations

import json
import logging
import time
from typing import Any, Optional

logger = logging.getLogger(__name__)


class CentrifugoLogger:
    """
    Helper class for logging Centrifugo publish operations to D1.

    Status transitions are tracked by inserting new rows (append-only).
    The log_entry returned by create_log / create_log_async is a simple
    dict (not an ORM object) — downstream callers only need message_id
    and channel from it.

    Usage:
        >>> log_entry = await CentrifugoLogger.create_log_async(
        ...     message_id="abc123",
        ...     channel="user#456",
        ...     data={"title": "Hello", "message": "World"},
        ...     wait_for_ack=True,
        ... )
        >>> # ... publish message ...
        >>> await CentrifugoLogger.mark_success_async(log_entry, acks_received=1, duration_ms=125)
    """

    @staticmethod
    def is_logging_enabled() -> bool:
        """Check if Centrifugo logging is enabled in django-cfg config."""
        from .config_helper import get_centrifugo_config

        config = get_centrifugo_config()
        if not config:
            return False
        if config.log_only_with_ack:
            return True  # Will check wait_for_ack in create_log
        return config.log_all_calls

    # ─────────────────────────────────────────────────────────────────────────
    # Create (pending)
    # ─────────────────────────────────────────────────────────────────────────

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
    ) -> dict | None:
        """Create a pending log row in D1 (async). Returns dict or None if disabled."""
        if not CentrifugoLogger.is_logging_enabled():
            return None

        from .config_helper import get_centrifugo_config

        config = get_centrifugo_config()
        if config and config.log_only_with_ack and not wait_for_ack:
            return None

        try:
            from ..events.service import CentrifugoD1Service
            from ..events.types import CentrifugoLogRow

            user_id = str(user.id) if user and hasattr(user, "id") else None
            data_str = json.dumps(data, ensure_ascii=False, default=str)[:10000]

            row = CentrifugoLogRow.create_pending(
                message_id=message_id,
                channel=channel,
                data=data_str,
                wait_for_ack=wait_for_ack,
                ack_timeout=ack_timeout,
                acks_expected=acks_expected,
                is_notification=is_notification,
                user_id=user_id,
                caller_ip=caller_ip,
                user_agent=user_agent,
            )

            svc = CentrifugoD1Service()
            svc.insert_log(row)

            logger.debug(
                "centrifugo: log created message_id=%s channel=%s wait_for_ack=%s",
                message_id, channel, wait_for_ack,
            )

            return {"message_id": message_id, "channel": channel, "row_id": row.id}

        except Exception as exc:
            logger.error("centrifugo: create_log_async failed: %s", exc)
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
    ) -> dict | None:
        """Create a pending log row in D1 (sync). Returns dict or None if disabled."""
        if not CentrifugoLogger.is_logging_enabled():
            return None

        from .config_helper import get_centrifugo_config

        config = get_centrifugo_config()
        if config and config.log_only_with_ack and not wait_for_ack:
            return None

        try:
            from ..events.service import CentrifugoD1Service
            from ..events.types import CentrifugoLogRow

            user_id = str(user.id) if user and hasattr(user, "id") else None
            data_str = json.dumps(data, ensure_ascii=False, default=str)[:10000]

            row = CentrifugoLogRow.create_pending(
                message_id=message_id,
                channel=channel,
                data=data_str,
                wait_for_ack=wait_for_ack,
                ack_timeout=ack_timeout,
                acks_expected=acks_expected,
                is_notification=is_notification,
                user_id=user_id,
                caller_ip=caller_ip,
                user_agent=user_agent,
            )

            svc = CentrifugoD1Service()
            svc.insert_log(row)

            logger.debug(
                "centrifugo: log created message_id=%s channel=%s wait_for_ack=%s",
                message_id, channel, wait_for_ack,
            )

            return {"message_id": message_id, "channel": channel, "row_id": row.id}

        except Exception as exc:
            logger.error("centrifugo: create_log failed: %s", exc)
            return None

    # ─────────────────────────────────────────────────────────────────────────
    # Status transitions — each inserts a NEW row (append-only)
    # ─────────────────────────────────────────────────────────────────────────

    @staticmethod
    async def mark_success_async(
        log_entry: dict | None,
        acks_received: int = 0,
        duration_ms: int | None = None,
    ) -> None:
        if log_entry is None:
            return
        try:
            from ..events.service import CentrifugoD1Service
            from ..events.types import CentrifugoLogRow, CentrifugoLogStatus

            row = CentrifugoLogRow.create_transition(
                message_id=log_entry["message_id"],
                channel=log_entry["channel"],
                status=CentrifugoLogStatus.SUCCESS,
                acks_received=acks_received,
                duration_ms=duration_ms,
            )
            CentrifugoD1Service().insert_log(row)
            logger.info("centrifugo: mark_success message_id=%s acks=%s", log_entry["message_id"], acks_received)
        except Exception as exc:
            logger.error("centrifugo: mark_success_async failed: %s", exc)

    @staticmethod
    def mark_success(
        log_entry: dict | None,
        acks_received: int = 0,
        duration_ms: int | None = None,
    ) -> None:
        if log_entry is None:
            return
        try:
            from ..events.service import CentrifugoD1Service
            from ..events.types import CentrifugoLogRow, CentrifugoLogStatus

            row = CentrifugoLogRow.create_transition(
                message_id=log_entry["message_id"],
                channel=log_entry["channel"],
                status=CentrifugoLogStatus.SUCCESS,
                acks_received=acks_received,
                duration_ms=duration_ms,
            )
            CentrifugoD1Service().insert_log(row)
            logger.info("centrifugo: mark_success message_id=%s acks=%s", log_entry["message_id"], acks_received)
        except Exception as exc:
            logger.error("centrifugo: mark_success failed: %s", exc)

    @staticmethod
    async def mark_failed_async(
        log_entry: dict | None,
        error_code: str,
        error_message: str,
        duration_ms: int | None = None,
    ) -> None:
        if log_entry is None:
            return
        try:
            from ..events.service import CentrifugoD1Service
            from ..events.types import CentrifugoLogRow, CentrifugoLogStatus

            row = CentrifugoLogRow.create_transition(
                message_id=log_entry["message_id"],
                channel=log_entry["channel"],
                status=CentrifugoLogStatus.FAILED,
                error_code=error_code,
                error_message=error_message,
                duration_ms=duration_ms,
            )
            CentrifugoD1Service().insert_log(row)
            logger.error("centrifugo: mark_failed message_id=%s code=%s", log_entry["message_id"], error_code)
        except Exception as exc:
            logger.error("centrifugo: mark_failed_async failed: %s", exc)

    @staticmethod
    def mark_failed(
        log_entry: dict | None,
        error_code: str,
        error_message: str,
        duration_ms: int | None = None,
    ) -> None:
        if log_entry is None:
            return
        try:
            from ..events.service import CentrifugoD1Service
            from ..events.types import CentrifugoLogRow, CentrifugoLogStatus

            row = CentrifugoLogRow.create_transition(
                message_id=log_entry["message_id"],
                channel=log_entry["channel"],
                status=CentrifugoLogStatus.FAILED,
                error_code=error_code,
                error_message=error_message,
                duration_ms=duration_ms,
            )
            CentrifugoD1Service().insert_log(row)
            logger.error("centrifugo: mark_failed message_id=%s code=%s", log_entry["message_id"], error_code)
        except Exception as exc:
            logger.error("centrifugo: mark_failed failed: %s", exc)

    @staticmethod
    async def mark_timeout_async(
        log_entry: dict | None,
        acks_received: int = 0,
        duration_ms: int | None = None,
    ) -> None:
        if log_entry is None:
            return
        try:
            from ..events.service import CentrifugoD1Service
            from ..events.types import CentrifugoLogRow, CentrifugoLogStatus

            row = CentrifugoLogRow.create_transition(
                message_id=log_entry["message_id"],
                channel=log_entry["channel"],
                status=CentrifugoLogStatus.TIMEOUT,
                acks_received=acks_received,
                error_code="timeout",
                error_message="ACK timeout",
                duration_ms=duration_ms,
            )
            CentrifugoD1Service().insert_log(row)
            logger.warning("centrifugo: mark_timeout message_id=%s acks=%s", log_entry["message_id"], acks_received)
        except Exception as exc:
            logger.error("centrifugo: mark_timeout_async failed: %s", exc)

    @staticmethod
    def mark_timeout(
        log_entry: dict | None,
        acks_received: int = 0,
        duration_ms: int | None = None,
    ) -> None:
        if log_entry is None:
            return
        try:
            from ..events.service import CentrifugoD1Service
            from ..events.types import CentrifugoLogRow, CentrifugoLogStatus

            row = CentrifugoLogRow.create_transition(
                message_id=log_entry["message_id"],
                channel=log_entry["channel"],
                status=CentrifugoLogStatus.TIMEOUT,
                acks_received=acks_received,
                error_code="timeout",
                error_message="ACK timeout",
                duration_ms=duration_ms,
            )
            CentrifugoD1Service().insert_log(row)
            logger.warning("centrifugo: mark_timeout message_id=%s acks=%s", log_entry["message_id"], acks_received)
        except Exception as exc:
            logger.error("centrifugo: mark_timeout failed: %s", exc)

    @staticmethod
    def mark_partial(
        log_entry: dict | None,
        acks_received: int,
        acks_expected: int,
        duration_ms: int | None = None,
    ) -> None:
        if log_entry is None:
            return
        try:
            from ..events.service import CentrifugoD1Service
            from ..events.types import CentrifugoLogRow, CentrifugoLogStatus

            row = CentrifugoLogRow.create_transition(
                message_id=log_entry["message_id"],
                channel=log_entry["channel"],
                status=CentrifugoLogStatus.PARTIAL,
                acks_received=acks_received,
                acks_expected=acks_expected,
                duration_ms=duration_ms,
            )
            CentrifugoD1Service().insert_log(row)
            logger.warning(
                "centrifugo: mark_partial message_id=%s acks=%s/%s",
                log_entry["message_id"], acks_received, acks_expected,
            )
        except Exception as exc:
            logger.error("centrifugo: mark_partial failed: %s", exc)


class CentrifugoLogContext:
    """
    Context manager for automatic Centrifugo publish logging.

    Interface is backward-compatible with the original ORM-backed version.
    log_entry is now a dict instead of an ORM model instance.

    Usage:
        >>> with CentrifugoLogContext(
        ...     message_id="abc123",
        ...     channel="user#456",
        ...     data={"title": "Hello"},
        ...     wait_for_ack=True
        ... ) as log_ctx:
        ...     result = client.publish(...)
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

        self.log_entry: dict | None = None
        self.start_time: float = 0
        self._result_set: bool = False

    def __enter__(self) -> "CentrifugoLogContext":
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
        duration_ms = int((time.time() - self.start_time) * 1000)

        if self._result_set:
            return False

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

        if not self.wait_for_ack:
            CentrifugoLogger.mark_success(self.log_entry, acks_received=0, duration_ms=duration_ms)

        return False

    def set_result(self, acks_received: int) -> None:
        duration_ms = int((time.time() - self.start_time) * 1000)
        CentrifugoLogger.mark_success(self.log_entry, acks_received=acks_received, duration_ms=duration_ms)
        self._result_set = True

    def set_timeout(self, acks_received: int = 0) -> None:
        duration_ms = int((time.time() - self.start_time) * 1000)
        CentrifugoLogger.mark_timeout(self.log_entry, acks_received=acks_received, duration_ms=duration_ms)
        self._result_set = True

    def set_partial(self, acks_received: int, acks_expected: int) -> None:
        duration_ms = int((time.time() - self.start_time) * 1000)
        CentrifugoLogger.mark_partial(
            self.log_entry,
            acks_received=acks_received,
            acks_expected=acks_expected,
            duration_ms=duration_ms,
        )
        self._result_set = True

    def set_error(self, error_code: str, error_message: str) -> None:
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
]
