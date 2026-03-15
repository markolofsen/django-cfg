"""Backup recovery code service."""

from typing import List, Optional

from django.contrib.auth import get_user_model
from django.db import transaction

from django_cfg.utils import get_logger

from ..models import BackupCode

logger = get_logger(__name__)

User = get_user_model()


class BackupCodeService:
    """
    Backup recovery code management service.

    Backup codes provide emergency access when TOTP device is unavailable.
    Each code can only be used once.
    """

    CODE_LENGTH = 8
    CODE_COUNT = 10

    @classmethod
    @transaction.atomic
    def generate_codes(
        cls,
        user: User,
        count: Optional[int] = None,
        length: Optional[int] = None,
    ) -> List[str]:
        """
        Generate new set of backup codes for user.

        - Invalidates all existing codes
        - Generates CODE_COUNT new codes
        - Returns plaintext codes (show once to user)
        - Stores only hashed codes in database

        Args:
            user: User to generate codes for
            count: Number of codes to generate (default: CODE_COUNT)
            length: Length of each code (default: CODE_LENGTH)

        Returns:
            List of plaintext backup codes
        """
        count = count or cls.CODE_COUNT
        length = length or cls.CODE_LENGTH

        # Invalidate all existing backup codes
        cls.invalidate_all(user)

        # Generate new codes
        plaintext_codes = []
        for _ in range(count):
            code = BackupCode.generate_code(length=length)
            plaintext_codes.append(code)

            # Store hashed version
            BackupCode.objects.create(
                user=user,
                code_hash=BackupCode.hash_code(code),
            )

        logger.info(f"Generated {count} backup codes for user {user.email}")
        return plaintext_codes

    @classmethod
    @transaction.atomic
    def verify_code(cls, user: User, code: str) -> bool:
        """
        Verify and consume backup code.

        Args:
            user: User attempting to use backup code
            code: Plaintext backup code

        Returns:
            True if code is valid and consumed
        """
        if not code:
            return False

        cleaned_code = code.strip().lower()
        code_hash = BackupCode.hash_code(cleaned_code)

        # Find matching unused code
        backup_code = BackupCode.objects.filter(
            user=user,
            code_hash=code_hash,
            is_used=False,
        ).first()

        if not backup_code:
            logger.warning(
                f"Invalid or already used backup code attempt for user {user.email}"
            )
            return False

        # Consume the code
        backup_code.consume()
        remaining = cls.get_remaining_count(user)

        logger.info(
            f"Backup code consumed for user {user.email}. {remaining} codes remaining."
        )
        return True

    @classmethod
    def get_remaining_count(cls, user: User) -> int:
        """
        Count unused backup codes for user.

        Args:
            user: User to count codes for

        Returns:
            Number of unused backup codes
        """
        return BackupCode.objects.filter(
            user=user,
            is_used=False,
        ).count()

    @classmethod
    @transaction.atomic
    def invalidate_all(cls, user: User) -> int:
        """
        Invalidate all backup codes for user.

        Args:
            user: User to invalidate codes for

        Returns:
            Number of codes invalidated
        """
        count = BackupCode.objects.filter(
            user=user,
            is_used=False,
        ).update(is_used=True)

        if count > 0:
            logger.info(f"Invalidated {count} backup codes for user {user.email}")

        return count

    @classmethod
    def has_codes(cls, user: User) -> bool:
        """
        Check if user has any unused backup codes.

        Args:
            user: User to check

        Returns:
            True if user has at least one unused code
        """
        return BackupCode.objects.filter(
            user=user,
            is_used=False,
        ).exists()

    @classmethod
    def should_regenerate(cls, user: User, threshold: int = 3) -> bool:
        """
        Check if user should regenerate backup codes.

        Args:
            user: User to check
            threshold: Minimum number of codes before suggesting regeneration

        Returns:
            True if remaining codes <= threshold
        """
        remaining = cls.get_remaining_count(user)
        return remaining <= threshold
