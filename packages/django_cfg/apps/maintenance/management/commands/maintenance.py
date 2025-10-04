"""
Simplified maintenance management command.

Single command instead of 2+ complex commands.
Usage: python manage.py maintenance enable/disable/status/sync domain.com
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from typing import Any, Optional

from ...models import CloudflareSite, MaintenanceLog
from ...services import MaintenanceService


class Command(BaseCommand):
    """Simple maintenance management command."""
    
    help = 'Manage maintenance mode for Cloudflare sites'
    
    def add_arguments(self, parser) -> None:
        """Add command arguments."""
        parser.add_argument(
            'action',
            choices=['enable', 'disable', 'status', 'sync', 'list'],
            help='Action to perform'
        )
        
        parser.add_argument(
            'domain',
            nargs='?',
            help='Domain to operate on (required for enable/disable/status/sync)'
        )
        
        parser.add_argument(
            '--reason',
            default='Maintenance via CLI',
            help='Reason for enabling maintenance (default: "Maintenance via CLI")'
        )
        
        parser.add_argument(
            '--force',
            action='store_true',
            help='Skip confirmation prompts'
        )
        
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed output'
        )
    
    def handle(self, *args: Any, **options: Any) -> None:
        """Handle the command."""
        action = options['action']
        domain = options['domain']
        reason = options['reason']
        force = options['force']
        verbose = options['verbose']
        
        # Validate arguments
        if action in ['enable', 'disable', 'status', 'sync'] and not domain:
            raise CommandError(f"Domain is required for '{action}' action")
        
        try:
            if action == 'list':
                self._handle_list(verbose)
            elif action == 'status':
                self._handle_status(domain, verbose)
            elif action == 'enable':
                self._handle_enable(domain, reason, force, verbose)
            elif action == 'disable':
                self._handle_disable(domain, force, verbose)
            elif action == 'sync':
                self._handle_sync(domain, verbose)
                
        except CloudflareSite.DoesNotExist:
            raise CommandError(f"Site '{domain}' not found. Use 'list' action to see available sites.")
        except Exception as e:
            raise CommandError(f"Operation failed: {str(e)}")
    
    def _handle_list(self, verbose: bool) -> None:
        """List all sites."""
        sites = CloudflareSite.objects.all().order_by('name')
        
        if not sites:
            self.stdout.write(self.style.WARNING("No sites configured"))
            return
        
        self.stdout.write(self.style.SUCCESS(f"Found {sites.count()} sites:"))
        self.stdout.write("")
        
        for site in sites:
            status_style = self.style.WARNING if site.maintenance_active else self.style.SUCCESS
            status_text = "🔧 MAINTENANCE" if site.maintenance_active else "🟢 ACTIVE"
            
            self.stdout.write(f"  {status_style(status_text)} {site.name} ({site.domain})")
            
            if verbose:
                self.stdout.write(f"    Zone ID: {site.zone_id}")
                self.stdout.write(f"    Account ID: {site.account_id}")
                self.stdout.write(f"    Created: {site.created_at.strftime('%Y-%m-%d %H:%M')}")
                if site.last_maintenance_at:
                    self.stdout.write(f"    Last Maintenance: {site.last_maintenance_at.strftime('%Y-%m-%d %H:%M')}")
                
                # Show recent logs
                recent_logs = site.logs.all()[:3]
                if recent_logs:
                    self.stdout.write("    Recent logs:")
                    for log in recent_logs:
                        status_emoji = {
                            MaintenanceLog.Status.SUCCESS: "✅",
                            MaintenanceLog.Status.FAILED: "❌",
                            MaintenanceLog.Status.PENDING: "⏳"
                        }.get(log.status, "❓")
                        
                        self.stdout.write(f"      {status_emoji} {log.get_action_display()} - {log.created_at.strftime('%m-%d %H:%M')}")
                
                self.stdout.write("")
    
    def _handle_status(self, domain: str, verbose: bool) -> None:
        """Show status for specific site."""
        site = CloudflareSite.objects.get(domain=domain)
        
        status_style = self.style.WARNING if site.maintenance_active else self.style.SUCCESS
        status_text = "🔧 MAINTENANCE ACTIVE" if site.maintenance_active else "🟢 ACTIVE"
        
        self.stdout.write(f"Status for {site.name} ({domain}):")
        self.stdout.write(f"  {status_style(status_text)}")
        
        if verbose:
            self.stdout.write(f"  Zone ID: {site.zone_id}")
            self.stdout.write(f"  Account ID: {site.account_id}")
            self.stdout.write(f"  Created: {site.created_at.strftime('%Y-%m-%d %H:%M')}")
            self.stdout.write(f"  Updated: {site.updated_at.strftime('%Y-%m-%d %H:%M')}")
            
            if site.last_maintenance_at:
                self.stdout.write(f"  Last Maintenance: {site.last_maintenance_at.strftime('%Y-%m-%d %H:%M')}")
            
            # Show recent logs
            recent_logs = site.logs.all()[:5]
            if recent_logs:
                self.stdout.write("  Recent activity:")
                for log in recent_logs:
                    status_emoji = {
                        MaintenanceLog.Status.SUCCESS: "✅",
                        MaintenanceLog.Status.FAILED: "❌",
                        MaintenanceLog.Status.PENDING: "⏳"
                    }.get(log.status, "❓")
                    
                    duration_text = f" ({log.duration_seconds}s)" if log.duration_seconds else ""
                    self.stdout.write(f"    {status_emoji} {log.get_action_display()}{duration_text} - {log.created_at.strftime('%Y-%m-%d %H:%M')}")
                    
                    if log.error_message and verbose:
                        self.stdout.write(f"      Error: {log.error_message[:100]}")
    
    def _handle_enable(self, domain: str, reason: str, force: bool, verbose: bool) -> None:
        """Enable maintenance for site."""
        site = CloudflareSite.objects.get(domain=domain)
        
        if site.maintenance_active:
            self.stdout.write(self.style.WARNING(f"Maintenance is already active for {domain}"))
            return
        
        # Confirmation
        if not force:
            confirm = input(f"Enable maintenance for {site.name} ({domain})? [y/N]: ")
            if confirm.lower() not in ['y', 'yes']:
                self.stdout.write("Cancelled")
                return
        
        self.stdout.write(f"Enabling maintenance for {domain}...")
        if verbose:
            self.stdout.write(f"Reason: {reason}")
        
        try:
            with transaction.atomic():
                service = MaintenanceService(site)
                log_entry = service.enable_maintenance(reason)
            
            if log_entry.status == MaintenanceLog.Status.SUCCESS:
                duration_text = f" ({log_entry.duration_seconds}s)" if log_entry.duration_seconds else ""
                self.stdout.write(self.style.SUCCESS(f"✅ Maintenance enabled successfully{duration_text}"))
                
                if verbose and log_entry.cloudflare_response:
                    self.stdout.write("Cloudflare response:")
                    import json
                    self.stdout.write(json.dumps(log_entry.cloudflare_response, indent=2))
            else:
                self.stdout.write(self.style.ERROR(f"❌ Failed to enable maintenance: {log_entry.error_message}"))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error: {str(e)}"))
    
    def _handle_disable(self, domain: str, force: bool, verbose: bool) -> None:
        """Disable maintenance for site."""
        site = CloudflareSite.objects.get(domain=domain)
        
        if not site.maintenance_active:
            self.stdout.write(self.style.WARNING(f"Maintenance is not active for {domain}"))
            return
        
        # Confirmation
        if not force:
            confirm = input(f"Disable maintenance for {site.name} ({domain})? [y/N]: ")
            if confirm.lower() not in ['y', 'yes']:
                self.stdout.write("Cancelled")
                return
        
        self.stdout.write(f"Disabling maintenance for {domain}...")
        
        try:
            with transaction.atomic():
                service = MaintenanceService(site)
                log_entry = service.disable_maintenance()
            
            if log_entry.status == MaintenanceLog.Status.SUCCESS:
                duration_text = f" ({log_entry.duration_seconds}s)" if log_entry.duration_seconds else ""
                self.stdout.write(self.style.SUCCESS(f"✅ Maintenance disabled successfully{duration_text}"))
                
                if verbose and log_entry.cloudflare_response:
                    self.stdout.write("Cloudflare response:")
                    import json
                    self.stdout.write(json.dumps(log_entry.cloudflare_response, indent=2))
            else:
                self.stdout.write(self.style.ERROR(f"❌ Failed to disable maintenance: {log_entry.error_message}"))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error: {str(e)}"))
    
    def _handle_sync(self, domain: str, verbose: bool) -> None:
        """Sync site from Cloudflare."""
        site = CloudflareSite.objects.get(domain=domain)
        
        self.stdout.write(f"Syncing {domain} from Cloudflare...")
        
        try:
            service = MaintenanceService(site)
            log_entry = service.sync_site_from_cloudflare()
            
            if log_entry.status == MaintenanceLog.Status.SUCCESS:
                duration_text = f" ({log_entry.duration_seconds}s)" if log_entry.duration_seconds else ""
                self.stdout.write(self.style.SUCCESS(f"✅ Sync completed successfully{duration_text}"))
                
                if verbose and log_entry.cloudflare_response:
                    response = log_entry.cloudflare_response
                    if 'updated_fields' in response and response['updated_fields']:
                        self.stdout.write(f"Updated fields: {', '.join(response['updated_fields'])}")
                    
                    maintenance_status = response.get('maintenance_active', 'unknown')
                    self.stdout.write(f"Current maintenance status: {maintenance_status}")
                    
                    if verbose:
                        import json
                        self.stdout.write("Full Cloudflare response:")
                        self.stdout.write(json.dumps(response, indent=2))
            else:
                self.stdout.write(self.style.ERROR(f"❌ Sync failed: {log_entry.error_message}"))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error: {str(e)}"))
