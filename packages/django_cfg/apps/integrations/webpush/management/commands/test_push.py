"""
Management command to send test push notification.

Usage:
    python manage.py test_push 1 --title "Hello" --body "Test"
    python manage.py test_push 1 2 3  # Send to multiple users
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = 'Send test push notification to user(s)'

    def add_arguments(self, parser):
        parser.add_argument(
            'user_ids',
            nargs='+',
            type=int,
            help='User ID(s) to send notification to'
        )
        parser.add_argument(
            '--title',
            default='Test Notification',
            help='Notification title'
        )
        parser.add_argument(
            '--body',
            default='This is a test notification from Django',
            help='Notification body'
        )
        parser.add_argument(
            '--icon',
            default=None,
            help='Notification icon URL'
        )
        parser.add_argument(
            '--url',
            default='/',
            help='URL to open on click'
        )

    async def handle(self, *args, **options):
        from django_cfg.apps.integrations.webpush import send_push, send_push_to_many

        user_ids = options['user_ids']
        title = options['title']
        body = options['body']
        icon = options['icon']
        url = options['url']

        User = get_user_model()

        self.stdout.write(self.style.SUCCESS(f'Sending to {len(user_ids)} user(s)...'))

        if len(user_ids) == 1:
            # Send to single user
            try:
                user = await User.objects.aget(id=user_ids[0])
                count = await send_push(user, title, body, icon, url)

                if count > 0:
                    self.stdout.write(self.style.SUCCESS(
                        f'✅ Sent to {count} device(s) for user {user.username}'
                    ))
                else:
                    self.stdout.write(self.style.WARNING(
                        f'⚠️  No active subscriptions for user {user.username}'
                    ))

            except User.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'❌ User {user_ids[0]} not found'))

        else:
            # Send to multiple users
            result = await send_push_to_many(user_ids, title, body, icon, url)

            self.stdout.write(self.style.SUCCESS(
                f'✅ Sent to {result["sent"]} device(s) '
                f'({result["failed"]} users had no subscriptions)'
            ))


__all__ = ['Command']
