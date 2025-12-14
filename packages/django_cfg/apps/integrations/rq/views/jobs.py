"""
Django-RQ Job Management ViewSet.

Provides REST API endpoints for managing RQ jobs.
"""

import json

from django_cfg.mixins import AdminAPIMixin
from django_cfg.middleware.pagination import DefaultPagination
from django_cfg.utils import get_logger
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from ..serializers import JobListSerializer, JobDetailSerializer, JobActionResponseSerializer
from ..services import job_to_model

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

    # Pagination for registry endpoints
    pagination_class = DefaultPagination

    serializer_class = JobListSerializer

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
            import django_rq
            from django.conf import settings
            from rq.job import Job
            from rq.registry import (
                FinishedJobRegistry,
                FailedJobRegistry,
                StartedJobRegistry,
                DeferredJobRegistry,
                ScheduledJobRegistry,
            )

            queue_filter = request.query_params.get('queue')
            status_filter = request.query_params.get('status')

            all_jobs = []

            if hasattr(settings, 'RQ_QUEUES'):
                for queue_name in settings.RQ_QUEUES.keys():
                    # Apply queue filter
                    if queue_filter and queue_filter != queue_name:
                        continue

                    try:
                        queue = django_rq.get_queue(queue_name)

                        # Get jobs from all registries
                        registries = {
                            'queued': {'jobs': queue.job_ids, 'status': 'queued'},
                            'started': {'registry': StartedJobRegistry(queue_name, connection=queue.connection), 'status': 'started'},
                            'finished': {'registry': FinishedJobRegistry(queue_name, connection=queue.connection), 'status': 'finished'},
                            'failed': {'registry': FailedJobRegistry(queue_name, connection=queue.connection), 'status': 'failed'},
                            'deferred': {'registry': DeferredJobRegistry(queue_name, connection=queue.connection), 'status': 'deferred'},
                            'scheduled': {'registry': ScheduledJobRegistry(queue_name, connection=queue.connection), 'status': 'scheduled'},
                        }

                        for reg_name, reg_data in registries.items():
                            # Apply status filter
                            if status_filter and status_filter != reg_data['status']:
                                continue

                            # Get job IDs
                            if 'registry' in reg_data:
                                job_ids = reg_data['registry'].get_job_ids()
                            else:
                                job_ids = reg_data['jobs']

                            # Fetch jobs (limit to 100 per registry to avoid overload)
                            for job_id in job_ids[:100]:
                                try:
                                    job = Job.fetch(job_id, connection=queue.connection)
                                    job_model = job_to_model(job, queue_name)

                                    # Convert to dict for DRF serializer (minimal fields for list)
                                    job_dict = {
                                        "id": job_model.id,
                                        "func_name": job_model.func_name,
                                        "status": job_model.status,
                                        "queue": queue_name,
                                        "created_at": job_model.created_at,
                                        "started_at": job_model.started_at,
                                        "ended_at": job_model.ended_at,
                                    }

                                    serializer = JobListSerializer(data=job_dict)
                                    serializer.is_valid(raise_exception=True)
                                    all_jobs.append(serializer.data)

                                except Exception:
                                    # Job was deleted from Redis (expired TTL) - skip silently
                                    continue

                    except Exception as e:
                        logger.debug(f"Failed to get jobs from queue {queue_name}: {e}")
                        continue

            return Response(all_jobs)

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
            from rq.job import Job
            from django.conf import settings
            import django_rq

            # Try to find job in all queues
            job = None
            job_queue = None

            if hasattr(settings, 'RQ_QUEUES'):
                for queue_name in settings.RQ_QUEUES.keys():
                    try:
                        queue = django_rq.get_queue(queue_name)
                        job = Job.fetch(pk, connection=queue.connection)
                        job_queue = queue_name
                        break
                    except Exception:
                        continue

            if not job:
                return Response(
                    {"error": f"Job {pk} not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Convert RQ Job to Pydantic model
            job_model = job_to_model(job, job_queue)

            # Convert Pydantic model to dict for DRF serializer
            # DRF expects args/kwargs/meta as dicts/lists, not JSON strings
            job_dict = {
                "id": job_model.id,
                "func_name": job_model.func_name,
                "args": json.loads(job_model.args_json),
                "kwargs": json.loads(job_model.kwargs_json),
                "created_at": job_model.created_at,
                "enqueued_at": job_model.enqueued_at,
                "started_at": job_model.started_at,
                "ended_at": job_model.ended_at,
                "status": job_model.status,
                "queue": job_model.queue,
                "worker_name": job_model.worker_name,
                "timeout": job_model.timeout,
                "result_ttl": job_model.result_ttl,
                "failure_ttl": job_model.failure_ttl,
                "result": json.loads(job_model.result_json) if job_model.result_json else None,
                "exc_info": job_model.exc_info,
                "meta": json.loads(job_model.meta_json) if job_model.meta_json else {},
                "dependency_ids": job_model.dependency_ids.split(",") if job_model.dependency_ids else [],
            }

            serializer = JobDetailSerializer(data=job_dict)
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
        description="Cancels a job (if it's queued or started).",
        responses={
            200: JobActionResponseSerializer,
            404: {"description": "Job not found"},
        },
    )
    @action(detail=True, methods=["post"], url_path="cancel")
    def cancel(self, request, pk=None):
        """Cancel job."""
        try:
            from rq.job import Job
            from django.conf import settings
            import django_rq

            # Try to find job in all queues
            job = None

            if hasattr(settings, 'RQ_QUEUES'):
                for queue_name in settings.RQ_QUEUES.keys():
                    try:
                        queue = django_rq.get_queue(queue_name)
                        job = Job.fetch(pk, connection=queue.connection)
                        break
                    except Exception:
                        continue

            if not job:
                return Response(
                    {"error": f"Job {pk} not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Cancel job
            job.cancel()

            response_data = {
                "success": True,
                "message": f"Job {pk} canceled successfully",
                "job_id": pk,
                "action": "cancel",
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
            from rq.job import Job
            from django.conf import settings
            import django_rq

            # Try to find job in all queues
            job = None
            queue = None

            if hasattr(settings, 'RQ_QUEUES'):
                for queue_name in settings.RQ_QUEUES.keys():
                    try:
                        queue = django_rq.get_queue(queue_name)
                        job = Job.fetch(pk, connection=queue.connection)
                        break
                    except Exception:
                        continue

            if not job or not queue:
                return Response(
                    {"error": f"Job {pk} not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Requeue job
            queue.failed_job_registry.requeue(pk)

            response_data = {
                "success": True,
                "message": f"Job {pk} requeued successfully",
                "job_id": pk,
                "action": "requeue",
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
            from rq.job import Job
            from django.conf import settings
            import django_rq

            # Try to find job in all queues
            job = None

            if hasattr(settings, 'RQ_QUEUES'):
                for queue_name in settings.RQ_QUEUES.keys():
                    try:
                        queue = django_rq.get_queue(queue_name)
                        job = Job.fetch(pk, connection=queue.connection)
                        break
                    except Exception:
                        continue

            if not job:
                return Response(
                    {"error": f"Job {pk} not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Delete job
            job.delete()

            response_data = {
                "success": True,
                "message": f"Job {pk} deleted successfully",
                "job_id": pk,
                "action": "delete",
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
            import django_rq
            from django.conf import settings
            from rq.job import Job

            queue_filter = request.query_params.get('queue')
            queue_names = settings.RQ_QUEUES.keys() if hasattr(settings, 'RQ_QUEUES') else []

            if queue_filter:
                queue_names = [q for q in queue_names if q == queue_filter]

            all_jobs = []

            for queue_name in queue_names:
                try:
                    queue = django_rq.get_queue(queue_name)
                    failed_registry = queue.failed_job_registry

                    # Get failed job IDs
                    job_ids = failed_registry.get_job_ids()

                    for job_id in job_ids:
                        try:
                            job = Job.fetch(job_id, connection=queue.connection)

                            # Convert RQ Job to Pydantic model
                            job_model = job_to_model(job, queue_name)

                            # Convert to dict for DRF serializer (JobListSerializer needs minimal fields)
                            job_data = {
                                "id": job_model.id,
                                "func_name": job_model.func_name,
                                "created_at": job_model.created_at,
                                "status": job_model.status,
                                "queue": job_model.queue,
                                "timeout": job_model.timeout,
                            }
                            all_jobs.append(job_data)
                        except Exception as e:
                            # Job was deleted from Redis (expired TTL) - skip silently
                            pass

                except Exception as e:
                    logger.debug(f"Failed to get failed jobs for queue {queue_name}: {e}")

            # Use DRF pagination
            page = self.paginate_queryset(all_jobs)
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
            import django_rq
            from django.conf import settings
            from rq.job import Job

            queue_filter = request.query_params.get('queue')
            queue_names = settings.RQ_QUEUES.keys() if hasattr(settings, 'RQ_QUEUES') else []

            if queue_filter:
                queue_names = [q for q in queue_names if q == queue_filter]

            all_jobs = []

            for queue_name in queue_names:
                try:
                    queue = django_rq.get_queue(queue_name)
                    finished_registry = queue.finished_job_registry

                    # Get finished job IDs
                    job_ids = finished_registry.get_job_ids()

                    for job_id in job_ids:
                        try:
                            job = Job.fetch(job_id, connection=queue.connection)

                            # Convert RQ Job to Pydantic model
                            job_model = job_to_model(job, queue_name)

                            # Convert to dict for DRF serializer (JobListSerializer needs minimal fields)
                            job_data = {
                                "id": job_model.id,
                                "func_name": job_model.func_name,
                                "created_at": job_model.created_at,
                                "status": job_model.status,
                                "queue": job_model.queue,
                                "timeout": job_model.timeout,
                            }
                            all_jobs.append(job_data)
                        except Exception as e:
                            # Job was deleted from Redis (expired TTL) - skip silently
                            pass

                except Exception as e:
                    logger.debug(f"Failed to get finished jobs for queue {queue_name}: {e}")

            # Use DRF pagination
            page = self.paginate_queryset(all_jobs)
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
            import django_rq

            queue_name = request.query_params.get('queue')
            if not queue_name:
                return Response(
                    {"error": "queue parameter is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            queue = django_rq.get_queue(queue_name)
            failed_registry = queue.failed_job_registry

            # Get all failed job IDs
            job_ids = failed_registry.get_job_ids()
            count = len(job_ids)

            # Requeue all
            for job_id in job_ids:
                try:
                    failed_registry.requeue(job_id)
                except Exception as e:
                    logger.debug(f"Failed to requeue job {job_id}: {e}")

            response_data = {
                "success": True,
                "message": f"Requeued {count} failed jobs from queue '{queue_name}'",
                "job_id": None,
                "action": "requeue_all",
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
            import django_rq
            from rq.job import Job

            queue_name = request.query_params.get('queue')
            if not queue_name:
                return Response(
                    {"error": "queue parameter is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            queue = django_rq.get_queue(queue_name)
            failed_registry = queue.failed_job_registry

            # Get all failed job IDs
            job_ids = failed_registry.get_job_ids()
            count = len(job_ids)

            # Delete all failed jobs
            for job_id in job_ids:
                try:
                    job = Job.fetch(job_id, connection=queue.connection)
                    failed_registry.remove(job, delete_job=True)
                except Exception as e:
                    logger.debug(f"Failed to delete job {job_id}: {e}")

            response_data = {
                "success": True,
                "message": f"Cleared {count} failed jobs from queue '{queue_name}'",
                "job_id": None,
                "action": "clear_failed",
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
            import django_rq
            from rq.job import Job

            queue_name = request.query_params.get('queue')
            if not queue_name:
                return Response(
                    {"error": "queue parameter is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            queue = django_rq.get_queue(queue_name)
            finished_registry = queue.finished_job_registry

            # Get all finished job IDs
            job_ids = finished_registry.get_job_ids()
            count = len(job_ids)

            # Delete all finished jobs
            for job_id in job_ids:
                try:
                    job = Job.fetch(job_id, connection=queue.connection)
                    finished_registry.remove(job, delete_job=True)
                except Exception as e:
                    logger.debug(f"Failed to delete job {job_id}: {e}")

            response_data = {
                "success": True,
                "message": f"Cleared {count} finished jobs from queue '{queue_name}'",
                "job_id": None,
                "action": "clear_finished",
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
            import django_rq
            from django.conf import settings
            from rq.job import Job

            queue_filter = request.query_params.get('queue')
            queue_names = settings.RQ_QUEUES.keys() if hasattr(settings, 'RQ_QUEUES') else []

            if queue_filter:
                queue_names = [q for q in queue_names if q == queue_filter]

            all_jobs = []

            for queue_name in queue_names:
                try:
                    queue = django_rq.get_queue(queue_name)
                    deferred_registry = queue.deferred_job_registry

                    # Get deferred job IDs
                    job_ids = deferred_registry.get_job_ids()

                    for job_id in job_ids:
                        try:
                            job = Job.fetch(job_id, connection=queue.connection)

                            # Convert RQ Job to Pydantic model
                            job_model = job_to_model(job, queue_name)

                            # Convert to dict for DRF serializer
                            job_data = {
                                "id": job_model.id,
                                "func_name": job_model.func_name,
                                "created_at": job_model.created_at,
                                "status": job_model.status,
                                "queue": job_model.queue,
                                "timeout": job_model.timeout,
                            }
                            all_jobs.append(job_data)
                        except Exception as e:
                            # Job was deleted from Redis (expired TTL) - skip silently
                            pass

                except Exception as e:
                    logger.debug(f"Failed to get deferred jobs for queue {queue_name}: {e}")

            # Use DRF pagination
            page = self.paginate_queryset(all_jobs)
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
            import django_rq
            from django.conf import settings
            from rq.job import Job

            queue_filter = request.query_params.get('queue')
            queue_names = settings.RQ_QUEUES.keys() if hasattr(settings, 'RQ_QUEUES') else []

            if queue_filter:
                queue_names = [q for q in queue_names if q == queue_filter]

            all_jobs = []

            for queue_name in queue_names:
                try:
                    queue = django_rq.get_queue(queue_name)
                    started_registry = queue.started_job_registry

                    # Get started job IDs
                    job_ids = started_registry.get_job_ids()

                    for job_id in job_ids:
                        try:
                            job = Job.fetch(job_id, connection=queue.connection)

                            # Convert RQ Job to Pydantic model
                            job_model = job_to_model(job, queue_name)

                            # Convert to dict for DRF serializer
                            job_data = {
                                "id": job_model.id,
                                "func_name": job_model.func_name,
                                "created_at": job_model.created_at,
                                "status": job_model.status,
                                "queue": job_model.queue,
                                "timeout": job_model.timeout,
                            }
                            all_jobs.append(job_data)
                        except Exception as e:
                            # Job was deleted from Redis (expired TTL) - skip silently
                            pass

                except Exception as e:
                    logger.debug(f"Failed to get started jobs for queue {queue_name}: {e}")

            # Use DRF pagination
            page = self.paginate_queryset(all_jobs)
            serializer = JobListSerializer(data=page, many=True)
            serializer.is_valid(raise_exception=True)
            return self.get_paginated_response(serializer.data)

        except Exception as e:
            logger.error(f"Started jobs list error: {e}", exc_info=True)
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
