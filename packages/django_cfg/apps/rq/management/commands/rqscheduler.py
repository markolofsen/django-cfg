"""
Django-CFG wrapper for django-rq rqscheduler command.

Runs the RQ scheduler daemon for scheduled/periodic jobs.

Example:
    python manage.py rqscheduler
    python manage.py rqscheduler --queue default
"""

from django_rq.management.commands.rqscheduler import Command as DjangoRQSchedulerCommand


class Command(DjangoRQSchedulerCommand):
    """
    Runs the RQ scheduler daemon.

    The scheduler handles:
    - Scheduled jobs (enqueue at specific time)
    - Periodic jobs (cron-like scheduling)
    - Delayed job execution

    Inherits all functionality from django-rq's rqscheduler command.

    Common options:
        --queue QUEUE        Queue to schedule jobs on (default: 'default')
        --interval SECONDS   Polling interval (default: 1)
        --pid FILE          Write PID to file
    """

    help = 'Runs RQ scheduler daemon for django-cfg (wrapper for django-rq rqscheduler)'
