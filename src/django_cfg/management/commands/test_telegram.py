"""
Test Telegram Command

Tests Telegram notification functionality using django_cfg configuration.
"""

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Command to test Telegram functionality."""
    help = "Test Telegram notification functionality"

    def add_arguments(self, parser):
        parser.add_argument(
            "--message",
            type=str,
            help="Message to send",
            default="Test message from UnrealON"
        )

    def handle(self, *args, **options):
        message = options["message"]

        self.stdout.write("🚀 Testing Telegram notification service")

        # Get telegram service from django-cfg (автоматически настроен!)
        try:
            from django_cfg.modules.django_telegram import DjangoTelegram
            telegram_service = DjangoTelegram()
            
            self.stdout.write("\n📱 Sending test messages...")

            # Send info message (модуль сам знает настройки!)
            self.stdout.write("\n1️⃣ Sending info message...")
            telegram_service.send_info(
                message,
                {
                    "Type": "System Test",
                    "Status": "Running", 
                    "Environment": "Development"
                }
            )
            self.stdout.write(self.style.SUCCESS("✅ Info message sent!"))

            # Send success message
            self.stdout.write("\n2️⃣ Sending success message...")
            telegram_service.send_success(
                "Test completed successfully!",
                {"Message": message}
            )
            self.stdout.write(self.style.SUCCESS("✅ Success message sent!"))

            self.stdout.write(self.style.SUCCESS("\n✅ All test messages sent successfully!"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"\n❌ Failed to send Telegram messages: {e}"))