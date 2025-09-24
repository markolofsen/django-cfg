"""
Dramatiq broker module for django-cfg CLI integration.

This module provides the broker instance required by Dramatiq CLI.
It's a thin wrapper around django_dramatiq.setup with broker export.

Usage:
    dramatiq django_cfg.modules.dramatiq_setup [task_modules...]
"""

# Import django_dramatiq setup (handles Django initialization)
import django_dramatiq.setup

# Re-export the broker for Dramatiq CLI
import dramatiq
broker = dramatiq.get_broker()
