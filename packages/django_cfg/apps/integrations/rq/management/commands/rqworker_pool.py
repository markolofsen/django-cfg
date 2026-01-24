"""
Django-CFG wrapper for django-rq rqworker-pool command.

Runs multiple RQ workers in a pool for better performance.

Example:
    python manage.py rqworker_pool default --num-workers 4
    python manage.py rqworker_pool high default --num-workers 8
"""

import os
import sys

from django_rq.management.commands.rqworker_pool import Command as DjangoRQWorkerPoolCommand


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


class Command(DjangoRQWorkerPoolCommand):
    """
    Runs a pool of RQ workers for improved throughput.

    Inherits all functionality from django-rq's rqworker-pool command.
    Creates multiple worker processes to handle jobs in parallel.

    Common options:
        --num-workers N      Number of worker processes (default: CPU count)
        --burst              Run in burst mode
        --name NAME          Worker name prefix

    Note: On macOS, OBJC_DISABLE_INITIALIZE_FORK_SAFETY is automatically
    set to prevent fork() crashes with certain libraries (numpy, httpx, etc.)
    """

    help = 'Runs a pool of RQ workers for django-cfg (wrapper for django-rq rqworker-pool)'
