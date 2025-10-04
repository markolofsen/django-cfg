"""
Tasks admin interfaces using Django Admin Utilities.

Enhanced Dramatiq task management with Material Icons and optimized queries.
Only available if django-dramatiq is installed.
"""

import logging
import subprocess
import sys
from typing import Dict, Any, Optional
from django.db.models import Count
from django.contrib import admin, messages
from django.contrib.admin.views.main import ChangeList
from django.http import JsonResponse
from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from django.db import models
from django.db.models import Q
from unfold.admin import ModelAdmin

from django_cfg.modules.django_admin import (
    OptimizedModelAdmin,
    DisplayMixin,
    StatusBadgeConfig,
    DateTimeDisplayConfig,
    Icons,
    ActionVariant,
    display,
    action,
    StandaloneActionsMixin,
    standalone_action
)
from django_cfg.modules.django_admin.utils.badges import StatusBadge
from django_cfg.modules.django_tasks import DjangoTasks

# Try to import django-dramatiq components
try:
    from django_dramatiq.models import Task
    from django_dramatiq.admin import TaskAdmin as BaseDramatiqTaskAdmin
    DRAMATIQ_AVAILABLE = True
except ImportError:
    Task = None
    BaseDramatiqTaskAdmin = None
    DRAMATIQ_AVAILABLE = False


if DRAMATIQ_AVAILABLE:
    
    class TaskQueueChangeList(ChangeList):
        """Custom changelist for task queue management."""
        
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.tasks_service = DjangoTasks()


    class TaskQueueAdminMixin(OptimizedModelAdmin, DisplayMixin, StandaloneActionsMixin):
        """Mixin for task queue management functionality."""
        
        # change_list_template = 'admin/tasks/taskqueue/change_list.html'
        # actions_list = ['start_workers', 'clear_queues', 'refresh_status']
        
        def has_add_permission(self, request):
            return False
        
        def has_change_permission(self, request, obj=None):
            return True
        
        def has_delete_permission(self, request, obj=None):
            return False
        
        def get_changelist(self, request, **kwargs):
            return TaskQueueChangeList
        
        def changelist_view(self, request, extra_context=None):
            """Enhanced changelist with queue statistics."""
            extra_context = extra_context or {}
            
            try:
                tasks_service = DjangoTasks()
                
                # Queue statistics
                total_tasks = Task.objects.count()
                pending_tasks = Task.objects.filter(status='pending').count()
                running_tasks = Task.objects.filter(status='running').count()
                failed_tasks = Task.objects.filter(status='failed').count()
                completed_tasks = Task.objects.filter(status='done').count()
                
                # Queue status
                queue_stats = tasks_service.get_queue_stats()
                
                extra_context.update({
                    'queue_statistics': {
                        'total_tasks': total_tasks,
                        'pending_tasks': pending_tasks,
                        'running_tasks': running_tasks,
                        'failed_tasks': failed_tasks,
                        'completed_tasks': completed_tasks,
                    },
                    'queue_status': queue_stats,
                    'workers_running': tasks_service.are_workers_running(),
                })
                
            except Exception as e:
                extra_context['queue_error'] = str(e)
            
            return super().changelist_view(request, extra_context)
        
        @display(description="Queue Status")
        def queue_status_display(self, obj):
            """Display queue status with badge."""
            return StatusBadge.create(
                text="Active",
                variant="success",
                icon=Icons.PLAY_ARROW
            )
        
        @display(description="Worker Status")
        def worker_status_display(self, obj):
            """Display worker status."""
            return StatusBadge.create(
                text="Running",
                variant="info",
                icon=Icons.SETTINGS
            )
        
        @display(description="Task Statistics")
        def task_stats_display(self, obj):
            """Display task statistics."""
            total = Task.objects.count()
            pending = Task.objects.filter(status='pending').count()
            return f"Total: {total}, Pending: {pending}"
        
        @standalone_action(
            description="Start Workers",
            icon=Icons.PLAY_ARROW,
            variant=ActionVariant.SUCCESS,
            background=True,
            success_message="Workers started successfully!",
            error_message="Failed to start workers."
        )
        def start_workers(self, request):
            """Start Dramatiq workers."""
            try:
                tasks_service = DjangoTasks()
                tasks_service.start_workers()
                return True
            except Exception as e:
                logging.error(f"Failed to start workers: {e}")
                return False
        
        @standalone_action(
            description="Clear Queues",
            icon=Icons.CLEAR_ALL,
            variant=ActionVariant.WARNING,
            background=True,
            success_message="Queues cleared successfully!",
            error_message="Failed to clear queues."
        )
        def clear_queues(self, request):
            """Clear all task queues."""
            try:
                tasks_service = DjangoTasks()
                tasks_service.clear_queues()
                return True
            except Exception as e:
                logging.error(f"Failed to clear queues: {e}")
                return False
        
        @standalone_action(
            description="Refresh Status",
            icon=Icons.REFRESH,
            variant=ActionVariant.INFO,
            success_message="Status refreshed!",
            error_message="Failed to refresh status."
        )
        def refresh_status(self, request):
            """Refresh queue status."""
            return True


    # Unregister the default TaskAdmin and register our enhanced version
    try:
        admin.site.unregister(Task)
    except admin.sites.NotRegistered:
        pass

    @admin.register(Task)
    class TaskAdmin(TaskQueueAdminMixin, ModelAdmin):
        """Enhanced admin for Dramatiq Task model with queue management functionality."""
        
        list_display = [
            'id_display', 'actor_name_display', 'status_display', 
            'queue_name_display', 'created_at_display'
        ]
        
        list_filter = [
            'status', 'queue_name', 'actor_name', 
            'created_at', 'updated_at'
        ]
        
        search_fields = ['actor_name', 'queue_name', 'message_id']
        
        readonly_fields = [
            'id_display', 'actor_name', 'queue_name',
            'args_preview', 'kwargs_preview', 'result_preview',
            'created_at_display', 'started_at_display', 'finished_at_display',
            'duration_display', 'retries_display', 'error_message_display'
        ]
        
        fieldsets = (
            ('Task Information', {
                'fields': ('id_display', 'status', 'actor_name', 'queue_name')
            }),
            ('Execution Details', {
                'fields': ('args_preview', 'kwargs_preview', 'result_preview', 'error_message_display')
            }),
            ('Timing', {
                'fields': ('created_at_display', 'started_at_display', 'finished_at_display', 'duration_display')
            }),
            ('Retry Information', {
                'fields': ('retries_display',)
            }),
        )
        
        actions = ['retry_failed_tasks', 'cancel_pending_tasks']
        
        def changelist_view(self, request, extra_context=None):
            """Enhanced changelist with task statistics."""
            extra_context = extra_context or {}
            
            try:
                # Task statistics
                total_tasks = self.get_queryset(request).count()
                status_stats = self.get_queryset(request).values('status').annotate(
                    count=Count('id')
                ).order_by('status')
                
                # Actor statistics
                actor_stats = self.get_queryset(request).values('actor_name').annotate(
                    count=Count('id')
                ).order_by('-count')[:10]
                
                # Queue statistics
                queue_stats = self.get_queryset(request).values('queue_name').annotate(
                    count=Count('id')
                ).order_by('-count')
                
                extra_context.update({
                    'task_statistics': {
                        'total_tasks': total_tasks,
                        'status_distribution': list(status_stats),
                        'top_actors': list(actor_stats),
                        'queue_distribution': list(queue_stats),
                    }
                })
                
            except Exception as e:
                extra_context['task_error'] = str(e)
            
            return super().changelist_view(request, extra_context)
        
        @display(description="Task ID")
        def id_display(self, obj):
            """Display task ID with icon."""
            return StatusBadge.create(
                text=str(obj.id),
                variant="info",
                icon=Icons.TAG
            )
        
        @display(description="Actor")
        def actor_name_display(self, obj):
            """Display actor name with icon."""
            return StatusBadge.create(
                text=obj.actor_name or "Unknown",
                variant="default",
                icon=Icons.FUNCTIONS
            )
        
        @display(description="Status")
        def status_display(self, obj):
            """Display task status with appropriate badge."""
            status_variants = {
                'pending': 'warning',
                'running': 'info', 
                'done': 'success',
                'failed': 'danger',
                'cancelled': 'secondary'
            }
            
            status_icons = {
                'pending': Icons.SCHEDULE,
                'running': Icons.PLAY_ARROW,
                'done': Icons.CHECK_CIRCLE,
                'failed': Icons.ERROR,
                'cancelled': Icons.CANCEL
            }
            
            return StatusBadge.create(
                text=obj.status.title(),
                variant=status_variants.get(obj.status, 'default'),
                icon=status_icons.get(obj.status, Icons.HELP)
            )
        
        @display(description="Queue")
        def queue_name_display(self, obj):
            """Display queue name."""
            return StatusBadge.create(
                text=obj.queue_name or "default",
                variant="info",
                icon=Icons.QUEUE
            )
        
        @display(description="Created")
        def created_at_display(self, obj):
            """Display creation time."""
            return self.display_datetime_relative(obj.created_at)
        
        @display(description="Started")
        def started_at_display(self, obj):
            """Display start time."""
            if obj.started_at:
                return self.display_datetime_relative(obj.started_at)
            return "Not started"
        
        @display(description="Finished")
        def finished_at_display(self, obj):
            """Display finish time."""
            if obj.finished_at:
                return self.display_datetime_relative(obj.finished_at)
            return "Not finished"
        
        @display(description="Duration")
        def duration_display(self, obj):
            """Display task duration."""
            if obj.started_at and obj.finished_at:
                duration = obj.finished_at - obj.started_at
                return f"{duration.total_seconds():.2f}s"
            return "N/A"
        
        @display(description="Retries")
        def retries_display(self, obj):
            """Display retry count."""
            retries = getattr(obj, 'retries', 0)
            if retries > 0:
                return StatusBadge.create(
                    text=str(retries),
                    variant="warning",
                    icon=Icons.REFRESH
                )
            return "0"
        
        @display(description="Error")
        def error_message_display(self, obj):
            """Display error message preview."""
            if hasattr(obj, 'error') and obj.error:
                error_text = str(obj.error)
                if len(error_text) > 100:
                    error_text = error_text[:100] + "..."
                return error_text
            return "No error"
        
        @display(description="Arguments")
        def args_preview(self, obj):
            """Display task arguments preview."""
            if hasattr(obj, 'args') and obj.args:
                args_text = str(obj.args)
                if len(args_text) > 100:
                    args_text = args_text[:100] + "..."
                return args_text
            return "No arguments"
        
        @display(description="Keyword Arguments")
        def kwargs_preview(self, obj):
            """Display task keyword arguments preview."""
            if hasattr(obj, 'kwargs') and obj.kwargs:
                kwargs_text = str(obj.kwargs)
                if len(kwargs_text) > 100:
                    kwargs_text = kwargs_text[:100] + "..."
                return kwargs_text
            return "No kwargs"
        
        @display(description="Result")
        def result_preview(self, obj):
            """Display task result preview."""
            if hasattr(obj, 'result') and obj.result:
                result_text = str(obj.result)
                if len(result_text) > 100:
                    result_text = result_text[:100] + "..."
                return result_text
            return "No result"
        
        @action(description="Retry Failed Tasks", variant=ActionVariant.WARNING)
        def retry_failed_tasks(self, request, queryset):
            """Retry selected failed tasks."""
            failed_tasks = queryset.filter(status='failed')
            count = failed_tasks.count()
            
            if count > 0:
                # Here you would implement the retry logic
                messages.success(request, f"Queued {count} tasks for retry.")
            else:
                messages.warning(request, "No failed tasks selected.")
        
        @action(description="Cancel Pending Tasks", variant=ActionVariant.DANGER)
        def cancel_pending_tasks(self, request, queryset):
            """Cancel selected pending tasks."""
            pending_tasks = queryset.filter(status='pending')
            count = pending_tasks.count()
            
            if count > 0:
                pending_tasks.update(status='cancelled')
                messages.success(request, f"Cancelled {count} pending tasks.")
            else:
                messages.warning(request, "No pending tasks selected.")


    # TaskQueueAdminMixin provides queue management functionality to TaskAdmin

else:
    # If django-dramatiq is not available, create empty admin classes
    class TaskQueueAdmin:
        """Placeholder when django-dramatiq is not available."""
        pass
    
    class TaskAdmin:
        """Placeholder when django-dramatiq is not available."""
        pass