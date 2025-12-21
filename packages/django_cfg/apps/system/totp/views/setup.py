"""Views for TOTP setup flow."""

from django.db import transaction
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from django_cfg.utils import get_logger

from ..models import DeviceStatus, TOTPDevice
from ..serializers.setup import (
    ConfirmSetupResponseSerializer,
    ConfirmSetupSerializer,
    SetupResponseSerializer,
    SetupSerializer,
)
from ..services import BackupCodeService, TOTPService

logger = get_logger(__name__)


@extend_schema_view(
    setup=extend_schema(
        request=SetupSerializer,
        responses={
            200: SetupResponseSerializer,
            400: {"description": "2FA already enabled or invalid request"},
        },
        tags=["TOTP Setup"],
    ),
    confirm=extend_schema(
        request=ConfirmSetupSerializer,
        responses={
            200: ConfirmSetupResponseSerializer,
            400: {"description": "Invalid code or setup expired"},
        },
        tags=["TOTP Setup"],
    ),
)
class SetupViewSet(viewsets.GenericViewSet):
    """
    ViewSet for TOTP device setup.

    Handles the 2FA setup flow:
    1. Start setup - generate QR code
    2. Confirm setup - verify first code and generate backup codes
    """

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SetupSerializer

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == "confirm":
            return ConfirmSetupSerializer
        return SetupSerializer

    @action(detail=False, methods=["post"], url_path="start", url_name="start")
    @transaction.atomic
    def setup(self, request):
        """
        Start 2FA setup process.

        Creates a new TOTP device and returns QR code for scanning.
        """
        user = request.user

        # Check if user already has active 2FA
        if TOTPService.has_active_device(user):
            return Response(
                {
                    "error": "2FA is already enabled for your account",
                    "code": "2FA_ALREADY_ENABLED",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Get device name from request
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        device_name = serializer.validated_data.get("device_name", "Authenticator")

        # Create device
        device = TOTPService.create_device(
            user=user,
            name=device_name,
            make_primary=True,
        )

        # Generate QR code
        from django_cfg.core.config import get_current_config
        config = get_current_config()
        issuer_name = config.project_name if config else "Django CFG"
        provisioning_uri = TOTPService.get_provisioning_uri(device, issuer=issuer_name)
        qr_code_base64 = TOTPService.generate_qr_code(provisioning_uri)

        logger.info(f"Started 2FA setup for user {user.email}, device {device.id}")

        return Response(
            {
                "device_id": str(device.id),
                "secret": device.secret,
                "provisioning_uri": provisioning_uri,
                "qr_code_base64": qr_code_base64,
                "expires_in": 600,  # 10 minutes
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["post"], url_path="confirm", url_name="confirm")
    @transaction.atomic
    def confirm(self, request):
        """
        Confirm 2FA setup with first valid code.

        Activates the device and generates backup codes.
        """
        user = request.user
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        device_id = serializer.validated_data["device_id"]
        code = serializer.validated_data["code"]

        # Get device
        try:
            device = TOTPDevice.objects.get(
                id=device_id,
                user=user,
                status=DeviceStatus.PENDING,
            )
        except TOTPDevice.DoesNotExist:
            return Response(
                {
                    "error": "Device not found or already confirmed",
                    "code": "DEVICE_NOT_FOUND",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # Verify and confirm device
        if not TOTPService.confirm_device(device, code):
            return Response(
                {
                    "error": "Invalid verification code",
                    "code": "INVALID_CODE",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Generate backup codes
        backup_codes = BackupCodeService.generate_codes(user)

        logger.info(f"Confirmed 2FA setup for user {user.email}, device {device.id}")

        return Response(
            {
                "message": "2FA enabled successfully",
                "backup_codes": backup_codes,
                "backup_codes_warning": "Store these codes securely. They will not be shown again.",
            },
            status=status.HTTP_200_OK,
        )
