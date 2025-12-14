"""
LLM Balance Notifier.

Sends email + telegram notifications when LLM provider balances
are low based on configurable thresholds.
"""

import logging
from typing import Dict, Optional
from django.core.cache import cache

from .models import BalanceResponse

logger = logging.getLogger("django_cfg.llm_monitoring")


class LLMBalanceNotifier:
    """
    Send notifications when LLM balances are low.

    Thresholds:
    - WARNING: $10 - sends warning notification
    - CRITICAL: $5 - sends critical notification
    """

    # Threshold levels (USD)
    THRESHOLD_WARNING = 10.0
    THRESHOLD_CRITICAL = 5.0

    # Cache keys for tracking notification state
    CACHE_PREFIX = "llm_monitoring:notification_sent"

    def __init__(self):
        """Initialize notifier."""
        pass

    def _get_notification_cache_key(self, provider: str, level: str) -> str:
        """Get cache key for tracking sent notifications."""
        return f"{self.CACHE_PREFIX}:{provider}:{level}"

    def _was_notification_sent(self, provider: str, level: str) -> bool:
        """Check if notification was already sent for this provider/level."""
        cache_key = self._get_notification_cache_key(provider, level)
        return cache.get(cache_key, False)

    def _mark_notification_sent(self, provider: str, level: str):
        """Mark notification as sent (cached for 24 hours)."""
        cache_key = self._get_notification_cache_key(provider, level)
        # Cache for 24 hours - so we don't spam admins
        cache.set(cache_key, True, 60 * 60 * 24)

    def _clear_notification_cache(self, provider: str, level: str):
        """Clear notification cache (when balance is restored)."""
        cache_key = self._get_notification_cache_key(provider, level)
        cache.delete(cache_key)

    def check_and_notify(
        self,
        provider: str,
        balance_data: BalanceResponse,
        force: bool = False
    ) -> Optional[str]:
        """
        Check balance and send notification if needed.

        Also sends notifications for critical API key errors:
        - Invalid API key
        - Insufficient funds
        - Quota exceeded

        Args:
            provider: Provider name ("openai", "openrouter")
            balance_data: BalanceResponse with balance data
            force: If True, send notification even if already sent

        Returns:
            Notification level sent ("warning", "critical", "api_error", None)

        Example:
            >>> notifier = LLMBalanceNotifier()
            >>> balance = BalanceResponse(balance=4.50, currency="usd")
            >>> level = notifier.check_and_notify("openai", balance)
            >>> if level:
            ...     print(f"Sent {level} notification")
        """
        if balance_data.error:
            # Check if this is a critical API error that needs notification
            error_lower = balance_data.error.lower()
            is_critical_error = any([
                "invalid" in error_lower and "key" in error_lower,
                "unauthorized" in error_lower,
                "quota" in error_lower,
                "insufficient" in error_lower and "funds" in error_lower,
            ])

            if is_critical_error:
                # Send critical notification for API key errors
                if not force and self._was_notification_sent(provider, "api_error"):
                    logger.debug(
                        f"Skipping API error notification for {provider} - already sent in last 24h"
                    )
                    return None

                self._send_error_notification(provider, balance_data.error)
                self._mark_notification_sent(provider, "api_error")
                return "api_error"
            else:
                # Non-critical error, just log it
                logger.warning(f"Skipping notification for {provider}: {balance_data.error}")
                return None

        # Check if balance is available
        if balance_data.balance is None:
            # Balance not available (e.g., OpenAI) - only check API key status
            if balance_data.status == "valid":
                # API key is valid, no notification needed
                logger.debug(f"{provider.title()} API key valid (balance unavailable)")
                return None
            # If status is not valid, the error handling above will catch it
            return None

        balance = balance_data.balance

        # Determine notification level
        notification_level = None
        if balance <= self.THRESHOLD_CRITICAL:
            notification_level = "critical"
        elif balance <= self.THRESHOLD_WARNING:
            notification_level = "warning"

        if not notification_level:
            # Balance is OK - clear any previous notifications
            self._clear_notification_cache(provider, "warning")
            self._clear_notification_cache(provider, "critical")
            logger.debug(f"{provider.title()} balance OK: ${balance:.2f}")
            return None

        # Check if notification was already sent (unless force=True)
        if not force and self._was_notification_sent(provider, notification_level):
            logger.debug(
                f"Skipping {notification_level} notification for {provider} - already sent in last 24h"
            )
            return None

        # Send notification
        self._send_notification(provider, balance, notification_level)

        # Mark as sent
        self._mark_notification_sent(provider, notification_level)

        return notification_level

    def _send_notification(self, provider: str, balance: float, level: str):
        """
        Send email + telegram notification to admins.

        Args:
            provider: Provider name ("openai", "openrouter")
            balance: Current balance (USD)
            level: Notification level ("warning", "critical")
        """
        try:
            from django_cfg.modules.django_email import send_admin_notification

            provider_display = provider.replace("_", " ").title()

            if level == "critical":
                emoji = "🚨"
                subject = f"🚨 CRITICAL: {provider_display} Balance Low"
            else:
                emoji = "⚠️"
                subject = f"⚠️ WARNING: {provider_display} Balance Low"

            message = f"""
{emoji} {provider_display} API Balance Alert

Current Balance: ${balance:.2f} USD
Threshold: ${self.THRESHOLD_CRITICAL if level == 'critical' else self.THRESHOLD_WARNING:.2f} USD

Please add funds to your {provider_display} account to avoid service interruption.

---
This is an automated alert from LLM Balance Monitoring.
You will receive this notification once per 24 hours until the balance is restored.
            """.strip()

            # Send to admins (email + telegram)
            result = send_admin_notification(
                subject=subject,
                message=message,
                send_telegram=True,
                send_email=True,
                fail_silently=True,
            )

            if result.get("telegram") or result.get("email"):
                logger.info(
                    f"Sent {level} notification for {provider} "
                    f"(email: {result.get('email')}, telegram: {result.get('telegram')})"
                )
            else:
                logger.warning(f"Failed to send notification for {provider} - no channels succeeded")

        except Exception as e:
            logger.exception(f"Failed to send notification for {provider}: {e}")

    def _send_error_notification(self, provider: str, error: str):
        """
        Send email + telegram notification for API key errors.

        Args:
            provider: Provider name ("openai", "openrouter")
            error: Error message
        """
        try:
            from django_cfg.modules.django_email import send_admin_notification

            provider_display = provider.replace("_", " ").title()
            subject = f"🔴 CRITICAL: {provider_display} API Key Error"

            message = f"""
🔴 {provider_display} API Key Error

Error: {error}

This is a critical issue that requires immediate attention:
- Check if the API key is valid and correctly configured
- Verify the API key has not expired
- Ensure sufficient funds are available in the account

Configuration location:
- Check .env or .env.secrets file
- Verify API_KEYS__{'OPENAI' if provider == 'openai' else 'OPENROUTER'} environment variable

---
This is an automated alert from LLM Balance Monitoring.
You will receive this notification once per 24 hours until the issue is resolved.
            """.strip()

            # Send to admins (email + telegram)
            result = send_admin_notification(
                subject=subject,
                message=message,
                send_telegram=True,
                send_email=True,
                fail_silently=True,
            )

            if result.get("telegram") or result.get("email"):
                logger.info(
                    f"Sent API error notification for {provider} "
                    f"(email: {result.get('email')}, telegram: {result.get('telegram')})"
                )
            else:
                logger.warning(f"Failed to send API error notification for {provider} - no channels succeeded")

        except Exception as e:
            logger.exception(f"Failed to send API error notification for {provider}: {e}")

    def check_all_and_notify(
        self,
        balances: Dict[str, BalanceResponse],
        force: bool = False
    ) -> Dict[str, Optional[str]]:
        """
        Check all provider balances and send notifications.

        Args:
            balances: Dict with provider names as keys, BalanceResponse as values
            force: If True, send notifications even if already sent

        Returns:
            Dict with provider names as keys, notification levels as values
                {"openai": "critical", "openrouter": None}

        Example:
            >>> notifier = LLMBalanceNotifier()
            >>> checker = BalanceChecker()
            >>> balances = checker.check_all_balances()
            >>> results = notifier.check_all_and_notify(balances)
        """
        results = {}
        for provider, balance_data in balances.items():
            results[provider] = self.check_and_notify(provider, balance_data, force=force)
        return results
