"""
Create default admin user for development.

Usage:
    python manage.py create_default_admin
"""

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create default admin user (admin@example.com/admin123)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--email",
            default="admin@example.com",
            help="Admin email (default: admin@example.com)",
        )
        parser.add_argument(
            "--password",
            default="admin123",
            help="Admin password (default: admin123)",
        )

    def handle(self, *args, **options):
        User = get_user_model()
        email = options["email"]
        password = options["password"]

        if User.objects.filter(email=email).exists():
            self.stdout.write(
                self.style.WARNING(f"ℹ️  User {email} already exists. Skipping.")
            )
            return

        user = User.objects.create_user(
            email=email,
            password=password,
            is_staff=True,
            is_superuser=True,
        )

        self.stdout.write(
            self.style.SUCCESS(f"✅ Superuser created: {email} / {password}")
        )
