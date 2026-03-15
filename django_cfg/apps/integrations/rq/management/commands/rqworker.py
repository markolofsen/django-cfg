"""
Django-CFG wrapper for django-rq rqworker command.

This is a simple proxy that inherits all functionality from django-rq's rqworker.
Allows running: python manage.py rqworker [queues]

Example:
    python manage.py rqworker default
    python manage.py rqworker high default low
    python manage.py rqworker default --with-scheduler
"""

import os
import sys

from django_rq.management.commands.rqworker import Command as DjangoRQWorkerCommand


def _fix_macos_fork_safety():
    """
    Fix macOS fork() safety issue with Objective-C runtime.

    On macOS Big Sur+, fork() after ObjC initialization causes crashes.
    Libraries like numpy, httpx, ML frameworks trigger this.

    Setting OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES disables the check.
    This is safe for RQ workers as they don't share ObjC state.

    Only applied on macOS (darwin).
    """
    if sys.platform == "darwin":
        if "OBJC_DISABLE_INITIALIZE_FORK_SAFETY" not in os.environ:
            os.environ["OBJC_DISABLE_INITIALIZE_FORK_SAFETY"] = "YES"


# Apply fix before any imports that might initialize ObjC
_fix_macos_fork_safety()


class Command(DjangoRQWorkerCommand):
    """
    Runs RQ workers on specified queues.

    Inherits all functionality from django-rq's rqworker command.
    See django-rq documentation for available options.

    Common options:
        --burst              Run in burst mode (exit when queue is empty)
        --with-scheduler     Run worker with embedded scheduler
        --name NAME          Custom worker name
        --worker-ttl SEC     Worker timeout (default: 420)
        --sentry-dsn DSN     Report exceptions to Sentry

    Note: On macOS, OBJC_DISABLE_INITIALIZE_FORK_SAFETY is automatically
    set to prevent fork() crashes with certain libraries (numpy, httpx, etc.)
    """

    help = 'Runs RQ workers for django-cfg (wrapper for django-rq rqworker)'
