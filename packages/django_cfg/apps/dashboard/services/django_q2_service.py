"""
Django-Q2 Service

Business logic for collecting Django-Q2 task data.
"""

from typing import Dict, List, Any


class DjangoQ2Service:
    """Service for aggregating Django-Q2 task information."""

    @staticmethod
    def get_schedules() -> List[Dict[str, Any]]:
        """
        Get all scheduled tasks from Django-Q2.

        Returns:
            List of scheduled tasks with their configurations
        """
        try:
            from django_q.models import Schedule

            schedules = Schedule.objects.all().order_by('-next_run')
            return [
                {
                    'id': schedule.id,
                    'name': schedule.name,
                    'func': schedule.func,
                    'schedule_type': schedule.schedule_type,
                    'repeats': schedule.repeats,
                    'next_run': schedule.next_run,
                    'last_run': getattr(schedule, 'last_run', None),
                }
                for schedule in schedules
            ]
        except ImportError:
            # django-q2 not installed
            return []
        except Exception:
            # Database error or table doesn't exist yet
            return []

    @staticmethod
    def get_recent_tasks(limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get recent task executions from Django-Q2.

        Args:
            limit: Maximum number of tasks to return

        Returns:
            List of recent task executions with their results
        """
        try:
            from django_q.models import Task

            tasks = Task.objects.all().order_by('-started')[:limit]
            return [
                {
                    'id': task.id,
                    'name': task.name,
                    'func': task.func,
                    'started': task.started,
                    'stopped': task.stopped,
                    'success': task.success,
                    'result': str(task.result) if task.result else None,
                }
                for task in tasks
            ]
        except ImportError:
            # django-q2 not installed
            return []
        except Exception:
            # Database error or table doesn't exist yet
            return []

    @staticmethod
    def get_cluster_status() -> Dict[str, Any]:
        """
        Get Django-Q2 cluster status.

        Returns:
            Dictionary with cluster status information
        """
        try:
            from django_q.models import Schedule, Task
            from django_q.cluster import Cluster

            # Count schedules
            total_schedules = Schedule.objects.count()
            active_schedules = Schedule.objects.filter(repeats__gt=0).count()

            # Count recent tasks (last 24 hours)
            from django.utils import timezone
            from datetime import timedelta

            last_24h = timezone.now() - timedelta(hours=24)
            recent_tasks = Task.objects.filter(started__gte=last_24h).count()
            successful_tasks = Task.objects.filter(
                started__gte=last_24h, success=True
            ).count()
            failed_tasks = Task.objects.filter(
                started__gte=last_24h, success=False
            ).count()

            # Check if cluster is running
            cluster_running = False
            try:
                # Check for recent task activity as proxy for cluster status
                recent_task = Task.objects.filter(
                    started__gte=timezone.now() - timedelta(minutes=5)
                ).exists()
                cluster_running = recent_task
            except Exception:
                pass

            return {
                'cluster_running': cluster_running,
                'total_schedules': total_schedules,
                'active_schedules': active_schedules,
                'recent_tasks': recent_tasks,
                'successful_tasks': successful_tasks,
                'failed_tasks': failed_tasks,
            }
        except ImportError:
            # django-q2 not installed
            return {
                'cluster_running': False,
                'total_schedules': 0,
                'active_schedules': 0,
                'recent_tasks': 0,
                'successful_tasks': 0,
                'failed_tasks': 0,
            }
        except Exception:
            # Database error or table doesn't exist yet
            return {
                'cluster_running': False,
                'total_schedules': 0,
                'active_schedules': 0,
                'recent_tasks': 0,
                'successful_tasks': 0,
                'failed_tasks': 0,
            }

    @classmethod
    def get_summary(cls) -> Dict[str, Any]:
        """
        Get complete Django-Q2 summary for dashboard.

        Returns:
            Dictionary with status, schedules, and recent tasks
        """
        return {
            'status': cls.get_cluster_status(),
            'schedules': cls.get_schedules(),
            'recent_tasks': cls.get_recent_tasks(limit=10),
        }
