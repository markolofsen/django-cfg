"""
Tasks Admin v2.0 - NEW Declarative Pydantic Approach

Enhanced Dramatiq task management with Material Icons and auto-generated displays.
"""

import logging
from django.contrib import admin, messages
from django.contrib.admin.views.main import ChangeList
from django.db.models import Count

from django_cfg.modules.django_admin import (
    ActionConfig,
    AdminConfig,
    BadgeField,
    DateTimeField,
    FieldsetConfig,
    Icons,
)
from django_cfg.modules.django_admin.base import PydanticAdmin
from django_cfg.modules.django_tasks import DjangoTasks
from .actions import retry_failed_tasks, cancel_pending_tasks

try:
    from django_dramatiq.admin import TaskAdmin as BaseDramatiqTaskAdmin
    from django_dramatiq.models import Task
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

    task_config = AdminConfig(
        model=Task,
        list_display=["id", "actor_name", "status", "queue_name", "created_at"],
        display_fields=[
            BadgeField(name="id", title="Task ID", variant="info", icon=Icons.TAG),
            BadgeField(name="actor_name", title="Actor", variant="secondary", icon=Icons.FUNCTIONS, empty_value="Unknown"),
            BadgeField(name="status", title="Status", label_map={
                "pending": "warning", "running": "info", "done": "success",
                "failed": "danger", "cancelled": "secondary"
            }),
            BadgeField(name="queue_name", title="Queue", variant="info", icon=Icons.QUEUE, empty_value="default"),
            DateTimeField(name="created_at", title="Created", ordering="created_at"),
        ],
        search_fields=["actor_name", "queue_name", "message_id"],
        list_filter=["status", "queue_name", "actor_name", "created_at", "updated_at"],
        readonly_fields=["id", "actor_name", "queue_name", "args_preview", "kwargs_preview",
                        "result_preview", "created_at", "duration_display", "retries_display", "error_message_display"],
        fieldsets=[
            FieldsetConfig(title="Task Information", fields=["status", "actor_name", "queue_name"]),
            FieldsetConfig(title="Execution Details", fields=["args_preview", "kwargs_preview", "result_preview", "error_message_display"]),
            FieldsetConfig(title="Timing", fields=["created_at", "duration_display"]),
            FieldsetConfig(title="Retry Information", fields=["retries_display"]),
        ],
        actions=[
            ActionConfig(name="retry_failed_tasks", description="Retry failed tasks",
                        variant="warning", handler=retry_failed_tasks),
            ActionConfig(name="cancel_pending_tasks", description="Cancel pending tasks",
                        variant="danger", handler=cancel_pending_tasks),
        ],
        ordering=["-created_at"],
    )

    try:
        admin.site.unregister(Task)
    except admin.sites.NotRegistered:
        pass

    @admin.register(Task)
    class TaskAdmin(PydanticAdmin):
        """Enhanced admin for Dramatiq Task model."""
        config = task_config
        
        def has_add_permission(self, request):
            return False
        
        def has_delete_permission(self, request, obj=None):
            return False
        
        def get_changelist(self, request, **kwargs):
            return TaskQueueChangeList
        
        # Custom readonly methods (for detail view)
        def args_preview(self, obj):
            if hasattr(obj, 'args') and obj.args:
                args_text = str(obj.args)
                return args_text[:100] + "..." if len(args_text) > 100 else args_text
            return "No arguments"
        args_preview.short_description = "Arguments"
        
        def kwargs_preview(self, obj):
            if hasattr(obj, 'kwargs') and obj.kwargs:
                kwargs_text = str(obj.kwargs)
                return kwargs_text[:100] + "..." if len(kwargs_text) > 100 else kwargs_text
            return "No kwargs"
        kwargs_preview.short_description = "Keyword Arguments"
        
        def result_preview(self, obj):
            if hasattr(obj, 'result') and obj.result:
                result_text = str(obj.result)
                return result_text[:100] + "..." if len(result_text) > 100 else result_text
            return "No result"
        result_preview.short_description = "Result"
        
        def duration_display(self, obj):
            if obj.started_at and obj.finished_at:
                duration = obj.finished_at - obj.started_at
                return f"{duration.total_seconds():.2f}s"
            return "N/A"
        duration_display.short_description = "Duration"
        
        def retries_display(self, obj):
            return str(getattr(obj, 'retries', 0))
        retries_display.short_description = "Retries"
        
        def error_message_display(self, obj):
            if hasattr(obj, 'error') and obj.error:
                error_text = str(obj.error)
                return error_text[:100] + "..." if len(error_text) > 100 else error_text
            return "No error"
        error_message_display.short_description = "Error"
        
        def changelist_view(self, request, extra_context=None):
            extra_context = extra_context or {}
            try:
                total_tasks = self.get_queryset(request).count()
                status_stats = self.get_queryset(request).values('status').annotate(count=Count('id')).order_by('status')
                actor_stats = self.get_queryset(request).values('actor_name').annotate(count=Count('id')).order_by('-count')[:10]
                queue_stats = self.get_queryset(request).values('queue_name').annotate(count=Count('id')).order_by('-count')
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

else:
    class TaskAdmin:
        """Placeholder when django-dramatiq is not available."""
        pass
