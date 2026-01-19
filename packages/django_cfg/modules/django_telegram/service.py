"""
Django Telegram Service for django_cfg.

Auto-configuring Telegram notification service that integrates with DjangoConfig.
Supports custom bot_token and chat_id per-call with fallback to config defaults.
"""

from typing import Any, BinaryIO, Dict, Optional, Union

import telebot

from ..base import BaseCfgModule
from ..django_logging import get_logger

from .exceptions import TelegramConfigError, TelegramSendError
from .formatters import EMOJI_MAP
from .queue import MessagePriority, telegram_queue
from .types import TelegramParseMode

logger = get_logger("django_cfg.telegram")


class DjangoTelegram(BaseCfgModule):
    """
    Telegram Service for django_cfg, configured via DjangoConfig.

    Provides Telegram messaging functionality with automatic configuration
    from the main DjangoConfig instance.

    All messages are queued through a global singleton queue with rate limiting
    (20 messages/second) to avoid hitting Telegram API limits.

    Supports custom bot_token and chat_id per-call with fallback to config defaults.
    """

    # Reference to EMOJI_MAP for backward compatibility
    EMOJI_MAP = EMOJI_MAP

    # Cache for custom bot instances by token
    _custom_bots: Dict[str, telebot.TeleBot] = {}

    def __init__(
        self,
        bot_token: Optional[str] = None,
        chat_id: Optional[Union[int, str]] = None,
        disable_prefix: bool = False,
    ):
        """
        Initialize Telegram service.

        Args:
            bot_token: Custom bot token (uses config default if not provided)
            chat_id: Custom chat ID (uses config default if not provided)
            disable_prefix: If True, don't add project name prefix to messages
        """
        self._bot = None
        self._is_configured = None
        self._custom_bot_token = bot_token
        self._custom_chat_id = chat_id
        self._disable_prefix = disable_prefix

    # ========== CONFIG PROPERTIES ==========

    @property
    def config(self):
        """Get the DjangoConfig instance."""
        return self.get_config()

    @property
    def project_prefix(self) -> str:
        """Get project name prefix for messages."""
        if self._disable_prefix:
            return ""
        try:
            config = self.config
            if config and hasattr(config, "project_name") and config.project_name:
                return f"[{config.project_name}] "
        except Exception:
            pass
        return ""

    @property
    def is_configured(self) -> bool:
        """Check if Telegram is properly configured (custom or default)."""
        if self._custom_bot_token and len(self._custom_bot_token.strip()) > 0:
            return True

        if self._is_configured is None:
            try:
                telegram_config = self.config.telegram
                self._is_configured = (
                    telegram_config is not None
                    and telegram_config.bot_token
                    and len(telegram_config.bot_token.strip()) > 0
                )
            except Exception:
                self._is_configured = False

        return self._is_configured

    # ========== BOT MANAGEMENT ==========

    @property
    def bot(self):
        """Get Telegram bot instance (custom or default)."""
        return self._get_bot()

    def _get_bot(self, bot_token: Optional[str] = None) -> telebot.TeleBot:
        """Get bot instance by token (cached)."""
        token = bot_token or self._custom_bot_token

        if token:
            if token not in self._custom_bots:
                try:
                    self._custom_bots[token] = telebot.TeleBot(token)
                    logger.debug(f"Created custom bot instance (token: {token[:10]}...)")
                except ImportError:
                    raise TelegramConfigError(
                        "pyTelegramBotAPI is not installed. Install with: pip install pyTelegramBotAPI"
                    )
                except Exception as e:
                    raise TelegramConfigError(f"Failed to initialize custom Telegram bot: {e}")
            return self._custom_bots[token]

        if not self.is_configured:
            raise TelegramConfigError("Telegram is not properly configured")

        if self._bot is None:
            try:
                telegram_config = self.config.telegram
                self._bot = telebot.TeleBot(telegram_config.bot_token)
            except ImportError:
                raise TelegramConfigError(
                    "pyTelegramBotAPI is not installed. Install with: pip install pyTelegramBotAPI"
                )
            except Exception as e:
                raise TelegramConfigError(f"Failed to initialize Telegram bot: {e}")

        return self._bot

    # ========== RESOLVERS ==========

    def _resolve_chat_id(self, chat_id: Optional[Union[int, str]] = None) -> Optional[Union[int, str]]:
        """Resolve chat_id from param > instance > config."""
        target_chat_id = chat_id or self._custom_chat_id
        if not target_chat_id:
            try:
                telegram_config = self.config.telegram
                if telegram_config:
                    target_chat_id = telegram_config.chat_id
            except Exception:
                pass
        return target_chat_id

    def _resolve_parse_mode(self, parse_mode: Optional[TelegramParseMode] = None) -> Optional[str]:
        """Resolve parse_mode and convert to string."""
        target_parse_mode = parse_mode
        if not target_parse_mode:
            try:
                telegram_config = self.config.telegram
                if telegram_config:
                    target_parse_mode = telegram_config.parse_mode
            except Exception:
                pass

        if target_parse_mode:
            if isinstance(target_parse_mode, TelegramParseMode):
                return target_parse_mode.value
            return target_parse_mode
        return None

    # ========== CONFIG INFO ==========

    def get_config_info(self) -> Dict[str, Any]:
        """Get Telegram configuration information with queue stats."""
        queue_stats = telegram_queue.get_stats()

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
        return telegram_queue.size()

    @staticmethod
    def get_queue_stats() -> dict:
        """Get detailed queue statistics."""
        return telegram_queue.get_stats()

    # ========== SEND METHODS ==========

    def _enqueue_message(self, func, priority=MessagePriority.NORMAL, *args, **kwargs):
        """Add message to global queue with priority and rate limiting."""
        telegram_queue.enqueue(func, priority, *args, **kwargs)

    def send_message(
        self,
        message: str,
        chat_id: Optional[Union[int, str]] = None,
        bot_token: Optional[str] = None,
        parse_mode: Optional[TelegramParseMode] = None,
        disable_notification: bool = False,
        reply_to_message_id: Optional[int] = None,
        fail_silently: bool = False,
        priority: int = MessagePriority.NORMAL,
    ) -> bool:
        """Send a text message to Telegram via global queue (non-blocking, rate-limited)."""
        try:
            effective_token = bot_token or self._custom_bot_token

            if not effective_token and not self.is_configured:
                error_msg = "Telegram is not configured"
                logger.error(error_msg)
                if not fail_silently:
                    raise TelegramConfigError(error_msg)
                return False

            target_chat_id = self._resolve_chat_id(chat_id)
            if not target_chat_id:
                error_msg = "No chat_id provided and none configured"
                logger.error(error_msg)
                if not fail_silently:
                    raise TelegramConfigError(error_msg)
                return False

            parse_mode_str = self._resolve_parse_mode(parse_mode)
            bot_instance = self._get_bot(effective_token)

            def _do_send():
                prefixed_message = f"{self.project_prefix}{message}"
                bot_instance.send_message(
                    chat_id=target_chat_id,
                    text=prefixed_message,
                    parse_mode=parse_mode_str,
                    disable_notification=disable_notification,
                    reply_to_message_id=reply_to_message_id,
                )
                logger.info(f"Telegram message sent successfully to chat {target_chat_id}")

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
        bot_token: Optional[str] = None,
        parse_mode: Optional[TelegramParseMode] = None,
        fail_silently: bool = False,
        priority: int = MessagePriority.NORMAL,
    ) -> bool:
        """Send a photo to Telegram via global queue (non-blocking, rate-limited)."""
        try:
            effective_token = bot_token or self._custom_bot_token

            if not effective_token and not self.is_configured:
                error_msg = "Telegram is not configured"
                logger.error(error_msg)
                if not fail_silently:
                    raise TelegramConfigError(error_msg)
                return False

            target_chat_id = self._resolve_chat_id(chat_id)
            if not target_chat_id:
                error_msg = "No chat_id provided and none configured"
                logger.error(error_msg)
                if not fail_silently:
                    raise TelegramConfigError(error_msg)
                return False

            parse_mode_str = self._resolve_parse_mode(parse_mode)
            bot_instance = self._get_bot(effective_token)

            def _do_send():
                prefixed_caption = (
                    f"{self.project_prefix}{caption}"
                    if caption
                    else self.project_prefix.strip() if self.project_prefix else None
                )
                bot_instance.send_photo(
                    chat_id=target_chat_id,
                    photo=photo,
                    caption=prefixed_caption,
                    parse_mode=parse_mode_str,
                )
                logger.info(f"Telegram photo sent successfully to chat {target_chat_id}")

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
        bot_token: Optional[str] = None,
        parse_mode: Optional[TelegramParseMode] = None,
        fail_silently: bool = False,
        priority: int = MessagePriority.NORMAL,
    ) -> bool:
        """Send a document to Telegram via global queue (non-blocking, rate-limited)."""
        try:
            effective_token = bot_token or self._custom_bot_token

            if not effective_token and not self.is_configured:
                error_msg = "Telegram is not configured"
                logger.error(error_msg)
                if not fail_silently:
                    raise TelegramConfigError(error_msg)
                return False

            target_chat_id = self._resolve_chat_id(chat_id)
            if not target_chat_id:
                error_msg = "No chat_id provided and none configured"
                logger.error(error_msg)
                if not fail_silently:
                    raise TelegramConfigError(error_msg)
                return False

            parse_mode_str = self._resolve_parse_mode(parse_mode)
            bot_instance = self._get_bot(effective_token)

            def _do_send():
                prefixed_caption = (
                    f"{self.project_prefix}{caption}"
                    if caption
                    else self.project_prefix.strip() if self.project_prefix else None
                )
                bot_instance.send_document(
                    chat_id=target_chat_id,
                    document=document,
                    caption=prefixed_caption,
                    parse_mode=parse_mode_str,
                )
                logger.info(f"Telegram document sent successfully to chat {target_chat_id}")

            self._enqueue_message(_do_send, priority=priority)
            return True

        except Exception as e:
            error_msg = f"Failed to send Telegram document: {e}"
            logger.error(error_msg)
            if not fail_silently:
                raise TelegramSendError(error_msg) from e
            return False

    # ========== BOT INFO ==========

    def get_me(self) -> Optional[Dict[str, Any]]:
        """Get information about the bot."""
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

    def get_updates(self, limit: int = 100, offset: int = 0) -> list[Dict[str, Any]]:
        """
        Get recent updates (messages) received by the bot.

        Useful for discovering chat_id of groups/channels where the bot is added.
        Note: Bot must have received at least one message after being added to a chat.

        Args:
            limit: Maximum number of updates to retrieve (1-100)
            offset: Identifier of the first update to be returned

        Returns:
            List of update dicts with chat info
        """
        try:
            if not self.is_configured:
                return []

            updates = self.bot.get_updates(limit=min(limit, 100), offset=offset)
            result = []

            for update in updates:
                update_data = {"update_id": update.update_id}

                # Extract message info if present
                message = update.message or update.edited_message or update.channel_post
                if message:
                    chat = message.chat
                    update_data["chat"] = {
                        "id": chat.id,
                        "type": chat.type,
                        "title": getattr(chat, "title", None),
                        "username": getattr(chat, "username", None),
                        "first_name": getattr(chat, "first_name", None),
                        "last_name": getattr(chat, "last_name", None),
                    }
                    update_data["message"] = {
                        "message_id": message.message_id,
                        "date": message.date,
                        "text": getattr(message, "text", None),
                    }
                    if message.from_user:
                        update_data["from"] = {
                            "id": message.from_user.id,
                            "username": getattr(message.from_user, "username", None),
                            "first_name": getattr(message.from_user, "first_name", None),
                        }

                result.append(update_data)

            return result
        except Exception as e:
            logger.error(f"Failed to get updates: {e}")
            return []

    def get_chats(self) -> list[Dict[str, Any]]:
        """
        Get unique chats where the bot received messages.

        Convenience method that extracts unique chats from recent updates.
        Use this to discover chat_id for configuration.

        Returns:
            List of unique chat dicts: [{"id": -123, "type": "group", "title": "My Group"}, ...]
        """
        updates = self.get_updates(limit=100)
        seen_ids = set()
        chats = []

        for update in updates:
            chat = update.get("chat")
            if chat and chat["id"] not in seen_ids:
                seen_ids.add(chat["id"])
                chats.append(chat)

        return chats

    # ========== CLASS METHOD SHORTCUTS (backward compatibility) ==========

    @classmethod
    def send_error(cls, error: str, context: Optional[Dict[str, Any]] = None) -> None:
        """Send error notification. See shortcuts.send_error for details."""
        from .shortcuts import send_error
        send_error(error, context)

    @classmethod
    def send_success(cls, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        """Send success notification. See shortcuts.send_success for details."""
        from .shortcuts import send_success
        send_success(message, details)

    @classmethod
    def send_warning(cls, warning: str, context: Optional[Dict[str, Any]] = None) -> None:
        """Send warning notification. See shortcuts.send_warning for details."""
        from .shortcuts import send_warning
        send_warning(warning, context)

    @classmethod
    def send_info(cls, message: str, data: Optional[Dict[str, Any]] = None) -> None:
        """Send info notification. See shortcuts.send_info for details."""
        from .shortcuts import send_info
        send_info(message, data)

    @classmethod
    def send_stats(cls, title: str, stats: Dict[str, Any]) -> None:
        """Send stats notification. See shortcuts.send_stats for details."""
        from .shortcuts import send_stats
        send_stats(title, stats)


__all__ = [
    "DjangoTelegram",
]
