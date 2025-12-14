"""
Django-RQ Worker Management ViewSet.

Provides REST API endpoints for monitoring RQ workers.
"""

from datetime import datetime

from django_cfg.mixins import AdminAPIMixin
from django_cfg.utils import get_logger
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from ..serializers import WorkerSerializer, WorkerStatsSerializer
from ..services import worker_to_model

logger = get_logger("rq.workers")


class WorkerViewSet(AdminAPIMixin, viewsets.ViewSet):
    """
    ViewSet for RQ worker monitoring.

    Provides endpoints for:
    - Listing all workers with statistics
    - Getting worker aggregated stats
    - Getting individual worker details

    Requires admin authentication (JWT, Session, or Basic Auth).
    """

    @extend_schema(
        tags=["RQ Workers"],
        summary="List all workers",
        description="Returns list of all RQ workers with their current state. Supports filtering by state and queue.",
        parameters=[
            OpenApiParameter(
                name="state",
                type=str,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Filter by worker state (idle, busy, suspended)",
            ),
            OpenApiParameter(
                name="queue",
                type=str,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Filter by queue name",
            ),
        ],
        responses={
            200: WorkerSerializer(many=True),
        },
    )
    def list(self, request):
        """List all workers with optional filtering."""
        try:
            import django_rq
            from rq import Worker

            # Get query params for filtering
            state_filter = request.query_params.get('state')
            queue_filter = request.query_params.get('queue')

            # Get all workers using connection from default queue
            # All queues share the same Redis connection, so we only need one
            queue = django_rq.get_queue('default')
            all_workers = Worker.all(connection=queue.connection)

            workers_data = []
            for worker in all_workers:
                try:
                    # Convert RQ Worker to Pydantic model
                    worker_model = worker_to_model(worker)

                    # Apply filters
                    if state_filter and worker_model.state != state_filter:
                        continue

                    if queue_filter and queue_filter not in worker_model.get_queue_list():
                        continue

                    # Convert Pydantic model to dict for DRF serializer
                    # mode='json' converts datetime objects to ISO format strings
                    worker_dict = worker_model.model_dump(mode='json')

                    # DRF serializer expects 'queues' as list, not comma-separated string
                    worker_dict['queues'] = worker_model.get_queue_list()

                    # DRF serializer expects 'current_job' not 'current_job_id'
                    worker_dict['current_job'] = worker_dict.pop('current_job_id')

                    serializer = WorkerSerializer(data=worker_dict)
                    serializer.is_valid(raise_exception=True)
                    workers_data.append(serializer.data)

                except Exception as e:
                    logger.debug(f"Failed to get worker {worker.name}: {e}")
                    continue

            return Response(workers_data)

        except Exception as e:
            import traceback
            logger.error(f"Worker list error: {e}", exc_info=True)
            return Response(
                {
                    "error": str(e),
                    "traceback": traceback.format_exc(),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @extend_schema(
        tags=["RQ Workers"],
        summary="Get worker statistics",
        description="Returns aggregated statistics for all workers.",
        responses={
            200: WorkerStatsSerializer,
        },
    )
    @action(detail=False, methods=["get"], url_path="stats")
    def stats(self, request):
        """Get aggregated worker statistics."""
        try:
            import django_rq
            from rq import Worker

            # Get all workers using connection from default queue
            # All queues share the same Redis connection, so we only need one
            queue = django_rq.get_queue('default')
            all_workers = Worker.all(connection=queue.connection)

            # Count by state
            busy_workers = 0
            idle_workers = 0
            suspended_workers = 0
            total_successful = 0
            total_failed = 0
            total_working_time = 0.0

            workers_list = []

            for worker in all_workers:
                try:
                    # Convert RQ Worker to Pydantic model
                    worker_model = worker_to_model(worker)

                    # Count by state
                    if worker_model.is_busy:
                        busy_workers += 1
                    elif worker_model.is_idle:
                        idle_workers += 1
                    elif worker_model.state == 'suspended':
                        suspended_workers += 1

                    total_successful += worker_model.successful_job_count
                    total_failed += worker_model.failed_job_count
                    total_working_time += worker_model.total_working_time

                    # Convert to dict for serializer (mode='json' converts datetime to ISO strings)
                    worker_dict = worker_model.model_dump(mode='json')
                    worker_dict['queues'] = worker_model.get_queue_list()
                    worker_dict['current_job'] = worker_dict.pop('current_job_id')
                    workers_list.append(worker_dict)

                except Exception as e:
                    logger.debug(f"Failed to process worker: {e}")
                    continue

            stats_data = {
                "total_workers": len(all_workers),
                "busy_workers": busy_workers,
                "idle_workers": idle_workers,
                "suspended_workers": suspended_workers,
                "total_successful_jobs": total_successful,
                "total_failed_jobs": total_failed,
                "total_working_time": total_working_time,
                "workers": workers_list,
            }

            serializer = WorkerStatsSerializer(data=stats_data)
            serializer.is_valid(raise_exception=True)
            return Response(serializer.data)

        except Exception as e:
            import traceback
            logger.error(f"Worker stats error: {e}", exc_info=True)
            return Response(
                {
                    "error": str(e),
                    "traceback": traceback.format_exc(),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
