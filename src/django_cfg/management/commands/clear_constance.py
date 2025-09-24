"""
Clear Constance Command for Django Config Toolkit
Clear Constance configuration cache and database records.
"""

from django.core.management.base import BaseCommand
from django.core.cache import cache
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Clear Constance configuration cache and database records'

    def add_arguments(self, parser):
        parser.add_argument(
            '--cache-only',
            action='store_true',
            help='Clear only cache, not database records'
        )
        parser.add_argument(
            '--db-only',
            action='store_true',
            help='Clear only database records, not cache'
        )
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Skip confirmation prompt'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be cleared without actually clearing'
        )

    def handle(self, *args, **options):
        """Handle the command execution."""
        self.stdout.write(self.style.SUCCESS('🧹 Constance Clear Tool - Django Config Toolkit\n'))
        
        # Check if constance is installed
        if 'constance' not in settings.INSTALLED_APPS:
            self.stdout.write(self.style.ERROR('❌ Constance is not installed or not in INSTALLED_APPS'))
            return
        
        # Determine what to clear
        clear_cache = not options['db_only']
        clear_db = not options['cache_only']
        
        if options['dry_run']:
            self._show_dry_run(clear_cache, clear_db)
            return
        
        # Confirm action
        if not options['confirm']:
            if not self._confirm_clear(clear_cache, clear_db):
                self.stdout.write('Operation cancelled')
                return
        
        # Perform clearing
        self._clear_constance(clear_cache, clear_db)

    def _show_dry_run(self, clear_cache, clear_db):
        """Show what would be cleared in dry run mode."""
        self.stdout.write(self.style.SUCCESS('=== Dry Run - What would be cleared ==='))
        
        if clear_cache:
            self.stdout.write('🗑️  Cache: All Django cache entries')
            self.stdout.write('🗑️  Cache: Constance-specific cache entries')
        
        if clear_db:
            self.stdout.write('🗑️  Database: All Constance configuration records')
            
            # Try to show current records count
            try:
                from django.apps import apps
                Constance = apps.get_model('constance', 'Constance')
                count = Constance.objects.count()
                self.stdout.write(f'    Current records: {count}')
            except Exception as e:
                self.stdout.write(f'    Could not count records: {e}')
        
        self.stdout.write('\n✅ Dry run completed - nothing was actually cleared')

    def _confirm_clear(self, clear_cache, clear_db) -> bool:
        """Confirm the clear operation with user."""
        actions = []
        if clear_cache:
            actions.append('cache')
        if clear_db:
            actions.append('database records')
        
        action_text = ' and '.join(actions)
        
        self.stdout.write(
            self.style.WARNING(f'⚠️  This will clear Constance {action_text}')
        )
        self.stdout.write('This action cannot be undone!')
        
        response = input('Are you sure? [y/N]: ').lower().strip()
        return response in ['y', 'yes']

    def _clear_constance(self, clear_cache, clear_db):
        """Clear Constance cache and/or database records."""
        cleared_items = []
        
        # Clear cache
        if clear_cache:
            try:
                self.stdout.write('🧹 Clearing Django cache...')
                cache.clear()
                self.stdout.write(self.style.SUCCESS('✅ Django cache cleared'))
                cleared_items.append('cache')
                
                # Also try to clear specific constance cache keys
                try:
                    from constance import config as constance_config
                    # Force reload of constance configuration
                    if hasattr(constance_config, '_backend'):
                        constance_config._backend = None
                    self.stdout.write(self.style.SUCCESS('✅ Constance cache backend reset'))
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f'⚠️  Could not reset Constance backend: {e}'))
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'❌ Failed to clear cache: {e}'))
        
        # Clear database records
        if clear_db:
            try:
                self.stdout.write('🗑️  Clearing Constance database records...')
                
                from django.apps import apps
                Constance = apps.get_model('constance', 'Constance')
                
                # Count records before deletion
                count_before = Constance.objects.count()
                self.stdout.write(f'   Found {count_before} Constance records')
                
                if count_before > 0:
                    # Delete all records
                    deleted_info = Constance.objects.all().delete()
                    deleted_count = deleted_info[0] if deleted_info else 0
                    
                    self.stdout.write(self.style.SUCCESS(f'✅ Deleted {deleted_count} Constance records'))
                    cleared_items.append(f'{deleted_count} database records')
                else:
                    self.stdout.write('ℹ️  No Constance records found to delete')
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'❌ Failed to clear database records: {e}'))
        
        # Show summary
        if cleared_items:
            self.stdout.write(
                self.style.SUCCESS(f'\n🎉 Successfully cleared: {", ".join(cleared_items)}')
            )
            self.stdout.write('\n💡 Next steps:')
            self.stdout.write('   1. Restart your Django server')
            self.stdout.write('   2. Visit Django admin to reconfigure settings')
            self.stdout.write('   3. Check that boolean fields now work correctly')
        else:
            self.stdout.write(self.style.WARNING('⚠️  Nothing was cleared'))

    def _show_current_status(self):
        """Show current Constance status."""
        self.stdout.write(self.style.SUCCESS('\n📊 Current Constance Status:'))
        
        # Check database records
        try:
            from django.apps import apps
            Constance = apps.get_model('constance', 'Constance')
            db_count = Constance.objects.count()
            self.stdout.write(f'   Database records: {db_count}')
            
            if db_count > 0:
                self.stdout.write('   Recent records:')
                for record in Constance.objects.all()[:5]:
                    self.stdout.write(f'     - {record.key}: {record.value}')
                if db_count > 5:
                    self.stdout.write(f'     ... and {db_count - 5} more')
        except Exception as e:
            self.stdout.write(f'   Database: Error - {e}')
        
        # Check cache
        try:
            from django.core.cache import cache
            # Try to get a test key to see if cache is working
            test_key = 'constance_test_key'
            cache.set(test_key, 'test_value', 1)
            test_result = cache.get(test_key)
            
            if test_result:
                self.stdout.write('   Cache: Working')
            else:
                self.stdout.write('   Cache: Not working or empty')
        except Exception as e:
            self.stdout.write(f'   Cache: Error - {e}')
