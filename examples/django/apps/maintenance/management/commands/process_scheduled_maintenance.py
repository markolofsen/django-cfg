"""
Management command for processing scheduled maintenance events.

Handles automatic start/stop of scheduled maintenance windows.
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta

from ...services.scheduled_maintenance_service import scheduled_maintenance_service
from ...models import ScheduledMaintenance


class Command(BaseCommand):
    """Process scheduled maintenance events."""
    
    help = 'Process scheduled maintenance events (start due, complete overdue)'
    
    def add_arguments(self, parser):
        """Add command arguments."""
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be processed without making changes'
        )
        
        parser.add_argument(
            '--upcoming',
            type=int,
            default=24,
            help='Show upcoming maintenances within N hours (default: 24)'
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
        
        # Show current status
        self._show_current_status(verbosity)
        
        if not options['dry_run']:
            # Process due maintenances
            self._process_due_maintenances(verbosity)
            
            # Process overdue maintenances
            self._process_overdue_maintenances(verbosity)
        else:
            # Show what would be processed
            self._show_dry_run_info()
        
        # Show upcoming maintenances
        self._show_upcoming_maintenances(options['upcoming'], verbosity)
    
    def _show_current_status(self, verbosity: int):
        """Show current maintenance status."""
        self.stdout.write("\n" + "="*60)
        self.stdout.write(self.style.SUCCESS("📊 SCHEDULED MAINTENANCE STATUS"))
        self.stdout.write("="*60)
        
        # Active maintenances
        active = scheduled_maintenance_service.get_active_maintenances()
        if active:
            self.stdout.write(f"\n🔧 Active Maintenances ({len(active)}):")
            for maintenance in active:
                time_left = ""
                if maintenance['time_until_end']:
                    hours = int(maintenance['time_until_end'] // 3600)
                    minutes = int((maintenance['time_until_end'] % 3600) // 60)
                    time_left = f" ({hours}h {minutes}m remaining)"
                
                overdue = " ⚠️ OVERDUE" if maintenance['is_overdue'] else ""
                
                self.stdout.write(
                    f"   • {maintenance['title']}{time_left}{overdue}"
                )
                if verbosity >= 2:
                    self.stdout.write(f"     Sites: {maintenance['sites_count']}, Priority: {maintenance['priority']}")
        else:
            self.stdout.write("\n✅ No active maintenances")
        
        # Due maintenances
        due = ScheduledMaintenance.get_due_maintenances()
        if due:
            self.stdout.write(f"\n⏰ Due to Start ({due.count()}):")
            for maintenance in due:
                auto_text = " (auto)" if maintenance.auto_enable else " (manual)"
                self.stdout.write(f"   • {maintenance.title}{auto_text}")
                if verbosity >= 2:
                    self.stdout.write(f"     Sites: {maintenance.affected_sites_count}, Scheduled: {maintenance.scheduled_start}")
        
        # Overdue maintenances
        overdue = ScheduledMaintenance.get_overdue_maintenances()
        if overdue:
            self.stdout.write(f"\n⚠️  Overdue to Complete ({overdue.count()}):")
            for maintenance in overdue:
                auto_text = " (auto)" if maintenance.auto_disable else " (manual)"
                self.stdout.write(f"   • {maintenance.title}{auto_text}")
                if verbosity >= 2:
                    overdue_time = timezone.now() - maintenance.scheduled_end
                    hours = int(overdue_time.total_seconds() // 3600)
                    minutes = int((overdue_time.total_seconds() % 3600) // 60)
                    self.stdout.write(f"     Overdue by: {hours}h {minutes}m")
    
    def _process_due_maintenances(self, verbosity: int):
        """Process maintenances that are due to start."""
        self.stdout.write("\n" + "-"*40)
        self.stdout.write("🚀 Processing Due Maintenances")
        self.stdout.write("-"*40)
        
        results = scheduled_maintenance_service.process_due_maintenances()
        
        if results['processed'] == 0:
            self.stdout.write("✅ No due maintenances to process")
            return
        
        self.stdout.write(f"📊 Processed: {results['processed']}")
        self.stdout.write(f"✅ Successful: {results['successful']}")
        
        if results['failed'] > 0:
            self.stdout.write(f"❌ Failed: {results['failed']}")
        
        # Show details
        if verbosity >= 2 and results['details']:
            self.stdout.write("\n📋 Details:")
            for detail in results['details']:
                status = "✅" if detail['success'] else "❌"
                self.stdout.write(f"   {status} {detail['title']}")
                if detail.get('sites_affected'):
                    self.stdout.write(f"      Sites affected: {detail['sites_affected']}")
                if detail.get('error'):
                    self.stdout.write(f"      Error: {detail['error']}")
    
    def _process_overdue_maintenances(self, verbosity: int):
        """Process maintenances that are overdue to complete."""
        self.stdout.write("\n" + "-"*40)
        self.stdout.write("🏁 Processing Overdue Maintenances")
        self.stdout.write("-"*40)
        
        results = scheduled_maintenance_service.process_overdue_maintenances()
        
        if results['processed'] == 0:
            self.stdout.write("✅ No overdue maintenances to process")
            return
        
        self.stdout.write(f"📊 Processed: {results['processed']}")
        self.stdout.write(f"✅ Successful: {results['successful']}")
        
        if results['failed'] > 0:
            self.stdout.write(f"❌ Failed: {results['failed']}")
        
        # Show details
        if verbosity >= 2 and results['details']:
            self.stdout.write("\n📋 Details:")
            for detail in results['details']:
                status = "✅" if detail['success'] else "❌"
                self.stdout.write(f"   {status} {detail['title']}")
                if detail.get('sites_affected'):
                    self.stdout.write(f"      Sites affected: {detail['sites_affected']}")
                if detail.get('actual_duration'):
                    duration_hours = detail['actual_duration'] / 3600
                    self.stdout.write(f"      Duration: {duration_hours:.1f}h")
                if detail.get('error'):
                    self.stdout.write(f"      Error: {detail['error']}")
    
    def _show_dry_run_info(self):
        """Show what would be processed in dry run mode."""
        self.stdout.write("\n" + "-"*40)
        self.stdout.write("🔍 Dry Run - What Would Be Processed")
        self.stdout.write("-"*40)
        
        # Due maintenances
        due = ScheduledMaintenance.get_due_maintenances().filter(auto_enable=True)
        if due:
            self.stdout.write(f"\n🚀 Would start {due.count()} maintenances:")
            for maintenance in due:
                self.stdout.write(f"   • {maintenance.title} ({maintenance.affected_sites_count} sites)")
        
        # Overdue maintenances
        overdue = ScheduledMaintenance.get_overdue_maintenances().filter(auto_disable=True)
        if overdue:
            self.stdout.write(f"\n🏁 Would complete {overdue.count()} maintenances:")
            for maintenance in overdue:
                self.stdout.write(f"   • {maintenance.title} ({maintenance.affected_sites_count} sites)")
        
        if not due and not overdue:
            self.stdout.write("✅ Nothing to process")
    
    def _show_upcoming_maintenances(self, hours: int, verbosity: int):
        """Show upcoming maintenance events."""
        upcoming = scheduled_maintenance_service.get_upcoming_maintenances(hours=hours)
        
        if not upcoming:
            self.stdout.write(f"\n📅 No maintenances scheduled in next {hours} hours")
            return
        
        self.stdout.write(f"\n📅 Upcoming Maintenances (next {hours}h):")
        
        for maintenance in upcoming:
            # Calculate time until start
            time_until = maintenance['time_until_start']
            if time_until:
                hours_until = int(time_until // 3600)
                minutes_until = int((time_until % 3600) // 60)
                time_str = f"in {hours_until}h {minutes_until}m"
            else:
                time_str = "now"
            
            priority_emoji = {
                'low': '🟢',
                'normal': '🟡',
                'high': '🟠',
                'critical': '🔴'
            }.get(maintenance['priority'], '⚪')
            
            auto_text = " (auto)" if maintenance['auto_enable'] else " (manual)"
            
            self.stdout.write(
                f"   {priority_emoji} {maintenance['title']} - {time_str}{auto_text}"
            )
            
            if verbosity >= 2:
                start_time = maintenance['scheduled_start'][:16].replace('T', ' ')
                duration_hours = maintenance['estimated_duration'] / 3600
                self.stdout.write(
                    f"      Start: {start_time}, Duration: {duration_hours:.1f}h, Sites: {maintenance['sites_count']}"
                )
        
        self.stdout.write(f"\n💡 Run with --dry-run to see what would be processed")
        self.stdout.write(f"⏰ Current time: {timezone.now().strftime('%Y-%m-%d %H:%M:%S %Z')}")
