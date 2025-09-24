"""
Django management command for clearing task queues.

This command provides utilities for clearing failed tasks,
specific queues, or all tasks from the Dramatiq system.
"""

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from typing import Any, Optional, List
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Clear tasks from Dramatiq queues.
    
    Provides options to:
    - Clear all tasks from specific queues
    - Clear only failed tasks
    - Clear all tasks from all queues
    """
    
    help = "Clear tasks from Dramatiq queues"
    
    def add_arguments(self, parser):
        """Add command line arguments."""
        parser.add_argument(
            "--queue",
            type=str,
            help="Specific queue to clear (default: all queues)",
        )
        parser.add_argument(
            "--failed-only",
            action="store_true",
            help="Clear only failed tasks",
        )
        parser.add_argument(
            "--confirm",
            action="store_true",
            help="Skip confirmation prompt",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be cleared without actually clearing",
        )
    
    def handle(self, *args, **options):
        """Handle the command execution."""
        try:
            # Import here to avoid issues if dramatiq is not installed
            from django_cfg.modules.django_tasks import get_task_service
            
            # Get task service
            task_service = get_task_service()
            
            # Check if task system is enabled
            if not task_service.is_enabled():
                raise CommandError(
                    "Task system is not enabled. "
                    "Please configure 'tasks' in your Django-CFG configuration."
                )
            
            # Get task manager
            manager = task_service.manager
            if not manager:
                raise CommandError("Task manager not available")
            
            # Get configuration
            config = task_service.config
            if not config:
                raise CommandError("Task configuration not available")
            
            # Determine queues to clear
            if options.get("queue"):
                queues_to_clear = [options["queue"]]
                # Validate queue exists
                if options["queue"] not in config.get_effective_queues():
                    self.stdout.write(
                        self.style.WARNING(
                            f"Queue '{options['queue']}' not in configured queues: "
                            f"{', '.join(config.get_effective_queues())}"
                        )
                    )
            else:
                queues_to_clear = config.get_effective_queues()
            
            # Show what will be cleared
            self._show_clear_plan(queues_to_clear, options)
            
            if options["dry_run"]:
                self.stdout.write(
                    self.style.SUCCESS("Dry run completed - no tasks were cleared")
                )
                return
            
            # Confirm action
            if not options["confirm"]:
                if not self._confirm_clear(queues_to_clear, options):
                    self.stdout.write("Operation cancelled")
                    return
            
            # Perform clearing
            self._clear_queues(manager, queues_to_clear, options)
            
        except ImportError:
            raise CommandError(
                "Dramatiq dependencies not installed. "
                "Install with: pip install django-cfg[tasks]"
            )
        except Exception as e:
            logger.exception("Failed to clear tasks")
            raise CommandError(f"Failed to clear tasks: {e}")
    
    def _show_clear_plan(self, queues: List[str], options):
        """Show what will be cleared."""
        self.stdout.write(
            self.style.SUCCESS("=== Clear Plan ===")
        )
        
        if options.get("failed_only"):
            self.stdout.write("Action: Clear FAILED tasks only")
        else:
            self.stdout.write("Action: Clear ALL tasks")
        
        self.stdout.write(f"Queues: {', '.join(queues)}")
        
        # Get current queue statistics
        try:
            from django_cfg.modules.django_tasks import get_task_service
            task_service = get_task_service()
            manager = task_service.manager
            
            if manager:
                queue_stats = manager.get_queue_stats()
                
                self.stdout.write("\nCurrent Queue Statistics:")
                for stat in queue_stats:
                    if stat["name"] in queues:
                        name = stat["name"]
                        pending = stat.get("pending", 0)
                        failed = stat.get("failed", 0)
                        
                        if options.get("failed_only"):
                            self.stdout.write(f"  {name}: {failed} failed tasks")
                        else:
                            total = pending + stat.get("running", 0) + failed
                            self.stdout.write(f"  {name}: {total} total tasks")
        except Exception as e:
            self.stdout.write(f"Could not get queue statistics: {e}")
        
        self.stdout.write()
    
    def _confirm_clear(self, queues: List[str], options) -> bool:
        """Confirm the clear operation with user."""
        if options.get("failed_only"):
            action = "clear FAILED tasks"
        else:
            action = "clear ALL tasks"
        
        queue_list = ", ".join(queues)
        
        self.stdout.write(
            self.style.WARNING(
                f"This will {action} from queues: {queue_list}"
            )
        )
        
        response = input("Are you sure? [y/N]: ").lower().strip()
        return response in ["y", "yes"]
    
    def _clear_queues(self, manager, queues: List[str], options):
        """Clear the specified queues."""
        cleared_count = 0
        
        self.stdout.write(
            self.style.SUCCESS("Starting queue clearing...")
        )
        
        for queue_name in queues:
            try:
                self.stdout.write(f"Clearing queue: {queue_name}")
                
                if options.get("failed_only"):
                    # Clear only failed tasks
                    # TODO: Implement failed task clearing
                    # This would require specific Dramatiq broker methods
                    count = 0  # Placeholder
                    self.stdout.write(f"  Cleared {count} failed tasks")
                else:
                    # Clear all tasks
                    success = manager.clear_queue(queue_name)
                    if success:
                        # TODO: Get actual count of cleared tasks
                        count = 0  # Placeholder
                        self.stdout.write(f"  Cleared {count} tasks")
                        cleared_count += count
                    else:
                        self.stdout.write(
                            self.style.ERROR(f"  Failed to clear queue: {queue_name}")
                        )
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"  Error clearing queue {queue_name}: {e}")
                )
        
        if cleared_count > 0:
            self.stdout.write(
                self.style.SUCCESS(f"Successfully cleared {cleared_count} tasks")
            )
        else:
            self.stdout.write(
                self.style.WARNING("No tasks were cleared")
            )
