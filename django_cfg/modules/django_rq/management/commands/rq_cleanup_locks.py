"""
Clean up stale RQ scheduler locks from Redis.

rq-scheduler uses Redis keys 'rq:scheduler_instance:*' to track running
scheduler instances. If a scheduler crashes without proper cleanup, these
keys remain and block new schedulers from acquiring the lock.

Example:
    python manage.py rq_cleanup_locks
    python manage.py rq_cleanup_locks --dry-run
"""

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    Clean up stale rq-scheduler locks from Redis.

    Use this command if rq-scheduler fails to start due to stale locks
    from previous crashed scheduler processes.

    Options:
        --dry-run    Show what would be deleted without actually deleting
    """

    help = 'Clean up stale rq-scheduler locks from Redis'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting',
        )

    def handle(self, *args, **options):
        """Handle command execution."""
        dry_run = options.get('dry_run', False)

        try:
            from django_rq import get_connection

            conn = get_connection()
            keys = conn.keys('rq:scheduler_instance:*')

            if not keys:
                self.stdout.write(
                    self.style.SUCCESS('No stale scheduler locks found')
                )
                return

            self.stdout.write(f'Found {len(keys)} scheduler lock(s):')
            for key in keys:
                key_str = key.decode() if isinstance(key, bytes) else key
                self.stdout.write(f'  - {key_str}')

            if dry_run:
                self.stdout.write(
                    self.style.WARNING(
                        f'\nDry run: would delete {len(keys)} key(s)'
                    )
                )
            else:
                deleted = conn.delete(*keys)
                self.stdout.write(
                    self.style.SUCCESS(
                        f'\nDeleted {deleted} stale scheduler lock(s)'
                    )
                )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Failed to cleanup scheduler locks: {e}')
            )
            raise
