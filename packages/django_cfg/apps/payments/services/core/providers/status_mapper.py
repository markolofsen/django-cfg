"""
Provider status mapping.

Maps provider-specific statuses to universal payment statuses.
"""

from typing import Optional


class StatusMapper:
    """Map provider statuses to universal statuses."""

    # Universal status mapping for NowPayments
    NOWPAYMENTS_STATUS_MAP = {
        'waiting': 'pending',
        'confirming': 'confirming',
        'confirmed': 'confirmed',
        'finished': 'completed',
        'failed': 'failed',
        'refunded': 'refunded',
        'expired': 'expired'
    }

    # For compatibility with UniversalPayment.PaymentStatus enum
    ENUM_STATUS_MAP = {
        'waiting': 'PENDING',
        'confirming': 'PENDING',
        'confirmed': 'COMPLETED',
        'sending': 'PENDING',
        'partially_paid': 'PENDING',
        'finished': 'COMPLETED',
        'failed': 'FAILED',
        'refunded': 'FAILED',
        'expired': 'EXPIRED',
    }

    @classmethod
    def map_status(
        cls,
        provider_status: str,
        provider: str
    ) -> Optional[str]:
        """
        Map provider status to universal status.

        Args:
            provider_status: Status from provider
            provider: Provider name (e.g., 'nowpayments')

        Returns:
            Universal status string or None if mapping not found
        """
        if not provider_status:
            return None

        provider_status_lower = provider_status.lower()

        if provider == 'nowpayments':
            return cls.NOWPAYMENTS_STATUS_MAP.get(provider_status_lower)

        # Default: return lowercased status
        return provider_status_lower

    @classmethod
    def map_status_to_enum(
        cls,
        provider_status: str,
        payment_status_enum
    ):
        """
        Map provider status to PaymentStatus enum value.

        Args:
            provider_status: Status from provider
            payment_status_enum: UniversalPayment.PaymentStatus enum class

        Returns:
            Enum value or None
        """
        if not provider_status:
            return None

        provider_status_lower = provider_status.lower()
        enum_key = cls.ENUM_STATUS_MAP.get(provider_status_lower)

        if enum_key:
            return getattr(payment_status_enum, enum_key, None)

        return None
