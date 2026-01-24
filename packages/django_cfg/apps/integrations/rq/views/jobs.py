"""
Django-RQ Job Management ViewSet.

Provides REST API endpoints for managing RQ jobs.
"""

from django_cfg.mixins import AdminAPIMixin
from django_cfg.middleware.pagination import DefaultPagination
from django_cfg.utils import get_logger
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from ..serializers import JobListSerializer, JobDetailSerializer, JobActionResponseSerializer
from ..services import JobService

logger = get_logger("rq.jobs")


class JobViewSet(AdminAPIMixin, viewsets.GenericViewSet):
    """
    ViewSet for RQ job management.

    Provides endpoints for:
    - Listing all jobs
    - Getting job details
    - Canceling jobs
    - Requeuing failed jobs
    - Deleting jobs

    Requires admin authentication (JWT, Session, or Basic Auth).
    """

    pagination_class = DefaultPagination
    serializer_class = JobListSerializer

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._job_service = JobService()

    @extend_schema(
        tags=["RQ Jobs"],
        summary="List all jobs",
        description="Returns all jobs across all registries (queued, started, finished, failed, deferred, scheduled).",
        parameters=[
            OpenApiParameter(
                name="queue",
                type=str,
                location=OpenApiParameter.QUERY,
                description="Filter by queue name",
                required=False,
            ),
            OpenApiParameter(
                name="status",
                type=str,
                location=OpenApiParameter.QUERY,
                description="Filter by status (queued, started, finished, failed, deferred, scheduled)",
                required=False,
            ),
        ],
        responses={
            200: JobListSerializer(many=True),
        },
    )
    def list(self, request):
        """List all jobs across all registries."""
        try:
            queue_filter = request.query_params.get("queue")
            status_filter = request.query_params.get("status")

            jobs = self._job_service.list_jobs(
                queue_filter=queue_filter,
                status_filter=status_filter,
            )

            # Convert to serializer format
            jobs_data = [
                {
                    "id": j.id,
                    "func_name": j.func_name,
                    "status": j.status,
                    "queue": j.queue,
                    "created_at": j.created_at,
                    "started_at": j.started_at,
                    "ended_at": j.ended_at,
                }
                for j in jobs
            ]

            return Response(jobs_data)

        except Exception as e:
            import traceback
            logger.error(f"Jobs list error: {e}", exc_info=True)
            return Response(
                {
                    "error": str(e),
                    "traceback": traceback.format_exc(),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @extend_schema(
        tags=["RQ Jobs"],
        summary="Get job details",
        description="Returns detailed information about a specific job.",
        responses={
            200: JobDetailSerializer,
            404: {"description": "Job not found"},
        },
    )
    def retrieve(self, request, pk=None):
        """Get job details by ID."""
        try:
            job_detail = self._job_service.get_job_detail(pk)

            if not job_detail:
                return Response(
                    {"error": f"Job {pk} not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            job_data = {
                "id": job_detail.id,
                "func_name": job_detail.func_name,
                "args": job_detail.args,
                "kwargs": job_detail.kwargs,
                "created_at": job_detail.created_at,
                "enqueued_at": job_detail.enqueued_at,
                "started_at": job_detail.started_at,
                "ended_at": job_detail.ended_at,
                "status": job_detail.status,
                "queue": job_detail.queue,
                "worker_name": job_detail.worker_name,
                "timeout": job_detail.timeout,
                "result_ttl": job_detail.result_ttl,
                "failure_ttl": job_detail.failure_ttl,
                "result": job_detail.result,
                "exc_info": job_detail.exc_info,
                "meta": job_detail.meta,
                "dependency_ids": job_detail.dependency_ids,
            }

            serializer = JobDetailSerializer(data=job_data)
            serializer.is_valid(raise_exception=True)
            return Response(serializer.data)

        except Exception as e:
            logger.error(f"Job detail error: {e}", exc_info=True)
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @extend_schema(
        tags=["RQ Jobs"],
        summary="Cancel job",
        description="Cancels a job. For queued jobs, cancels immediately. For running jobs, sets cancellation flag for cooperative cancellation. Use force=true to send SIGTERM (dangerous).",
        parameters=[
            OpenApiParameter(
                name="force",
                type=bool,
                location=OpenApiParameter.QUERY,
                description="Force stop by sending SIGTERM to worker (dangerous, kills all jobs on worker)",
                required=False,
            ),
        ],
        responses={
            200: JobActionResponseSerializer,
            404: {"description": "Job not found or already finished"},
        },
    )
    @action(detail=True, methods=["post"], url_path="cancel")
    def cancel(self, request, pk=None):
        """Cancel job (queued or running)."""
        try:
            force = request.query_params.get("force", "").lower() == "true"
            result = self._job_service.cancel_job(pk, force=force)

            if not result.success:
                return Response(
                    {"error": result.error or result.message},
                    status=status.HTTP_404_NOT_FOUND,
                )

            response_data = {
                "success": True,
                "message": result.message,
                "job_id": result.job_id,
                "action": result.action,
            }

            serializer = JobActionResponseSerializer(data=response_data)
            serializer.is_valid(raise_exception=True)
            return Response(serializer.data)

        except Exception as e:
            logger.error(f"Job cancel error: {e}", exc_info=True)
            return Response(
                {"error": f"Failed to cancel job: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @extend_schema(
        tags=["RQ Jobs"],
        summary="Requeue job",
        description="Requeues a failed job.",
        responses={
            200: JobActionResponseSerializer,
            404: {"description": "Job not found"},
        },
    )
    @action(detail=True, methods=["post"], url_path="requeue")
    def requeue(self, request, pk=None):
        """Requeue failed job."""
        try:
            result = self._job_service.requeue_job(pk)

            if not result.success:
                return Response(
                    {"error": result.error or result.message},
                    status=status.HTTP_404_NOT_FOUND,
                )

            response_data = {
                "success": True,
                "message": result.message,
                "job_id": result.job_id,
                "action": result.action,
            }

            serializer = JobActionResponseSerializer(data=response_data)
            serializer.is_valid(raise_exception=True)
            return Response(serializer.data)

        except Exception as e:
            logger.error(f"Job requeue error: {e}", exc_info=True)
            return Response(
                {"error": f"Failed to requeue job: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @extend_schema(
        tags=["RQ Jobs"],
        summary="Delete job",
        description="Deletes a job from the queue.",
        responses={
            200: JobActionResponseSerializer,
            404: {"description": "Job not found"},
        },
    )
    def destroy(self, request, pk=None):
        """Delete job."""
        try:
            result = self._job_service.delete_job(pk)

            if not result.success:
                return Response(
                    {"error": result.error or result.message},
                    status=status.HTTP_404_NOT_FOUND,
                )

            response_data = {
                "success": True,
                "message": result.message,
                "job_id": result.job_id,
                "action": result.action,
            }

            serializer = JobActionResponseSerializer(data=response_data)
            serializer.is_valid(raise_exception=True)
            return Response(serializer.data)

        except Exception as e:
            logger.error(f"Job delete error: {e}", exc_info=True)
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    # Registry Management Endpoints

    @extend_schema(
        tags=["RQ Registries"],
        summary="List failed jobs",
        description="Returns list of all failed jobs from failed job registry.",
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
            200: JobListSerializer(many=True),
        },
    )
    @action(detail=False, methods=["get"], url_path="registries/failed")
    def failed_jobs(self, request):
        """List all failed jobs."""
        try:
            queue_filter = request.query_params.get("queue")
            jobs = self._job_service.list_jobs_by_registry("failed", queue_filter)

            jobs_data = [
                {
                    "id": j.id,
                    "func_name": j.func_name,
                    "status": j.status,
                    "queue": j.queue,
                    "created_at": j.created_at,
                }
                for j in jobs
            ]

            page = self.paginate_queryset(jobs_data)
            serializer = JobListSerializer(data=page, many=True)
            serializer.is_valid(raise_exception=True)
            return self.get_paginated_response(serializer.data)

        except Exception as e:
            logger.error(f"Failed jobs list error: {e}", exc_info=True)
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @extend_schema(
        tags=["RQ Registries"],
        summary="List finished jobs",
        description="Returns list of all finished jobs from finished job registry.",
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
            200: JobListSerializer(many=True),
        },
    )
    @action(detail=False, methods=["get"], url_path="registries/finished")
    def finished_jobs(self, request):
        """List all finished jobs."""
        try:
            queue_filter = request.query_params.get("queue")
            jobs = self._job_service.list_jobs_by_registry("finished", queue_filter)

            jobs_data = [
                {
                    "id": j.id,
                    "func_name": j.func_name,
                    "status": j.status,
                    "queue": j.queue,
                    "created_at": j.created_at,
                }
                for j in jobs
            ]

            page = self.paginate_queryset(jobs_data)
            serializer = JobListSerializer(data=page, many=True)
            serializer.is_valid(raise_exception=True)
            return self.get_paginated_response(serializer.data)

        except Exception as e:
            logger.error(f"Finished jobs list error: {e}", exc_info=True)
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @extend_schema(
        tags=["RQ Registries"],
        summary="Requeue all failed jobs",
        description="Requeues all failed jobs in the failed job registry.",
        parameters=[
            OpenApiParameter(
                name="queue",
                type=str,
                location=OpenApiParameter.QUERY,
                required=True,
                description="Queue name",
            ),
        ],
        responses={
            200: JobActionResponseSerializer,
        },
    )
    @action(detail=False, methods=["post"], url_path="registries/failed/requeue-all")
    def requeue_all_failed(self, request):
        """Requeue all failed jobs."""
        try:
            queue_name = request.query_params.get("queue")
            if not queue_name:
                return Response(
                    {"error": "queue parameter is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            result = self._job_service.requeue_all_failed(queue_name)

            response_data = {
                "success": result.success,
                "message": result.message,
                "job_id": result.job_id,
                "action": result.action,
            }

            serializer = JobActionResponseSerializer(data=response_data)
            serializer.is_valid(raise_exception=True)
            return Response(serializer.data)

        except Exception as e:
            logger.error(f"Requeue all failed error: {e}", exc_info=True)
            return Response(
                {"error": f"Failed to requeue jobs: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @extend_schema(
        tags=["RQ Registries"],
        summary="Clear failed jobs registry",
        description="Removes all jobs from the failed job registry.",
        parameters=[
            OpenApiParameter(
                name="queue",
                type=str,
                location=OpenApiParameter.QUERY,
                required=True,
                description="Queue name",
            ),
        ],
        responses={
            200: JobActionResponseSerializer,
        },
    )
    @action(detail=False, methods=["post"], url_path="registries/failed/clear")
    def clear_failed_registry(self, request):
        """Clear failed jobs registry."""
        try:
            queue_name = request.query_params.get("queue")
            if not queue_name:
                return Response(
                    {"error": "queue parameter is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            result = self._job_service.clear_registry("failed", queue_name)

            response_data = {
                "success": result.success,
                "message": result.message,
                "job_id": result.job_id,
                "action": result.action,
            }

            serializer = JobActionResponseSerializer(data=response_data)
            serializer.is_valid(raise_exception=True)
            return Response(serializer.data)

        except Exception as e:
            logger.error(f"Clear failed registry error: {e}", exc_info=True)
            return Response(
                {"error": f"Failed to clear registry: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @extend_schema(
        tags=["RQ Registries"],
        summary="Clear finished jobs registry",
        description="Removes all jobs from the finished job registry.",
        parameters=[
            OpenApiParameter(
                name="queue",
                type=str,
                location=OpenApiParameter.QUERY,
                required=True,
                description="Queue name",
            ),
        ],
        responses={
            200: JobActionResponseSerializer,
        },
    )
    @action(detail=False, methods=["post"], url_path="registries/finished/clear")
    def clear_finished_registry(self, request):
        """Clear finished jobs registry."""
        try:
            queue_name = request.query_params.get("queue")
            if not queue_name:
                return Response(
                    {"error": "queue parameter is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            result = self._job_service.clear_registry("finished", queue_name)

            response_data = {
                "success": result.success,
                "message": result.message,
                "job_id": result.job_id,
                "action": result.action,
            }

            serializer = JobActionResponseSerializer(data=response_data)
            serializer.is_valid(raise_exception=True)
            return Response(serializer.data)

        except Exception as e:
            logger.error(f"Clear finished registry error: {e}", exc_info=True)
            return Response(
                {"error": f"Failed to clear registry: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @extend_schema(
        tags=["RQ Registries"],
        summary="List deferred jobs",
        description="Returns list of all deferred jobs from deferred job registry.",
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
            200: JobListSerializer(many=True),
        },
    )
    @action(detail=False, methods=["get"], url_path="registries/deferred")
    def deferred_jobs(self, request):
        """List all deferred jobs."""
        try:
            queue_filter = request.query_params.get("queue")
            jobs = self._job_service.list_jobs_by_registry("deferred", queue_filter)

            jobs_data = [
                {
                    "id": j.id,
                    "func_name": j.func_name,
                    "status": j.status,
                    "queue": j.queue,
                    "created_at": j.created_at,
                }
                for j in jobs
            ]

            page = self.paginate_queryset(jobs_data)
            serializer = JobListSerializer(data=page, many=True)
            serializer.is_valid(raise_exception=True)
            return self.get_paginated_response(serializer.data)

        except Exception as e:
            logger.error(f"Deferred jobs list error: {e}", exc_info=True)
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @extend_schema(
        tags=["RQ Registries"],
        summary="List started jobs",
        description="Returns list of all currently running jobs from started job registry.",
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
            200: JobListSerializer(many=True),
        },
    )
    @action(detail=False, methods=["get"], url_path="registries/started")
    def started_jobs(self, request):
        """List all started (running) jobs."""
        try:
            queue_filter = request.query_params.get("queue")
            jobs = self._job_service.list_jobs_by_registry("started", queue_filter)

            jobs_data = [
                {
                    "id": j.id,
                    "func_name": j.func_name,
                    "status": j.status,
                    "queue": j.queue,
                    "created_at": j.created_at,
                }
                for j in jobs
            ]

            page = self.paginate_queryset(jobs_data)
            serializer = JobListSerializer(data=page, many=True)
            serializer.is_valid(raise_exception=True)
            return self.get_paginated_response(serializer.data)

        except Exception as e:
            logger.error(f"Started jobs list error: {e}", exc_info=True)
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
