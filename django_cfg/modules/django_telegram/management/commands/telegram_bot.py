"""
Telegram Bot Management Command.

Manage Telegram bot: get info, discover chats, send messages.

Usage:
    python manage.py telegram_bot info                          # Bot info
    python manage.py telegram_bot chats                         # List chats (need to message bot first)
    python manage.py telegram_bot send "Hello!" --chat_id=-123  # Send message
    python manage.py telegram_bot test                          # Interactive test
    python manage.py telegram_bot --bot_token=XXX chats         # Use custom bot token
"""

import json

from django.core.management.base import BaseCommand

from django_cfg.modules.django_telegram import DjangoTelegram, TelegramParseMode


class Command(BaseCommand):
    help = "Telegram bot management: info, chats, send messages"

    def add_arguments(self, parser):
        parser.add_argument(
            "action",
            choices=["info", "chats", "send", "test"],
            help="Action: info, chats, send, test",
        )
        parser.add_argument(
            "message",
            nargs="?",
            default=None,
            help="Message to send (for 'send' action)",
        )
        parser.add_argument(
            "--bot_token",
            type=str,
            default=None,
            help="Custom bot token (overrides config)",
        )
        parser.add_argument(
            "--chat_id",
            type=str,
            default=None,
            help="Target chat ID",
        )

    def handle(self, *args, **options):
        action = options["action"]
        bot_token = options["bot_token"]
        chat_id = options["chat_id"]

        telegram = DjangoTelegram(bot_token=bot_token, chat_id=chat_id)

        if action == "info":
            self._show_info(telegram)
        elif action == "chats":
            self._show_chats(telegram)
        elif action == "send":
            self._send_message(telegram, options["message"], chat_id)
        elif action == "test":
            self._send_test(telegram, chat_id)

    def _show_info(self, telegram: DjangoTelegram):
        """Show bot info."""
        self.stdout.write("=" * 50)
        self.stdout.write("Bot Info:")
        self.stdout.write("=" * 50)

        bot_info = telegram.get_me()
        if bot_info:
            self.stdout.write(json.dumps(bot_info, indent=2, default=str))
        else:
            self.stdout.write(self.style.ERROR("Bot not configured or invalid token"))

        self.stdout.write("\nQueue Stats:")
        stats = telegram.get_queue_stats()
        self.stdout.write(json.dumps(stats, indent=2))

    def _show_chats(self, telegram: DjangoTelegram):
        """Show available chats."""
        self.stdout.write("=" * 50)
        self.stdout.write("Available Chats:")
        self.stdout.write("=" * 50)
        self.stdout.write(self.style.WARNING("(Send a message to the bot first!)\n"))

        chats = telegram.get_chats()
        if chats:
            for chat in chats:
                chat_type = chat.get("type", "unknown")
                title = chat.get("title") or chat.get("first_name") or "N/A"
                username = chat.get("username")

                self.stdout.write(f"  ID: {self.style.SUCCESS(str(chat['id']))}")
                self.stdout.write(f"  Type: {chat_type}")
                self.stdout.write(f"  Title: {title}")
                if username:
                    self.stdout.write(f"  Username: @{username}")
                self.stdout.write("")
        else:
            self.stdout.write(self.style.WARNING("No chats found."))
            self.stdout.write("Send a message to the bot in Telegram first!")

    def _send_message(self, telegram: DjangoTelegram, message: str, chat_id: str = None):
        """Send a message."""
        if not message:
            self.stdout.write(self.style.ERROR('Message required: telegram_bot send "Your message"'))
            return

        if not chat_id and not telegram._custom_chat_id:
            try:
                config_chat_id = telegram._resolve_chat_id()
                if not config_chat_id:
                    self.stdout.write(self.style.ERROR("No chat_id. Use --chat_id=XXX"))
                    return
            except Exception:
                self.stdout.write(self.style.ERROR("No chat_id configured. Use --chat_id=XXX"))
                return

        telegram.send_message(
            message=message,
            chat_id=chat_id,
            parse_mode=TelegramParseMode.HTML,
            fail_silently=False,
        )
        self.stdout.write(self.style.SUCCESS("Message queued!"))

        import time
        time.sleep(0.5)
        self.stdout.write(self.style.SUCCESS("Sent!"))

    def _send_test(self, telegram: DjangoTelegram, chat_id: str = None):
        """Send test message with chat_id info."""
        target_chat_id = chat_id or telegram._resolve_chat_id()

        if not target_chat_id:
            chats = telegram.get_chats()
            if not chats:
                self.stdout.write(self.style.ERROR("No chat_id and no chats found."))
                self.stdout.write("Use --chat_id=XXX or send a message to the bot first.")
                return

            self.stdout.write("Select chat:")
            for i, chat in enumerate(chats):
                title = chat.get("title") or chat.get("first_name", "Unknown")
                self.stdout.write(f"  [{i}] {title} (ID: {chat['id']})")

            try:
                choice = input("\nEnter number: ")
                if choice.isdigit() and int(choice) < len(chats):
                    target_chat_id = chats[int(choice)]["id"]
                else:
                    return
            except (EOFError, KeyboardInterrupt):
                return

        message = f"<b>Test from DjangoTelegram</b>\n\nChat ID: <code>{target_chat_id}</code>"
        telegram.send_message(
            message=message,
            chat_id=target_chat_id,
            parse_mode=TelegramParseMode.HTML,
            fail_silently=False,
        )

        import time
        time.sleep(0.5)

        self.stdout.write(self.style.SUCCESS(f"\nTest sent to {target_chat_id}"))
        self.stdout.write(f"\nUse in config:")
        self.stdout.write(self.style.WARNING(f'  chat_id = "{target_chat_id}"'))
