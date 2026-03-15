"""
Django-CFG wrapper for django-rq rqscheduler command.

Runs the RQ scheduler daemon for scheduled/periodic jobs.

Before starting:
1. Cleans up stale scheduler locks from crashed processes
2. Registers scheduled jobs from django-cfg config

Example:
    python manage.py rqscheduler
    python manage.py rqscheduler --queue high
"""

from django_rq.management.commands.rqscheduler import Command as DjangoRQSchedulerCommand


class Command(DjangoRQSchedulerCommand):
    """
    Runs the RQ scheduler daemon.

    The scheduler handles:
    - Scheduled jobs (enqueue at specific time)
    - Periodic jobs (cron-like scheduling)
    - Delayed job execution

    Before starting, this command:
    1. Cleans up stale scheduler locks (rq:scheduler_instance:*) from
       previous crashed scheduler processes
    2. Registers scheduled jobs from django-cfg config (RQScheduleConfig)

    This ensures only one process (the scheduler) registers jobs,
    preventing race conditions when multiple containers start simultaneously.

    Inherits all functionality from django-rq's rqscheduler command.

    Common options:
        --queue QUEUE        Queue to schedule jobs on (default: 'default')
        --interval SECONDS   Polling interval (default: 1)
        --pid FILE          Write PID to file

    IMPORTANT: rqscheduler only processes jobs for ONE queue.
    If your scheduled tasks use queue="high", you MUST run:
        python manage.py rqscheduler --queue high
    """

    help = 'Runs RQ scheduler daemon for django-cfg (wrapper for django-rq rqscheduler)'

    def handle(self, *args, **options):
        """Handle command execution with lock cleanup and schedule registration."""
        self._cleanup_stale_scheduler_locks()
        self._register_schedules()
        super().handle(*args, **options)

    def _cleanup_stale_scheduler_locks(self):
        """
        Clean up stale rq-scheduler locks from Redis.

        rq-scheduler uses Redis keys like 'rq:scheduler_instance:*' to
        track running scheduler instances. If a scheduler crashes without
        proper cleanup, these keys remain and block new schedulers from
        acquiring the lock.

        This method removes all such keys before starting the scheduler.
        """
        try:
            from django_rq import get_connection

            conn = get_connection()
            keys = conn.keys('rq:scheduler_instance:*')

            if keys:
                deleted = conn.delete(*keys)
                self.stdout.write(
                    self.style.WARNING(
                        f'Cleaned up {deleted} stale scheduler lock(s) from Redis'
                    )
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS('No stale scheduler locks found')
                )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Failed to cleanup scheduler locks: {e}')
            )

    def _register_schedules(self):
        """
        Register scheduled jobs from django-cfg config.

        This is called only by rqscheduler command to prevent race conditions
        when multiple containers (django, rq-worker, rq-scheduler) start
        simultaneously. Only the scheduler should register jobs.

        Reads schedules from config.django_rq.schedules and registers them
        with deterministic job IDs to prevent duplicates.
        """
        try:
            from django_cfg.apps.integrations.rq.services import register_schedules_from_config
            register_schedules_from_config()
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Failed to register schedules: {e}')
            )
