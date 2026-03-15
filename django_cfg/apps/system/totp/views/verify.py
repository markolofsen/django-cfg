"""Views for 2FA verification during login flow."""

from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from django_cfg.utils import get_logger

from ..models import SessionStatus, TwoFactorSession
from ..serializers.verify import (
    VerifyBackupSerializer,
    VerifyResponseSerializer,
    VerifySerializer,
)
from ..services import BackupCodeService, TwoFactorSessionService

logger = get_logger(__name__)

User = get_user_model()


@extend_schema_view(
    verify=extend_schema(
        request=VerifySerializer,
        responses={
            200: VerifyResponseSerializer,
            400: {"description": "Invalid code or session"},
            403: {"description": "Too many attempts"},
        },
        tags=["TOTP Verification"],
    ),
    verify_backup=extend_schema(
        request=VerifyBackupSerializer,
        responses={
            200: VerifyResponseSerializer,
            400: {"description": "Invalid backup code or session"},
        },
        tags=["TOTP Verification"],
    ),
)
class VerifyViewSet(viewsets.GenericViewSet):
    """
    ViewSet for 2FA verification during authentication.

    Used after successful primary authentication (OTP/password)
    to complete the 2FA challenge.
    """

    permission_classes = [permissions.AllowAny]
    serializer_class = VerifySerializer

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == "verify_backup":
            return VerifyBackupSerializer
        return VerifySerializer

    @action(detail=False, methods=["post"], url_path="verify", url_name="verify")
    def verify(self, request):
        """
        Verify TOTP code for 2FA session.

        Completes authentication and returns JWT tokens on success.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        session_id = serializer.validated_data["session_id"]
        code = serializer.validated_data["code"]

        # Get session
        session = TwoFactorSessionService.get_session(session_id)
        if not session:
            return Response(
                {
                    "error": "2FA session not found",
                    "code": "SESSION_NOT_FOUND",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # Check session state
        if session.is_expired:
            return Response(
                {
                    "error": "Verification session expired. Please login again.",
                    "code": "SESSION_EXPIRED",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if session.is_locked:
            return Response(
                {
                    "error": "Too many failed attempts. Please login again.",
                    "code": "MAX_ATTEMPTS_EXCEEDED",
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        # Verify code
        if not TwoFactorSessionService.verify_session(session, code, is_backup_code=False):
            return Response(
                {
                    "error": "Invalid verification code",
                    "code": "INVALID_CODE",
                    "attempts_remaining": session.attempts_remaining,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Issue tokens
        user = session.user
        refresh = RefreshToken.for_user(user)

        # Import UserSerializer from accounts app
        try:
            from django_cfg.apps.system.accounts.serializers import UserSerializer

            user_data = UserSerializer(user, context={"request": request}).data
        except ImportError:
            # Fallback if accounts app not available
            user_data = {
                "id": user.id,
                "email": user.email,
                "username": user.username,
            }

        logger.info(f"Successful 2FA verification for user {user.email}, session {session.id}")

        return Response(
            {
                "message": "2FA verification successful",
                "access_token": str(refresh.access_token),
                "refresh_token": str(refresh),
                "user": user_data,
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["post"], url_path="backup", url_name="backup")
    def verify_backup(self, request):
        """
        Verify backup recovery code for 2FA session.

        Alternative verification method when TOTP device unavailable.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        session_id = serializer.validated_data["session_id"]
        backup_code = serializer.validated_data["backup_code"]

        # Get session
        session = TwoFactorSessionService.get_session(session_id)
        if not session:
            return Response(
                {
                    "error": "2FA session not found",
                    "code": "SESSION_NOT_FOUND",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # Check session state
        if session.is_expired:
            return Response(
                {
                    "error": "Verification session expired. Please login again.",
                    "code": "SESSION_EXPIRED",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Verify backup code
        if not TwoFactorSessionService.verify_session(
            session, backup_code, is_backup_code=True
        ):
            return Response(
                {
                    "error": "Invalid backup code",
                    "code": "INVALID_CODE",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Issue tokens
        user = session.user
        refresh = RefreshToken.for_user(user)

        # Get remaining backup codes
        remaining_codes = BackupCodeService.get_remaining_count(user)
        warning = None
        if remaining_codes <= 3:
            warning = f"You have only {remaining_codes} backup codes remaining. Consider regenerating."

        # Import UserSerializer
        try:
            from django_cfg.apps.system.accounts.serializers import UserSerializer

            user_data = UserSerializer(user, context={"request": request}).data
        except ImportError:
            user_data = {
                "id": user.id,
                "email": user.email,
                "username": user.username,
            }

        logger.info(
            f"Successful backup code verification for user {user.email}, "
            f"{remaining_codes} codes remaining"
        )

        response_data = {
            "message": "Backup code accepted",
            "access_token": str(refresh.access_token),
            "refresh_token": str(refresh),
            "user": user_data,
            "remaining_backup_codes": remaining_codes,
        }

        if warning:
            response_data["warning"] = warning

        return Response(response_data, status=status.HTTP_200_OK)
