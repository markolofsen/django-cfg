"""
Django-CFG wrapper for django-rq rqstats command.

Displays real-time statistics about RQ queues and workers.

Example:
    python manage.py rqstats
    python manage.py rqstats --interval 5
"""

from django_rq.management.commands.rqstats import Command as DjangoRQStatsCommand


class Command(DjangoRQStatsCommand):
    """
    Displays real-time RQ statistics in terminal.

    Shows:
    - Queue sizes (queued, started, finished, failed)
    - Worker count and status
    - Job processing rates
    - Updates in real-time

    Inherits all functionality from django-rq's rqstats command.

    Common options:
        --interval SECONDS   Update interval (default: 1)
        --raw               Show raw numbers (no colors)
        --only-queues       Show only queue statistics
        --only-workers      Show only worker statistics
    """

    help = 'Shows real-time RQ statistics for django-cfg (wrapper for django-rq rqstats)'
