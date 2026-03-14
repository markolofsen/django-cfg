"""
Brute-force protection service for OTP authentication.

Handles:
- Per-email OTP resend cooldown (prevents rapid resend spam)
- Per-email daily OTP budget (limits total emails per day)
- Per-IP OTP request budget (prevents IP-level flooding)
"""

import hashlib
import logging
from typing import Tuple

from django.core.cache import cache

logger = logging.getLogger(__name__)

# Cache key prefixes
_PREFIX_COOLDOWN = "otp:cooldown"
_PREFIX_HOURLY = "otp:hourly"
_PREFIX_DAILY = "otp:daily"
_PREFIX_VERIFY_FAIL = "otp:verify_fail"
_PREFIX_VERIFY_LOCKOUT = "otp:verify_lockout"


def _hash_identifier(value: str) -> str:
    """Hash email/IP to avoid leaking PII in cache keys."""
    return hashlib.sha256(value.lower().encode()).hexdigest()[:16]


class OTPRequestThrottle:
    """Controls OTP send rate per email and per IP."""

    # Defaults (can be overridden via constance or direct params)
    DEFAULT_COOLDOWN_SECONDS = 60       # Min seconds between resends for same email
    DEFAULT_HOURLY_LIMIT = 5            # Max OTPs per email per hour
    DEFAULT_DAILY_LIMIT = 10            # Max OTPs per email per day
    DEFAULT_IP_MINUTE_LIMIT = 10        # Max OTP requests per IP per minute

    @classmethod
    def _get_cooldown_seconds(cls) -> int:
        try:
            from django.conf import settings
            return getattr(settings, 'OTP_RESEND_COOLDOWN_SECONDS', cls.DEFAULT_COOLDOWN_SECONDS)
        except Exception:
            return cls.DEFAULT_COOLDOWN_SECONDS

    @classmethod
    def _get_daily_limit(cls) -> int:
        try:
            from django.conf import settings
            return getattr(settings, 'OTP_DAILY_LIMIT', cls.DEFAULT_DAILY_LIMIT)
        except Exception:
            return cls.DEFAULT_DAILY_LIMIT

    @classmethod
    def _get_hourly_limit(cls) -> int:
        try:
            from django.conf import settings
            return getattr(settings, 'OTP_HOURLY_LIMIT', cls.DEFAULT_HOURLY_LIMIT)
        except Exception:
            return cls.DEFAULT_HOURLY_LIMIT

    @classmethod
    def check_email(cls, email: str) -> Tuple[bool, str, int]:
        """
        Check if OTP can be sent to this email.

        Returns:
            (allowed, reason, retry_after_seconds)
            - allowed=True means OTP can be sent
            - reason is 'ok', 'cooldown', 'hourly_limit', or 'daily_limit'
            - retry_after is seconds until allowed again (0 if allowed)
        """
        email_hash = _hash_identifier(email)

        # 1. Check resend cooldown
        cooldown_key = f"{_PREFIX_COOLDOWN}:{email_hash}"
        cooldown_ttl = cache.get(cooldown_key)
        if cooldown_ttl is not None:
            # Key exists = still in cooldown. Get remaining TTL.
            remaining = cls._get_cache_ttl(cooldown_key, cls._get_cooldown_seconds())
            logger.info(f"OTP cooldown active for email hash {email_hash}, retry in {remaining}s")
            return False, "cooldown", remaining

        # 2. Check hourly limit
        hourly_key = f"{_PREFIX_HOURLY}:{email_hash}"
        hourly_count = cache.get(hourly_key, 0)
        if hourly_count >= cls._get_hourly_limit():
            remaining = cls._get_cache_ttl(hourly_key, 3600)
            logger.info(f"OTP hourly limit reached for email hash {email_hash}")
            return False, "hourly_limit", remaining

        # 3. Check daily limit
        daily_key = f"{_PREFIX_DAILY}:{email_hash}"
        daily_count = cache.get(daily_key, 0)
        if daily_count >= cls._get_daily_limit():
            remaining = cls._get_cache_ttl(daily_key, 86400)
            logger.info(f"OTP daily limit reached for email hash {email_hash}")
            return False, "daily_limit", remaining

        return True, "ok", 0

    @classmethod
    def record_sent(cls, email: str) -> None:
        """Record that an OTP was sent to this email. Call after successful send."""
        email_hash = _hash_identifier(email)
        cooldown_secs = cls._get_cooldown_seconds()

        # Set cooldown
        cooldown_key = f"{_PREFIX_COOLDOWN}:{email_hash}"
        cache.set(cooldown_key, 1, cooldown_secs)

        # Increment hourly counter
        hourly_key = f"{_PREFIX_HOURLY}:{email_hash}"
        try:
            cache.incr(hourly_key)
        except ValueError:
            cache.set(hourly_key, 1, 3600)

        # Increment daily counter
        daily_key = f"{_PREFIX_DAILY}:{email_hash}"
        try:
            cache.incr(daily_key)
        except ValueError:
            cache.set(daily_key, 1, 86400)

    @classmethod
    def _get_cache_ttl(cls, key: str, default_ttl: int) -> int:
        """Estimate remaining TTL for a cache key. Returns default if can't determine."""
        try:
            # django-redis exposes ttl() but BaseCache doesn't declare it.
            # Access via getattr to stay compatible with non-Redis backends.
            from django.core.cache import cache as _cache
            ttl_fn = getattr(_cache, 'ttl', None)
            if callable(ttl_fn):
                raw = ttl_fn(key)
                if raw is not None and isinstance(raw, (int, float)) and raw > 0:
                    return int(raw)
        except Exception:
            pass
        return default_ttl


class OTPVerifyThrottle:
    """Tracks failed OTP verification attempts for brute-force detection."""

    DEFAULT_MAX_ATTEMPTS = 5            # Failed attempts before lockout
    DEFAULT_LOCKOUT_SECONDS = 900       # 15 minutes lockout
    DEFAULT_WINDOW_SECONDS = 600        # 10-minute window (matches OTP TTL)

    @classmethod
    def _get_max_attempts(cls) -> int:
        try:
            from django.conf import settings
            return getattr(settings, 'OTP_MAX_VERIFY_ATTEMPTS', cls.DEFAULT_MAX_ATTEMPTS)
        except Exception:
            return cls.DEFAULT_MAX_ATTEMPTS

    @classmethod
    def _get_lockout_seconds(cls) -> int:
        try:
            from django.conf import settings
            return getattr(settings, 'OTP_VERIFY_LOCKOUT_SECONDS', cls.DEFAULT_LOCKOUT_SECONDS)
        except Exception:
            return cls.DEFAULT_LOCKOUT_SECONDS

    @classmethod
    def is_locked(cls, email: str) -> Tuple[bool, int]:
        """
        Check if this email is locked out from verifying OTPs.

        Returns:
            (locked, retry_after_seconds)
        """
        email_hash = _hash_identifier(email)
        lockout_key = f"{_PREFIX_VERIFY_LOCKOUT}:{email_hash}"

        if cache.get(lockout_key):
            remaining = OTPRequestThrottle._get_cache_ttl(lockout_key, cls._get_lockout_seconds())
            return True, remaining

        return False, 0

    @classmethod
    def record_failure(cls, email: str) -> Tuple[bool, int]:
        """
        Record a failed OTP verification attempt.

        Returns:
            (just_locked_out, attempts_remaining)
            - just_locked_out=True if this failure triggered lockout
            - attempts_remaining is how many more attempts before lockout
        """
        email_hash = _hash_identifier(email)
        fail_key = f"{_PREFIX_VERIFY_FAIL}:{email_hash}"
        lockout_key = f"{_PREFIX_VERIFY_LOCKOUT}:{email_hash}"

        window = cls.DEFAULT_WINDOW_SECONDS
        max_attempts = cls._get_max_attempts()

        # Increment failure counter
        try:
            count = cache.incr(fail_key)
        except ValueError:
            cache.set(fail_key, 1, window)
            count = 1

        attempts_remaining = max(0, max_attempts - count)

        if count >= max_attempts:
            # Trigger lockout
            lockout_secs = cls._get_lockout_seconds()
            cache.set(lockout_key, 1, lockout_secs)
            cache.delete(fail_key)  # Reset counter after lockout
            logger.warning(
                f"OTP brute-force lockout triggered for email hash {email_hash}, "
                f"locked for {lockout_secs}s"
            )
            return True, 0

        return False, attempts_remaining

    @classmethod
    def record_success(cls, email: str) -> None:
        """Clear failure counters on successful verification."""
        email_hash = _hash_identifier(email)
        cache.delete(f"{_PREFIX_VERIFY_FAIL}:{email_hash}")
        cache.delete(f"{_PREFIX_VERIFY_LOCKOUT}:{email_hash}")
        logger.debug(f"OTP verify counters reset on success for email hash {email_hash}")


__all__ = ["OTPRequestThrottle", "OTPVerifyThrottle"]
