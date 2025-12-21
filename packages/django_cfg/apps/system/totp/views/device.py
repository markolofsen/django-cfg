"""Views for TOTP device management."""

from django.db import transaction
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from django_cfg.utils import get_logger

from ..models import DeviceStatus, TOTPDevice
from ..serializers.device import DeviceDeleteSerializer, DeviceListSerializer, DisableSerializer
from ..services import BackupCodeService, TOTPService

logger = get_logger(__name__)


@extend_schema_view(
    list=extend_schema(
        responses={200: DeviceListSerializer(many=True)},
        tags=["TOTP Management"],
    ),
    disable=extend_schema(
        request=DisableSerializer,
        responses={
            200: {"description": "2FA disabled successfully"},
            400: {"description": "Invalid code"},
        },
        tags=["TOTP Management"],
    ),
)
class DeviceViewSet(viewsets.GenericViewSet):
    """ViewSet for managing TOTP devices."""

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = DeviceListSerializer

    def get_queryset(self):
        """Return devices for authenticated user."""
        return TOTPDevice.objects.filter(user=self.request.user)

    @action(detail=False, methods=["get"], url_path="list", url_name="list")
    def list(self, request):
        """List all TOTP devices for user."""
        devices = self.get_queryset()
        serializer = self.get_serializer(devices, many=True)

        return Response(
            {
                "devices": serializer.data,
                "has_2fa_enabled": TOTPService.has_active_device(request.user),
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["delete"], url_path="delete", url_name="delete")
    @transaction.atomic
    def delete_device(self, request, pk=None):
        """
        Delete a TOTP device.

        Requires verification code if removing the last/primary device.
        """
        user = request.user

        # Get device
        try:
            device = TOTPDevice.objects.get(id=pk, user=user)
        except TOTPDevice.DoesNotExist:
            return Response(
                {
                    "error": "Device not found",
                    "code": "DEVICE_NOT_FOUND",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # Check if this is the last active device
        active_devices_count = TOTPDevice.objects.filter(
            user=user, status=DeviceStatus.ACTIVE
        ).count()

        if active_devices_count == 1 and device.status == DeviceStatus.ACTIVE:
            # Require verification code to remove last device
            serializer = DeviceDeleteSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            code = serializer.validated_data.get("code")

            if not code:
                return Response(
                    {
                        "error": "Cannot remove last device without verification code",
                        "code": "CODE_REQUIRED",
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

        # Delete device
        device.delete()
        logger.info(f"Deleted TOTP device {device.id} for user {user.email}")

        return Response(
            {"message": "Device removed successfully"},
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["post"], url_path="disable", url_name="disable")
    @transaction.atomic
    def disable(self, request):
        """
        Completely disable 2FA for account.

        Requires verification code.
        """
        user = request.user
        serializer = DisableSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        code = serializer.validated_data["code"]

        # Get primary device for verification
        device = TOTPService.get_primary_device(user)
        if not device:
            return Response(
                {
                    "error": "2FA is not enabled",
                    "code": "2FA_NOT_ENABLED",
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

        # Disable all devices
        TOTPDevice.objects.filter(user=user).update(
            status=DeviceStatus.DISABLED,
            is_primary=False,
        )

        # Invalidate all backup codes
        BackupCodeService.invalidate_all(user)

        logger.info(f"Disabled 2FA for user {user.email}")

        return Response(
            {"message": "2FA has been disabled"},
            status=status.HTTP_200_OK,
        )
