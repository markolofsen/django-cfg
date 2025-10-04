"""
Django views for RPC Dashboard.

Provides both template views and JSON API endpoints.
"""

import logging
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_http_methods

from .monitor import RPCMonitor

logger = logging.getLogger(__name__)


@staff_member_required
def dashboard_view(request):
    """
    Main RPC dashboard view.

    Renders dashboard template with initial data.
    JavaScript will poll API endpoints for live updates.
    """
    try:
        monitor = RPCMonitor()

        # Get initial data
        overview_stats = monitor.get_overview_stats()
        health = monitor.health_check()

        # Build navigation items (can be extended later)
        rpc_nav_items = []

        context = {
            'overview_stats': overview_stats,
            'health': health,
            'page_title': 'RPC Monitor Dashboard',
            'rpc_nav_items': rpc_nav_items,
        }

        return render(request, 'django_ipc_dashboard/dashboard.html', context)

    except Exception as e:
        logger.error(f"Dashboard view error: {e}", exc_info=True)

        # Build navigation items (can be extended later)
        rpc_nav_items = []

        # Fallback context
        context = {
            'overview_stats': {
                'redis_connected': False,
                'error': str(e),
            },
            'health': {
                'redis_connected': False,
                'error': str(e),
            },
            'page_title': 'RPC Monitor Dashboard - Error',
            'rpc_nav_items': rpc_nav_items,
        }

        return render(request, 'django_ipc_dashboard/dashboard.html', context)


# === JSON API Endpoints ===

@staff_member_required
@require_http_methods(["GET"])
def api_overview_stats(request):
    """
    API endpoint for overview statistics.

    Returns JSON with current RPC metrics.
    """
    try:
        monitor = RPCMonitor()
        stats = monitor.get_overview_stats()

        return JsonResponse({
            'success': True,
            'data': stats,
        })

    except ValueError as e:
        logger.warning(f"API overview stats validation error: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e),
        }, status=400)  # Bad Request

    except ConnectionError as e:
        logger.error(f"API overview stats connection error: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Redis connection unavailable',
        }, status=503)  # Service Unavailable

    except Exception as e:
        logger.error(f"API overview stats error: {e}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': 'Internal server error',
        }, status=500)


@staff_member_required
@require_http_methods(["GET"])
def api_recent_requests(request):
    """
    API endpoint for recent RPC requests.

    Query params:
        - count: Number of requests to return (default: 50, max: 200)
    """
    try:
        count = int(request.GET.get('count', 50))
        count = min(count, 200)  # Max 200

        monitor = RPCMonitor()
        requests_list = monitor.get_recent_requests(count=count)

        return JsonResponse({
            'success': True,
            'data': {
                'requests': requests_list,
                'count': len(requests_list),
            },
        })

    except ValueError as e:
        logger.warning(f"API recent requests validation error: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Invalid count parameter',
        }, status=400)

    except ConnectionError as e:
        logger.error(f"API recent requests connection error: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Redis connection unavailable',
        }, status=503)

    except Exception as e:
        logger.error(f"API recent requests error: {e}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': 'Internal server error',
        }, status=500)


@staff_member_required
@require_http_methods(["GET"])
def api_notification_stats(request):
    """
    API endpoint for notification statistics.

    Returns stats about sent notifications.
    """
    try:
        monitor = RPCMonitor()
        stats = monitor.get_notification_stats()

        return JsonResponse({
            'success': True,
            'data': stats,
        })

    except ConnectionError as e:
        logger.error(f"API notification stats connection error: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Redis connection unavailable',
        }, status=503)

    except Exception as e:
        logger.error(f"API notification stats error: {e}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': 'Internal server error',
        }, status=500)


@staff_member_required
@require_http_methods(["GET"])
def api_method_stats(request):
    """
    API endpoint for method statistics.

    Returns stats grouped by RPC method.
    """
    try:
        monitor = RPCMonitor()
        stats = monitor.get_method_stats()

        return JsonResponse({
            'success': True,
            'data': {
                'methods': stats,
                'count': len(stats),
            },
        })

    except ConnectionError as e:
        logger.error(f"API method stats connection error: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Redis connection unavailable',
        }, status=503)

    except Exception as e:
        logger.error(f"API method stats error: {e}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': 'Internal server error',
        }, status=500)


@staff_member_required
@require_http_methods(["GET"])
def api_health_check(request):
    """
    API endpoint for health check.

    Returns current health status of RPC monitoring.
    """
    try:
        monitor = RPCMonitor()
        health = monitor.health_check()

        return JsonResponse({
            'success': True,
            'data': health,
        })

    except ConnectionError as e:
        logger.error(f"API health check connection error: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Redis connection unavailable',
        }, status=503)

    except Exception as e:
        logger.error(f"API health check error: {e}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': 'Internal server error',
        }, status=500)
