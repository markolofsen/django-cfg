"""TOTP service for code generation and verification."""

import io
from typing import Optional

import pyotp
import qrcode
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

from django_cfg.utils import get_logger

from ..models import DeviceStatus, TOTPDevice

logger = get_logger(__name__)

User = get_user_model()


class TOTPService:
    """
    TOTP code generation and verification service.

    Implements RFC 6238 (TOTP) using pyotp library for Google Authenticator compatibility.
    """

    ALGORITHM = "SHA1"
    DIGITS = 6
    INTERVAL = 30
    VALID_WINDOW = 1

    @classmethod
    def generate_secret(cls) -> str:
        """Generate cryptographically secure TOTP secret."""
        return pyotp.random_base32()

    @classmethod
    @transaction.atomic
    def create_device(
        cls,
        user: User,
        name: str = "Authenticator",
        make_primary: bool = True,
    ) -> TOTPDevice:
        """
        Create new TOTP device for user.

        Device is created in PENDING status until confirmed with a valid TOTP code.

        Args:
            user: User to create device for
            name: Device name for identification
            make_primary: Whether to make this the primary device

        Returns:
            Created TOTPDevice instance
        """
        secret = cls.generate_secret()

        device = TOTPDevice.objects.create(
            user=user,
            name=name,
            secret=secret,
            status=DeviceStatus.PENDING,
            is_primary=False,
        )

        if make_primary:
            device.make_primary()

        logger.info(f"Created TOTP device '{name}' for user {user.email}")
        return device

    @classmethod
    def get_provisioning_uri(
        cls,
        device: TOTPDevice,
        issuer: str = "Django CFG",
    ) -> str:
        """
        Generate otpauth:// URI for QR code.

        Format: otpauth://totp/{issuer}:{email}?secret={secret}&issuer={issuer}

        Args:
            device: TOTP device
            issuer: Issuer name shown in authenticator app

        Returns:
            Provisioning URI string
        """
        totp = pyotp.TOTP(device.secret)
        return totp.provisioning_uri(
            name=device.user.email,
            issuer_name=issuer,
        )

    @classmethod
    def generate_qr_code(
        cls,
        provisioning_uri: str,
        format: str = "base64",
    ) -> str:
        """
        Generate QR code for provisioning URI.

        Args:
            provisioning_uri: otpauth:// URI from get_provisioning_uri
            format: Output format ('base64' or 'svg')

        Returns:
            Base64 data URI or SVG string
        """
        import base64

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(provisioning_uri)
        qr.make(fit=True)

        if format == "svg":
            from qrcode.image.svg import SvgPathImage

            img = qr.make_image(image_factory=SvgPathImage)
            buffer = io.BytesIO()
            img.save(buffer)
            return buffer.getvalue().decode("utf-8")

        # Default: base64 PNG
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        img_base64 = base64.b64encode(buffer.getvalue()).decode()
        return f"data:image/png;base64,{img_base64}"

    @classmethod
    @transaction.atomic
    def verify_code(
        cls,
        device: TOTPDevice,
        code: str,
        save_on_success: bool = True,
    ) -> bool:
        """
        Verify TOTP code against device secret.

        Features:
        - Time window tolerance (±30 seconds)
        - Code reuse prevention (replay attack protection)
        - Failed attempts tracking

        Args:
            device: TOTP device to verify against
            code: 6-digit TOTP code
            save_on_success: Whether to update device on success

        Returns:
            True if code is valid
        """
        cleaned_code = code.strip()

        # Check if code was already used (replay protection)
        if device.last_verified_code == cleaned_code:
            logger.warning(
                f"Code reuse attempt for device {device.id} (user {device.user.email})"
            )
            device.record_failure()
            return False

        # Verify code with pyotp
        totp = pyotp.TOTP(device.secret)
        is_valid = totp.verify(cleaned_code, valid_window=cls.VALID_WINDOW)

        if is_valid:
            if save_on_success:
                device.record_success(cleaned_code)
            logger.info(
                f"Successful TOTP verification for device {device.id} (user {device.user.email})"
            )
            return True

        device.record_failure()
        logger.warning(
            f"Failed TOTP verification for device {device.id} (user {device.user.email})"
        )
        return False

    @classmethod
    @transaction.atomic
    def confirm_device(cls, device: TOTPDevice, code: str) -> bool:
        """
        Confirm device setup with first valid code.

        Transitions device from PENDING to ACTIVE status.

        Args:
            device: TOTP device to confirm
            code: Verification code

        Returns:
            True if confirmation successful
        """
        if device.status != DeviceStatus.PENDING:
            logger.warning(
                f"Attempted to confirm non-pending device {device.id} (status: {device.status})"
            )
            return False

        if cls.verify_code(device, code, save_on_success=False):
            device.confirm()
            device.record_success(code)
            logger.info(f"Confirmed TOTP device {device.id} for user {device.user.email}")
            return True

        return False

    @classmethod
    @transaction.atomic
    def disable_device(cls, device: TOTPDevice) -> None:
        """
        Disable a TOTP device.

        Args:
            device: Device to disable
        """
        device.disable()
        logger.info(f"Disabled TOTP device {device.id} for user {device.user.email}")

    @classmethod
    def get_primary_device(cls, user: User) -> Optional[TOTPDevice]:
        """
        Get user's primary active TOTP device.

        Args:
            user: User to get device for

        Returns:
            Primary TOTPDevice or None
        """
        return (
            TOTPDevice.objects.filter(
                user=user,
                status=DeviceStatus.ACTIVE,
                is_primary=True,
            )
            .first()
        )

    @classmethod
    def get_active_devices(cls, user: User):
        """
        Get all active TOTP devices for user.

        Args:
            user: User to get devices for

        Returns:
            QuerySet of active TOTPDevice instances
        """
        return TOTPDevice.objects.filter(
            user=user,
            status=DeviceStatus.ACTIVE,
        )

    @classmethod
    def has_active_device(cls, user: User) -> bool:
        """
        Check if user has any active TOTP device.

        Args:
            user: User to check

        Returns:
            True if user has at least one active device
        """
        return TOTPDevice.objects.filter(
            user=user,
            status=DeviceStatus.ACTIVE,
        ).exists()
