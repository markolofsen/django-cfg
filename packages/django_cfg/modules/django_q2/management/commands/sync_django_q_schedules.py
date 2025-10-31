"""
Management command to sync Django-Q2 schedules from config.

Usage:
    python manage.py sync_django_q_schedules           # Create/update schedules
    python manage.py sync_django_q_schedules --dry-run # Show what would be created
"""
from django.core.management.base import BaseCommand
from django_q.models import Schedule
from django_cfg.core.config import get_current_config


class Command(BaseCommand):
    help = 'Sync Django-Q2 schedules from config to database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be created without actually creating',
        )

    def handle(self, *args, **options):
        config = get_current_config()
        
        if not config:
            self.stdout.write(self.style.ERROR('❌ No config found'))
            return
            
        # Check if Django-Q2 is enabled
        if not hasattr(config, 'django_q2') or not config.django_q2 or not config.django_q2.enabled:
            self.stdout.write(self.style.WARNING('⚠️  Django-Q2 is not enabled in config'))
            return
        
        enabled_schedules = config.django_q2.get_enabled_schedules()
        
        if not enabled_schedules:
            self.stdout.write(self.style.WARNING('⚠️  No schedules found in config'))
            return
        
        self.stdout.write(f'📋 Found {len(enabled_schedules)} schedule(s) in config\n')
        
        created = 0
        updated = 0
        
        for schedule_config in enabled_schedules:
            schedule_dict = schedule_config.to_django_q_format()
            name = schedule_dict['name']
            
            if options['dry_run']:
                self.stdout.write(f'  [DRY RUN] Would create/update: {name}')
                continue
            
            # Update or create schedule
            schedule, created_flag = Schedule.objects.update_or_create(
                name=name,
                defaults=schedule_dict
            )
            
            if created_flag:
                created += 1
                self.stdout.write(self.style.SUCCESS(f'  ✓ Created: {name}'))
            else:
                updated += 1
                self.stdout.write(self.style.SUCCESS(f'  ✓ Updated: {name}'))
        
        if not options['dry_run']:
            self.stdout.write(self.style.SUCCESS(
                f'\n✅ Summary: {created} created, {updated} updated'
            ))
        else:
            self.stdout.write(self.style.WARNING(
                f'\n[DRY RUN] Would create {len(enabled_schedules)} schedule(s)'
            ))
