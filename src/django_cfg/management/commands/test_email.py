"""
Test Email Command

Tests email sending functionality using django_cfg configuration.
"""

import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.core.mail import send_mail

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
            "--backend",
            type=str,
            choices=["smtp", "console"],
            help="Email backend to use (smtp/console)",
            default="smtp",
        )
        parser.add_argument(
            "--subject",
            type=str,
            help="Email subject",
            default="Test Email from CarAPIS",
        )
        parser.add_argument(
            "--message",
            type=str,
            help="Email message",
            default="This is a test email from CarAPIS system.",
        )

    def handle(self, *args, **options):
        email = options["email"]
        backend = options["backend"]

        # Get email config from toolkit
        email_config = toolkit._result.email
        
        # Override backend for this command
        if backend == "console":
            email_config.email_backend = "console"
        else:
            email_config.email_backend = "smtp"
            
        subject = options["subject"]
        message = options["message"]

        self.stdout.write(f"🚀 Testing email service for {email}")

        # Create test user if not exists
        user, created = User.objects.get_or_create(
            email=email, defaults={"username": email.split("@")[0], "is_active": True}
        )
        if created:
            self.stdout.write(f"✨ Created test user: {user.username}")

        # Get email service from toolkit
        email_service = toolkit.get_email_service()

        # Show current settings
        modules_config = toolkit.get_modules()
        self.stdout.write("\n📧 Email Settings:")
        self.stdout.write(f"Site URL: {modules_config.site_url}")
        self.stdout.write(f"Site Name: {modules_config.site_name}")
        self.stdout.write(f"Logo URL: {modules_config.logo_url}")
        self.stdout.write(f"Default From Email: {modules_config.default_from_email}")

        # Show SMTP settings from toolkit
        email_config = toolkit._result.email
        self.stdout.write("\n📨 SMTP Settings from Toolkit:")
        self.stdout.write(f"Backend: {email_config.backend}")
        self.stdout.write(f"Host: {email_config.host}")
        self.stdout.write(f"Port: {email_config.port}")
        self.stdout.write(f"Username: {email_config.username}")
        self.stdout.write(
            f"Password: {'*' * len(email_config.password) if email_config.password else 'Not set'}"
        )
        self.stdout.write(f"Use TLS: {email_config.use_tls}")
        self.stdout.write(f"Use SSL: {email_config.use_ssl}")
        self.stdout.write(f"Timeout: {email_config.timeout}")
        self.stdout.write(f"Default From: {email_config.default_from}")

        # Send test email
        try:
            self.stdout.write("\n📧 Sending test email...")
            email_service.send_templated_email(
                user=user,
                subject=subject,
                main_text=message,
                main_html_content=f"<h1>Test Email</h1><p>{message}</p>",
                template_name="emails/base_email.html",
                button_text="Visit Dashboard",
                button_url=f"{modules_config.site_url}/dashboard",
                secondary_text="If you received this email, the email service is working correctly.",
                is_async=False,  # Send synchronously for testing
            )
            self.stdout.write(self.style.SUCCESS("✅ Email sent successfully!"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Failed to send email: {e}"))
