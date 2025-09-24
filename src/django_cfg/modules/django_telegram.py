"""
Django Telegram Service for django_cfg.

Auto-configuring Telegram notification service that integrates with DjangoConfig.
"""

import logging
import time
from typing import Optional, Dict, Any, Union, List, BinaryIO
from enum import Enum
import yaml
from django_cfg.modules import BaseCfgModule
from django_cfg.core.exceptions import ConfigurationError
import telebot

logger = logging.getLogger(__name__)


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
        """Get Telegram configuration information."""
        if not self.is_configured:
            return {
                "configured": False,
                "bot_token": "Not configured",
                "chat_id": "Not configured",
                "enabled": False,
            }

        telegram_config = self.config.telegram
        return {
            "configured": True,
            "bot_token": f"{telegram_config.bot_token[:10]}..." if telegram_config.bot_token else "Not set",
            "chat_id": telegram_config.chat_id or "Not set",
            "enabled": True,  # Always enabled if configured
            "parse_mode": telegram_config.parse_mode or "None",
        }

    def send_message(
        self,
        message: str,
        chat_id: Optional[Union[int, str]] = None,
        parse_mode: Optional[TelegramParseMode] = None,
        disable_notification: bool = False,
        reply_to_message_id: Optional[int] = None,
        fail_silently: bool = False,
    ) -> bool:
        """
        Send a text message to Telegram.

        Args:
            message: Message text to send
            chat_id: Target chat ID (uses config default if not provided)
            parse_mode: Message parse mode (Markdown, HTML, etc.)
            disable_notification: Send silently
            reply_to_message_id: Reply to specific message
            fail_silently: Don't raise exceptions on failure

        Returns:
            True if message sent successfully, False otherwise
        """
        try:
            if not self.is_configured:
                error_msg = "Telegram is not configured"
                logger.error(error_msg)
                if not fail_silently:
                    raise TelegramConfigError(error_msg)
                return False

            telegram_config = self.config.telegram

            # Use provided chat_id or fall back to config
            target_chat_id = chat_id or telegram_config.chat_id
            if not target_chat_id:
                error_msg = "No chat_id provided and none configured"
                logger.error(error_msg)
                if not fail_silently:
                    raise TelegramConfigError(error_msg)
                return False

            # Use provided parse_mode or fall back to config
            target_parse_mode = parse_mode or telegram_config.parse_mode
            
            # Handle both enum and string parse modes
            if target_parse_mode:
                if isinstance(target_parse_mode, TelegramParseMode):
                    parse_mode_str = target_parse_mode.value
                else:
                    # If it's already a string from config, use it directly
                    parse_mode_str = target_parse_mode
            else:
                parse_mode_str = None

            # Send message
            self.bot.send_message(
                chat_id=target_chat_id,
                text=message,
                parse_mode=parse_mode_str,
                disable_notification=disable_notification,
                reply_to_message_id=reply_to_message_id,
            )

            logger.info(f"Telegram message sent successfully to chat {target_chat_id}")
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
    ) -> bool:
        """
        Send a photo to Telegram.

        Args:
            photo: Photo file path, URL, or file-like object
            caption: Photo caption
            chat_id: Target chat ID (uses config default if not provided)
            parse_mode: Caption parse mode
            fail_silently: Don't raise exceptions on failure

        Returns:
            True if photo sent successfully, False otherwise
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
                    # If it's already a string from config, use it directly
                    parse_mode_str = target_parse_mode
            else:
                parse_mode_str = None

            self.bot.send_photo(
                chat_id=target_chat_id,
                photo=photo,
                caption=caption,
                parse_mode=parse_mode_str,
            )

            logger.info(f"Telegram photo sent successfully to chat {target_chat_id}")
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
    ) -> bool:
        """
        Send a document to Telegram.

        Args:
            document: Document file path, URL, or file-like object
            caption: Document caption
            chat_id: Target chat ID (uses config default if not provided)
            parse_mode: Caption parse mode
            fail_silently: Don't raise exceptions on failure

        Returns:
            True if document sent successfully, False otherwise
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
                    # If it's already a string from config, use it directly
                    parse_mode_str = target_parse_mode
            else:
                parse_mode_str = None

            self.bot.send_document(
                chat_id=target_chat_id,
                document=document,
                caption=caption,
                parse_mode=parse_mode_str,
            )

            logger.info(f"Telegram document sent successfully to chat {target_chat_id}")
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
            import yaml

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
            # Final fallback to string representation
            return str(data)

    @classmethod
    def send_error(cls, error: str, context: Optional[Dict[str, Any]] = None) -> None:
        """Send error notification.

        Args:
            error: Error message
            context: Optional context data
        """
        telegram = cls()
        text = f"{cls.EMOJI_MAP['error']} <b>Error</b>\n\n{error}"
        if context:
            text += "\n\n<pre>" + cls._format_to_yaml(context) + "</pre>"
        telegram.send_message(text, parse_mode=TelegramParseMode.HTML)

    @classmethod
    def send_success(cls, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        """Send success notification.

        Args:
            message: Success message
            details: Optional details
        """
        telegram = cls()
        text = f"{cls.EMOJI_MAP['success']} <b>Success</b>\n\n{message}"
        if details:
            text += "\n\n<pre>" + cls._format_to_yaml(details) + "</pre>"
        telegram.send_message(text, parse_mode=TelegramParseMode.HTML)

    @classmethod
    def send_warning(cls, warning: str, context: Optional[Dict[str, Any]] = None) -> None:
        """Send warning notification.

        Args:
            warning: Warning message
            context: Optional context data
        """
        telegram = cls()
        text = f"{cls.EMOJI_MAP['warning']} <b>Warning</b>\n\n{warning}"
        if context:
            text += "\n\n<pre>" + cls._format_to_yaml(context) + "</pre>"
        telegram.send_message(text, parse_mode=TelegramParseMode.HTML)

    @classmethod
    def send_info(cls, message: str, data: Optional[Dict[str, Any]] = None) -> None:
        """Send informational message.

        Args:
            message: Info message
            data: Optional data
        """
        telegram = cls()
        text = f"{cls.EMOJI_MAP['info']} <b>Info</b>\n\n{message}"
        if data:
            text += "\n\n<pre>" + cls._format_to_yaml(data) + "</pre>"
        telegram.send_message(text, parse_mode=TelegramParseMode.HTML)

    @classmethod
    def send_stats(cls, title: str, stats: Dict[str, Any]) -> None:
        """Send statistics data.

        Args:
            title: Stats title
            stats: Statistics data
        """
        telegram = cls()
        text = f"{cls.EMOJI_MAP['stats']} <b>{title}</b>"
        text += "\n\n<pre>" + cls._format_to_yaml(stats) + "</pre>"
        telegram.send_message(text, parse_mode=TelegramParseMode.HTML)


# Convenience functions for direct usage
def send_telegram_message(
    message: str,
    chat_id: Optional[Union[int, str]] = None,
    parse_mode: Optional[TelegramParseMode] = None,
    fail_silently: bool = False,
) -> bool:
    """Send a Telegram message using auto-configured service."""
    telegram = DjangoTelegram()
    return telegram.send_message(
        message=message,
        chat_id=chat_id,
        parse_mode=parse_mode,
        fail_silently=fail_silently,
    )


def send_telegram_photo(
    photo: Union[str, BinaryIO],
    caption: Optional[str] = None,
    chat_id: Optional[Union[int, str]] = None,
    fail_silently: bool = False,
) -> bool:
    """Send a Telegram photo using auto-configured service."""
    telegram = DjangoTelegram()
    return telegram.send_photo(
        photo=photo,
        caption=caption,
        chat_id=chat_id,
        fail_silently=fail_silently,
    )


def send_telegram_document(
    document: Union[str, BinaryIO],
    caption: Optional[str] = None,
    chat_id: Optional[Union[int, str]] = None,
    fail_silently: bool = False,
) -> bool:
    """Send a Telegram document using auto-configured service."""
    telegram = DjangoTelegram()
    return telegram.send_document(
        document=document,
        caption=caption,
        chat_id=chat_id,
        fail_silently=fail_silently,
    )
