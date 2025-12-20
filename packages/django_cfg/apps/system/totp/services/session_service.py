"""Two-factor authentication session service."""

from datetime import timedelta
from typing import Optional

from django.contrib.auth import get_user_model
from django.db import transaction
from django.http import HttpRequest
from django.utils import timezone

from django_cfg.utils import get_logger

from ..models import SessionStatus, TwoFactorSession
from .backup_service import BackupCodeService
from .totp_service import TOTPService

logger = get_logger(__name__)

User = get_user_model()


class TwoFactorSessionService:
    """
    Manage 2FA verification sessions during authentication flow.

    Sessions are created after primary authentication (OTP/password)
    and track the 2FA verification state.
    """

    SESSION_LIFETIME = timedelta(minutes=5)
    VERIFIED_LIFETIME = timedelta(hours=24)

    @classmethod
    def create_session(
        cls,
        user: User,
        request: Optional[HttpRequest] = None,
        lifetime_minutes: Optional[int] = None,
    ) -> TwoFactorSession:
        """
        Create pending 2FA session after primary auth.

        Args:
            user: User who completed primary authentication
            request: HTTP request for context (IP, user agent)
            lifetime_minutes: Session validity in minutes (default: 5)

        Returns:
            Created TwoFactorSession instance
        """
        lifetime = lifetime_minutes or 5

        session = TwoFactorSession.create_for_user(
            user=user,
            request=request,
            lifetime_minutes=lifetime,
        )

        logger.info(
            f"Created 2FA session {session.id} for user {user.email}, "
            f"expires in {lifetime} minutes"
        )
        return session

    @classmethod
    @transaction.atomic
    def verify_session(
        cls,
        session: TwoFactorSession,
        code: str,
        is_backup_code: bool = False,
    ) -> bool:
        """
        Verify 2FA code for session.

        Validates code against user's primary device or backup codes.
        Marks session as verified on success.

        Args:
            session: 2FA session to verify
            code: TOTP code or backup code
            is_backup_code: Whether code is a backup code

        Returns:
            True if verification successful
        """
        # Check session validity
        if session.is_expired:
            session.mark_expired()
            logger.warning(f"Attempted verification of expired session {session.id}")
            return False

        if session.is_locked:
            logger.warning(f"Attempted verification of locked session {session.id}")
            return False

        if session.is_verified:
            logger.warning(f"Attempted re-verification of session {session.id}")
            return True

        # Verify code
        is_valid = False

        if is_backup_code:
            # Verify with backup code
            is_valid = BackupCodeService.verify_code(session.user, code)
            if is_valid:
                logger.info(
                    f"Session {session.id} verified with backup code for user {session.user.email}"
                )
        else:
            # Verify with TOTP device
            device = TOTPService.get_primary_device(session.user)
            if not device:
                logger.error(
                    f"No primary TOTP device found for user {session.user.email}"
                )
                session.record_attempt()
                return False

            is_valid = TOTPService.verify_code(device, code)
            if is_valid:
                logger.info(
                    f"Session {session.id} verified with TOTP device for user {session.user.email}"
                )

        # Update session
        if is_valid:
            session.mark_verified()
            return True

        # Failed verification
        session.record_attempt()
        logger.warning(
            f"Failed verification attempt for session {session.id}. "
            f"Attempts: {session.attempts}/{session.max_attempts}"
        )
        return False

    @classmethod
    def get_session(cls, session_id: str) -> Optional[TwoFactorSession]:
        """
        Get 2FA session by ID.

        Args:
            session_id: UUID of session

        Returns:
            TwoFactorSession instance or None
        """
        try:
            return TwoFactorSession.objects.get(id=session_id)
        except TwoFactorSession.DoesNotExist:
            return None

    @classmethod
    def is_verified(
        cls,
        user: User,
        request: Optional[HttpRequest] = None,
    ) -> bool:
        """
        Check if current request has valid 2FA verification.

        Used by middleware and decorators to enforce 2FA.

        Args:
            user: User to check verification for
            request: HTTP request (optional, for session tracking)

        Returns:
            True if 2FA verified within validity period
        """
        if not user.is_authenticated:
            return False

        # Check if user has 2FA enabled
        if not TOTPService.has_active_device(user):
            return True  # 2FA not enabled, allow access

        # Check for recent verified session
        cutoff = timezone.now() - cls.VERIFIED_LIFETIME

        return TwoFactorSession.objects.filter(
            user=user,
            status=SessionStatus.VERIFIED,
            verified_at__gte=cutoff,
        ).exists()

    @classmethod
    def is_recently_verified(
        cls,
        user: User,
        max_age_hours: int = 1,
    ) -> bool:
        """
        Check if user has recent 2FA verification.

        Args:
            user: User to check
            max_age_hours: Maximum age of verification in hours

        Returns:
            True if verified within max_age_hours
        """
        if not user.is_authenticated:
            return False

        if not TOTPService.has_active_device(user):
            return True  # 2FA not enabled

        cutoff = timezone.now() - timedelta(hours=max_age_hours)

        return TwoFactorSession.objects.filter(
            user=user,
            status=SessionStatus.VERIFIED,
            verified_at__gte=cutoff,
        ).exists()

    @classmethod
    @transaction.atomic
    def cleanup_expired(cls, older_than_hours: int = 24) -> int:
        """
        Clean up expired 2FA sessions.

        Args:
            older_than_hours: Remove sessions older than this many hours

        Returns:
            Number of sessions deleted
        """
        cutoff = timezone.now() - timedelta(hours=older_than_hours)

        # Mark expired pending sessions
        expired_count = TwoFactorSession.objects.filter(
            status=SessionStatus.PENDING,
            expires_at__lt=timezone.now(),
        ).update(status=SessionStatus.EXPIRED)

        # Delete old sessions
        deleted_count, _ = TwoFactorSession.objects.filter(
            created_at__lt=cutoff,
        ).delete()

        if expired_count or deleted_count:
            logger.info(
                f"Cleaned up 2FA sessions: {expired_count} expired, {deleted_count} deleted"
            )

        return deleted_count

    @classmethod
    def get_user_sessions(cls, user: User, status: Optional[str] = None):
        """
        Get 2FA sessions for user.

        Args:
            user: User to get sessions for
            status: Optional status filter

        Returns:
            QuerySet of TwoFactorSession instances
        """
        qs = TwoFactorSession.objects.filter(user=user)
        if status:
            qs = qs.filter(status=status)
        return qs.order_by("-created_at")
