"""
Check Settings Command for Django Config Toolkit
Comprehensive validation of Django settings and configuration.
"""

import os
import sys
from pathlib import Path
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
import questionary
from datetime import datetime

from django_cfg import ConfigToolkit


class Command(BaseCommand):
    help = "Comprehensive validation of Django settings and configuration"

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        self.print_all_settings()

    def print_all_settings(self):
        """Print all Django settings"""
        self.stdout.write(self.style.SUCCESS("\n📋 Django Settings Dump:\n"))

        # Print AUTH_USER_MODEL
        self.stdout.write(self.style.SUCCESS("\n👤 AUTH_USER_MODEL:"))
        if hasattr(settings, "AUTH_USER_MODEL"):
            self.stdout.write(f"  ✅ AUTH_USER_MODEL = {settings.AUTH_USER_MODEL}")
        else:
            self.stdout.write(self.style.ERROR("  ❌ AUTH_USER_MODEL is not set"))

        # Print INSTALLED_APPS
        self.stdout.write(self.style.SUCCESS("\n📦 INSTALLED_APPS:"))
        if hasattr(settings, "INSTALLED_APPS"):
            for app in settings.INSTALLED_APPS:
                self.stdout.write(f"  - {app}")
        else:
            self.stdout.write(self.style.ERROR("  ❌ INSTALLED_APPS is not set"))

        # Print ALLOWED_HOSTS
        self.stdout.write(self.style.SUCCESS("\n🌐 ALLOWED_HOSTS:"))
        if hasattr(settings, "ALLOWED_HOSTS"):
            self.stdout.write(f"  ✅ ALLOWED_HOSTS = {settings.ALLOWED_HOSTS}")
        else:
            self.stdout.write(self.style.ERROR("  ❌ ALLOWED_HOSTS is not set"))

        # Print DATABASES
        self.stdout.write(self.style.SUCCESS("\n🗄️ DATABASES:"))
        if hasattr(settings, "DATABASES"):
            for db_name, db_config in settings.DATABASES.items():
                engine = db_config.get("ENGINE", "Unknown")
                name = db_config.get("NAME", "Unknown")
                self.stdout.write(f"  - {db_name}: {engine} - {name}")
        else:
            self.stdout.write(self.style.ERROR("  ❌ DATABASES is not set"))

        # Print DEBUG
        self.stdout.write(self.style.SUCCESS("\n🐞 DEBUG:"))
        if hasattr(settings, "DEBUG"):
            self.stdout.write(f"  ✅ DEBUG = {settings.DEBUG}")
        else:
            self.stdout.write(self.style.ERROR("  ❌ DEBUG is not set"))

        # Print EMAIL settings
        self.stdout.write(self.style.SUCCESS("\n📧 EMAIL Settings:"))
        email_settings = {
            "EMAIL_BACKEND": getattr(settings, "EMAIL_BACKEND", None),
            "EMAIL_HOST": getattr(settings, "EMAIL_HOST", None),
            "EMAIL_PORT": getattr(settings, "EMAIL_PORT", None),
            "EMAIL_HOST_USER": getattr(settings, "EMAIL_HOST_USER", None),
            "EMAIL_HOST_PASSWORD": (
                getattr(settings, "EMAIL_HOST_PASSWORD", "***")
                if hasattr(settings, "EMAIL_HOST_PASSWORD")
                else None
            ),
            "DEFAULT_FROM_EMAIL": getattr(settings, "DEFAULT_FROM_EMAIL", None),
        }
        for key, value in email_settings.items():
            if value is not None:
                self.stdout.write(f"  ✅ {key} = {value}")
            else:
                self.stdout.write(self.style.WARNING(f"  ⚠️ {key} is not set"))
