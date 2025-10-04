"""
Payment service orchestrator for the Universal Payment System v2.0.

Coordinates payment operations using specialized components.
"""

from typing import Optional
from django.contrib.auth import get_user_model

from .base import BaseService
from ..types import (
    PaymentCreateRequest, PaymentStatusRequest, PaymentResult,
    ServiceOperationResult
)
from ...models import UniversalPayment
from ..providers import get_provider_registry

# Import specialized components
from .currency import CurrencyValidator, CurrencyConverter
from .providers import ProviderClient, StatusMapper
from .utils import DataConverter, StatisticsCalculator
from .operations import PaymentCreator, PaymentCanceller, StatusChecker

User = get_user_model()


class PaymentService(BaseService):
    """
    Payment service orchestrator.

    Coordinates payment operations using specialized components.
    Delegates to:
    - PaymentCreator: Payment creation logic
    - StatusChecker: Status checking and retrieval
    - PaymentCanceller: Payment cancellation
    - CurrencyValidator/Converter: Currency operations
    - ProviderClient: Provider communication
    - DataConverter: Data transformations
    - StatisticsCalculator: Statistics and metrics
    """

    def __init__(self):
        """Initialize service with components."""
        super().__init__()

        # Initialize provider registry
        self.provider_registry = get_provider_registry()

        # Initialize currency components
        self.currency_validator = CurrencyValidator(self)
        self.currency_converter = CurrencyConverter(self)

        # Initialize provider components
        self.provider_client = ProviderClient(self.provider_registry, self)
        self.status_mapper = StatusMapper()

        # Initialize utilities
        self.data_converter = DataConverter()
        self.stats_calculator = StatisticsCalculator(self)

        # Initialize operations
        self.payment_creator = PaymentCreator(
            self.provider_registry,
            self.currency_validator,
            self
        )
        self.payment_canceller = PaymentCanceller(self)
        self.status_checker = StatusChecker(self.provider_client, self)

    def create_payment(self, request: PaymentCreateRequest) -> PaymentResult:
        """
        Create new payment.

        Delegates to PaymentCreator.

        Args:
            request: Payment creation request with validation

        Returns:
            PaymentResult: Result with payment data or error
        """
        try:
            # Validate request
            if isinstance(request, dict):
                request = PaymentCreateRequest(**request)

            # Get user
            try:
                user = User.objects.get(id=request.user_id)
            except User.DoesNotExist:
                return PaymentResult(
                    success=False,
                    message=f"User {request.user_id} not found",
                    error_code="user_not_found"
                )

            # Delegate to creator
            return self.payment_creator.create_payment(request, user)

        except Exception as e:
            return PaymentResult(**self._handle_exception(
                "create_payment", e,
                user_id=request.user_id if hasattr(request, 'user_id') else None
            ).model_dump())

    def get_payment_status(self, request: PaymentStatusRequest) -> PaymentResult:
        """
        Get payment status.

        Delegates to StatusChecker.

        Args:
            request: Payment status request

        Returns:
            PaymentResult: Current payment status
        """
        return self.status_checker.get_payment_status(request)

    def cancel_payment(self, payment_id: str, reason: str = None) -> PaymentResult:
        """
        Cancel payment.

        Delegates to PaymentCanceller.

        Args:
            payment_id: Payment ID to cancel
            reason: Cancellation reason

        Returns:
            PaymentResult: Cancellation result
        """
        return self.payment_canceller.cancel_payment(payment_id, reason)

    def get_user_payments(
        self,
        user_id: int,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> ServiceOperationResult:
        """
        Get user payments with pagination.

        Simple query method - kept in main service.

        Args:
            user_id: User ID
            status: Optional status filter
            limit: Page size
            offset: Page offset

        Returns:
            ServiceOperationResult with payments list
        """
        try:
            queryset = UniversalPayment.objects.filter(user_id=user_id)

            if status:
                queryset = queryset.filter(status=status)

            total_count = queryset.count()
            payments = queryset.order_by('-created_at')[offset:offset + limit]

            payment_data = []
            for payment in payments:
                payment_obj = self.data_converter.payment_to_data(payment)
                payment_data.append(payment_obj.model_dump())

            return self._create_success_result(
                f"Retrieved {len(payment_data)} payments",
                {
                    'payments': payment_data,
                    'total_count': total_count,
                    'limit': limit,
                    'offset': offset,
                    'has_more': offset + limit < total_count
                }
            )

        except Exception as e:
            return self._handle_exception(
                "get_user_payments", e,
                user_id=user_id
            )

    def get_payment_stats(self, days: int = 30) -> ServiceOperationResult:
        """
        Get payment statistics.

        Delegates to StatisticsCalculator.

        Args:
            days: Number of days to analyze

        Returns:
            ServiceOperationResult with statistics
        """
        return self.stats_calculator.get_payment_stats(days)

    # Private helper methods for backward compatibility

    def _get_user(self, user_id: int):
        """
        Get user by ID.

        Helper method for internal use.

        Args:
            user_id: User ID

        Returns:
            User instance or None
        """
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None
