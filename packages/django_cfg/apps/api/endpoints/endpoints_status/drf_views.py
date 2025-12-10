"""
Django CFG Endpoints Status DRF Views

DRF browsable API views with Tailwind theme support.
"""

from rest_framework import status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from .checker import check_all_endpoints
from .serializers import EndpointsStatusSerializer


class DRFEndpointsStatusView(APIView):
    """
    Django CFG endpoints status check with DRF Browsable API.

    Checks all registered URL endpoints and returns their health status.
    Excludes health check endpoints and admin to avoid recursion.

    Query Parameters:
        - include_unnamed: Include endpoints without names (default: false)
        - timeout: Request timeout in seconds (default: 5)
        - auto_auth: Auto-retry with JWT on 401/403 (default: true)

    This endpoint uses DRF Browsable API with Tailwind CSS theme! 🎨

    **IMPORTANT**: Admin-only for security (shows all endpoint statuses).
    For public health checks, use /cfg/health/ instead.
    """

    permission_classes = [IsAdminUser]  # Admin-only for security
    serializer_class = EndpointsStatusSerializer  # For schema generation

    def get(self, request):
        """Return endpoints status data."""
        # Get query parameters
        include_unnamed = request.query_params.get('include_unnamed', 'false').lower() == 'true'
        timeout = int(request.query_params.get('timeout', 5))
        auto_auth = request.query_params.get('auto_auth', 'true').lower() == 'true'

        # Check all endpoints
        status_data = check_all_endpoints(
            include_unnamed=include_unnamed,
            timeout=timeout,
            auto_auth=auto_auth
        )

        # Return appropriate HTTP status
        http_status = status.HTTP_200_OK
        if status_data["status"] == "unhealthy":
            http_status = status.HTTP_503_SERVICE_UNAVAILABLE
        elif status_data["status"] == "degraded":
            http_status = status.HTTP_200_OK  # Still operational

        return Response(status_data, status=http_status)
