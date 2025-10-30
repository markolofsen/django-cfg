"""
TaskLog FilterSet for advanced filtering.

Provides comprehensive filtering capabilities for task logs.
"""
import django_filters
from django.db.models import Q

from ..models import TaskLog


class TaskLogFilter(django_filters.FilterSet):
    """
    Advanced FilterSet for TaskLog.

    Matches ReArq API query parameters where possible.

    Provides filters for:
    - Task name (exact, contains)
    - Queue name (exact, in)
    - Status (exact, in) - matching ReArq JobStatus
    - Date ranges (enqueue, start, finish)
    - Duration ranges
    - Retry count ranges
    - Success/failure flags
    """

    # Task name filters (matching ReArq "task" param)
    task = django_filters.CharFilter(field_name='task_name', lookup_expr='exact')
    task_name = django_filters.CharFilter(lookup_expr='icontains')
    task_name_exact = django_filters.CharFilter(field_name='task_name', lookup_expr='exact')

    # Queue filters
    queue_name = django_filters.CharFilter(lookup_expr='exact')
    queue_name_in = django_filters.BaseInFilter(field_name='queue_name')

    # Status filters (matching ReArq "status" param)
    status = django_filters.CharFilter(lookup_expr='exact')
    status_in = django_filters.BaseInFilter(field_name='status')

    # Success filter (matching ReArq JobResult)
    success = django_filters.BooleanFilter()

    # Boolean flags (computed properties)
    is_completed = django_filters.BooleanFilter(method='filter_is_completed')
    is_successful = django_filters.BooleanFilter(method='filter_is_successful')
    is_failed = django_filters.BooleanFilter(method='filter_is_failed')

    # Date range filters (matching ReArq "start_time" / "end_time")
    start_time = django_filters.DateTimeFilter(field_name='enqueue_time', lookup_expr='gte')
    end_time = django_filters.DateTimeFilter(field_name='enqueue_time', lookup_expr='lte')

    # Additional date filters
    enqueue_after = django_filters.DateTimeFilter(field_name='enqueue_time', lookup_expr='gte')
    enqueue_before = django_filters.DateTimeFilter(field_name='enqueue_time', lookup_expr='lte')

    start_after = django_filters.DateTimeFilter(field_name='start_time', lookup_expr='gte')
    start_before = django_filters.DateTimeFilter(field_name='start_time', lookup_expr='lte')

    finish_after = django_filters.DateTimeFilter(field_name='finish_time', lookup_expr='gte')
    finish_before = django_filters.DateTimeFilter(field_name='finish_time', lookup_expr='lte')

    # Django-specific filters
    created_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')

    # Duration filters (milliseconds)
    duration_min = django_filters.NumberFilter(field_name='duration_ms', lookup_expr='gte')
    duration_max = django_filters.NumberFilter(field_name='duration_ms', lookup_expr='lte')

    # Retry filters (matching ReArq Job fields)
    job_retries_min = django_filters.NumberFilter(field_name='job_retries', lookup_expr='gte')
    job_retries_max = django_filters.NumberFilter(field_name='job_retries', lookup_expr='lte')

    # Job ID filter (matching ReArq "job_id" param)
    job_id = django_filters.CharFilter(lookup_expr='exact')

    # Worker filter (matching ReArq JobResult "worker" param)
    worker = django_filters.CharFilter(field_name='worker_id', lookup_expr='exact')

    # Error message search
    has_error = django_filters.BooleanFilter(method='filter_has_error')

    class Meta:
        model = TaskLog
        fields = [
            'task_name',
            'queue_name',
            'status',
            'success',
            'job_id',
            'worker_id',
        ]

    def filter_has_error(self, queryset, name, value):
        """Filter tasks with/without errors."""
        if value:
            return queryset.filter(error_message__isnull=False).exclude(error_message='')
        else:
            return queryset.filter(Q(error_message__isnull=True) | Q(error_message=''))

    def filter_is_completed(self, queryset, name, value):
        """Filter by completed status."""
        if value:
            return queryset.filter(status__in=['success', 'failed', 'expired', 'canceled'])
        else:
            return queryset.filter(status__in=['deferred', 'queued', 'in_progress'])

    def filter_is_successful(self, queryset, name, value):
        """Filter by successful completion."""
        if value:
            return queryset.filter(status='success', success=True)
        else:
            return queryset.exclude(status='success', success=True)

    def filter_is_failed(self, queryset, name, value):
        """Filter by failed status."""
        if value:
            return queryset.filter(Q(status__in=['failed', 'expired']) | Q(success=False))
        else:
            return queryset.exclude(Q(status__in=['failed', 'expired']) | Q(success=False))
