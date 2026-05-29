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

    Staff-only: it discloses the full URL map and (with auto_auth) creates a probe
    user, so it must never be reachable anonymously (DASHBOARD-001).
    """

    def get(self, request):
        """Return endpoints status data."""
        # Staff-only — never expose the URL map or trigger probe-user creation to anon callers.
        if not (request.user.is_authenticated and request.user.is_staff):
            return JsonResponse({"detail": "Forbidden"}, status=403)

        # Get query parameters
        include_unnamed = request.GET.get('include_unnamed', 'false').lower() == 'true'
        timeout = int(request.GET.get('timeout', 5))
        # auto_auth defaults OFF — opt-in only, never plant a probe user implicitly.
        auto_auth = request.GET.get('auto_auth', 'false').lower() == 'true'

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
