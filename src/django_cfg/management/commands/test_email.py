"""
Test Email Command

Tests email sending functionality using django_cfg configuration.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    """Command to test email functionality."""

    help = "Test email sending functionality"

    def add_arguments(self, parser):
        parser.add_argument(
            "--email",
            type=str,
            help="Email address to send test message to",
            default="markolofsen@gmail.com",
        )
        parser.add_argument(
            "--subject",
            type=str,
            help="Email subject",
            default="Test Email from UnrealON",
        )
        parser.add_argument(
            "--message",
            type=str,
            help="Email message",
            default="This is a test email from UnrealON system.",
        )

    def handle(self, *args, **options):
        email = options["email"]
        subject = options["subject"]
        message = options["message"]

        self.stdout.write(f"🚀 Testing email service for {email}")

        # Create test user if not exists
        user, created = User.objects.get_or_create(
            email=email, defaults={"username": email.split("@")[0], "is_active": True}
        )
        if created:
            self.stdout.write(f"✨ Created test user: {user.username}")

        # Get email service from django-cfg (автоматически настроен!)
        try:
            from django_cfg.modules.django_email import DjangoEmailService
            email_service = DjangoEmailService()
            
            # Показать информацию о backend
            backend_info = email_service.get_backend_info()
            self.stdout.write(f"\n📧 Backend: {backend_info['backend']}")
            self.stdout.write(f"📧 Configured: {backend_info['configured']}")
            
            self.stdout.write("\n📧 Sending test email...")
            
            # Отправить простое письмо (модуль сам знает настройки!)
            result = email_service.send_simple(
                subject=subject,
                message=f"Hello!\n\n{message}\n\nBest regards,\nUnrealON Team",
                recipient_list=[email]
            )
            
            self.stdout.write(self.style.SUCCESS(f"✅ Email sent successfully! Result: {result}"))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Failed to send email: {e}"))