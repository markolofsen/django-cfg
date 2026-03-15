import logging
import traceback

from django.contrib.auth import get_user_model
from django_ratelimit.core import is_ratelimited
from drf_spectacular.utils import extend_schema
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from django_cfg.apps.system.totp.services import TOTPService, TwoFactorSessionService
from django_cfg.modules.base import BaseCfgModule

from ..serializers.otp import (
    OTPErrorResponseSerializer,
    OTPRequestResponseSerializer,
    OTPRequestSerializer,
    OTPVerifyResponseSerializer,
    OTPVerifySerializer,
)
from ..serializers.profile import UserSerializer
from ..services import OTPService
from ..services.otp_service import OTPRequestResult

logger = logging.getLogger(__name__)


def _is_ip_limited(request, group: str, rate: str) -> bool:
    """Check IP-based rate limit using django-ratelimit's core function."""
    return is_ratelimited(request, group=group, key='ip', rate=rate, increment=True)


class OTPViewSet(viewsets.GenericViewSet):
    """OTP authentication ViewSet with nested router support."""

    permission_classes = [permissions.AllowAny]
    serializer_class = OTPRequestSerializer  # Default serializer for the viewset

    def get_serializer_class(self):  # type: ignore[override]
        """Return the appropriate serializer class based on the action."""
        if self.action == 'request_otp':
            return OTPRequestSerializer
        elif self.action == 'verify_otp':
            return OTPVerifySerializer
        return super().get_serializer_class()

    @extend_schema(
        request=OTPRequestSerializer,
        responses={
            200: OTPRequestResponseSerializer,
            400: OTPErrorResponseSerializer,
            429: OTPErrorResponseSerializer,
            500: OTPErrorResponseSerializer,
        },
    )
    @action(detail=False, methods=["post"], url_path="request", url_name="request")
    def request_otp(self, request):
        """Request OTP code to email."""
        if _is_ip_limited(request, group='otp_request_ip', rate='10/m'):
            return Response(
                {"error": "Too many requests", "error_code": "rate_limited"},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        serializer = OTPRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        identifier: str = serializer.validated_data["identifier"]  # type: ignore[index]
        source_url: str | None = serializer.validated_data.get("source_url")  # type: ignore[union-attr]

        accept_language = request.META.get('HTTP_ACCEPT_LANGUAGE', '') or ''
        logger.debug(f"Starting OTP request for: {identifier}, source: {source_url}")

        try:
            result: OTPRequestResult = OTPService.request_otp(  # type: ignore[assignment]
                identifier, source_url, accept_language=accept_language
            )
        except Exception as e:
            logger.error(f"OTP request failed with exception: {str(e)}")
            logger.error(f"Full traceback: {traceback.format_exc()}")
            return Response(
                {"error": "Internal server error during OTP request", "error_code": "internal_error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        if result.success:
            return Response(
                {"message": "OTP sent to your email address"}, status=status.HTTP_200_OK
            )

        if result.error_code == "invalid_email":
            logger.warning(f"Invalid identifier provided: {identifier}")
            return Response(
                {"error": "Invalid identifier format", "error_code": "invalid_identifier"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        elif result.error_code == "user_creation_failed":
            logger.error(f"User creation failed for identifier: {identifier}")
            logger.error(f"Full traceback for user creation failure: {traceback.format_exc()}")
            return Response(
                {"error": "Failed to create user account", "error_code": "user_creation_failed"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        elif result.error_code == "cooldown":
            return Response(
                {
                    "error": "Please wait before requesting another code",
                    "error_code": "cooldown",
                    "retry_after": result.retry_after,
                },
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )
        elif result.error_code in ("hourly_limit", "daily_limit"):
            return Response(
                {
                    "error": "Too many OTP requests. Please try again later.",
                    "error_code": result.error_code,
                    "retry_after": result.retry_after,
                },
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )
        elif result.error_code == "email_send_failed":
            return Response(
                {"error": "Failed to send verification code. Please try again.", "error_code": "send_failed"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        else:
            logger.error(f"Unknown error code: {result.error_code} for identifier: {identifier}")
            return Response(
                {"error": "Failed to send OTP", "error_code": "internal_error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @extend_schema(
        request=OTPVerifySerializer,
        responses={
            200: OTPVerifyResponseSerializer,
            401: OTPErrorResponseSerializer,
            429: OTPErrorResponseSerializer,
        },
    )
    @action(detail=False, methods=["post"], url_path="verify", url_name="verify")
    def verify_otp(self, request):
        """
        Verify OTP code and return JWT tokens or 2FA session.

        If user has 2FA enabled:
        - Returns requires_2fa=True with session_id
        - Client must complete 2FA verification at /cfg/totp/verify/

        If user has no 2FA:
        - Returns JWT tokens and user data directly
        """
        if _is_ip_limited(request, group='otp_verify_ip', rate='20/m'):
            return Response({"error": "Too many requests"}, status=status.HTTP_429_TOO_MANY_REQUESTS)

        serializer = OTPVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        identifier: str = serializer.validated_data["identifier"]  # type: ignore[index]
        otp: str = serializer.validated_data["otp"]  # type: ignore[index]
        source_url: str | None = serializer.validated_data.get("source_url")  # type: ignore[union-attr]

        user = OTPService.verify_otp(identifier, otp, source_url)

        if user:
            # Check if 2FA is enabled system-wide AND user has TOTP device
            is_2fa_enabled = BaseCfgModule().is_totp_enabled()
            has_device = TOTPService.has_active_device(user)

            if is_2fa_enabled and has_device:
                # Create 2FA session
                session = TwoFactorSessionService.create_session(user, request)
                logger.info(f"2FA required for user {user.email}, session {session.id}")

                return Response(
                    {
                        "requires_2fa": True,
                        "session_id": str(session.id),
                        "refresh": None,
                        "access": None,
                        "user": None,
                        "should_prompt_2fa": False,
                    },
                    status=status.HTTP_200_OK,
                )

            # No 2FA - generate tokens directly
            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    "requires_2fa": False,
                    "session_id": None,
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                    "user": UserSerializer(user, context={'request': request}).data,
                    "should_prompt_2fa": user.should_prompt_2fa,
                },
                status=status.HTTP_200_OK,
            )
        else:
            # Log the failure reason internally — response is always uniform (anti-enumeration)
            try:
                UserModel = get_user_model()
                UserModel.objects.get(email=identifier)
                logger.warning(f"Invalid or expired OTP for identifier: {identifier}")
            except Exception:
                logger.warning(f"OTP verify attempt for deleted/non-existent user: {identifier}")
            return Response(
                {"error": "Authentication failed"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
