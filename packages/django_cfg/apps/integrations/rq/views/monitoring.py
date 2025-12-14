"""
Django-RQ Monitoring ViewSet.

Provides REST API endpoints for RQ health checks and configuration.
"""

from datetime import datetime

from django_cfg.mixins import AdminAPIMixin
from django_cfg.utils import get_logger
from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from ..serializers import HealthCheckSerializer, RQConfigSerializer

logger = get_logger("rq.monitoring")


class RQMonitorViewSet(AdminAPIMixin, viewsets.ViewSet):
    """
    ViewSet for RQ monitoring and health checks.

    Provides endpoints for:
    - Health check (cluster status)
    - Configuration view
    - Prometheus metrics

    Requires admin authentication (JWT, Session, or Basic Auth).
    """

    @extend_schema(
        tags=["RQ Monitoring"],
        summary="Health check",
        description="Returns RQ cluster health status including worker count and queue status.",
        responses={
            200: HealthCheckSerializer,
        },
    )
    @action(detail=False, methods=["get"], url_path="health")
    def health(self, request):
        """Health check endpoint."""
        try:
            import django_rq
            from rq import Worker

            # Check Redis connection
            redis_connected = True
            worker_count = 0
            total_jobs = 0
            queue_count = 0

            try:
                # Get all queues
                from django.conf import settings

                queue_names = settings.RQ_QUEUES.keys() if hasattr(settings, 'RQ_QUEUES') else []
                queue_count = len(queue_names)

                # Count workers per queue (use set to avoid duplicates)
                worker_names = set()
                for queue_name in queue_names:
                    try:
                        queue = django_rq.get_queue(queue_name)
                        # Get workers for this queue's connection
                        queue_workers = Worker.all(connection=queue.connection)
                        worker_names.update(w.name for w in queue_workers)
                        # Count jobs
                        total_jobs += queue.count
                    except Exception as e:
                        logger.debug(f"Failed to get queue {queue_name}: {e}")

                worker_count = len(worker_names)

            except Exception as e:
                logger.error(f"Redis connection error: {e}", exc_info=True)
                redis_connected = False

            # Determine health status
            if not redis_connected:
                health_status = "unhealthy"
            elif worker_count == 0:
                health_status = "degraded"
            else:
                health_status = "healthy"

            health_data = {
                "status": health_status,
                "worker_count": worker_count,
                "queue_count": queue_count,
                "total_jobs": total_jobs,
                "timestamp": datetime.now().isoformat(),
                "enabled": True,
                "redis_connected": redis_connected,
                "wrapper_url": "",  # Empty for now, can be configured later
                "has_api_key": False,  # No API key required for RQ
            }

            serializer = HealthCheckSerializer(data=health_data)
            serializer.is_valid(raise_exception=True)
            return Response(serializer.data)

        except Exception as e:
            logger.error(f"Health check error: {e}", exc_info=True)
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @extend_schema(
        tags=["RQ Monitoring"],
        summary="Get RQ configuration",
        description="Returns current RQ configuration from django-cfg.",
        responses={
            200: RQConfigSerializer,
        },
    )
    @action(detail=False, methods=["get"], url_path="config")
    def config(self, request):
        """Get RQ configuration."""
        try:
            from django.conf import settings
            from ..services import get_rq_config

            # Get configuration
            queues = {}
            if hasattr(settings, 'RQ_QUEUES'):
                # Sanitize queue config (hide passwords)
                for name, config in settings.RQ_QUEUES.items():
                    queues[name] = {
                        k: v if k not in ('PASSWORD', 'password') else '***'
                        for k, v in config.items()
                    }

            async_mode = True
            show_admin_link = getattr(settings, 'RQ_SHOW_ADMIN_LINK', True)
            api_token_configured = bool(getattr(settings, 'RQ_API_TOKEN', None))

            # Check prometheus
            prometheus_enabled = True
            try:
                import prometheus_client  # noqa: F401
            except ImportError:
                prometheus_enabled = False

            # Get scheduled tasks from django-cfg config
            schedules = []
            rq_config = get_rq_config()
            if rq_config and hasattr(rq_config, 'schedules'):
                for schedule in rq_config.schedules:
                    schedules.append({
                        "func": schedule.func,
                        "queue": schedule.queue,
                        "cron": schedule.cron,
                        "interval": schedule.interval,
                        "scheduled_time": schedule.scheduled_time,
                        "description": schedule.description,
                        "timeout": schedule.timeout,
                        "result_ttl": schedule.result_ttl,
                        "repeat": schedule.repeat,
                    })

            config_data = {
                "enabled": True,
                "queues": queues,
                "async_mode": async_mode,
                "show_admin_link": show_admin_link,
                "prometheus_enabled": prometheus_enabled,
                "api_token_configured": api_token_configured,
                "schedules": schedules,
            }

            serializer = RQConfigSerializer(data=config_data)
            serializer.is_valid(raise_exception=True)
            return Response(serializer.data)

        except Exception as e:
            logger.error(f"Config error: {e}", exc_info=True)
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @extend_schema(
        tags=["RQ Monitoring"],
        summary="Prometheus metrics",
        description="Returns Prometheus metrics for RQ queues and workers.",
        responses={
            200: {"description": "Prometheus metrics in text format"},
        },
    )
    @action(detail=False, methods=["get"], url_path="metrics")
    def metrics(self, request):
        """
        Prometheus metrics endpoint.

        Uses django-rq's built-in RQCollector for comprehensive metrics:
        - rq_workers: Worker count by name, state, and queues
        - rq_job_successful_total: Successful job count per worker
        - rq_job_failed_total: Failed job count per worker
        - rq_working_seconds_total: Total working time per worker
        - rq_jobs: Job count by queue and status (queued, started, finished, failed, deferred, scheduled)
        """
        try:
            # Try to import prometheus_client and RQCollector
            try:
                from prometheus_client import CollectorRegistry
                from prometheus_client.exposition import choose_encoder
            except ImportError:
                return Response(
                    {"error": "prometheus_client not installed. Install with: pip install django-rq[prometheus]"},
                    status=status.HTTP_501_NOT_IMPLEMENTED,
                )

            try:
                from django_rq.contrib.prometheus import RQCollector
            except ImportError:
                return Response(
                    {"error": "RQCollector not available. Ensure prometheus_client is installed."},
                    status=status.HTTP_501_NOT_IMPLEMENTED,
                )

            # Create registry and register RQCollector
            registry = CollectorRegistry(auto_describe=True)
            registry.register(RQCollector())

            # Choose encoder based on Accept header
            encoder, content_type = choose_encoder(request.META.get('HTTP_ACCEPT', ''))

            # Support filtering by metric name (Prometheus query param)
            if 'name[]' in request.GET:
                registry = registry.restricted_registry(request.GET.getlist('name[]'))

            # Generate and return metrics
            metrics_output = encoder(registry)

            return Response(
                metrics_output,
                content_type=content_type,
            )

        except Exception as e:
            logger.error(f"Metrics error: {e}", exc_info=True)
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
