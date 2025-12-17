"""
Django Telegram Service for django_cfg.

Auto-configuring Telegram notification service that integrates with DjangoConfig.
"""

import itertools
import queue
import threading
import time
from enum import Enum
from typing import Any, BinaryIO, Dict, Optional, Union

import telebot
import yaml

from ..base import BaseCfgModule
from ..django_logging import get_logger

logger = get_logger("django_cfg.telegram")


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
        self._worker = threading.Thread(target=self._process_queue, daemon=True, name="TelegramQueueWorker")
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
                    f"Queue FULL but CRITICAL message queued anyway: {current_size}/{self.MAX_QUEUE_SIZE}"
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
_telegram_queue = TelegramMessageQueue()


class TelegramParseMode(Enum):
    """Telegram message parse modes."""

    MARKDOWN = "Markdown"
    MARKDOWN_V2 = "MarkdownV2"
    HTML = "HTML"


class TelegramError(Exception):
    """Base exception for Telegram-related errors."""
    pass


class TelegramConfigError(TelegramError):
    """Raised when configuration is missing or invalid."""
    pass


class TelegramSendError(TelegramError):
    """Raised when message sending fails."""
    pass


class DjangoTelegram(BaseCfgModule):
    """
    Telegram Service for django_cfg, configured via DjangoConfig.

    Provides Telegram messaging functionality with automatic configuration
    from the main DjangoConfig instance.

    All messages are queued through a global singleton queue with rate limiting
    (20 messages/second) to avoid hitting Telegram API limits.
    """

    # Emoji mappings for different message types
    EMOJI_MAP = {
        "success": "✅",
        "error": "❌",
        "warning": "⚠️",
        "info": "ℹ️",
        "start": "🚀",
        "finish": "🏁",
        "stats": "📊",
        "alert": "🚨",
    }

    def __init__(self):
        self._bot = None
        self._is_configured = None

    @property
    def config(self):
        """Get the DjangoConfig instance."""
        return self.get_config()

    @property
    def project_prefix(self) -> str:
        """Get project name prefix for messages."""
        try:
            config = self.config
            if config and hasattr(config, 'project_name') and config.project_name:
                return f"[{config.project_name}] "
        except Exception:
            pass
        return ""

    @property
    def is_configured(self) -> bool:
        """Check if Telegram is properly configured."""
        if self._is_configured is None:
            try:
                telegram_config = self.config.telegram
                self._is_configured = telegram_config is not None and telegram_config.bot_token and len(telegram_config.bot_token.strip()) > 0
            except Exception:
                self._is_configured = False

        return self._is_configured

    @property
    def bot(self):
        """Get Telegram bot instance."""
        if not self.is_configured:
            raise TelegramConfigError("Telegram is not properly configured")

        if self._bot is None:
            try:
                telegram_config = self.config.telegram
                self._bot = telebot.TeleBot(telegram_config.bot_token)
            except ImportError:
                raise TelegramConfigError("pyTelegramBotAPI is not installed. Install with: pip install pyTelegramBotAPI")
            except Exception as e:
                raise TelegramConfigError(f"Failed to initialize Telegram bot: {e}")

        return self._bot

    def get_config_info(self) -> Dict[str, Any]:
        """Get Telegram configuration information with queue stats."""
        queue_stats = _telegram_queue.get_stats()

        if not self.is_configured:
            return {
                "configured": False,
                "bot_token": "Not configured",
                "chat_id": "Not configured",
                "enabled": False,
                **queue_stats,
            }

        telegram_config = self.config.telegram
        return {
            "configured": True,
            "bot_token": f"{telegram_config.bot_token[:10]}..." if telegram_config.bot_token else "Not set",
            "chat_id": telegram_config.chat_id or "Not set",
            "enabled": True,
            "parse_mode": telegram_config.parse_mode or "None",
            "rate_limit": "20 messages/second",
            **queue_stats,
        }

    @staticmethod
    def get_queue_size() -> int:
        """Get current number of messages in the global queue."""
        return _telegram_queue.size()

    @staticmethod
    def get_queue_stats() -> dict:
        """Get detailed queue statistics."""
        return _telegram_queue.get_stats()

    def _enqueue_message(self, func, priority=MessagePriority.NORMAL, *args, **kwargs):
        """
        Add message to global queue with priority and rate limiting.

        Args:
            func: Function to execute
            priority: Message priority (1=CRITICAL, 2=HIGH, 3=NORMAL, 4=LOW)
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function
        """
        _telegram_queue.enqueue(func, priority, *args, **kwargs)

    def send_message(
        self,
        message: str,
        chat_id: Optional[Union[int, str]] = None,
        parse_mode: Optional[TelegramParseMode] = None,
        disable_notification: bool = False,
        reply_to_message_id: Optional[int] = None,
        fail_silently: bool = False,
        priority: int = MessagePriority.NORMAL,
    ) -> bool:
        """
        Send a text message to Telegram via global queue (non-blocking, rate-limited).

        Messages are queued and sent at max 20 msg/sec to avoid Telegram API limits.
        Higher priority messages (lower number) are sent first.

        Args:
            message: Message text to send
            chat_id: Target chat ID (uses config default if not provided)
            parse_mode: Message parse mode (Markdown, HTML, etc.)
            disable_notification: Send silently
            reply_to_message_id: Reply to specific message
            fail_silently: Don't raise exceptions on failure
            priority: Message priority (1=CRITICAL, 2=HIGH, 3=NORMAL, 4=LOW)

        Returns:
            True if message queued successfully, False otherwise
        """
        try:
            if not self.is_configured:
                error_msg = "Telegram is not configured"
                logger.error(error_msg)
                if not fail_silently:
                    raise TelegramConfigError(error_msg)
                return False

            telegram_config = self.config.telegram
            target_chat_id = chat_id or telegram_config.chat_id
            if not target_chat_id:
                error_msg = "No chat_id provided and none configured"
                logger.error(error_msg)
                if not fail_silently:
                    raise TelegramConfigError(error_msg)
                return False

            target_parse_mode = parse_mode or telegram_config.parse_mode

            # Handle both enum and string parse modes
            if target_parse_mode:
                if isinstance(target_parse_mode, TelegramParseMode):
                    parse_mode_str = target_parse_mode.value
                else:
                    parse_mode_str = target_parse_mode
            else:
                parse_mode_str = None

            def _do_send():
                # Add project prefix to message
                prefixed_message = f"{self.project_prefix}{message}"

                self.bot.send_message(
                    chat_id=target_chat_id,
                    text=prefixed_message,
                    parse_mode=parse_mode_str,
                    disable_notification=disable_notification,
                    reply_to_message_id=reply_to_message_id,
                )
                logger.info(f"Telegram message sent successfully to chat {target_chat_id}")

            # Always enqueue to global queue with rate limiting
            self._enqueue_message(_do_send, priority=priority)
            return True

        except Exception as e:
            error_msg = f"Failed to send Telegram message: {e}"
            logger.error(error_msg)
            if not fail_silently:
                raise TelegramSendError(error_msg) from e
            return False

    def send_photo(
        self,
        photo: Union[str, BinaryIO],
        caption: Optional[str] = None,
        chat_id: Optional[Union[int, str]] = None,
        parse_mode: Optional[TelegramParseMode] = None,
        fail_silently: bool = False,
        priority: int = MessagePriority.NORMAL,
    ) -> bool:
        """
        Send a photo to Telegram via global queue (non-blocking, rate-limited).

        Messages are queued and sent at max 20 msg/sec to avoid Telegram API limits.
        Higher priority messages (lower number) are sent first.

        Args:
            photo: Photo file path, URL, or file-like object
            caption: Photo caption
            chat_id: Target chat ID (uses config default if not provided)
            parse_mode: Caption parse mode
            fail_silently: Don't raise exceptions on failure
            priority: Message priority (1=CRITICAL, 2=HIGH, 3=NORMAL, 4=LOW)

        Returns:
            True if photo queued successfully, False otherwise
        """
        try:
            if not self.is_configured:
                error_msg = "Telegram is not configured"
                logger.error(error_msg)
                if not fail_silently:
                    raise TelegramConfigError(error_msg)
                return False

            telegram_config = self.config.telegram
            target_chat_id = chat_id or telegram_config.chat_id

            if not target_chat_id:
                error_msg = "No chat_id provided and none configured"
                logger.error(error_msg)
                if not fail_silently:
                    raise TelegramConfigError(error_msg)
                return False

            target_parse_mode = parse_mode or telegram_config.parse_mode

            # Handle both enum and string parse modes
            if target_parse_mode:
                if isinstance(target_parse_mode, TelegramParseMode):
                    parse_mode_str = target_parse_mode.value
                else:
                    parse_mode_str = target_parse_mode
            else:
                parse_mode_str = None

            def _do_send():
                # Add project prefix to caption if present
                prefixed_caption = f"{self.project_prefix}{caption}" if caption else self.project_prefix.strip() if self.project_prefix else None

                self.bot.send_photo(
                    chat_id=target_chat_id,
                    photo=photo,
                    caption=prefixed_caption,
                    parse_mode=parse_mode_str,
                )
                logger.info(f"Telegram photo sent successfully to chat {target_chat_id}")

            # Always enqueue to global queue with rate limiting
            self._enqueue_message(_do_send, priority=priority)
            return True

        except Exception as e:
            error_msg = f"Failed to send Telegram photo: {e}"
            logger.error(error_msg)
            if not fail_silently:
                raise TelegramSendError(error_msg) from e
            return False

    def send_document(
        self,
        document: Union[str, BinaryIO],
        caption: Optional[str] = None,
        chat_id: Optional[Union[int, str]] = None,
        parse_mode: Optional[TelegramParseMode] = None,
        fail_silently: bool = False,
        priority: int = MessagePriority.NORMAL,
    ) -> bool:
        """
        Send a document to Telegram via global queue (non-blocking, rate-limited).

        Messages are queued and sent at max 20 msg/sec to avoid Telegram API limits.
        Higher priority messages (lower number) are sent first.

        Args:
            document: Document file path, URL, or file-like object
            caption: Document caption
            chat_id: Target chat ID (uses config default if not provided)
            parse_mode: Caption parse mode
            fail_silently: Don't raise exceptions on failure
            priority: Message priority (1=CRITICAL, 2=HIGH, 3=NORMAL, 4=LOW)

        Returns:
            True if document queued successfully, False otherwise
        """
        try:
            if not self.is_configured:
                error_msg = "Telegram is not configured"
                logger.error(error_msg)
                if not fail_silently:
                    raise TelegramConfigError(error_msg)
                return False

            telegram_config = self.config.telegram
            target_chat_id = chat_id or telegram_config.chat_id

            if not target_chat_id:
                error_msg = "No chat_id provided and none configured"
                logger.error(error_msg)
                if not fail_silently:
                    raise TelegramConfigError(error_msg)
                return False

            target_parse_mode = parse_mode or telegram_config.parse_mode

            # Handle both enum and string parse modes
            if target_parse_mode:
                if isinstance(target_parse_mode, TelegramParseMode):
                    parse_mode_str = target_parse_mode.value
                else:
                    parse_mode_str = target_parse_mode
            else:
                parse_mode_str = None

            def _do_send():
                # Add project prefix to caption if present
                prefixed_caption = f"{self.project_prefix}{caption}" if caption else self.project_prefix.strip() if self.project_prefix else None

                self.bot.send_document(
                    chat_id=target_chat_id,
                    document=document,
                    caption=prefixed_caption,
                    parse_mode=parse_mode_str,
                )
                logger.info(f"Telegram document sent successfully to chat {target_chat_id}")

            # Always enqueue to global queue with rate limiting
            self._enqueue_message(_do_send, priority=priority)
            return True

        except Exception as e:
            error_msg = f"Failed to send Telegram document: {e}"
            logger.error(error_msg)
            if not fail_silently:
                raise TelegramSendError(error_msg) from e
            return False

    def get_me(self) -> Optional[Dict[str, Any]]:
        """
        Get information about the bot.

        Returns:
            Bot information dict or None if failed
        """
        try:
            if not self.is_configured:
                return None

            bot_info = self.bot.get_me()
            return {
                "id": bot_info.id,
                "is_bot": bot_info.is_bot,
                "first_name": bot_info.first_name,
                "username": bot_info.username,
                "can_join_groups": bot_info.can_join_groups,
                "can_read_all_group_messages": bot_info.can_read_all_group_messages,
                "supports_inline_queries": bot_info.supports_inline_queries,
            }

        except Exception as e:
            logger.error(f"Failed to get bot info: {e}")
            return None

    @classmethod
    def _format_to_yaml(cls, data: Dict[str, Any]) -> str:
        """Format dictionary data as YAML string."""
        try:
            yaml_str = yaml.safe_dump(
                data,
                default_flow_style=False,
                allow_unicode=True,
                sort_keys=False,
                indent=2,
            )
            return yaml_str
        except Exception as e:
            logger.error(f"Error formatting to YAML: {str(e)}")
            return str(data)

    @classmethod
    def send_error(cls, error: str, context: Optional[Dict[str, Any]] = None) -> None:
        """Send error notification with HIGH priority."""
        try:
            telegram = cls()
            text = f"{cls.EMOJI_MAP['error']} <b>Error</b>\n\n{error}"
            if context:
                text += "\n\n<pre>" + cls._format_to_yaml(context) + "</pre>"
            telegram.send_message(text, parse_mode=TelegramParseMode.HTML, priority=MessagePriority.HIGH)
        except Exception:
            # Silently fail - error notifications should not cause cascading failures
            pass

    @classmethod
    def send_success(cls, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        """Send success notification with NORMAL priority."""
        try:
            telegram = cls()
            text = f"{cls.EMOJI_MAP['success']} <b>Success</b>\n\n{message}"
            if details:
                text += "\n\n<pre>" + cls._format_to_yaml(details) + "</pre>"
            telegram.send_message(text, parse_mode=TelegramParseMode.HTML, priority=MessagePriority.NORMAL)
        except Exception:
            # Silently fail - success notifications should not cause failures
            pass

    @classmethod
    def send_warning(cls, warning: str, context: Optional[Dict[str, Any]] = None) -> None:
        """Send warning notification with HIGH priority."""
        try:
            telegram = cls()
            text = f"{cls.EMOJI_MAP['warning']} <b>Warning</b>\n\n{warning}"
            if context:
                text += "\n\n<pre>" + cls._format_to_yaml(context) + "</pre>"
            telegram.send_message(text, parse_mode=TelegramParseMode.HTML, priority=MessagePriority.HIGH)
        except Exception:
            # Silently fail - warning notifications should not cause failures
            pass

    @classmethod
    def send_info(cls, message: str, data: Optional[Dict[str, Any]] = None) -> None:
        """Send informational message with NORMAL priority."""
        telegram = cls()
        text = f"{cls.EMOJI_MAP['info']} <b>Info</b>\n\n{message}"
        if data:
            text += "\n\n<pre>" + cls._format_to_yaml(data) + "</pre>"
        telegram.send_message(text, parse_mode=TelegramParseMode.HTML, priority=MessagePriority.NORMAL)

    @classmethod
    def send_stats(cls, title: str, stats: Dict[str, Any]) -> None:
        """Send statistics data with LOW priority."""
        telegram = cls()
        text = f"{cls.EMOJI_MAP['stats']} <b>{title}</b>"
        text += "\n\n<pre>" + cls._format_to_yaml(stats) + "</pre>"
        telegram.send_message(text, parse_mode=TelegramParseMode.HTML, priority=MessagePriority.LOW)


__all__ = [
    "TelegramParseMode",
    "TelegramError",
    "TelegramConfigError",
    "TelegramSendError",
    "DjangoTelegram",
    "MessagePriority",
]
