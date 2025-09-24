"""
Views for Django CFG Tasks app.

Provides DRF ViewSets for task management with nested router structure.
"""

import logging
from typing import Dict, Any

from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter

from ...modules.django_tasks import DjangoTasks
from .serializers import (
    QueueStatusSerializer,
    TaskStatisticsSerializer,
    WorkerActionSerializer,
    QueueActionSerializer,
    APIResponseSerializer
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
        return super().get_serializer_class()
    
    def get_tasks_service(self):
        """Get DjangoTasks service instance."""
        return DjangoTasks()
    
    @action(detail=False, methods=['get'], url_path='queues/status')
    @extend_schema(
        summary="Get queue status",
        description="Retrieve current status of all task queues including pending and failed counts",
        responses={
            200: OpenApiResponse(response=QueueStatusSerializer, description="Queue status retrieved successfully"),
            500: OpenApiResponse(response=APIResponseSerializer, description="Internal server error")
        },
        tags=["Task Management"]
    )
    def queue_status(self, request):
        """Get current queue status."""
        try:
            tasks_service = self.get_tasks_service()
            status_data = self._get_queue_status(tasks_service)
            
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
        description="Clear, purge, or flush task queues",
        request=QueueActionSerializer,
        responses={
            200: OpenApiResponse(response=APIResponseSerializer, description="Queue action completed successfully"),
            400: OpenApiResponse(response=APIResponseSerializer, description="Invalid request data"),
            500: OpenApiResponse(response=APIResponseSerializer, description="Internal server error")
        },
        tags=["Task Management"]
    )
    def queue_manage(self, request):
        """Manage task queues."""
        serializer = QueueActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            action = serializer.validated_data['action']
            queue_names = serializer.validated_data.get('queue_names', [])
            
            # TODO: Implement actual queue management
            target = f"queues: {', '.join(queue_names)}" if queue_names else "all queues"
            message = f"Queue {action} command sent for {target}"
            
            return Response({
                'success': True,
                'message': message
            })
            
        except Exception as e:
            logger.error(f"Queue management API error: {e}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'], url_path='workers/manage')
    @extend_schema(
        summary="Manage workers",
        description="Start, stop, or restart Dramatiq workers",
        request=WorkerActionSerializer,
        responses={
            200: OpenApiResponse(response=APIResponseSerializer, description="Worker action completed successfully"),
            400: OpenApiResponse(response=APIResponseSerializer, description="Invalid request data"),
            500: OpenApiResponse(response=APIResponseSerializer, description="Internal server error")
        },
        tags=["Task Management"]
    )
    def worker_manage(self, request):
        """Manage worker processes."""
        serializer = WorkerActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            action = serializer.validated_data['action']
            processes = serializer.validated_data.get('processes', 1)
            threads = serializer.validated_data.get('threads', 2)
            
            # TODO: Implement actual worker management
            message = f"Worker {action} command sent (processes: {processes}, threads: {threads})"
            
            return Response({
                'success': True,
                'message': message
            })
            
        except Exception as e:
            logger.error(f"Worker management API error: {e}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'], url_path='tasks/stats')
    @extend_schema(
        summary="Get task statistics",
        description="Retrieve task execution statistics and recent task history",
        responses={
            200: OpenApiResponse(response=TaskStatisticsSerializer, description="Task statistics retrieved successfully"),
            500: OpenApiResponse(response=APIResponseSerializer, description="Internal server error")
        },
        tags=["Task Management"]
    )
    def task_stats(self, request):
        """Get task execution statistics."""
        try:
            tasks_service = self.get_tasks_service()
            stats_data = self._get_task_statistics(tasks_service)
            
            return Response({
                'success': True,
                'data': stats_data
            })
            
        except Exception as e:
            logger.error(f"Task stats API error: {e}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'], url_path='tasks/list')
    @extend_schema(
        summary="Get detailed task list",
        description="Get detailed list of all tasks with filtering options",
        parameters=[
            OpenApiParameter(name='status', description='Filter by task status', required=False, type=str),
            OpenApiParameter(name='queue', description='Filter by queue name', required=False, type=str),
            OpenApiParameter(name='search', description='Search in task names', required=False, type=str),
            OpenApiParameter(name='limit', description='Limit number of results', required=False, type=int),
            OpenApiParameter(name='offset', description='Offset for pagination', required=False, type=int),
        ],
        responses={
            200: OpenApiResponse(response=APIResponseSerializer, description="Task list retrieved successfully"),
            500: OpenApiResponse(response=APIResponseSerializer, description="Internal server error")
        },
        tags=["Task Management"]
    )
    def task_list(self, request):
        """Get detailed task list with filtering."""
        try:
            tasks_service = self.get_tasks_service()
            data = self._get_detailed_task_list(tasks_service, request.query_params)
            
            return Response({
                'success': True,
                'data': data
            })
            
        except Exception as e:
            logger.error(f"Task list API error: {e}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _get_queue_status(self, tasks_service: DjangoTasks) -> Dict[str, Any]:
        """Get current queue status."""
        try:
            redis_client = tasks_service.get_redis_client()
            
            if not redis_client:
                return {
                    'error': 'Redis connection not available',
                    'queues': {},
                    'workers': 0,
                    'redis_connected': False,
                    'timestamp': tasks_service._get_current_timestamp()
                }
            
            # Get queue information
            queues_info = {}
            config = tasks_service.config
            
            if config and config.dramatiq and config.dramatiq.queues:
                for queue_name in config.dramatiq.queues:
                    # Try different queue key patterns
                    queue_keys = [
                        f"dramatiq:queue:{queue_name}",
                        f"dramatiq:default.DQ.{queue_name}",
                        f"dramatiq:{queue_name}"
                    ]
                    
                    queue_length = 0
                    failed_length = 0
                    
                    # Check for pending tasks
                    for queue_key in queue_keys:
                        length = redis_client.llen(queue_key)
                        if length > 0:
                            queue_length = length
                            break
                    
                    # Check for failed tasks
                    failed_keys = [
                        f"dramatiq:queue:{queue_name}.failed",
                        f"dramatiq:default.DQ.{queue_name}.failed",
                        f"dramatiq:{queue_name}.failed"
                    ]
                    
                    for failed_key in failed_keys:
                        length = redis_client.llen(failed_key)
                        if length > 0:
                            failed_length = length
                            break
                    
                    queues_info[queue_name] = {
                        'pending': queue_length,
                        'failed': failed_length,
                        'total': queue_length + failed_length
                    }
            
            # Get worker information
            worker_keys = redis_client.keys("dramatiq:worker:*")
            active_workers = len(worker_keys) if worker_keys else 0
            
            return {
                'queues': queues_info,
                'workers': active_workers,
                'redis_connected': True,
                'timestamp': tasks_service._get_current_timestamp()
            }
            
        except Exception as e:
            logger.error(f"Queue status error: {e}")
            return {
                'error': str(e),
                'queues': {},
                'workers': 0,
                'redis_connected': False,
                'timestamp': tasks_service._get_current_timestamp()
            }
    
    def _get_task_statistics(self, tasks_service: DjangoTasks) -> Dict[str, Any]:
        """Get task execution statistics."""
        try:
            # Try to import django_dramatiq models
            try:
                from django_dramatiq.models import Task
                from django.db.models import Count
                
                # Check if Task model has tasks manager (django_dramatiq uses 'tasks' not 'objects')
                if not hasattr(Task, 'tasks'):
                    logger.warning("Task model does not have tasks manager")
                    return {
                        'statistics': {'total': 0},
                        'recent_tasks': [],
                        'error': 'Task model not properly initialized',
                        'timestamp': tasks_service._get_current_timestamp()
                    }
                
                # Get task counts by status
                stats = Task.tasks.aggregate(
                    total=Count('id'),
                )
                
                # Get recent tasks
                recent_tasks = list(
                    Task.tasks.order_by('-created_at')[:10]
                    .values('actor_name', 'status', 'created_at', 'updated_at')
                )
                
                return {
                    'statistics': stats,
                    'recent_tasks': recent_tasks,
                    'timestamp': tasks_service._get_current_timestamp()
                }
                
            except ImportError:
                return {
                    'error': 'django_dramatiq not available',
                    'statistics': {'total': 0},
                    'recent_tasks': [],
                    'timestamp': tasks_service._get_current_timestamp()
                }
                    
        except Exception as e:
            logger.error(f"Task statistics error: {e}")
            return {
                'error': str(e),
                'statistics': {'total': 0},
                'recent_tasks': [],
                'timestamp': tasks_service._get_current_timestamp()
            }

    def _get_detailed_task_list(self, tasks_service: DjangoTasks, query_params) -> Dict[str, Any]:
        """Get detailed task list with filtering."""
        try:
            # Import django_dramatiq models if available
            try:
                from django_dramatiq.models import Task
                from django.db.models import Q
                
                # Check if Task model has tasks manager
                if not hasattr(Task, 'tasks'):
                    logger.warning("Task model does not have tasks manager")
                    return {
                        'tasks': [],
                        'total': 0,
                        'error': 'Task model not properly initialized',
                        'timestamp': tasks_service._get_current_timestamp()
                    }
                
                # Build query
                queryset = Task.tasks.all()
                
                # Apply filters
                status_filter = query_params.get('status')
                if status_filter:
                    queryset = queryset.filter(status=status_filter)
                
                queue_filter = query_params.get('queue')
                if queue_filter:
                    queryset = queryset.filter(queue_name=queue_filter)
                
                search_filter = query_params.get('search')
                if search_filter:
                    queryset = queryset.filter(
                        Q(actor_name__icontains=search_filter) |
                        Q(id__icontains=search_filter)
                    )
                
                # Get total count before pagination
                total_count = queryset.count()
                
                # Apply pagination
                limit = int(query_params.get('limit', 50))
                offset = int(query_params.get('offset', 0))
                queryset = queryset.order_by('-created_at')[offset:offset + limit]
                
                # Convert to list of dictionaries
                tasks = []
                for task in queryset:
                    task_data = {
                        'id': str(task.id),
                        'actor_name': task.actor_name,
                        'status': task.status,
                        'queue': getattr(task, 'queue_name', 'default'),
                        'created_at': task.created_at.isoformat() if task.created_at else None,
                        'updated_at': task.updated_at.isoformat() if task.updated_at else None,
                        'args': task.args if hasattr(task, 'args') else None,
                        'kwargs': task.kwargs if hasattr(task, 'kwargs') else None,
                        'result': task.result if hasattr(task, 'result') else None,
                        'traceback': task.traceback if hasattr(task, 'traceback') else None,
                        'progress': getattr(task, 'progress', None),
                    }
                    tasks.append(task_data)
                
                return {
                    'tasks': tasks,
                    'total': total_count,
                    'limit': limit,
                    'offset': offset,
                    'timestamp': tasks_service._get_current_timestamp()
                }
                
            except ImportError:
                return {
                    'error': 'django_dramatiq not available',
                    'tasks': [],
                    'total': 0,
                    'timestamp': tasks_service._get_current_timestamp()
                }
                
        except Exception as e:
            logger.error(f"Task list error: {e}")
            return {
                'error': str(e),
                'tasks': [],
                'total': 0,
                'timestamp': tasks_service._get_current_timestamp()
            }




def dashboard_view(request):
    """Dashboard view for task management."""
    try:
        # Use main ViewSet to get data
        main_viewset = TaskManagementViewSet()
        tasks_service = main_viewset.get_tasks_service()
        
        context = {
            'queue_status': main_viewset._get_queue_status(tasks_service),
            'task_stats': main_viewset._get_task_statistics(tasks_service),
        }
        
        return render(request, 'tasks/dashboard.html', context)
        
    except Exception as e:
        logger.error(f"Dashboard view error: {e}")
        context = {
            'error': str(e)
        }
        return render(request, 'tasks/dashboard.html', context)
