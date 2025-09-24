"""
Django management command for checking task system status.

This command provides comprehensive status information about the
Dramatiq task system, including queue statistics, worker status,
and configuration details.
"""

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from typing import Any, Dict, List
import json
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Display comprehensive task system status.
    
    Shows information about:
    - Task system configuration
    - Redis connection status
    - Queue statistics
    - Worker status
    - Discovered task modules
    """
    
    help = "Display task system status and statistics"
    
    def add_arguments(self, parser):
        """Add command line arguments."""
        parser.add_argument(
            "--format",
            choices=["text", "json"],
            default="text",
            help="Output format (default: text)",
        )
        parser.add_argument(
            "--verbose",
            action="store_true",
            help="Show detailed information",
        )
    
    def handle(self, *args, **options):
        """Handle the command execution."""
        try:
            # Import here to avoid issues if dramatiq is not installed
            from django_cfg.modules.django_tasks import get_task_service
            
            # Get task service
            task_service = get_task_service()
            
            # Get comprehensive health status
            status = task_service.get_health_status()
            
            # Format and display output
            if options["format"] == "json":
                self._output_json(status)
            else:
                self._output_text(status, options["verbose"])
                
        except ImportError:
            raise CommandError(
                "Dramatiq dependencies not installed. "
                "Install with: pip install django-cfg[tasks]"
            )
        except Exception as e:
            logger.exception("Failed to get task status")
            raise CommandError(f"Failed to get status: {e}")
    
    def _output_json(self, status: Dict[str, Any]):
        """Output status in JSON format."""
        self.stdout.write(json.dumps(status, indent=2, default=str))
    
    def _output_text(self, status: Dict[str, Any], verbose: bool):
        """Output status in human-readable text format."""
        # Header
        self.stdout.write(
            self.style.SUCCESS("=== Django-CFG Task System Status ===")
        )
        self.stdout.write()
        
        # Basic status
        enabled = status.get("enabled", False)
        if enabled:
            self.stdout.write(
                self.style.SUCCESS("✓ Task system is ENABLED")
            )
        else:
            self.stdout.write(
                self.style.ERROR("✗ Task system is DISABLED")
            )
            return
        
        # Redis connection
        redis_ok = status.get("redis_connection", False)
        if redis_ok:
            self.stdout.write(
                self.style.SUCCESS("✓ Redis connection is OK")
            )
        else:
            self.stdout.write(
                self.style.ERROR("✗ Redis connection FAILED")
            )
        
        # Configuration validation
        config_valid = status.get("configuration_valid", False)
        if config_valid:
            self.stdout.write(
                self.style.SUCCESS("✓ Configuration is VALID")
            )
        else:
            self.stdout.write(
                self.style.ERROR("✗ Configuration is INVALID")
            )
        
        self.stdout.write()
        
        # Configuration details (if verbose)
        if verbose:
            self._show_configuration_details()
        
        # Queue statistics
        queues = status.get("queues", [])
        if queues:
            self.stdout.write(
                self.style.SUCCESS("=== Queue Statistics ===")
            )
            for queue in queues:
                name = queue.get("name", "unknown")
                pending = queue.get("pending", 0)
                running = queue.get("running", 0)
                completed = queue.get("completed", 0)
                failed = queue.get("failed", 0)
                
                self.stdout.write(f"Queue: {name}")
                self.stdout.write(f"  Pending: {pending}")
                self.stdout.write(f"  Running: {running}")
                self.stdout.write(f"  Completed: {completed}")
                self.stdout.write(f"  Failed: {failed}")
                self.stdout.write()
        
        # Worker status
        workers = status.get("workers", [])
        if workers:
            self.stdout.write(
                self.style.SUCCESS("=== Worker Status ===")
            )
            for worker in workers:
                worker_id = worker.get("id", "unknown")
                worker_status = worker.get("status", "unknown")
                current_task = worker.get("current_task")
                processed = worker.get("processed_tasks", 0)
                
                status_style = (
                    self.style.SUCCESS if worker_status == "active" 
                    else self.style.WARNING if worker_status == "idle"
                    else self.style.ERROR
                )
                
                self.stdout.write(f"Worker: {worker_id}")
                self.stdout.write(f"  Status: {status_style(worker_status)}")
                if current_task:
                    self.stdout.write(f"  Current Task: {current_task}")
                self.stdout.write(f"  Processed: {processed}")
                self.stdout.write()
        else:
            self.stdout.write(
                self.style.WARNING("No active workers found")
            )
        
        # Discovered modules
        modules = status.get("discovered_modules", [])
        if modules:
            self.stdout.write(
                self.style.SUCCESS("=== Discovered Task Modules ===")
            )
            for module in modules:
                self.stdout.write(f"  - {module}")
            self.stdout.write()
        else:
            self.stdout.write(
                self.style.WARNING("No task modules discovered")
            )
        
        # Error information
        if "error" in status:
            self.stdout.write(
                self.style.ERROR(f"Error: {status['error']}")
            )
    
    def _show_configuration_details(self):
        """Show detailed configuration information."""
        try:
            from django_cfg.modules.django_tasks import get_task_service
            
            task_service = get_task_service()
            config = task_service.config
            
            if not config:
                self.stdout.write(
                    self.style.WARNING("Configuration not available")
                )
                return
            
            self.stdout.write(
                self.style.SUCCESS("=== Configuration Details ===")
            )
            
            # Basic settings
            self.stdout.write(f"Backend: {config.backend}")
            self.stdout.write(f"Enabled: {config.enabled}")
            self.stdout.write(f"Auto-discover: {config.auto_discover_tasks}")
            self.stdout.write()
            
            # Dramatiq settings
            dramatiq = config.dramatiq
            self.stdout.write("Dramatiq Configuration:")
            self.stdout.write(f"  Redis DB: {dramatiq.redis_db}")
            self.stdout.write(f"  Max Retries: {dramatiq.max_retries}")
            self.stdout.write(f"  Processes: {dramatiq.processes}")
            self.stdout.write(f"  Threads: {dramatiq.threads}")
            self.stdout.write(f"  Queues: {', '.join(dramatiq.queues)}")
            self.stdout.write(f"  Time Limit: {dramatiq.time_limit_seconds}s")
            self.stdout.write(f"  Max Age: {dramatiq.max_age_seconds}s")
            self.stdout.write()
            
            # Worker settings
            worker = config.worker
            self.stdout.write("Worker Configuration:")
            self.stdout.write(f"  Log Level: {worker.log_level}")
            self.stdout.write(f"  Shutdown Timeout: {worker.shutdown_timeout}s")
            self.stdout.write(f"  Health Check: {worker.health_check_enabled}")
            if worker.max_memory_mb:
                self.stdout.write(f"  Memory Limit: {worker.max_memory_mb}MB")
            self.stdout.write()
            
            # Middleware
            if dramatiq.middleware:
                self.stdout.write("Middleware Stack:")
                for middleware in dramatiq.middleware:
                    self.stdout.write(f"  - {middleware}")
                self.stdout.write()
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Failed to show configuration: {e}")
            )
