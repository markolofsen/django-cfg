"""
Django-CFG wrapper for django-rq rqscheduler command.

Runs the RQ scheduler daemon for scheduled/periodic jobs.
Automatically cleans up stale scheduler locks before starting.

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

    Automatically cleans up stale scheduler locks (rq:scheduler_instance:*)
    from previous crashed scheduler processes before starting.

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
        """Handle command execution with automatic lock cleanup."""
        self._cleanup_stale_scheduler_locks()
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
