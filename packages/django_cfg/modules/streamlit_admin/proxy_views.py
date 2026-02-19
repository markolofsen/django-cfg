"""Views for Streamlit Admin integration."""

from django.http import HttpResponse, JsonResponse
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.clickjacking import xframe_options_exempt
from django.utils.decorators import method_decorator

import httpx


@method_decorator(xframe_options_exempt, name='dispatch')
class StreamlitProxyView(LoginRequiredMixin, View):
    """
    Proxy view for Streamlit requests.

    Forwards requests to Streamlit server with JWT token injection via query params.
    Used when reverse proxy (nginx) is not available.

    Features:
    - Auto-detects actual port from StreamlitAutoStart
    - Injects JWT token via query params for authenticated users
    - iframe-compatible (xframe_options_exempt)
    """

    def get_streamlit_url(self) -> str | None:
        """
        Get Streamlit server URL with auto-detected port.

        Priority:
        1. Running StreamlitAutoStart instance (actual port)
        2. Config default (fallback)
        """
        # Try to get actual port from running instance
        from .core.autostart import StreamlitAutoStart
        instance = StreamlitAutoStart.get_instance()
        if instance and instance.is_running:
            return instance.url

        # Fallback to config
        try:
            from django_cfg.core.config import get_current_config
            config = get_current_config()
            if config and config.streamlit_admin:
                return config.streamlit_admin.get_dev_url()
        except Exception:
            pass

        return None

    def get(self, request, path: str = ""):
        """Handle GET requests."""
        from django.conf import settings
        from django.shortcuts import redirect

        base_url = self.get_streamlit_url()
        if not base_url:
            return HttpResponse("Streamlit admin not configured", status=503)

        # In DEBUG mode, redirect to Streamlit directly (WebSocket works)
        # In production, use nginx proxy for WebSocket support
        if settings.DEBUG:
            redirect_url = f"{base_url}/{path}"

            # Inject JWT token
            if request.user.is_authenticated:
                token = self._get_jwt_token(request.user)
                if token:
                    separator = "&" if "?" in redirect_url else "?"
                    redirect_url += f"{separator}token={token}"

            return redirect(redirect_url)

        # Production: proxy HTTP requests (WebSocket via nginx)
        target_url = f"{base_url}/{path}"

        # Inject JWT token for authenticated users
        params = dict(request.GET)
        if request.user.is_authenticated and "token" not in params:
            token = self._get_jwt_token(request.user)
            if token:
                params["token"] = token

        if params:
            from urllib.parse import urlencode
            target_url += f"?{urlencode(params, doseq=True)}"

        try:
            # Forward request
            response = httpx.get(
                target_url,
                headers=self._get_forward_headers(request),
                timeout=30.0,
                follow_redirects=True,
            )

            # Build Django response
            django_response = HttpResponse(
                content=response.content,
                status=response.status_code,
                content_type=response.headers.get("content-type", "text/html"),
            )

            # Copy relevant headers
            for header in ["cache-control", "etag", "last-modified"]:
                if header in response.headers:
                    django_response[header] = response.headers[header]

            return django_response

        except httpx.ConnectError:
            return HttpResponse(
                "Streamlit server not running. "
                "Start with: python manage.py run_streamlit",
                status=503,
            )
        except httpx.TimeoutException:
            return HttpResponse("Streamlit server timeout", status=504)

    def _get_jwt_token(self, user) -> str | None:
        """Generate JWT access token for user."""
        try:
            from rest_framework_simplejwt.tokens import RefreshToken
            refresh = RefreshToken.for_user(user)
            return str(refresh.access_token)
        except ImportError:
            return None
        except Exception:
            return None

    def post(self, request, path: str = ""):
        """Handle POST requests."""
        base_url = self.get_streamlit_url()
        if not base_url:
            return HttpResponse("Streamlit admin not configured", status=503)

        target_url = f"{base_url}/{path}"

        try:
            response = httpx.post(
                target_url,
                headers=self._get_forward_headers(request),
                content=request.body,
                timeout=30.0,
            )

            return HttpResponse(
                content=response.content,
                status=response.status_code,
                content_type=response.headers.get("content-type"),
            )

        except httpx.ConnectError:
            return HttpResponse("Streamlit server not running", status=503)

    def _get_forward_headers(self, request) -> dict:
        """Build headers for forwarding to Streamlit."""
        headers = {}

        # Forward useful headers
        forward_headers = [
            "accept",
            "accept-language",
            "content-type",
            "user-agent",
            "cookie",
        ]

        for header in forward_headers:
            value = request.headers.get(header)
            if value:
                headers[header] = value

        # Add forwarded info
        headers["X-Forwarded-For"] = request.META.get(
            "HTTP_X_FORWARDED_FOR",
            request.META.get("REMOTE_ADDR", ""),
        )
        headers["X-Forwarded-Proto"] = (
            "https" if request.is_secure() else "http"
        )

        return headers


class StreamlitHealthView(View):
    """Health check endpoint for Streamlit server."""

    def get(self, request):
        """Check if Streamlit server is running."""
        from .core.autostart import StreamlitAutoStart

        # Check running instance first
        instance = StreamlitAutoStart.get_instance()
        if instance and instance.is_running:
            return JsonResponse({
                "status": "healthy",
                "url": instance.url,
                "port": instance.port,
                "pid": instance._process.pid if instance._process else None,
            })

        # Fallback: check config and try to connect
        try:
            from django_cfg.core.config import get_current_config
            config = get_current_config()
            if not config or not config.streamlit_admin:
                return JsonResponse(
                    {"status": "error", "message": "Streamlit not configured"},
                    status=503,
                )

            streamlit_config = config.streamlit_admin
            url = streamlit_config.get_dev_url()

            # Try to connect
            response = httpx.get(f"{url}/healthz", timeout=5.0)
            if response.status_code == 200:
                return JsonResponse({
                    "status": "healthy",
                    "url": url,
                    "port": streamlit_config.port,
                })

        except httpx.ConnectError:
            pass
        except Exception:
            pass

        return JsonResponse(
            {
                "status": "unhealthy",
                "message": "Streamlit server not responding",
            },
            status=503,
        )
