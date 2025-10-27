"""
Django CFG Endpoints Status Views

Plain Django views for endpoints status checking.
"""

from django.http import JsonResponse
from django.views import View

from .checker import check_all_endpoints


class EndpointsStatusView(View):
    """
    Django CFG endpoints status check.

    Checks all registered URL endpoints and returns their health status.
    Excludes health check endpoints to avoid recursion.
    """

    def get(self, request):
        """Return endpoints status data."""
        # Get query parameters
        include_unnamed = request.GET.get('include_unnamed', 'false').lower() == 'true'
        timeout = int(request.GET.get('timeout', 5))
        auto_auth = request.GET.get('auto_auth', 'true').lower() == 'true'

        # Check all endpoints
        status_data = check_all_endpoints(
            include_unnamed=include_unnamed,
            timeout=timeout,
            auto_auth=auto_auth
        )

        # Return appropriate HTTP status
        status_code = 200
        if status_data["status"] == "unhealthy":
            status_code = 503
        elif status_data["status"] == "degraded":
            status_code = 200  # Still operational

        return JsonResponse(status_data, status=status_code)
