"""
Admin Payment ViewSets.

DRF ViewSets for payment management in admin interface.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import serializers
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Count, Sum, Avg, Q
from django.utils import timezone
from datetime import timedelta

from django_cfg.apps.payments.admin_interface.views.base import AdminBaseViewSet
from django_cfg.apps.payments.models import UniversalPayment
from django_cfg.apps.payments.admin_interface.serializers import (
    AdminPaymentListSerializer,
    AdminPaymentDetailSerializer,
    AdminPaymentCreateSerializer,
    AdminPaymentUpdateSerializer,
    AdminPaymentStatsSerializer,
)
from django_cfg.modules.django_logging import get_logger

logger = get_logger("admin_payment_api")


class AdminPaymentViewSet(AdminBaseViewSet):
    """
    Admin ViewSet for payment management.
    
    Provides full CRUD operations for payments with admin-specific features.
    """
    
    queryset = UniversalPayment.objects.select_related('user').order_by('-created_at')
    serializer_class = AdminPaymentDetailSerializer
    
    serializer_classes = {
        'list': AdminPaymentListSerializer,
        'create': AdminPaymentCreateSerializer,
        'update': AdminPaymentUpdateSerializer,
        'partial_update': AdminPaymentUpdateSerializer,
        'stats': AdminPaymentStatsSerializer,
    }
    
    filterset_fields = ['status', 'provider', 'currency__code', 'user']
    search_fields = ['internal_payment_id', 'transaction_hash', 'description', 'user__username', 'user__email']
    ordering_fields = ['created_at', 'amount_usd', 'status']
    
    def get_queryset(self):
        """Optimized queryset for admin interface."""
        queryset = super().get_queryset()
        
        # Add filters based on query params
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        provider_filter = self.request.query_params.get('provider')
        if provider_filter:
            queryset = queryset.filter(provider=provider_filter)
        
        # Date range filter
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        if date_from:
            queryset = queryset.filter(created_at__gte=date_from)
        if date_to:
            queryset = queryset.filter(created_at__lte=date_to)
        
        return queryset
    
    def create(self, request, *args, **kwargs):
        """Create payment with enhanced error handling."""
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            try:
                payment = serializer.save()
                response_serializer = AdminPaymentDetailSerializer(payment, context={'request': request})
                return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            except serializers.ValidationError as e:
                # Extract the error message from ValidationError
                error_message = str(e)
                if hasattr(e, 'detail') and isinstance(e.detail, list) and len(e.detail) > 0:
                    error_message = str(e.detail[0])
                elif hasattr(e, 'detail') and isinstance(e.detail, dict):
                    # Handle field-specific errors
                    error_message = '; '.join([f"{field}: {', '.join(errors) if isinstance(errors, list) else errors}" 
                                             for field, errors in e.detail.items()])
                
                return Response(
                    {
                        'success': False,
                        'error': error_message,
                        'message': error_message  # Add message field for frontend compatibility
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            # Handle validation errors
            error_messages = []
            for field, errors in serializer.errors.items():
                if isinstance(errors, list):
                    error_messages.extend([str(error) for error in errors])
                else:
                    error_messages.append(str(errors))
            
            error_message = '; '.join(error_messages)
            return Response(
                {
                    'success': False,
                    'error': error_message,
                    'message': error_message,  # Add message field for frontend compatibility
                    'errors': serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get comprehensive payment statistics."""
        queryset = self.get_queryset()
        
        # Basic stats
        total_payments = queryset.count()
        total_amount = queryset.aggregate(Sum('amount_usd'))['amount_usd__sum'] or 0
        
        # Status breakdown
        status_stats = queryset.values('status').annotate(count=Count('id'))
        successful = sum(s['count'] for s in status_stats if s['status'] in ['completed', 'confirmed'])
        failed = sum(s['count'] for s in status_stats if s['status'] == 'failed')
        pending = sum(s['count'] for s in status_stats if s['status'] in ['pending', 'confirming'])
        
        success_rate = (successful / total_payments * 100) if total_payments > 0 else 0
        
        # Provider breakdown
        provider_stats = {}
        for provider_data in queryset.values('provider').annotate(
            count=Count('id'),
            total_amount=Sum('amount_usd')
        ):
            provider_stats[provider_data['provider']] = {
                'count': provider_data['count'],
                'total_amount': provider_data['total_amount'] or 0,
            }
        
        # Currency breakdown
        currency_stats = {}
        for currency_data in queryset.values('currency_code').annotate(
            count=Count('id'),
            total_amount=Sum('amount_usd')
        ):
            currency_stats[currency_data['currency_code']] = {
                'count': currency_data['count'],
                'total_amount': currency_data['total_amount'] or 0,
            }
        
        # Time-based stats
        now = timezone.now()
        last_24h = queryset.filter(created_at__gte=now - timedelta(hours=24)).aggregate(
            count=Count('id'),
            amount=Sum('amount_usd')
        )
        last_7d = queryset.filter(created_at__gte=now - timedelta(days=7)).aggregate(
            count=Count('id'),
            amount=Sum('amount_usd')
        )
        last_30d = queryset.filter(created_at__gte=now - timedelta(days=30)).aggregate(
            count=Count('id'),
            amount=Sum('amount_usd')
        )
        
        stats_data = {
            'total_payments': total_payments,
            'total_amount_usd': total_amount,
            'successful_payments': successful,
            'failed_payments': failed,
            'pending_payments': pending,
            'success_rate': round(success_rate, 2),
            'by_provider': provider_stats,
            'by_currency': currency_stats,
            'last_24h': {
                'count': last_24h['count'] or 0,
                'amount': last_24h['amount'] or 0,
            },
            'last_7d': {
                'count': last_7d['count'] or 0,
                'amount': last_7d['amount'] or 0,
            },
            'last_30d': {
                'count': last_30d['count'] or 0,
                'amount': last_30d['amount'] or 0,
            },
        }
        
        serializer = self.get_serializer(stats_data)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel a payment."""
        payment = self.get_object()
        
        if payment.status not in ['pending', 'confirming']:
            return Response(
                {'error': 'Payment cannot be cancelled in current status'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        payment.status = UniversalPayment.PaymentStatus.CANCELLED
        payment.save()
        
        logger.info(f"Payment {payment.id} cancelled by admin {request.user.id}")
        
        serializer = self.get_serializer(payment)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def refund(self, request, pk=None):
        """Refund a payment."""
        payment = self.get_object()
        
        if payment.status != 'completed':
            return Response(
                {'error': 'Only completed payments can be refunded'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        payment.status = UniversalPayment.PaymentStatus.REFUNDED
        payment.save()
        
        logger.info(f"Payment {payment.id} refunded by admin {request.user.id}")
        
        serializer = self.get_serializer(payment)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def refresh_status(self, request, pk=None):
        """Refresh payment status from provider via AJAX."""
        payment = self.get_object()
        
        try:
            # Import here to avoid circular imports
            from django_cfg.apps.payments.services.core.payment_service import PaymentService
            
            # Create PaymentStatusRequest
            from django_cfg.apps.payments.services.types import PaymentStatusRequest
            
            status_request = PaymentStatusRequest(
                payment_id=str(payment.id),
                force_provider_check=True
            )
            
            # Create service instance and force refresh from provider
            payment_service = PaymentService()
            result = payment_service.get_payment_status(status_request)
            
            if result.success:
                # Reload payment from database to get updated data
                payment.refresh_from_db()
                
                # Serialize updated payment data
                serializer = self.get_serializer(payment)
                
                return Response({
                    'success': True,
                    'message': 'Payment status refreshed successfully',
                    'payment': serializer.data,
                    'provider_response': result.data.get('provider_response') if result.data else None
                })
            else:
                return Response({
                    'success': False,
                    'message': result.message or 'Failed to refresh payment status',
                    'error_details': result.data if result.data else None
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            logger.error(f"Error refreshing payment {payment.id} status", extra={
                'payment_id': payment.id,
                'error': str(e),
                'admin_user': request.user.id
            })
            
            return Response({
                'success': False,
                'message': f'Error refreshing payment status: {str(e)}',
                'error_type': type(e).__name__
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
