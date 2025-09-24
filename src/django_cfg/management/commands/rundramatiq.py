"""
Django management command for running Dramatiq workers.

Based on django_dramatiq.management.commands.rundramatiq with Django-CFG integration.
Simple, clean, and working approach.
"""

import argparse
import importlib
import multiprocessing
import os
import sys

from django.apps import apps
from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.module_loading import module_has_submodule

from django_cfg.modules.django_tasks import get_task_service


# Default values
NPROCS = multiprocessing.cpu_count()
NTHREADS = 8


class Command(BaseCommand):
    help = "Run Dramatiq workers with Django-CFG configuration."

    def add_arguments(self, parser):
        parser.formatter_class = argparse.ArgumentDefaultsHelpFormatter
        
        parser.add_argument(
            "--processes", "-p",
            default=NPROCS,
            type=int,
            help="The number of processes to run",
        )
        parser.add_argument(
            "--threads", "-t",
            default=NTHREADS,
            type=int,
            help="The number of threads per process to use",
        )
        parser.add_argument(
            "--queues", "-Q",
            nargs="*",
            type=str,
            help="Listen to a subset of queues, or all when empty",
        )
        parser.add_argument(
            "--watch",
            dest="watch_dir",
            help="Reload workers when changes are detected in the given directory",
        )
        parser.add_argument(
            "--pid-file",
            type=str,
            help="Write the PID of the master process to this file",
        )
        parser.add_argument(
            "--log-file",
            type=str,
            help="Write all logs to a file, or stderr when empty",
        )
        parser.add_argument(
            "--worker-shutdown-timeout", 
            type=int, 
            default=600000,
            help="Timeout for worker shutdown, in milliseconds"
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show configuration without starting workers",
        )

    def handle(self, watch_dir, processes, threads, verbosity, queues, 
               pid_file, log_file, worker_shutdown_timeout, dry_run, **options):
        
        # Get task service and validate
        task_service = get_task_service()
        if not task_service.is_enabled():
            self.stdout.write(
                self.style.ERROR("Task system is not enabled in Django-CFG configuration")
            )
            return
        
        # Discover task modules
        tasks_modules = self._discover_tasks_modules()
        
        # Show configuration info
        self.stdout.write(self.style.SUCCESS("Dramatiq Worker Configuration:"))
        self.stdout.write(f"Processes: {processes}")
        self.stdout.write(f"Threads: {threads}")
        if queues:
            self.stdout.write(f"Queues: {', '.join(queues)}")
        else:
            self.stdout.write("Queues: all")
        
        self.stdout.write(f"\nDiscovered task modules:")
        for module in tasks_modules:
            self.stdout.write(f"  - {module}")
        
        # If dry run, show command and exit
        if dry_run:
            executable_name = "dramatiq"
            process_args = [
                executable_name,
                "--processes", str(processes),
                "--threads", str(threads),
                "--worker-shutdown-timeout", str(worker_shutdown_timeout),
            ]
            
            if watch_dir:
                process_args.extend(["--watch", watch_dir])
            
            verbosity_args = ["-v"] * (verbosity - 1)
            process_args.extend(verbosity_args)
            
            if queues:
                process_args.extend(["--queues"] + queues)
            
            if pid_file:
                process_args.extend(["--pid-file", pid_file])
            
            if log_file:
                process_args.extend(["--log-file", log_file])
            
            # Add task modules (broker module is already first in tasks_modules)
            process_args.extend(tasks_modules)
            
            self.stdout.write(f"\nCommand that would be executed:")
            self.stdout.write(f'  {" ".join(process_args)}')
            return
        
        # Show startup info
        self.stdout.write(self.style.SUCCESS("\nStarting Dramatiq workers..."))
        
        # Build dramatiq command
        executable_name = "dramatiq"
        executable_path = self._resolve_executable(executable_name)
        
        # Build process arguments exactly like django_dramatiq
        process_args = [
            executable_name,
            "--processes", str(processes),
            "--threads", str(threads),
            "--worker-shutdown-timeout", str(worker_shutdown_timeout),
        ]
        
        # Add watch directory if specified
        if watch_dir:
            process_args.extend(["--watch", watch_dir])
        
        # Add verbosity
        verbosity_args = ["-v"] * (verbosity - 1)
        process_args.extend(verbosity_args)
        
        # Add queues if specified
        if queues:
            process_args.extend(["--queues"] + queues)
        
        # Add PID file if specified
        if pid_file:
            process_args.extend(["--pid-file", pid_file])
        
        # Add log file if specified
        if log_file:
            process_args.extend(["--log-file", log_file])
        
        # Add task modules (broker module is already first in tasks_modules)
        process_args.extend(tasks_modules)
        
        self.stdout.write(f'Running dramatiq: "{" ".join(process_args)}"\n')
        
        # Ensure DJANGO_SETTINGS_MODULE is set for worker processes
        if not os.environ.get('DJANGO_SETTINGS_MODULE'):
            if hasattr(settings, 'SETTINGS_MODULE'):
                os.environ['DJANGO_SETTINGS_MODULE'] = settings.SETTINGS_MODULE
            else:
                # Try to detect from manage.py or current settings
                import django
                from django.conf import settings as django_settings
                if hasattr(django_settings, '_wrapped') and hasattr(django_settings._wrapped, '__module__'):
                    module_name = django_settings._wrapped.__module__
                    os.environ['DJANGO_SETTINGS_MODULE'] = module_name
                else:
                    self.stdout.write(
                        self.style.WARNING("Could not detect DJANGO_SETTINGS_MODULE")
                    )
        
        # Use os.execvp like django_dramatiq to preserve environment
        if sys.platform == "win32":
            import subprocess
            command = [executable_path] + process_args[1:]
            sys.exit(subprocess.run(command))
        
        os.execvp(executable_path, process_args)

    def _discover_tasks_modules(self):
        """Discover task modules like django_dramatiq does."""
        # Always include our broker setup module first
        tasks_modules = ["django_cfg.modules.dramatiq_setup"]
        
        # Get task service for configuration
        task_service = get_task_service()
        
        # Try to get task modules from Django-CFG config
        if task_service.config and task_service.config.auto_discover_tasks:
            discovered = task_service.discover_tasks()
            for module_name in discovered:
                self.stdout.write(f"Discovered tasks module: '{module_name}'")
                tasks_modules.append(module_name)
        
        # Fallback: use django_dramatiq discovery logic
        if len(tasks_modules) == 1:  # Only broker module found
            task_module_names = getattr(settings, "DRAMATIQ_AUTODISCOVER_MODULES", ("tasks",))
            
            for app_config in apps.get_app_configs():
                for task_module in task_module_names:
                    if module_has_submodule(app_config.module, task_module):
                        module_name = f"{app_config.name}.{task_module}"
                        try:
                            importlib.import_module(module_name)
                            self.stdout.write(f"Discovered tasks module: '{module_name}'")
                            tasks_modules.append(module_name)
                        except ImportError:
                            # Module exists but has import errors, skip it
                            pass
        
        return tasks_modules

    def _resolve_executable(self, exec_name):
        """Resolve executable path like django_dramatiq does."""
        bin_dir = os.path.dirname(sys.executable)
        if bin_dir:
            for d in [bin_dir, os.path.join(bin_dir, "Scripts")]:
                exec_path = os.path.join(d, exec_name)
                if os.path.isfile(exec_path):
                    return exec_path
        return exec_name