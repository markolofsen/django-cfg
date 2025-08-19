"""
Test Telegram Command

Tests Telegram notification functionality using the ModulesConfig and toolkit.
"""

from django.core.management.base import BaseCommand
from api.settings import toolkit


class Command(BaseCommand):
    """Command to test Telegram functionality."""
    help = "Test Telegram notification functionality"

    def add_arguments(self, parser):
        parser.add_argument(
            "--message",
            type=str,
            help="Message to send",
            default="Test message from Django-Cfg"
        )

    def handle(self, *args, **options):
        message = options["message"]

        self.stdout.write("🚀 Testing Telegram notification service")

        # Get Telegram notifier from toolkit
        telegram = toolkit.get_telegram_notifier()

        # Show current settings
        modules_config = toolkit.get_modules()
        self.stdout.write("\n📱 Telegram Settings:")
        self.stdout.write(f"Bot Token: {modules_config.telegram_bot_token[:10]}..." if modules_config.telegram_bot_token else "Bot Token: Not set")
        self.stdout.write(f"Group ID: {modules_config.telegram_group_id}")
        self.stdout.write(f"Enabled: {modules_config.telegram_enabled}")
        self.stdout.write(f"Retry Delay: {modules_config.telegram_retry_delay}")
        self.stdout.write(f"Max Retries: {modules_config.telegram_max_retries}")

        # Send test messages
        try:
            self.stdout.write("\n📱 Sending test messages...")

            # Send info message
            self.stdout.write("\n1️⃣ Sending info message...")
            telegram.send_info(
                message,
                {
                    "Type": "System Test",
                    "Status": "Running",
                    "Time": "Now",
                    "Site": modules_config.site_url,
                }
            )
            self.stdout.write(self.style.SUCCESS("✅ Info message sent!"))

            # Send success message
            self.stdout.write("\n2️⃣ Sending success message...")
            telegram.send_success(
                "Test completed successfully!",
                {
                    "Message": message,
                    "Duration": "1s",
                }
            )
            self.stdout.write(self.style.SUCCESS("✅ Success message sent!"))

            # Send warning message
            self.stdout.write("\n3️⃣ Sending warning message...")
            telegram.send_warning(
                "This is a test warning",
                {
                    "Source": "Test Command",
                    "Level": "Low",
                }
            )
            self.stdout.write(self.style.SUCCESS("✅ Warning message sent!"))

            # Send error message
            self.stdout.write("\n4️⃣ Sending error message...")
            telegram.send_error(
                "This is a test error",
                {
                    "Source": "Test Command",
                    "Level": "High",
                }
            )
            self.stdout.write(self.style.SUCCESS("✅ Error message sent!"))

            # Send stats message
            self.stdout.write("\n5️⃣ Sending stats message...")
            telegram.send_stats(
                "Test Statistics",
                {
                    "Total Tests": 5,
                    "Passed": 5,
                    "Failed": 0,
                    "Duration": "5s",
                }
            )
            self.stdout.write(self.style.SUCCESS("✅ Stats message sent!"))

            self.stdout.write(self.style.SUCCESS("\n✅ All test messages sent successfully!"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"\n❌ Failed to send Telegram messages: {e}"))
