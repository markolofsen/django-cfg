"""Views for backup recovery codes management."""

from django.db import transaction
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from django_cfg.utils import get_logger

from ..serializers.backup import (
    BackupCodesRegenerateResponseSerializer,
    BackupCodesRegenerateSerializer,
    BackupCodesStatusSerializer,
)
from ..services import BackupCodeService, TOTPService

logger = get_logger(__name__)


@extend_schema_view(
    status=extend_schema(
        responses={200: BackupCodesStatusSerializer},
        tags=["Backup Codes"],
    ),
    regenerate=extend_schema(
        request=BackupCodesRegenerateSerializer,
        responses={
            200: BackupCodesRegenerateResponseSerializer,
            400: {"description": "Invalid code or 2FA not enabled"},
        },
        tags=["Backup Codes"],
    ),
)
class BackupViewSet(viewsets.GenericViewSet):
    """ViewSet for managing backup recovery codes."""

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = BackupCodesStatusSerializer

    @action(detail=False, methods=["get"], url_path="status", url_name="status")
    def status(self, request):
        """Get backup codes status for user."""
        user = request.user

        # Check if 2FA is enabled
        if not TOTPService.has_active_device(user):
            return Response(
                {
                    "error": "2FA is not enabled",
                    "code": "2FA_NOT_ENABLED",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        remaining_count = BackupCodeService.get_remaining_count(user)
        total_generated = BackupCodeService.CODE_COUNT

        # Warning if low on codes
        warning = None
        if remaining_count <= 3:
            warning = f"You have only {remaining_count} backup codes remaining. Consider regenerating."

        return Response(
            {
                "remaining_count": remaining_count,
                "total_generated": total_generated,
                "warning": warning,
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["post"], url_path="regenerate", url_name="regenerate")
    @transaction.atomic
    def regenerate(self, request):
        """
        Regenerate backup codes.

        Requires TOTP code for verification.
        Invalidates all existing codes.
        """
        user = request.user
        serializer = BackupCodesRegenerateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        code = serializer.validated_data["code"]

        # Check if 2FA is enabled
        if not TOTPService.has_active_device(user):
            return Response(
                {
                    "error": "2FA is not enabled",
                    "code": "2FA_NOT_ENABLED",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Get primary device for verification
        device = TOTPService.get_primary_device(user)
        if not device:
            return Response(
                {
                    "error": "No primary TOTP device found",
                    "code": "NO_PRIMARY_DEVICE",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Verify code
        if not TOTPService.verify_code(device, code):
            return Response(
                {
                    "error": "Invalid verification code",
                    "code": "INVALID_CODE",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Generate new backup codes
        backup_codes = BackupCodeService.generate_codes(user)

        logger.info(f"Regenerated backup codes for user {user.email}")

        return Response(
            {
                "backup_codes": backup_codes,
                "warning": "Store these codes securely. Previous codes are now invalid.",
            },
            status=status.HTTP_200_OK,
        )




