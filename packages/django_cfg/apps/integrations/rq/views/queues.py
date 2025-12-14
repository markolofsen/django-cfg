"""
Django-RQ Queue Management ViewSet.

Provides REST API endpoints for managing RQ queues.
"""

from django_cfg.mixins import AdminAPIMixin
from django_cfg.utils import get_logger
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from ..serializers import QueueStatsSerializer, QueueDetailSerializer
from ..services import queue_to_model

logger = get_logger("rq.queues")


class QueueViewSet(AdminAPIMixin, viewsets.ViewSet):
    """
    ViewSet for RQ queue management.

    Provides endpoints for:
    - Listing all queues with statistics
    - Getting detailed queue information
    - Emptying queues
    - Getting queue job lists

    Requires admin authentication (JWT, Session, or Basic Auth).
    """

    @extend_schema(
        tags=["RQ Queues"],
        summary="List all queues",
        description="Returns list of all configured RQ queues with statistics. Supports filtering by queue name.",
        parameters=[
            OpenApiParameter(
                name="name",
                type=str,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Filter by queue name (exact match or substring)",
            ),
        ],
        responses={
            200: QueueStatsSerializer(many=True),
        },
    )
    def list(self, request):
        """List all queues with statistics and optional filtering."""
        try:
            import django_rq
            from django.conf import settings

            if not hasattr(settings, 'RQ_QUEUES'):
                return Response([])

            # Get query params for filtering
            name_filter = request.query_params.get('name')

            queues_data = []

            for queue_name in settings.RQ_QUEUES.keys():
                try:
                    # Apply name filter
                    if name_filter and name_filter.lower() not in queue_name.lower():
                        continue

                    queue = django_rq.get_queue(queue_name)

                    # Convert RQ Queue to Pydantic model
                    queue_model = queue_to_model(queue, queue_name)

                    # Convert to dict for DRF serializer (only stats fields)
                    queue_dict = {
                        "name": queue_model.name,
                        "count": queue_model.count,
                        "queued_jobs": queue_model.queued_jobs,
                        "started_jobs": queue_model.started_jobs,
                        "finished_jobs": queue_model.finished_jobs,
                        "failed_jobs": queue_model.failed_jobs,
                        "deferred_jobs": queue_model.deferred_jobs,
                        "scheduled_jobs": queue_model.scheduled_jobs,
                        "workers": queue_model.workers,
                    }

                    serializer = QueueStatsSerializer(data=queue_dict)
                    serializer.is_valid(raise_exception=True)
                    queues_data.append(serializer.data)

                except Exception as e:
                    logger.error(f"Failed to get queue {queue_name}: {e}", exc_info=True)
                    continue

            return Response(queues_data)

        except Exception as e:
            logger.error(f"Queue list error: {e}", exc_info=True)
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @extend_schema(
        tags=["RQ Queues"],
        summary="Get queue details",
        description="Returns detailed information about a specific queue.",
        responses={
            200: QueueDetailSerializer,
            404: {"description": "Queue not found"},
        },
    )
    def retrieve(self, request, pk=None):
        """Get detailed queue information."""
        try:
            import django_rq

            try:
                queue = django_rq.get_queue(pk)
            except Exception:
                return Response(
                    {"error": f"Queue {pk} not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Convert RQ Queue to Pydantic model
            queue_model = queue_to_model(queue, pk)

            # Convert to dict for DRF serializer
            queue_dict = {
                "name": queue_model.name,
                "count": queue_model.count,
                "queued_jobs": queue_model.queued_jobs,
                "started_jobs": queue_model.started_jobs,
                "finished_jobs": queue_model.finished_jobs,
                "failed_jobs": queue_model.failed_jobs,
                "deferred_jobs": queue_model.deferred_jobs,
                "scheduled_jobs": queue_model.scheduled_jobs,
                "workers": queue_model.workers,
                "oldest_job_timestamp": queue_model.oldest_job_timestamp,
                "connection_kwargs": {
                    'host': queue_model.connection_host,
                    'port': queue_model.connection_port,
                    'db': queue_model.connection_db,
                },
                "is_async": queue_model.is_async,
            }

            serializer = QueueDetailSerializer(data=queue_dict)
            serializer.is_valid(raise_exception=True)
            return Response(serializer.data)

        except Exception as e:
            logger.error(f"Queue detail error: {e}", exc_info=True)
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @extend_schema(
        tags=["RQ Queues"],
        summary="Empty queue",
        description="Removes all jobs from the specified queue.",
        responses={
            200: {"description": "Queue emptied successfully"},
            404: {"description": "Queue not found"},
        },
    )
    @action(detail=True, methods=["post"], url_path="empty")
    def empty(self, request, pk=None):
        """Empty queue (remove all jobs)."""
        try:
            import django_rq

            try:
                queue = django_rq.get_queue(pk)
            except Exception:
                return Response(
                    {"error": f"Queue {pk} not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            job_count = queue.count
            queue.empty()

            return Response({
                "success": True,
                "message": f"Emptied queue '{pk}', removed {job_count} jobs",
                "queue": pk,
                "removed_jobs": job_count,
            })

        except Exception as e:
            logger.error(f"Queue empty error: {e}", exc_info=True)
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @extend_schema(
        tags=["RQ Queues"],
        summary="Get queue jobs",
        description="Returns list of job IDs in the queue.",
        parameters=[
            OpenApiParameter(
                name="limit",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Number of jobs to return (default: 100)",
                required=False,
            ),
            OpenApiParameter(
                name="offset",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Offset for pagination (default: 0)",
                required=False,
            ),
        ],
        responses={
            200: {"description": "List of job IDs"},
            404: {"description": "Queue not found"},
        },
    )
    @action(detail=True, methods=["get"], url_path="jobs")
    def jobs(self, request, pk=None):
        """Get list of jobs in queue."""
        try:
            import django_rq

            try:
                queue = django_rq.get_queue(pk)
            except Exception:
                return Response(
                    {"error": f"Queue {pk} not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Pagination
            limit = min(int(request.query_params.get("limit", 100)), 500)
            offset = int(request.query_params.get("offset", 0))

            # Get job IDs
            job_ids = queue.get_job_ids(offset, offset + limit)

            return Response({
                "queue": pk,
                "total_jobs": queue.count,
                "limit": limit,
                "offset": offset,
                "job_ids": job_ids,
            })

        except Exception as e:
            logger.error(f"Queue jobs error: {e}", exc_info=True)
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
