"""Decorators for enforcing 2FA on specific views."""

from functools import wraps
from typing import Callable, Optional

from django.http import HttpRequest, JsonResponse

from django_cfg.utils import get_logger

from ..services import TwoFactorSessionService, TOTPService

logger = get_logger(__name__)


def require_2fa(
    max_age_hours: Optional[int] = None,
    on_failure: Optional[Callable] = None,
):
    """
    Decorator to require 2FA verification for a view.

    Args:
        max_age_hours: Maximum age of verification in hours (for re-verification)
        on_failure: Custom failure handler (optional)

    Usage:
        @require_2fa
        def my_view(request):
            pass

        @require_2fa(max_age_hours=1)
        def sensitive_view(request):
            pass
    """

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request: HttpRequest, *args, **kwargs):
            # Check authentication
            if not request.user.is_authenticated:
                if on_failure:
                    return on_failure(request)
                return JsonResponse(
                    {"error": "Authentication required", "code": "AUTH_REQUIRED"},
                    status=401,
                )

            # Check if user has 2FA enabled
            if not TOTPService.has_active_device(request.user):
                # 2FA not enabled, allow access
                return view_func(request, *args, **kwargs)

            # Check verification
            if max_age_hours is not None:
                is_verified = TwoFactorSessionService.is_recently_verified(
                    request.user, max_age_hours=max_age_hours
                )
            else:
                is_verified = TwoFactorSessionService.is_verified(request.user, request)

            if not is_verified:
                logger.warning(
                    f"2FA verification required for view {view_func.__name__}, "
                    f"user: {request.user.email}"
                )
                if on_failure:
                    return on_failure(request)
                return JsonResponse(
                    {
                        "error": "2FA verification required for this action",
                        "code": "2FA_REQUIRED",
                    },
                    status=403,
                )

            # Verification valid, proceed with view
            return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator


def require_2fa_verified(max_age_hours: Optional[int] = None):
    """
    Alias for require_2fa decorator.

    Usage:
        @require_2fa_verified
        def my_view(request):
            pass

        @require_2fa_verified(max_age_hours=1)
        def sensitive_view(request):
            pass
    """
    return require_2fa(max_age_hours=max_age_hours)




