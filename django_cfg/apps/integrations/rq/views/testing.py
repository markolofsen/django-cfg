"""
Django-RQ Testing & Simulation ViewSet.

Provides REST API endpoints for testing RQ functionality from the frontend.
"""

import time
from datetime import datetime, timezone

from django_cfg.mixins import AdminAPIMixin
from django_cfg.utils import get_logger
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from ..serializers import (
    TestScenarioSerializer,
    RunDemoRequestSerializer,
    StressTestRequestSerializer,
    TestingActionResponseSerializer,
    CleanupRequestSerializer,
)

logger = get_logger("rq.testing")


class TestingViewSet(AdminAPIMixin, viewsets.ViewSet):
    """
    ViewSet for RQ testing and simulation.

    Provides endpoints for:
    - List available test scenarios
    - Run demo tasks
    - Stress testing (generate N jobs)
    - Schedule demo tasks
    - Simulate queue load
    - Cleanup test jobs
    - Get test results

    Requires admin authentication (JWT, Session, or Basic Auth).

    Security:
    - Admin-only access via AdminAPIMixin
    - Rate limiting on stress test endpoints
    - Resource limits on memory/CPU intensive tasks
    - Can be disabled in production via config
    """

    # Scenario definitions
    SCENARIOS = {
        'heartbeat': {
            'id': 'heartbeat',
            'name': 'Scheduler Heartbeat',
            'description': 'Simple heartbeat task for testing RQ scheduler (development mode only)',
            'task_func': 'django_cfg.apps.integrations.rq.tasks.demo_tasks.demo_scheduler_heartbeat',
            'default_args': [],
            'default_kwargs': {},
            'estimated_duration': 1,
        },
    }

    @extend_schema(
        tags=["RQ Testing"],
        summary="List test scenarios",
        description="Returns list of all available test scenarios with metadata.",
        responses={
            200: TestScenarioSerializer(many=True),
        },
    )
    def list(self, request):
        """List all available test scenarios."""
        try:
            scenarios = list(self.SCENARIOS.values())
            serializer = TestScenarioSerializer(data=scenarios, many=True)
            serializer.is_valid(raise_exception=True)
            return Response(serializer.data)

        except Exception as e:
            logger.error(f"Failed to list scenarios: {e}", exc_info=True)
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @extend_schema(
        tags=["RQ Testing"],
        summary="Run demo task",
        description="Enqueue a single demo task for testing.",
        request=RunDemoRequestSerializer,
        responses={
            200: TestingActionResponseSerializer,
        },
    )
    @action(detail=False, methods=["post"], url_path="run-demo")
    def run_demo(self, request):
        """Run a single demo task."""
        try:
            import django_rq

            serializer = RunDemoRequestSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            data = serializer.validated_data

            scenario_id = data['scenario']
            queue_name = data.get('queue', 'default')

            # Get scenario config
            scenario = self.SCENARIOS.get(scenario_id)
            if not scenario:
                return Response(
                    {"error": f"Unknown scenario: {scenario_id}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Import task function
            task_func_path = scenario['task_func']
            module_path, func_name = task_func_path.rsplit('.', 1)

            try:
                import importlib
                module = importlib.import_module(module_path)
                task_func = getattr(module, func_name)
            except (ImportError, AttributeError) as e:
                logger.error(f"Failed to import task {task_func_path}: {e}")
                return Response(
                    {"error": f"Failed to import task function: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            # Merge kwargs (user overrides defaults)
            kwargs = {**scenario['default_kwargs'], **data.get('kwargs', {})}
            args = data.get('args', [])

            # Get queue
            queue = django_rq.get_queue(queue_name)

            # Enqueue job
            job = queue.enqueue(
                task_func,
                args=args,
                kwargs=kwargs,
                timeout=data.get('timeout'),
                meta={
                    'source': 'testing',
                    'scenario': scenario_id,
                    'created_via': 'testing_api',
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                },
            )

            response_data = {
                "success": True,
                "message": f"Demo task '{scenario['name']}' enqueued successfully",
                "job_ids": [job.id],
                "metadata": {
                    "scenario": scenario_id,
                    "queue": queue_name,
                    "func": task_func_path,
                    "estimated_duration": scenario.get('estimated_duration'),
                },
            }

            logger.info(f"Enqueued demo task: {scenario_id} -> {job.id}")

            response_serializer = TestingActionResponseSerializer(data=response_data)
            response_serializer.is_valid(raise_exception=True)
            return Response(response_serializer.data)

        except Exception as e:
            logger.error(f"Failed to run demo task: {e}", exc_info=True)
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @extend_schema(
        tags=["RQ Testing"],
        summary="Stress test",
        description="Generate N jobs for load testing and performance benchmarking.",
        request=StressTestRequestSerializer,
        responses={
            200: TestingActionResponseSerializer,
        },
    )
    @action(detail=False, methods=["post"], url_path="stress-test")
    def stress_test(self, request):
        """Generate N jobs for stress testing."""
        try:
            import django_rq

            serializer = StressTestRequestSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            data = serializer.validated_data

            num_jobs = data['num_jobs']
            queue_name = data.get('queue', 'default')
            scenario_id = data.get('scenario', 'success')
            duration = data.get('duration', 2)

            # Get scenario
            scenario = self.SCENARIOS.get(scenario_id)
            if not scenario:
                return Response(
                    {"error": f"Unknown scenario: {scenario_id}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Import task function
            task_func_path = scenario['task_func']
            module_path, func_name = task_func_path.rsplit('.', 1)

            try:
                import importlib
                module = importlib.import_module(module_path)
                task_func = getattr(module, func_name)
            except (ImportError, AttributeError) as e:
                return Response(
                    {"error": f"Failed to import task: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            # Get queue
            queue = django_rq.get_queue(queue_name)

            # Enqueue jobs
            job_ids = []
            for i in range(num_jobs):
                # Override duration for stress test
                kwargs = {**scenario['default_kwargs'], 'duration': duration}

                job = queue.enqueue(
                    task_func,
                    kwargs=kwargs,
                    meta={
                        'source': 'testing',
                        'scenario': scenario_id,
                        'created_via': 'stress_test',
                        'test_index': i + 1,
                        'timestamp': datetime.now(timezone.utc).isoformat(),
                    },
                )
                job_ids.append(job.id)

            estimated_total_time = num_jobs * duration

            response_data = {
                "success": True,
                "message": f"Created {num_jobs} stress test jobs",
                "job_ids": job_ids,
                "count": num_jobs,
                "metadata": {
                    "scenario": scenario_id,
                    "queue": queue_name,
                    "duration_per_job": duration,
                    "estimated_total_time": estimated_total_time,
                },
            }

            logger.info(f"Created {num_jobs} stress test jobs for scenario '{scenario_id}'")

            response_serializer = TestingActionResponseSerializer(data=response_data)
            response_serializer.is_valid(raise_exception=True)
            return Response(response_serializer.data)

        except Exception as e:
            logger.error(f"Stress test failed: {e}", exc_info=True)
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @extend_schema(
        tags=["RQ Testing"],
        summary="Schedule demo tasks",
        description="Register demo scheduled tasks using rq-scheduler.",
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'scenario': {'type': 'string'},
                    'schedule_type': {'type': 'string', 'enum': ['interval', 'cron', 'one-time']},
                    'interval': {'type': 'integer'},
                    'cron': {'type': 'string'},
                    'scheduled_time': {'type': 'string', 'format': 'date-time'},
                    'queue': {'type': 'string'},
                    'repeat': {'type': 'integer'},
                },
                'required': ['scenario', 'schedule_type'],
            }
        },
        responses={
            200: TestingActionResponseSerializer,
        },
    )
    @action(detail=False, methods=["post"], url_path="schedule-demo")
    def schedule_demo(self, request):
        """Schedule a demo task."""
        try:
            import django_rq
            from django.core.exceptions import ImproperlyConfigured

            data = request.data
            scenario_id = data.get('scenario')
            schedule_type = data.get('schedule_type')
            queue_name = data.get('queue', 'default')

            # Validate scenario
            scenario = self.SCENARIOS.get(scenario_id)
            if not scenario:
                return Response(
                    {"error": f"Unknown scenario: {scenario_id}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Import task function
            task_func_path = scenario['task_func']
            module_path, func_name = task_func_path.rsplit('.', 1)

            try:
                import importlib
                module = importlib.import_module(module_path)
                task_func = getattr(module, func_name)
            except (ImportError, AttributeError) as e:
                return Response(
                    {"error": f"Failed to import task: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            # Get scheduler
            try:
                scheduler = django_rq.get_scheduler(queue_name)
            except ImproperlyConfigured:
                return Response(
                    {"error": "rq-scheduler not installed. Install with: pip install rq-scheduler"},
                    status=status.HTTP_501_NOT_IMPLEMENTED,
                )

            # Schedule job based on type
            job_kwargs = {
                'func': task_func,
                'kwargs': scenario['default_kwargs'],
                'queue_name': queue_name,
            }

            if data.get('repeat') is not None:
                job_kwargs['repeat'] = data['repeat']

            if schedule_type == 'interval':
                interval = data.get('interval')
                if not interval:
                    return Response(
                        {"error": "interval is required for interval schedule"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                job = scheduler.schedule(
                    scheduled_time=datetime.now(timezone.utc),
                    interval=interval,
                    **job_kwargs
                )

            elif schedule_type == 'cron':
                cron_string = data.get('cron')
                if not cron_string:
                    return Response(
                        {"error": "cron is required for cron schedule"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                job = scheduler.cron(cron_string, **job_kwargs)

            elif schedule_type == 'one-time':
                scheduled_time = data.get('scheduled_time')
                if not scheduled_time:
                    return Response(
                        {"error": "scheduled_time is required for one-time schedule"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                scheduled_dt = datetime.fromisoformat(scheduled_time.replace('Z', '+00:00'))
                job = scheduler.enqueue_at(scheduled_dt, **job_kwargs)

            else:
                return Response(
                    {"error": f"Invalid schedule_type: {schedule_type}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Update job meta
            if job:
                job.meta = {
                    'source': 'testing',
                    'scenario': scenario_id,
                    'created_via': 'schedule_demo',
                    'schedule_type': schedule_type,
                }
                job.save_meta()

            response_data = {
                "success": True,
                "message": f"Demo schedule registered ({schedule_type})",
                "job_ids": [job.id] if job else [],
                "metadata": {
                    "schedule_type": schedule_type,
                    "scenario": scenario_id,
                    "queue": queue_name,
                },
            }

            logger.info(f"Scheduled demo task: {scenario_id} ({schedule_type})")

            response_serializer = TestingActionResponseSerializer(data=response_data)
            response_serializer.is_valid(raise_exception=True)
            return Response(response_serializer.data)

        except Exception as e:
            logger.error(f"Failed to schedule demo: {e}", exc_info=True)
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @extend_schema(
        tags=["RQ Testing"],
        summary="Cleanup test jobs",
        description="Clean demo jobs from registries.",
        request=CleanupRequestSerializer,
        parameters=[
            OpenApiParameter(
                name="queue",
                type=str,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Queue name (empty = all queues)",
            ),
            OpenApiParameter(
                name="registries",
                type=str,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Comma-separated list of registries (failed,finished,deferred,scheduled)",
            ),
            OpenApiParameter(
                name="delete_demo_jobs_only",
                type=bool,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Only delete demo jobs (default: true)",
            ),
        ],
        responses={
            200: TestingActionResponseSerializer,
        },
    )
    @action(detail=False, methods=["delete"])
    def cleanup(self, request):
        """Cleanup test jobs from registries."""
        try:
            import django_rq
            from django.conf import settings
            from rq.job import Job
            from rq.registry import (
                FinishedJobRegistry,
                FailedJobRegistry,
                DeferredJobRegistry,
                ScheduledJobRegistry,
            )

            queue_filter = request.query_params.get('queue')
            registries_param = request.query_params.get('registries', 'failed,finished')
            delete_demo_only = request.query_params.get('delete_demo_jobs_only', 'true').lower() == 'true'

            # Parse registries
            registry_names = [r.strip() for r in registries_param.split(',') if r.strip()]

            # Get queues
            if queue_filter:
                queue_names = [queue_filter]
            else:
                queue_names = list(settings.RQ_QUEUES.keys()) if hasattr(settings, 'RQ_QUEUES') else []

            total_deleted = 0
            breakdown = {}

            for queue_name in queue_names:
                try:
                    queue = django_rq.get_queue(queue_name)

                    # Get registries to clean
                    registries_to_clean = {}
                    if 'failed' in registry_names:
                        registries_to_clean['failed'] = FailedJobRegistry(queue_name, connection=queue.connection)
                    if 'finished' in registry_names:
                        registries_to_clean['finished'] = FinishedJobRegistry(queue_name, connection=queue.connection)
                    if 'deferred' in registry_names:
                        registries_to_clean['deferred'] = DeferredJobRegistry(queue_name, connection=queue.connection)
                    if 'scheduled' in registry_names:
                        registries_to_clean['scheduled'] = ScheduledJobRegistry(queue_name, connection=queue.connection)

                    # Clean from registries
                    for reg_name, registry in registries_to_clean.items():
                        job_ids = registry.get_job_ids()
                        deleted_count = 0

                        for job_id in job_ids:
                            try:
                                job = Job.fetch(job_id, connection=queue.connection)

                                # Check if it's a demo job
                                is_demo_job = False
                                if job.meta and job.meta.get('source') == 'testing':
                                    is_demo_job = True
                                elif job.func_name and 'demo_' in job.func_name:
                                    is_demo_job = True

                                # Delete if matches criteria
                                if not delete_demo_only or is_demo_job:
                                    registry.remove(job, delete_job=True)
                                    deleted_count += 1

                            except Exception as e:
                                logger.debug(f"Failed to delete job {job_id}: {e}")

                        breakdown[reg_name] = breakdown.get(reg_name, 0) + deleted_count
                        total_deleted += deleted_count

                    # Also clean from queued jobs (not in registry, but in queue itself)
                    if 'queued' in registry_names:
                        queued_job_ids = queue.job_ids
                        deleted_count = 0

                        for job_id in queued_job_ids:
                            try:
                                job = Job.fetch(job_id, connection=queue.connection)

                                # Check if it's a demo job
                                is_demo_job = False
                                if job.meta and job.meta.get('source') == 'testing':
                                    is_demo_job = True
                                elif job.func_name and 'demo_' in job.func_name:
                                    is_demo_job = True

                                # Delete if matches criteria
                                if not delete_demo_only or is_demo_job:
                                    job.cancel()
                                    job.delete()
                                    deleted_count += 1

                            except Exception as e:
                                logger.debug(f"Failed to delete queued job {job_id}: {e}")

                        breakdown['queued'] = breakdown.get('queued', 0) + deleted_count
                        total_deleted += deleted_count

                except Exception as e:
                    logger.debug(f"Failed to clean queue {queue_name}: {e}")

            response_data = {
                "success": True,
                "message": f"Cleaned {total_deleted} {'demo ' if delete_demo_only else ''}jobs",
                "count": total_deleted,
                "metadata": {
                    "queues_cleaned": queue_names,
                    "registries_cleaned": registry_names,
                    "demo_jobs_only": delete_demo_only,
                    "breakdown": breakdown,
                },
            }

            logger.info(f"Cleaned {total_deleted} test jobs from {len(queue_names)} queues")

            response_serializer = TestingActionResponseSerializer(data=response_data)
            response_serializer.is_valid(raise_exception=True)
            return Response(response_serializer.data)

        except Exception as e:
            logger.error(f"Cleanup failed: {e}", exc_info=True)
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @extend_schema(
        tags=["RQ Testing"],
        summary="Get test results",
        description="Get aggregated results of test jobs execution.",
        parameters=[
            OpenApiParameter(
                name="queue",
                type=str,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Filter by queue",
            ),
            OpenApiParameter(
                name="scenario",
                type=str,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Filter by scenario",
            ),
        ],
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'total_jobs': {'type': 'integer'},
                    'by_status': {'type': 'object'},
                    'by_scenario': {'type': 'object'},
                },
            },
        },
    )
    @action(detail=False, methods=["get"])
    def results(self, request):
        """Get test execution results."""
        try:
            import django_rq
            from django.conf import settings
            from rq.job import Job
            from rq.registry import (
                FinishedJobRegistry,
                FailedJobRegistry,
                StartedJobRegistry,
            )

            queue_filter = request.query_params.get('queue')
            scenario_filter = request.query_params.get('scenario')

            queue_names = list(settings.RQ_QUEUES.keys()) if hasattr(settings, 'RQ_QUEUES') else []
            if queue_filter:
                queue_names = [q for q in queue_names if q == queue_filter]

            total_jobs = 0
            by_status = {'finished': 0, 'failed': 0, 'queued': 0, 'started': 0}
            by_scenario = {}

            for queue_name in queue_names:
                try:
                    queue = django_rq.get_queue(queue_name)

                    # Check all registries
                    registries = {
                        'queued': {'jobs': queue.job_ids},
                        'started': {'registry': StartedJobRegistry(queue_name, connection=queue.connection)},
                        'finished': {'registry': FinishedJobRegistry(queue_name, connection=queue.connection)},
                        'failed': {'registry': FailedJobRegistry(queue_name, connection=queue.connection)},
                    }

                    for reg_name, reg_data in registries.items():
                        if 'registry' in reg_data:
                            job_ids = reg_data['registry'].get_job_ids()
                        else:
                            job_ids = reg_data['jobs']

                        for job_id in job_ids:
                            try:
                                job = Job.fetch(job_id, connection=queue.connection)

                                # Filter demo jobs only
                                if not job.meta or job.meta.get('source') != 'testing':
                                    continue

                                scenario = job.meta.get('scenario', 'unknown')

                                # Apply scenario filter
                                if scenario_filter and scenario != scenario_filter:
                                    continue

                                total_jobs += 1
                                by_status[reg_name] += 1

                                if scenario not in by_scenario:
                                    by_scenario[scenario] = {'total': 0, 'finished': 0, 'failed': 0}

                                by_scenario[scenario]['total'] += 1
                                if reg_name in ['finished', 'failed']:
                                    by_scenario[scenario][reg_name] += 1

                            except Exception:
                                continue

                except Exception as e:
                    logger.debug(f"Failed to get results for queue {queue_name}: {e}")

            return Response({
                "total_jobs": total_jobs,
                "by_status": by_status,
                "by_scenario": by_scenario,
            })

        except Exception as e:
            logger.error(f"Failed to get results: {e}", exc_info=True)
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
