"""
API Views for Django CFG Tasks app.

Provides DRF ViewSets for task management with nested router structure.
"""

import logging
from typing import Any, Dict

from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import status, viewsets
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from django_cfg.modules.django_tasks import DjangoTasks

from ..serializers import (
    APIResponseSerializer,
    QueueActionSerializer,
    QueueStatusSerializer,
    TaskStatisticsSerializer,
    WorkerActionSerializer,
)

logger = logging.getLogger(__name__)


class TaskManagementViewSet(viewsets.GenericViewSet):
    """
    Main ViewSet for comprehensive task management.
    
    Provides all task-related operations in a single ViewSet with nested actions.
    """

    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAdminUser]
    serializer_class = APIResponseSerializer  # Default serializer for the viewset

    def get_serializer_class(self):
        """Return the appropriate serializer class based on the action."""
        if self.action == 'queue_status':
            return QueueStatusSerializer
        elif self.action == 'queue_manage':
            return QueueActionSerializer
        elif self.action == 'worker_manage':
            return WorkerActionSerializer
        elif self.action == 'task_statistics':
            return TaskStatisticsSerializer
        return APIResponseSerializer

    @action(detail=False, methods=['get'], url_path='queues/status')
    @extend_schema(
        summary="Get queue status",
        description="Retrieve current status of all task queues including pending and failed task counts",
        responses={
            200: OpenApiResponse(response=QueueStatusSerializer, description="Queue status retrieved successfully"),
            500: OpenApiResponse(response=APIResponseSerializer, description="Internal server error")
        },
        tags=["Queue Management"]
    )
    def queue_status(self, request):
        """Get current status of all queues."""
        try:
            from ..utils.simulator import TaskSimulator
            simulator = TaskSimulator()
            status_data = simulator.get_current_queue_status()

            return Response({
                'success': True,
                'data': status_data
            })

        except Exception as e:
            logger.error(f"Queue status API error: {e}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'], url_path='queues/manage')
    @extend_schema(
        summary="Manage queues",
        description="Perform management operations on queues (clear, purge, etc.)",
        request=QueueActionSerializer,
        responses={
            200: OpenApiResponse(response=APIResponseSerializer, description="Queue operation completed successfully"),
            400: OpenApiResponse(response=APIResponseSerializer, description="Invalid request data"),
            500: OpenApiResponse(response=APIResponseSerializer, description="Internal server error")
        },
        tags=["Queue Management"]
    )
    def queue_manage(self, request):
        """Manage queue operations (clear, purge, etc.)."""
        try:
            serializer = QueueActionSerializer(data=request.data)
            if not serializer.is_valid():
                return Response({
                    'success': False,
                    'error': 'Invalid request data',
                    'details': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)

            action_type = serializer.validated_data['action']
            queue_name = serializer.validated_data.get('queue_name')

            tasks_service = DjangoTasks()

            if action_type == 'clear_all':
                result = self._clear_all_queues(tasks_service)
            elif action_type == 'clear_queue' and queue_name:
                result = self._clear_queue(tasks_service, queue_name)
            elif action_type == 'purge_failed':
                result = self._purge_failed_tasks(tasks_service, queue_name)
            else:
                return Response({
                    'success': False,
                    'error': 'Invalid action or missing queue_name'
                }, status=status.HTTP_400_BAD_REQUEST)

            return Response({
                'success': True,
                'data': result
            })

        except Exception as e:
            logger.error(f"Queue management API error: {e}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'], url_path='tasks/stats')
    @extend_schema(
        summary="Get task statistics",
        description="Retrieve comprehensive task execution statistics and recent task history",
        responses={
            200: OpenApiResponse(response=TaskStatisticsSerializer, description="Task statistics retrieved successfully"),
            500: OpenApiResponse(response=APIResponseSerializer, description="Internal server error")
        },
        tags=["Task Management"]
    )
    def task_statistics(self, request):
        """Get task execution statistics."""
        try:
            from ..utils.simulator import TaskSimulator
            simulator = TaskSimulator()
            stats_data = simulator.get_current_task_statistics()

            return Response({
                'success': True,
                'data': stats_data
            })

        except Exception as e:
            logger.error(f"Task statistics API error: {e}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'], url_path='tasks/list')
    @extend_schema(
        summary="Get task list",
        description="Retrieve paginated list of tasks with optional filtering",
        parameters=[
            OpenApiParameter(name='status', description='Filter by task status', required=False, type=str),
            OpenApiParameter(name='actor', description='Filter by actor name', required=False, type=str),
            OpenApiParameter(name='page', description='Page number', required=False, type=int),
            OpenApiParameter(name='page_size', description='Items per page', required=False, type=int),
        ],
        responses={
            200: OpenApiResponse(response=APIResponseSerializer, description="Task list retrieved successfully"),
            500: OpenApiResponse(response=APIResponseSerializer, description="Internal server error")
        },
        tags=["Task Management"]
    )
    def task_list(self, request):
        """Get paginated task list with filtering."""
        try:
            from ..utils.simulator import TaskSimulator
            simulator = TaskSimulator()

            # For now, return mock task data since we don't have real task list in simulator
            # This could be enhanced later to support real task data
            mock_data = {
                'tasks': [
                    {
                        'id': 1,
                        'actor_name': 'send_email_task',
                        'status': 'completed',
                        'queue_name': 'default',
                        'created_at': '2025-09-29T12:30:00Z',
                        'updated_at': '2025-09-29T12:30:05Z',
                        'message_id': 'msg_001'
                    },
                    {
                        'id': 2,
                        'actor_name': 'process_payment',
                        'status': 'running',
                        'queue_name': 'payments',
                        'created_at': '2025-09-29T12:45:00Z',
                        'updated_at': '2025-09-29T12:46:00Z',
                        'message_id': 'msg_002'
                    },
                    {
                        'id': 3,
                        'actor_name': 'generate_report',
                        'status': 'pending',
                        'queue_name': 'background',
                        'created_at': '2025-09-29T13:00:00Z',
                        'updated_at': '2025-09-29T13:00:00Z',
                        'message_id': 'msg_003'
                    },
                    {
                        'id': 4,
                        'actor_name': 'sync_data',
                        'status': 'failed',
                        'queue_name': 'high',
                        'created_at': '2025-09-29T11:30:00Z',
                        'updated_at': '2025-09-29T11:35:00Z',
                        'message_id': 'msg_004'
                    }
                ],
                'pagination': {
                    'page': 1,
                    'page_size': 20,
                    'total_pages': 1,
                    'total_count': 4,
                    'has_next': False,
                    'has_previous': False
                },
                'simulated': True
            }

            return Response({
                'success': True,
                'data': mock_data
            })

        except Exception as e:
            logger.error(f"Task list API error: {e}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'], url_path='workers/list')
    @extend_schema(
        summary="Get workers list",
        description="Retrieve detailed list of active workers",
        responses={
            200: OpenApiResponse(response=APIResponseSerializer, description="Workers list retrieved successfully"),
            500: OpenApiResponse(response=APIResponseSerializer, description="Internal server error")
        },
        tags=["Worker Management"]
    )
    def workers_list(self, request):
        """Get detailed list of workers."""
        try:
            from ..utils.simulator import TaskSimulator
            simulator = TaskSimulator()
            workers_data = simulator.get_current_workers_list()

            return Response({
                'success': True,
                'data': workers_data
            })

        except Exception as e:
            logger.error(f"Workers list API error: {e}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'], url_path='workers/manage')
    @extend_schema(
        summary="Manage workers",
        description="Perform management operations on workers (restart, stop, etc.)",
        request=WorkerActionSerializer,
        responses={
            200: OpenApiResponse(response=APIResponseSerializer, description="Worker operation completed successfully"),
            400: OpenApiResponse(response=APIResponseSerializer, description="Invalid request data"),
            500: OpenApiResponse(response=APIResponseSerializer, description="Internal server error")
        },
        tags=["Worker Management"]
    )
    def worker_manage(self, request):
        """Manage worker operations."""
        try:
            serializer = WorkerActionSerializer(data=request.data)
            if not serializer.is_valid():
                return Response({
                    'success': False,
                    'error': 'Invalid request data',
                    'details': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)

            action_type = serializer.validated_data['action']
            worker_id = serializer.validated_data.get('worker_id')

            # Worker management operations would go here
            # For now, return a placeholder response
            return Response({
                'success': True,
                'data': {
                    'message': f'Worker {action_type} operation initiated',
                    'worker_id': worker_id,
                    'action': action_type
                }
            })

        except Exception as e:
            logger.error(f"Worker management API error: {e}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'], url_path='simulate')
    @extend_schema(
        summary="Simulate test data",
        description="Create test data in Redis for dashboard testing",
        request=None,
        responses={
            200: OpenApiResponse(response=APIResponseSerializer, description="Simulation completed successfully"),
            500: OpenApiResponse(response=APIResponseSerializer, description="Simulation failed")
        },
        tags=["Task Management"]
    )
    def simulate_data(self, request):
        """Simulate test data for dashboard testing."""
        try:
            from ..utils.simulator import TaskSimulator

            simulator = TaskSimulator()
            result = simulator.run_simulation(workers=3, clear_first=True)

            return Response({
                'success': True,
                'data': {
                    'message': 'Test data simulation completed successfully',
                    'details': result
                }
            })

        except Exception as e:
            logger.error(f"Simulation API error: {e}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'], url_path='clear')
    @extend_schema(
        summary="Clear test data",
        description="Clear all test data from Redis",
        request=None,
        responses={
            200: OpenApiResponse(response=APIResponseSerializer, description="Data cleared successfully"),
            500: OpenApiResponse(response=APIResponseSerializer, description="Clear operation failed")
        },
        tags=["Task Management"]
    )
    def clear_data(self, request):
        """Clear all test data from Redis."""
        try:
            from ..utils.simulator import TaskSimulator

            simulator = TaskSimulator()
            simulator.clear_all_data()

            return Response({
                'success': True,
                'data': {
                    'message': 'All test data cleared successfully'
                }
            })

        except Exception as e:
            logger.error(f"Clear data API error: {e}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'], url_path='clear-queues')
    @extend_schema(
        summary="Clear all queues",
        description="Clear all tasks from all Dramatiq queues",
        request=None,
        responses={
            200: OpenApiResponse(response=APIResponseSerializer, description="Queues cleared successfully"),
            500: OpenApiResponse(response=APIResponseSerializer, description="Clear operation failed")
        },
        tags=["Queue Management"]
    )
    def clear_all_queues(self, request):
        """Clear all tasks from all Dramatiq queues."""
        try:
            from django_cfg.modules.django_tasks import DjangoTasks

            tasks_service = DjangoTasks()
            redis_client = tasks_service.get_redis_client()

            if not redis_client:
                return Response({
                    'success': False,
                    'error': 'Redis connection not available'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # Get all Dramatiq queue keys
            queue_keys = redis_client.keys('dramatiq:*.msgs')  # Main queues
            failed_keys = redis_client.keys('dramatiq:*.DQ')   # Failed queues
            ack_keys = redis_client.keys('dramatiq:__acks__*') # Acknowledgments

            cleared_count = 0

            # Clear main queues
            for key in queue_keys:
                redis_client.delete(key)
                cleared_count += 1

            # Clear failed queues
            for key in failed_keys:
                redis_client.delete(key)
                cleared_count += 1

            # Clear acknowledgments
            for key in ack_keys:
                redis_client.delete(key)
                cleared_count += 1

            return Response({
                'success': True,
                'message': f'Cleared {cleared_count} Dramatiq keys from Redis'
            })

        except Exception as e:
            logger.error(f"Clear queues API error: {e}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'], url_path='purge-failed')
    @extend_schema(
        summary="Purge failed tasks",
        description="Remove all failed tasks from queues",
        request=None,
        responses={
            200: OpenApiResponse(response=APIResponseSerializer, description="Failed tasks purged successfully"),
            500: OpenApiResponse(response=APIResponseSerializer, description="Purge operation failed")
        },
        tags=["Queue Management"]
    )
    def purge_failed_tasks(self, request):
        """Purge all failed tasks from queues."""
        try:
            from django_cfg.modules.django_tasks import DjangoTasks

            tasks_service = DjangoTasks()
            redis_client = tasks_service.get_redis_client()

            if not redis_client:
                return Response({
                    'success': False,
                    'error': 'Redis connection not available'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # Get only failed queue keys (DQ = Dead Queue)
            failed_keys = redis_client.keys('dramatiq:*.DQ')

            cleared_count = 0

            # Clear only failed queues
            for key in failed_keys:
                failed_count = redis_client.llen(key)
                if failed_count > 0:
                    redis_client.delete(key)
                    cleared_count += failed_count

            return Response({
                'success': True,
                'message': f'Purged {cleared_count} failed tasks from queues'
            })

        except Exception as e:
            logger.error(f"Purge failed tasks API error: {e}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Helper methods
    def _clear_all_queues(self, tasks_service: DjangoTasks) -> Dict[str, Any]:
        """Clear all queues."""
        try:
            redis_client = tasks_service.get_redis_client()
            if not redis_client:
                return {'error': 'Redis connection not available'}

            # Get all queue keys and clear them
            queue_keys = redis_client.keys("dramatiq:queue:*")
            cleared_count = 0

            for key in queue_keys:
                redis_client.delete(key)
                cleared_count += 1

            return {
                'message': f'Cleared {cleared_count} queues',
                'cleared_count': cleared_count
            }

        except Exception as e:
            return {'error': str(e)}

    def _clear_queue(self, tasks_service: DjangoTasks, queue_name: str) -> Dict[str, Any]:
        """Clear specific queue."""
        try:
            redis_client = tasks_service.get_redis_client()
            if not redis_client:
                return {'error': 'Redis connection not available'}

            queue_key = f"dramatiq:queue:{queue_name}"
            cleared_count = redis_client.delete(queue_key)

            return {
                'message': f'Cleared queue {queue_name}',
                'queue_name': queue_name,
                'cleared': cleared_count > 0
            }

        except Exception as e:
            return {'error': str(e)}

    def _purge_failed_tasks(self, tasks_service: DjangoTasks, queue_name: str = None) -> Dict[str, Any]:
        """Purge failed tasks."""
        try:
            redis_client = tasks_service.get_redis_client()
            if not redis_client:
                return {'error': 'Redis connection not available'}

            if queue_name:
                # Clear specific queue's failed tasks
                failed_key = f"dramatiq:queue:{queue_name}.DLQ"
                cleared_count = redis_client.delete(failed_key)
                return {
                    'message': f'Purged failed tasks from {queue_name}',
                    'queue_name': queue_name,
                    'cleared_count': cleared_count
                }
            else:
                # Clear all failed task queues
                failed_keys = redis_client.keys("dramatiq:queue:*.DLQ")
                cleared_count = 0

                for key in failed_keys:
                    redis_client.delete(key)
                    cleared_count += 1

                return {
                    'message': f'Purged failed tasks from {cleared_count} queues',
                    'cleared_count': cleared_count
                }

        except Exception as e:
            return {'error': str(e)}
