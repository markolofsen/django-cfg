"""
Payment statistics calculator.

Calculates various payment statistics and metrics.
"""

from datetime import timedelta
from django.db import models
from django.utils import timezone

from ....models import UniversalPayment
from ...types import ServiceOperationResult


class StatisticsCalculator:
    """Calculate payment statistics."""

    def __init__(self, base_service):
        """
        Initialize calculator.

        Args:
            base_service: Base service for error/success result creation
        """
        self.base_service = base_service

    def get_payment_stats(self, days: int = 30) -> ServiceOperationResult:
        """
        Get payment statistics for period.

        Args:
            days: Number of days to analyze

        Returns:
            ServiceOperationResult with statistics data
        """
        try:
            since = timezone.now() - timedelta(days=days)

            stats = UniversalPayment.objects.filter(
                created_at__gte=since
            ).aggregate(
                total_payments=models.Count('id'),
                total_amount_usd=models.Sum('amount_usd'),
                completed_payments=models.Count(
                    'id',
                    filter=models.Q(status=UniversalPayment.PaymentStatus.COMPLETED)
                ),
                failed_payments=models.Count(
                    'id',
                    filter=models.Q(status=UniversalPayment.PaymentStatus.FAILED)
                )
            )

            # Calculate success rate
            total = stats['total_payments'] or 0
            completed = stats['completed_payments'] or 0
            success_rate = (completed / total * 100) if total > 0 else 0

            stats['success_rate'] = round(success_rate, 2)
            stats['period_days'] = days

            return self.base_service._create_success_result(
                f"Payment statistics for {days} days",
                stats
            )

        except Exception as e:
            return self.base_service._handle_exception("get_payment_stats", e)
