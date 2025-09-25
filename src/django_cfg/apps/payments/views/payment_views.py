"""
Payment ViewSets with nested routing.
"""

from rest_framework import viewsets, permissions, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import get_user_model
from ..models import UniversalPayment
from ..serializers import (
    UniversalPaymentSerializer, PaymentCreateSerializer, PaymentListSerializer
)

User = get_user_model()


class UserPaymentViewSet(viewsets.ModelViewSet):
    """Nested ViewSet for user payments: /users/{user_id}/payments/"""
    
    serializer_class = UniversalPaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'provider', 'currency_code']
    
    def get_queryset(self):
        """Filter by user from URL."""
        user_id = self.kwargs.get('user_pk')
        return UniversalPayment.objects.filter(user_id=user_id).order_by('-created_at')
    
    def get_serializer_class(self):
        """Use different serializers for different actions."""
        if self.action == 'create':
            return PaymentCreateSerializer
        elif self.action == 'list':
            return PaymentListSerializer
        return UniversalPaymentSerializer
    
    def perform_create(self, serializer):
        """Set user from URL when creating."""
        user_id = self.kwargs.get('user_pk')
        user = User.objects.get(id=user_id)
        serializer.save(user=user)
    
    @action(detail=True, methods=['post'])
    def check_status(self, request, user_pk=None, pk=None):
        """Check payment status via provider API."""
        payment = self.get_object()
        
        # Import PaymentService to check status with provider
        from ..services.core.payment_service import PaymentService
        
        try:
            payment_service = PaymentService()
            status_result = payment_service.get_payment_status(str(payment.id))
            
            if status_result.success:
                # Update local payment status if it changed
                if payment.status != status_result.status:
                    payment.status = status_result.status
                    payment.save(update_fields=['status', 'updated_at'])
                
                return Response({
                    'payment_id': str(payment.id),
                    'status': status_result.status,
                    'provider_status': status_result.provider_status,
                    'updated': payment.status != status_result.status
                })
            else:
                return Response({
                    'payment_id': str(payment.id),
                    'status': payment.status,
                    'error': status_result.error_message,
                    'provider_check_failed': True
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            # Log error but don't fail completely
            from django_cfg.modules.django_logger import get_logger
            logger = get_logger("payment_views")
            logger.error(f"Payment status check failed for {payment.id}: {e}")
            
            return Response({
                'payment_id': str(payment.id),
                'status': payment.status,
                'error': 'Status check temporarily unavailable',
                'provider_check_failed': True
            })
    
    @action(detail=False, methods=['get'])
    def summary(self, request, user_pk=None):
        """Get payment summary for user."""
        queryset = self.get_queryset()
        
        total_payments = queryset.count()
        total_amount = sum(p.amount_usd for p in queryset if p.status == 'completed')
        pending_amount = sum(p.amount_usd for p in queryset if p.status == 'pending')
        
        return Response({
            'total_payments': total_payments,
            'total_amount_usd': total_amount,
            'pending_amount_usd': pending_amount,
            'completed_payments': queryset.filter(status='completed').count(),
            'pending_payments': queryset.filter(status='pending').count(),
        })


class UniversalPaymentViewSet(viewsets.ReadOnlyModelViewSet):
    """Global payment ViewSet: /payments/"""
    
    queryset = UniversalPayment.objects.all()
    serializer_class = UniversalPaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'provider', 'currency_code']
    
    def get_queryset(self):
        """Filter by current user for security."""
        return UniversalPayment.objects.filter(user=self.request.user).order_by('-created_at')
    
    def get_serializer_class(self):
        """Use list serializer for list action."""
        if self.action == 'list':
            return PaymentListSerializer
        return UniversalPaymentSerializer


# Generic views for specific use cases
class PaymentCreateView(generics.CreateAPIView):
    """Generic view to create payment."""
    
    serializer_class = PaymentCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        """Set current user when creating."""
        serializer.save(user=self.request.user)


class PaymentStatusView(generics.RetrieveAPIView):
    """Generic view to check payment status."""
    
    serializer_class = UniversalPaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'internal_payment_id'
    
    def get_queryset(self):
        """Filter by current user."""
        return UniversalPayment.objects.filter(user=self.request.user)
