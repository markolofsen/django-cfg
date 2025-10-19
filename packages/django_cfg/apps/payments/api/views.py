"""
DRF Views for Payments v2.0.

API endpoints for payment operations.
"""

import logging
from decimal import Decimal

from django.conf import settings
from django.core.cache import cache
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse

from ..models import Payment, Currency, UserBalance, Transaction
from ..services import (
    PaymentService,
    CreatePaymentRequest,
    CheckStatusRequest,
    ConfirmPaymentRequest,
    BalanceService,
    GetBalanceRequest,
    GetTransactionsRequest,
)
from ..services.providers import NowPaymentsProvider
from .serializers import (
    CurrencySerializer,
    PaymentCreateSerializer,
    PaymentDetailSerializer,
    PaymentListSerializer,
    BalanceSerializer,
    TransactionSerializer,
)

logger = logging.getLogger(__name__)


# Helper function to get provider instance
def get_nowpayments_provider() -> NowPaymentsProvider:
    """
    Get NowPayments provider instance from django_cfg configuration.

    Returns:
        NowPaymentsProvider instance

    Raises:
        ValueError: If configuration is not found or invalid
    """
    from ..config import get_nowpayments_config

    config = get_nowpayments_config()

    if not config:
        raise ValueError(
            "NowPayments configuration not found. "
            "Please configure payments.nowpayments in your django_cfg settings."
        )

    return NowPaymentsProvider(config)


# Currency Views

class CurrencyListView(APIView):
    """
    Get list of available currencies.

    Cached on production for performance.
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Get available currencies",
        description="Returns list of available currencies with token+network info",
        responses={
            200: CurrencySerializer(many=True)
        }
    )
    def get(self, request):
        """
        GET /api/v1/payments/currencies/

        Returns list of available currencies with token+network info.
        """
        cache_key = 'payments_currencies'
        cache_timeout = 3600  # 1 hour

        # Try to get from cache (only in production)
        if not settings.DEBUG:
            cached_data = cache.get(cache_key)
            if cached_data:
                logger.debug("Returning currencies from cache")
                return Response({
                    'success': True,
                    'currencies': cached_data,
                    'cached': True
                })

        # Get from database
        currencies = Currency.objects.filter(is_active=True).order_by('sort_order', 'token', 'network')
        serializer = CurrencySerializer(currencies, many=True)

        # Cache in production
        if not settings.DEBUG:
            cache.set(cache_key, serializer.data, cache_timeout)

        return Response({
            'success': True,
            'currencies': serializer.data,
            'cached': False
        })


# Payment Views

class PaymentViewSet(ReadOnlyModelViewSet):
    """
    ViewSet for payment operations.

    Endpoints:
    - GET /payments/ - List user's payments
    - GET /payments/{id}/ - Get payment details
    - POST /payments/create/ - Create new payment
    - GET /payments/{id}/status/ - Check payment status
    - POST /payments/{id}/confirm/ - Confirm payment
    """

    permission_classes = [IsAuthenticated]
    serializer_class = PaymentListSerializer

    def get_queryset(self):
        """Get payments for current user only."""
        return Payment.objects.filter(user=self.request.user).select_related('currency')

    def get_serializer_class(self):
        """Use detailed serializer for retrieve action."""
        if self.action == 'retrieve':
            return PaymentDetailSerializer
        return PaymentListSerializer

    @action(detail=False, methods=['post'], url_path='create')
    def create_payment(self, request):
        """
        POST /api/v1/payments/create/

        Create new payment.

        Request body:
        {
            "amount_usd": "100.00",
            "currency_code": "USDTTRC20",
            "description": "Optional description"
        }
        """
        # Validate request with DRF serializer
        serializer = PaymentCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        # Create Pydantic request for service layer
        service_request = CreatePaymentRequest(
            user_id=request.user.id,
            amount_usd=serializer.validated_data['amount_usd'],
            currency_code=serializer.validated_data['currency_code'],
            description=serializer.validated_data.get('description', '')
        )

        # Call service
        provider = get_nowpayments_provider()
        payment_service = PaymentService(provider)
        result = payment_service.create_payment(service_request)

        if not result.success:
            return Response({
                'success': False,
                'error': result.error
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Get payment and serialize
        payment = Payment.objects.select_related('currency').get(id=result.payment_id)
        payment_serializer = PaymentDetailSerializer(payment)

        return Response({
            'success': True,
            'payment': payment_serializer.data,
            'qr_code_url': result.qr_code_url,
        }, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'], url_path='status')
    def check_status(self, request, pk=None):
        """
        GET /api/v1/payments/{id}/status/?refresh=true

        Check payment status (with optional refresh from provider).

        Query params:
        - refresh: boolean (default: false) - Force refresh from provider
        """
        payment = self.get_object()

        # Get refresh parameter
        force_refresh = request.query_params.get('refresh', 'false').lower() == 'true'

        # Create service request
        service_request = CheckStatusRequest(
            payment_id=payment.id,
            user_id=request.user.id,
            force_refresh=force_refresh
        )

        # Call service
        provider = get_nowpayments_provider()
        payment_service = PaymentService(provider)
        result = payment_service.check_payment_status(service_request)

        if not result.success:
            return Response({
                'success': False,
                'error': result.error
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({
            'success': True,
            'status': result.status,
            'is_completed': result.is_completed,
            'transaction_hash': result.transaction_hash,
            'message': result.message
        })

    @action(detail=True, methods=['post'], url_path='confirm')
    def confirm_payment(self, request, pk=None):
        """
        POST /api/v1/payments/{id}/confirm/

        Confirm payment (user clicked "I have paid").
        Checks status with provider and creates transaction if completed.
        """
        payment = self.get_object()

        # Create service request
        service_request = ConfirmPaymentRequest(
            payment_id=payment.id,
            user_id=request.user.id
        )

        # Call service
        provider = get_nowpayments_provider()
        payment_service = PaymentService(provider)
        result = payment_service.confirm_payment(service_request)

        response_data = {
            'success': result.success,
            'payment_status': result.payment_status,
            'message': result.message
        }

        if result.success:
            response_data['transaction_id'] = str(result.transaction_id) if result.transaction_id else None
            response_data['balance_after'] = str(result.balance_after) if result.balance_after else None

        return Response(response_data)


# Balance Views

class BalanceView(APIView):
    """
    Get user balance.

    GET /api/v1/payments/balance/
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Get user balance",
        description="Get current user balance and transaction statistics",
        responses={
            200: BalanceSerializer
        }
    )
    def get(self, request):
        """Get current user balance."""
        service_request = GetBalanceRequest(user_id=request.user.id)

        balance_service = BalanceService()
        balance_info = balance_service.get_balance(service_request)

        if not balance_info:
            return Response({
                'success': False,
                'error': 'Failed to get balance'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({
            'success': True,
            'balance': {
                'balance_usd': str(balance_info.balance_usd),
                'total_deposited': str(balance_info.total_deposited),
                'total_withdrawn': str(balance_info.total_withdrawn),
                'last_transaction_at': balance_info.last_transaction_at
            }
        })


class TransactionListView(APIView):
    """
    Get user transactions.

    GET /api/v1/payments/transactions/?limit=50&offset=0&type=deposit
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Get user transactions",
        description="Get user transactions with pagination and filtering",
        parameters=[
            OpenApiParameter(
                name='limit',
                type=int,
                location=OpenApiParameter.QUERY,
                description='Number of transactions to return (max 100)',
                required=False
            ),
            OpenApiParameter(
                name='offset',
                type=int,
                location=OpenApiParameter.QUERY,
                description='Offset for pagination',
                required=False
            ),
            OpenApiParameter(
                name='type',
                type=str,
                location=OpenApiParameter.QUERY,
                description='Filter by transaction type (deposit/withdrawal)',
                required=False
            ),
        ],
        responses={
            200: TransactionSerializer(many=True)
        }
    )
    def get(self, request):
        """Get user transactions with pagination."""
        # Parse query params
        limit = int(request.query_params.get('limit', 50))
        offset = int(request.query_params.get('offset', 0))
        transaction_type = request.query_params.get('type')

        # Validate limit
        if limit > 100:
            limit = 100
        if limit < 1:
            limit = 1

        # Create service request
        service_request = GetTransactionsRequest(
            user_id=request.user.id,
            limit=limit,
            offset=offset,
            transaction_type=transaction_type
        )

        # Call service
        balance_service = BalanceService()
        result = balance_service.get_transactions(service_request)

        return Response({
            'success': True,
            'transactions': [
                {
                    'id': str(t.id),
                    'transaction_type': t.transaction_type,
                    'amount_usd': str(t.amount_usd),
                    'balance_after': str(t.balance_after),
                    'payment_id': t.payment_id,
                    'description': t.description,
                    'created_at': t.created_at
                }
                for t in result.transactions
            ],
            'total_count': result.total_count,
            'has_more': result.has_more,
            'limit': limit,
            'offset': offset
        })
