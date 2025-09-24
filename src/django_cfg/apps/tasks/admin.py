"""
Admin interface for Dramatiq task management.

Provides web interface for starting workers, checking queue status,
and clearing queues with AJAX endpoints and interactive buttons.
"""

import logging
import subprocess
import sys
from typing import Dict, Any

from django.db.models import Count            
from django.contrib import admin
from django.contrib.admin.views.main import ChangeList
from django.http import JsonResponse
from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from unfold.admin import ModelAdmin

try:
    from django_dramatiq.models import Task
    from django_dramatiq.admin import TaskAdmin as BaseDramatiqTaskAdmin
except ImportError:
    Task = None
    BaseDramatiqTaskAdmin = None

from ...modules.django_tasks import DjangoTasks


class TaskQueueChangeList(ChangeList):
    """Custom changelist for task queue management."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tasks_service = DjangoTasks()


class TaskQueueAdmin(ModelAdmin):
    """
    Enhanced admin for Dramatiq task management.
    
    Provides buttons for:
    - Starting/stopping workers
    - Checking queue status
    - Clearing queues
    - Viewing task statistics
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(__name__)
        self.tasks_service = DjangoTasks()
    
    def get_urls(self):
        """Add custom URLs for task management."""
        urls = super().get_urls()
        custom_urls = [
            path('queue-status/', csrf_exempt(self.queue_status_view), name='dramatiq_queue_status'),
            path('start-workers/', csrf_exempt(self.start_workers_view), name='dramatiq_start_workers'),
            path('clear-queues/', csrf_exempt(self.clear_queues_view), name='dramatiq_clear_queues'),
            path('task-stats/', csrf_exempt(self.task_stats_view), name='dramatiq_task_stats'),
        ]
        return custom_urls + urls
    
    def queue_status_view(self, request):
        """Get queue status and statistics."""
        if request.method != 'GET':
            return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)
        
        try:
            # Get queue status using tasks service
            status_data = self._get_queue_status()
            
            return JsonResponse({
                'success': True,
                'data': status_data
            })
            
        except Exception as e:
            self.logger.error(f"Queue status check failed: {e}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    def start_workers_view(self, request):
        """Start Dramatiq workers."""
        if request.method != 'POST':
            return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)
        
        try:
            # Get parameters from request
            processes = int(request.POST.get('processes', 2))
            threads = int(request.POST.get('threads', 8))
            queues = request.POST.get('queues', '')
            
            # Validate parameters
            if processes < 1 or processes > 16:
                return JsonResponse({
                    'success': False,
                    'error': 'Processes must be between 1 and 16'
                }, status=400)
            
            if threads < 1 or threads > 32:
                return JsonResponse({
                    'success': False,
                    'error': 'Threads must be between 1 and 32'
                }, status=400)
            
            # Build command
            cmd = [sys.executable, 'manage.py', 'rundramatiq']
            cmd.extend(['--processes', str(processes)])
            cmd.extend(['--threads', str(threads)])
            
            if queues:
                cmd.extend(['--queues', queues])
            
            # Start workers in background
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=None  # Use current working directory
            )
            
            return JsonResponse({
                'success': True,
                'message': f'Started {processes} worker processes with {threads} threads each',
                'pid': process.pid,
                'command': ' '.join(cmd)
            })
            
        except Exception as e:
            self.logger.error(f"Start workers failed: {e}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    def clear_queues_view(self, request):
        """Clear Dramatiq queues."""
        if request.method != 'POST':
            return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)
        
        try:
            # Get parameters
            queue_name = request.POST.get('queue', '')
            failed_only = request.POST.get('failed_only', 'false').lower() == 'true'
            
            # Build command
            cmd = [sys.executable, 'manage.py', 'task_clear', '--confirm']
            
            if queue_name:
                cmd.extend(['--queue', queue_name])
            
            if failed_only:
                cmd.append('--failed-only')
            
            # Execute command
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return JsonResponse({
                    'success': True,
                    'message': 'Queues cleared successfully',
                    'output': result.stdout
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': result.stderr or 'Clear command failed'
                }, status=500)
                
        except subprocess.TimeoutExpired:
            return JsonResponse({
                'success': False,
                'error': 'Clear operation timed out'
            }, status=500)
        except Exception as e:
            self.logger.error(f"Clear queues failed: {e}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    def task_stats_view(self, request):
        """Get task statistics."""
        if request.method != 'GET':
            return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)
        
        try:
            # Get task statistics using tasks service
            stats_data = self._get_task_statistics()
            
            return JsonResponse({
                'success': True,
                'data': stats_data
            })
            
        except Exception as e:
            self.logger.error(f"Task stats failed: {e}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    def _get_queue_status(self) -> Dict[str, Any]:
        """Get current queue status."""
        try:
            # Use tasks service to get Redis connection
            redis_client = self.tasks_service.get_redis_client()
            
            if not redis_client:
                return {
                    'error': 'Redis connection not available',
                    'queues': {},
                    'workers': 0
                }
            
            # Get queue information
            queues_info = {}
            config = self.tasks_service.config
            
            if config and config.dramatiq and config.dramatiq.queues:
                for queue_name in config.dramatiq.queues:
                    queue_key = f"dramatiq:default.DQ.{queue_name}"
                    queue_length = redis_client.llen(queue_key)
                    
                    # Get failed queue length
                    failed_key = f"dramatiq:default.DQ.{queue_name}.failed"
                    failed_length = redis_client.llen(failed_key)
                    
                    queues_info[queue_name] = {
                        'pending': queue_length,
                        'failed': failed_length,
                        'total': queue_length + failed_length
                    }
            
            # Get worker information (simplified)
            worker_keys = redis_client.keys("dramatiq:worker:*")
            active_workers = len(worker_keys) if worker_keys else 0
            
            return {
                'queues': queues_info,
                'workers': active_workers,
                'redis_connected': True,
                'timestamp': self.tasks_service._get_current_timestamp()
            }
            
        except Exception as e:
            self.logger.error(f"Queue status error: {e}")
            return {
                'error': str(e),
                'queues': {},
                'workers': 0,
                'redis_connected': False
            }
    
    def _get_task_statistics(self) -> Dict[str, Any]:
        """Get task execution statistics."""
        try:
            if not Task:
                return {'error': 'django_dramatiq not available'}
            
            
            stats = Task.tasks.aggregate(
                total=Count('id'),
                # Add more aggregations as needed
            )
            
            # Get recent tasks
            recent_tasks = list(
                Task.tasks.order_by('-created_at')[:10]
                .values('actor_name', 'status', 'created_at', 'updated_at')
            )
            
            return {
                'statistics': stats,
                'recent_tasks': recent_tasks,
                'timestamp': self.tasks_service._get_current_timestamp()
            }
            
        except Exception as e:
            self.logger.error(f"Task statistics error: {e}")
            return {'error': str(e)}


# Register the enhanced admin if django_dramatiq is available
if Task and BaseDramatiqTaskAdmin:
    # Unregister the default admin
    admin.site.unregister(Task)
    
    # Register our enhanced admin
    @admin.register(Task)
    class EnhancedTaskAdmin(TaskQueueAdmin, BaseDramatiqTaskAdmin):
        """Enhanced Task admin with queue management buttons."""
        
        def get_changelist(self, request, **kwargs):
            """Use custom changelist."""
            return TaskQueueChangeList
        
        def changelist_view(self, request, extra_context=None):
            """Add extra context for queue management."""
            extra_context = extra_context or {}
            
            # Add queue status to context
            try:
                queue_status = self._get_queue_status()
                extra_context['queue_status'] = queue_status
            except Exception as e:
                self.logger.error(f"Failed to get queue status: {e}")
                extra_context['queue_status'] = {'error': str(e)}
            
            return super().changelist_view(request, extra_context)
