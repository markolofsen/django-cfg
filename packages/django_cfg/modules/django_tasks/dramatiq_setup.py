"""
Dramatiq broker module for django-cfg CLI integration.

This module provides the broker instance required by Dramatiq CLI.
It's a thin wrapper around django_dramatiq.setup with broker export.

Usage:
    dramatiq django_cfg.modules.dramatiq_setup [task_modules...]
"""

# CRITICAL: Initialize Django BEFORE any model imports in worker processes
import django

# Initialize Django app registry (DJANGO_SETTINGS_MODULE must be set by caller)
django.setup()

# Re-export the broker for Dramatiq CLI
import dramatiq

broker = dramatiq.get_broker()
