"""Middleware for enforcing 2FA on protected paths."""

from typing import Callable, List, Optional

from django.conf import settings
from django.http import HttpRequest, JsonResponse

from django_cfg.utils import get_logger

from ..services import TwoFactorSessionService, TOTPService

logger = get_logger(__name__)


class TwoFactorMiddleware:
    """
    Middleware to enforce 2FA verification for protected paths.

    Configure protected paths in settings:
    TOTP_PROTECTED_PATHS = [
        '/api/terminal/',
        '/api/agents/',
    ]
    """

    def __init__(self, get_response: Callable):
        self.get_response = get_response
        self.protected_paths: List[str] = getattr(settings, "TOTP_PROTECTED_PATHS", [])

    def __call__(self, request: HttpRequest):
        if self._should_check_2fa(request):
            if not self._is_2fa_verified(request):
                logger.warning(
                    f"2FA verification required for {request.path}, "
                    f"user: {request.user.email if request.user.is_authenticated else 'anonymous'}"
                )
                return JsonResponse(
                    {
                        "error": "2FA verification required for this action",
                        "code": "2FA_REQUIRED",
                    },
                    status=403,
                )

        response = self.get_response(request)
        return response

    def _should_check_2fa(self, request: HttpRequest) -> bool:
        """Check if this path requires 2FA verification."""
        if not request.user.is_authenticated:
            return False

        # Check if path matches protected paths
        for protected_path in self.protected_paths:
            if request.path.startswith(protected_path):
                return True

        return False

    def _is_2fa_verified(self, request: HttpRequest) -> bool:
        """Check if user has valid 2FA verification."""
        if not request.user.is_authenticated:
            return False

        # Check if user has 2FA enabled
        if not TOTPService.has_active_device(request.user):
            return True  # 2FA not enabled, allow access

        # Check for recent verified session
        return TwoFactorSessionService.is_verified(request.user, request)




