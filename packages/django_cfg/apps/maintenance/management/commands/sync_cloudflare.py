"""
Management command for syncing sites with Cloudflare zones.

Automatically discovers and syncs Cloudflare zones with Django models.
"""

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from typing import Optional

from ...models import CloudflareApiKey
from ...services.site_sync_service import SiteSyncService


class Command(BaseCommand):
    """Sync sites with Cloudflare zones."""
    
    help = 'Sync CloudflareSite models with actual Cloudflare zones'
    
    def add_arguments(self, parser):
        """Add command arguments."""
        parser.add_argument(
            '--api-key',
            type=str,
            help='Name of specific API key to sync (default: all active keys)'
        )
        
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be changed without making changes'
        )
        
        parser.add_argument(
            '--force-update',
            action='store_true',
            help='Update existing sites even if they haven\'t changed'
        )
        
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Enable verbose output'
        )
    
    def handle(self, *args, **options):
        """Handle the command execution."""
        verbosity = 2 if options['verbose'] else 1
        
        if options['dry_run']:
            self.stdout.write(
                self.style.WARNING('🔍 DRY RUN MODE - No changes will be made')
            )
        
        # Get API keys to sync
        if options['api_key']:
            try:
                api_keys = [CloudflareApiKey.objects.get(
                    name=options['api_key'],
                    is_active=True
                )]
                self.stdout.write(f"📡 Syncing specific API key: {options['api_key']}")
            except CloudflareApiKey.DoesNotExist:
                raise CommandError(f"API key '{options['api_key']}' not found or inactive")
        else:
            api_keys = CloudflareApiKey.objects.filter(is_active=True)
            self.stdout.write(f"📡 Syncing all {api_keys.count()} active API keys")
        
        if not api_keys:
            self.stdout.write(
                self.style.WARNING('⚠️  No active API keys found')
            )
            return
        
        # Sync each API key
        total_stats = {
            'discovered': 0,
            'created': 0,
            'updated': 0,
            'skipped': 0,
            'errors': 0
        }
        
        for api_key in api_keys:
            self.stdout.write(f"\n🔑 Processing API key: {api_key.name}")
            
            try:
                sync_service = SiteSyncService(api_key)
                stats = sync_service.sync_zones(
                    force_update=options['force_update'],
                    dry_run=options['dry_run']
                )
                
                # Update totals
                for key in total_stats:
                    total_stats[key] += stats[key]
                
                # Display results for this API key
                self._display_api_key_results(api_key.name, stats, verbosity)
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'❌ Failed to sync {api_key.name}: {e}')
                )
                total_stats['errors'] += 1
        
        # Display overall summary
        self._display_summary(total_stats, options['dry_run'])
    
    def _display_api_key_results(self, api_key_name: str, stats: dict, verbosity: int):
        """Display results for a single API key."""
        if stats['errors'] > 0:
            self.stdout.write(
                self.style.ERROR(
                    f"   ❌ {stats['errors']} errors occurred"
                )
            )
        
        if stats['created'] > 0:
            action = "Would create" if stats.get('dry_run') else "Created"
            self.stdout.write(
                self.style.SUCCESS(
                    f"   ✅ {action} {stats['created']} new sites"
                )
            )
        
        if stats['updated'] > 0:
            action = "Would update" if stats.get('dry_run') else "Updated"
            self.stdout.write(
                self.style.SUCCESS(
                    f"   🔄 {action} {stats['updated']} existing sites"
                )
            )
        
        if stats['skipped'] > 0:
            self.stdout.write(
                self.style.WARNING(
                    f"   ⏭️  Skipped {stats['skipped']} sites (no changes)"
                )
            )
        
        # Verbose output - show individual sites
        if verbosity >= 2 and stats.get('sites'):
            self.stdout.write("   📋 Site details:")
            for site_info in stats['sites']:
                if site_info['action'] == 'created':
                    self.stdout.write(f"      ➕ Created: {site_info['domain']}")
                elif site_info['action'] == 'updated':
                    self.stdout.write(f"      🔄 Updated: {site_info['domain']}")
                elif site_info['action'] == 'would_create':
                    self.stdout.write(f"      ➕ Would create: {site_info['domain']}")
                elif site_info['action'] == 'would_update':
                    self.stdout.write(f"      🔄 Would update: {site_info['domain']}")
                    if 'changes' in site_info:
                        for field, change in site_info['changes'].items():
                            self.stdout.write(
                                f"         • {field}: {change['old']} → {change['new']}"
                            )
                elif site_info['action'] == 'error':
                    self.stdout.write(
                        self.style.ERROR(
                            f"      ❌ Error: {site_info['domain']} - {site_info['error']}"
                        )
                    )
    
    def _display_summary(self, stats: dict, dry_run: bool):
        """Display overall summary."""
        self.stdout.write("\n" + "="*50)
        self.stdout.write(
            self.style.SUCCESS("📊 SYNC SUMMARY") if not dry_run 
            else self.style.WARNING("📊 DRY RUN SUMMARY")
        )
        self.stdout.write("="*50)
        
        if stats['discovered'] > 0:
            self.stdout.write(f"🔍 Zones discovered: {stats['discovered']}")
        
        if stats['created'] > 0:
            action = "Would be created" if dry_run else "Created"
            self.stdout.write(
                self.style.SUCCESS(f"✅ Sites {action.lower()}: {stats['created']}")
            )
        
        if stats['updated'] > 0:
            action = "Would be updated" if dry_run else "Updated"
            self.stdout.write(
                self.style.SUCCESS(f"🔄 Sites {action.lower()}: {stats['updated']}")
            )
        
        if stats['skipped'] > 0:
            self.stdout.write(f"⏭️  Sites skipped: {stats['skipped']}")
        
        if stats['errors'] > 0:
            self.stdout.write(
                self.style.ERROR(f"❌ Errors: {stats['errors']}")
            )
        
        total_processed = stats['created'] + stats['updated'] + stats['skipped']
        if total_processed > 0:
            self.stdout.write(f"\n📈 Total sites processed: {total_processed}")
        
        if dry_run and (stats['created'] > 0 or stats['updated'] > 0):
            self.stdout.write(
                self.style.WARNING(
                    "\n💡 Run without --dry-run to apply these changes"
                )
            )
        
        self.stdout.write(f"⏰ Completed at: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}")
