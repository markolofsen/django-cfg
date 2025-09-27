"""
Payment ViewSets for the Universal Payment System v2.0.

DRF ViewSets with service layer integration and nested routing support.
"""

from rest_framework import viewsets, permissions, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from .base import PaymentBaseViewSet, NestedPaymentViewSet
from ...models import UniversalPayment
from ...services import get_payment_service
from ..serializers.payments import (
    PaymentSerializer,
    PaymentCreateSerializer,
    PaymentListSerializer,
    PaymentStatusSerializer,
    PaymentCancelSerializer,
    PaymentStatsSerializer,
)
from django_cfg.modules.django_logger import get_logger

User = get_user_model()
logger = get_logger("payment_viewsets")


class PaymentViewSet(PaymentBaseViewSet):
    """
    Global payment ViewSet: /api/v1/payments/
    
    Provides admin-level access to all payments with filtering and stats.
    """
    
    queryset = UniversalPayment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]  # Allow authenticated users
    filterset_fields = ['status', 'provider', 'currency__code', 'user']
    search_fields = ['description', 'provider_payment_id', 'transaction_hash']
    ordering_fields = ['created_at', 'updated_at', 'amount_usd', 'expires_at']
    
    serializer_classes = {
        'list': PaymentListSerializer,
        'create': PaymentCreateSerializer,
        'retrieve': PaymentSerializer,
        'update': PaymentSerializer,
        'partial_update': PaymentSerializer,
    }
    
    def get_queryset(self):
        """Optimized queryset with related objects."""
        queryset = super().get_queryset().select_related('user').prefetch_related(
            'user__payment_balance'
        )
        
        # Non-staff users can only see their own payments
        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def check_status(self, request, pk=None):
        """
        Check payment status with provider.
        
        POST /api/v1/payments/{id}/check_status/
        """
        payment = self.get_object()
        
        serializer = PaymentStatusSerializer(
            data=request.data,
            context={
                **self.get_serializer_context(),
                'payment_id': str(payment.id)
            }
        )
        
        if serializer.is_valid():
            result = serializer.save()
            return Response(result)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """
        Cancel payment.
        
        POST /api/v1/payments/{id}/cancel/
        """
        payment = self.get_object()
        
        if not payment.can_be_cancelled():
            return Response(
                {'error': f'Payment cannot be cancelled (status: {payment.status})'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = PaymentCancelSerializer(
            data=request.data,
            context={
                **self.get_serializer_context(),
                'payment_id': str(payment.id)
            }
        )
        
        if serializer.is_valid():
            result = serializer.save()
            return Response(result)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def analytics(self, request):
        """
        Get payment analytics.
        
        GET /api/v1/payments/analytics/?days=30
        """
        serializer = PaymentStatsSerializer(data=request.query_params)
        
        if serializer.is_valid():
            result = serializer.save()
            return Response(result)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def by_provider(self, request):
        """
        Get payments grouped by provider.
        
        GET /api/v1/payments/by_provider/
        """
        try:
            queryset = self.filter_queryset(self.get_queryset())
            
            provider_stats = {}
            for provider_choice in UniversalPayment.PaymentProvider.choices:
                provider_code = provider_choice[0]
                provider_name = provider_choice[1]
                
                provider_payments = queryset.filter(provider=provider_code)
                
                provider_stats[provider_code] = {
                    'name': provider_name,
                    'total_payments': provider_payments.count(),
                    'total_amount_usd': float(
                        provider_payments.aggregate(
                            total=models.Sum('amount_usd')
                        )['total'] or 0
                    ),
                    'status_breakdown': dict(
                        provider_payments.values('status')
                        .annotate(count=models.Count('id'))
                        .values_list('status', 'count')
                    )
                }
            
            return Response({
                'provider_stats': provider_stats,
                'generated_at': timezone.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Provider stats failed: {e}")
            return Response(
                {'error': f'Provider stats failed: {e}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UserPaymentViewSet(NestedPaymentViewSet):
    """
    User-specific payment ViewSet: /api/v1/users/{user_id}/payments/
    
    Provides user-scoped access to payments with full CRUD operations.
    """
    
    queryset = UniversalPayment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['status', 'provider', 'currency__code']
    search_fields = ['description', 'provider_payment_id']
    ordering_fields = ['created_at', 'updated_at', 'amount_usd', 'expires_at']
    
    # Nested ViewSet configuration
    parent_lookup_field = 'user_pk'
    parent_model_field = 'user'
    
    serializer_classes = {
        'list': PaymentListSerializer,
        'create': PaymentCreateSerializer,
        'retrieve': PaymentSerializer,
    }
    
    def get_queryset(self):
        """Filter by user and optimize queryset."""
        queryset = super().get_queryset()
        
        # Additional permission check: users can only see their own payments
        if not self.request.user.is_staff:
            user_id = self.kwargs.get('user_pk')
            if str(self.request.user.id) != str(user_id):
                return queryset.none()  # Return empty queryset for unauthorized access
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def check_status(self, request, user_pk=None, pk=None):
        """
        Check payment status with provider.
        
        POST /api/v1/users/{user_id}/payments/{id}/check_status/
        """
        payment = self.get_object()
        
        serializer = PaymentStatusSerializer(
            data=request.data,
            context={
                **self.get_serializer_context(),
                'payment_id': str(payment.id)
            }
        )
        
        if serializer.is_valid():
            result = serializer.save()
            return Response(result)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, user_pk=None, pk=None):
        """
        Cancel payment.
        
        POST /api/v1/users/{user_id}/payments/{id}/cancel/
        """
        payment = self.get_object()
        
        if not payment.can_be_cancelled():
            return Response(
                {'error': f'Payment cannot be cancelled (status: {payment.status})'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = PaymentCancelSerializer(
            data=request.data,
            context={
                **self.get_serializer_context(),
                'payment_id': str(payment.id)
            }
        )
        
        if serializer.is_valid():
            result = serializer.save()
            return Response(result)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def summary(self, request, user_pk=None):
        """
        Get user payment summary.
        
        GET /api/v1/users/{user_id}/payments/summary/
        """
        try:
            queryset = self.filter_queryset(self.get_queryset())
            
            from django.db import models
            
            summary = queryset.aggregate(
                total_payments=models.Count('id'),
                total_amount_usd=models.Sum('amount_usd'),
                completed_payments=models.Count(
                    'id',
                    filter=models.Q(status=UniversalPayment.PaymentStatus.COMPLETED)
                ),
                pending_payments=models.Count(
                    'id',
                    filter=models.Q(status=UniversalPayment.PaymentStatus.PENDING)
                ),
                failed_payments=models.Count(
                    'id',
                    filter=models.Q(status=UniversalPayment.PaymentStatus.FAILED)
                ),
            )
            
            # Calculate success rate
            total = summary['total_payments']
            completed = summary['completed_payments']
            success_rate = (completed / total * 100) if total > 0 else 0
            
            return Response({
                'user_id': user_pk,
                'summary': {
                    **summary,
                    'total_amount_usd': float(summary['total_amount_usd'] or 0),
                    'success_rate': round(success_rate, 2),
                },
                'generated_at': timezone.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"User payment summary failed: {e}")
            return Response(
                {'error': f'Summary generation failed: {e}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PaymentCreateView(generics.CreateAPIView):
    """
    Standalone payment creation endpoint: /api/v1/payments/create/
    
    Simplified endpoint for payment creation without full ViewSet overhead.
    """
    
    serializer_class = PaymentCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        """Create payment with enhanced response."""
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            try:
                payment = serializer.save()
                
                response_data = {
                    'success': True,
                    'message': 'Payment created successfully',
                    'payment': PaymentSerializer(payment, context={'request': request}).data
                }
                
                return Response(response_data, status=status.HTTP_201_CREATED)
                
            except Exception as e:
                logger.error(f"Payment creation failed: {e}")
                return Response(
                    {
                        'success': False,
                        'error': f'Payment creation failed: {e}',
                        'error_code': 'creation_failed'
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        return Response(
            {
                'success': False,
                'error': 'Invalid payment data',
                'errors': serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )


class PaymentStatusView(generics.RetrieveAPIView):
    """
    Standalone payment status endpoint: /api/v1/payments/{id}/status/
    
    Quick status check without full ViewSet overhead.
    """
    
    queryset = UniversalPayment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'
    
    def get_object(self):
        """Get payment with permission check."""
        payment = super().get_object()
        
        # Users can only check their own payments unless they're staff
        if not self.request.user.is_staff and payment.user != self.request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You can only check your own payments")
        
        return payment
    
    def retrieve(self, request, *args, **kwargs):
        """Get payment status with optional provider check."""
        payment = self.get_object()
        
        # Check if force provider check is requested
        force_check = request.query_params.get('force_check', 'false').lower() == 'true'
        
        if force_check:
            # Use PaymentService to check with provider
            try:
                payment_service = get_payment_service()
                from ...services.types import PaymentStatusRequest
                
                status_request = PaymentStatusRequest(
                    payment_id=str(payment.id),
                    user_id=request.user.id,
                    force_provider_check=True
                )
                
                result = payment_service.get_payment_status(status_request)
                
                if result.success:
                    # Refresh payment from database
                    payment.refresh_from_db()
                
            except Exception as e:
                logger.warning(f"Provider status check failed: {e}")
        
        serializer = self.get_serializer(payment)
        return Response({
            'success': True,
            'payment': serializer.data,
            'provider_checked': force_check,
            'timestamp': timezone.now().isoformat()
        })
