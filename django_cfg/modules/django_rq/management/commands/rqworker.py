"""
Django-CFG wrapper for django-rq rqworker command.

This is a simple proxy that inherits all functionality from django-rq's rqworker.
Allows running: python manage.py rqworker [queues]

Example:
    python manage.py rqworker default
    python manage.py rqworker high default low
    python manage.py rqworker default --with-scheduler
"""

from django_cfg.modules.django_rq.fork_safety import fix_macos_fork_safety, prepare_forking_worker

# Before any import that might initialise ObjC.
fix_macos_fork_safety()

from django_rq.management.commands.rqworker import Command as DjangoRQWorkerCommand  # noqa: E402


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

    Every job runs in a forked work horse, so the worker runs without the
    psycopg pool and a child never reuses its parent's connection — see
    ``django_cfg.modules.django_rq.fork_safety``. On macOS,
    OBJC_DISABLE_INITIALIZE_FORK_SAFETY is set to prevent fork() crashes.
    """

    help = 'Runs RQ workers for django-cfg (wrapper for django-rq rqworker)'

    def handle(self, *args, **options):
        prepare_forking_worker()
        return super().handle(*args, **options)
