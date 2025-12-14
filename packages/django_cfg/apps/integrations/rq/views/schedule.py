"""
Django-RQ Schedule Management ViewSet.

Provides REST API endpoints for managing scheduled jobs using rq-scheduler.
"""

from datetime import datetime

from django.core.exceptions import ImproperlyConfigured
from django_cfg.mixins import AdminAPIMixin
from django_cfg.middleware.pagination import DefaultPagination
from django_cfg.utils import get_logger
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from ..serializers import (
    ScheduleCreateSerializer,
    ScheduledJobSerializer,
    ScheduleActionResponseSerializer,
)

logger = get_logger("rq.schedule")


class ScheduleViewSet(AdminAPIMixin, viewsets.GenericViewSet):
    """
    ViewSet for RQ schedule management.

    Provides endpoints for:
    - List scheduled jobs
    - Create scheduled jobs (one-time, interval, cron)
    - Get scheduled job details
    - Cancel scheduled jobs

    Requires admin authentication (JWT, Session, or Basic Auth).
    Requires rq-scheduler to be installed: pip install rq-scheduler
    """

    # Pagination for list endpoint
    pagination_class = DefaultPagination

    serializer_class = ScheduledJobSerializer

    @extend_schema(
        tags=["RQ Schedules"],
        summary="List scheduled jobs",
        description="Returns list of all scheduled jobs across all queues.",
        parameters=[
            OpenApiParameter(
                name="queue",
                type=str,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Filter by queue name",
            ),
        ],
        responses={
            200: ScheduledJobSerializer(many=True),
        },
    )
    def list(self, request):
        """List all scheduled jobs (from rq-scheduler Redis + config preview)."""
        try:
            import django_rq
            from django.conf import settings

            queue_filter = request.query_params.get('queue')

            # Get all schedulers
            queue_names = settings.RQ_QUEUES.keys() if hasattr(settings, 'RQ_QUEUES') else []
            if queue_filter:
                queue_names = [q for q in queue_names if q == queue_filter]

            all_jobs = []

            for queue_name in queue_names:
                try:
                    scheduler = django_rq.get_scheduler(queue_name)
                    scheduled_jobs = scheduler.get_jobs()

                    for job in scheduled_jobs:
                        job_data = {
                            "id": job.id,
                            "func": job.func_name,
                            "args": list(job.args or []),
                            "kwargs": job.kwargs or {},
                            "queue_name": queue_name,
                            "scheduled_time": job.meta.get('scheduled_time'),
                            "interval": job.meta.get('interval'),
                            "cron": job.meta.get('cron_string'),
                            "timeout": job.timeout,
                            "result_ttl": job.result_ttl,
                            "repeat": job.meta.get('repeat'),
                            "description": job.description,
                            "created_at": job.created_at,
                            "meta": job.meta or {},
                        }
                        all_jobs.append(job_data)

                except ImproperlyConfigured as e:
                    logger.warning(f"rq-scheduler not installed: {e}")
                    return Response(
                        {"error": "rq-scheduler not installed. Install with: pip install rq-scheduler"},
                        status=status.HTTP_501_NOT_IMPLEMENTED,
                    )
                except Exception as e:
                    logger.debug(f"Failed to get scheduled jobs for queue {queue_name}: {e}")

            # If no jobs in scheduler, return schedules from config as preview
            if not all_jobs:
                from ..services import get_rq_config

                config = get_rq_config()
                if config and hasattr(config, 'schedules'):
                    for idx, schedule in enumerate(config.schedules):
                        # Apply queue filter
                        if queue_filter and schedule.queue != queue_filter:
                            continue

                        job_data = {
                            "id": schedule.job_id or f"config_{idx}",
                            "func": schedule.func,
                            "args": schedule.args,
                            "kwargs": schedule.kwargs,
                            "queue_name": schedule.queue,
                            "scheduled_time": schedule.scheduled_time,
                            "interval": schedule.interval,
                            "cron": schedule.cron,
                            "timeout": schedule.timeout,
                            "result_ttl": schedule.result_ttl,
                            "repeat": schedule.repeat,
                            "description": schedule.description or "",
                            "created_at": None,
                            "meta": {"source": "config", "status": "not_registered"},
                        }
                        all_jobs.append(job_data)

            # Use DRF pagination
            page = self.paginate_queryset(all_jobs)
            serializer = ScheduledJobSerializer(data=page, many=True)
            serializer.is_valid(raise_exception=True)
            return self.get_paginated_response(serializer.data)

        except Exception as e:
            logger.error(f"Failed to list scheduled jobs: {e}", exc_info=True)
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @extend_schema(
        tags=["RQ Schedules"],
        summary="Create scheduled job",
        description="Schedule a job to run at specific time, interval, or cron schedule.",
        request=ScheduleCreateSerializer,
        responses={
            201: ScheduleActionResponseSerializer,
        },
    )
    def create(self, request):
        """Create a new scheduled job."""
        try:
            import django_rq
            from datetime import datetime, timezone

            serializer = ScheduleCreateSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            data = serializer.validated_data

            queue_name = data['queue_name']

            try:
                scheduler = django_rq.get_scheduler(queue_name)
            except ImproperlyConfigured as e:
                logger.warning(f"rq-scheduler not installed: {e}")
                return Response(
                    {"error": "rq-scheduler not installed. Install with: pip install rq-scheduler"},
                    status=status.HTTP_501_NOT_IMPLEMENTED,
                )

            # Prepare job kwargs
            job_kwargs = {
                'func': data['func'],
                'args': data.get('args', []),
                'kwargs': data.get('kwargs', {}),
                'queue_name': queue_name,
            }

            if data.get('timeout'):
                job_kwargs['timeout'] = data['timeout']

            if data.get('result_ttl'):
                job_kwargs['result_ttl'] = data['result_ttl']

            if data.get('repeat') is not None:
                job_kwargs['repeat'] = data['repeat']

            if data.get('description'):
                job_kwargs['description'] = data['description']

            # Schedule based on method
            if data.get('scheduled_time'):
                # One-time schedule at specific time
                scheduled_time = data['scheduled_time']
                if scheduled_time.tzinfo is None:
                    scheduled_time = scheduled_time.replace(tzinfo=timezone.utc)
                job = scheduler.enqueue_at(scheduled_time, **job_kwargs)
                schedule_type = "one-time"

            elif data.get('interval'):
                # Interval-based scheduling
                interval = data['interval']
                scheduled_time = datetime.now(timezone.utc)
                job = scheduler.schedule(
                    scheduled_time=scheduled_time,
                    interval=interval,
                    **job_kwargs
                )
                schedule_type = "interval"

            elif data.get('cron'):
                # Cron-based scheduling
                cron_string = data['cron']
                job = scheduler.cron(
                    cron_string,
                    **job_kwargs
                )
                schedule_type = "cron"

            else:
                return Response(
                    {"error": "Must provide scheduled_time, interval, or cron"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            response_data = {
                "success": True,
                "message": f"Job scheduled successfully ({schedule_type})",
                "job_id": job.id,
                "action": "create",
            }

            response_serializer = ScheduleActionResponseSerializer(data=response_data)
            response_serializer.is_valid(raise_exception=True)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"Failed to create scheduled job: {e}", exc_info=True)
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @extend_schema(
        tags=["RQ Schedules"],
        summary="Get scheduled job details",
        description="Returns detailed information about a specific scheduled job.",
        parameters=[
            OpenApiParameter(
                name="pk",
                type=str,
                location=OpenApiParameter.PATH,
                description="Job ID",
            ),
            OpenApiParameter(
                name="queue",
                type=str,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Queue name (optional, improves performance)",
            ),
        ],
        responses={
            200: ScheduledJobSerializer,
        },
    )
    def retrieve(self, request, pk=None):
        """Get scheduled job details by ID."""
        try:
            import django_rq
            from django.conf import settings
            from rq.job import Job

            queue_filter = request.query_params.get('queue')
            queue_names = settings.RQ_QUEUES.keys() if hasattr(settings, 'RQ_QUEUES') else []

            if queue_filter:
                queue_names = [q for q in queue_names if q == queue_filter]

            # Search for job across queues
            for queue_name in queue_names:
                try:
                    scheduler = django_rq.get_scheduler(queue_name)
                    queue = django_rq.get_queue(queue_name)

                    # Try to fetch job
                    job = Job.fetch(pk, connection=queue.connection)

                    # Check if it's a scheduled job
                    if job and job.id in [j.id for j in scheduler.get_jobs()]:
                        job_data = {
                            "id": job.id,
                            "func": job.func_name,
                            "args": list(job.args or []),
                            "kwargs": job.kwargs or {},
                            "queue_name": queue_name,
                            "scheduled_time": job.meta.get('scheduled_time'),
                            "interval": job.meta.get('interval'),
                            "cron": job.meta.get('cron_string'),
                            "timeout": job.timeout,
                            "result_ttl": job.result_ttl,
                            "repeat": job.meta.get('repeat'),
                            "description": job.description,
                            "created_at": job.created_at,
                            "meta": job.meta or {},
                        }

                        serializer = ScheduledJobSerializer(data=job_data)
                        serializer.is_valid(raise_exception=True)
                        return Response(serializer.data)

                except Exception as e:
                    logger.debug(f"Job {pk} not found in queue {queue_name}: {e}")
                    continue

            return Response(
                {"error": f"Scheduled job {pk} not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        except Exception as e:
            logger.error(f"Failed to retrieve scheduled job: {e}", exc_info=True)
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @extend_schema(
        tags=["RQ Schedules"],
        summary="Cancel scheduled job",
        description="Cancel a scheduled job by ID.",
        parameters=[
            OpenApiParameter(
                name="pk",
                type=str,
                location=OpenApiParameter.PATH,
                description="Job ID",
            ),
            OpenApiParameter(
                name="queue",
                type=str,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Queue name (optional, improves performance)",
            ),
        ],
        responses={
            200: ScheduleActionResponseSerializer,
        },
    )
    def destroy(self, request, pk=None):
        """Cancel a scheduled job."""
        try:
            import django_rq
            from django.conf import settings

            queue_filter = request.query_params.get('queue')
            queue_names = settings.RQ_QUEUES.keys() if hasattr(settings, 'RQ_QUEUES') else []

            if queue_filter:
                queue_names = [q for q in queue_names if q == queue_filter]

            # Search for job across queues
            for queue_name in queue_names:
                try:
                    scheduler = django_rq.get_scheduler(queue_name)

                    # Try to cancel job
                    scheduler.cancel(pk)

                    response_data = {
                        "success": True,
                        "message": f"Scheduled job {pk} cancelled successfully",
                        "job_id": pk,
                        "action": "cancel",
                    }

                    response_serializer = ScheduleActionResponseSerializer(data=response_data)
                    response_serializer.is_valid(raise_exception=True)
                    return Response(response_serializer.data)

                except Exception as e:
                    logger.debug(f"Failed to cancel job {pk} in queue {queue_name}: {e}")
                    continue

            return Response(
                {"error": f"Scheduled job {pk} not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        except Exception as e:
            logger.error(f"Failed to cancel scheduled job: {e}", exc_info=True)
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
