"""
Base mixins and decorators for payment template views.

Provides security and common functionality for all payment dashboard views.
"""

from django.contrib.auth.decorators import user_passes_test
from django.utils.decorators import method_decorator
from django.db.models import Q, Count, Sum
from django.utils import timezone
from datetime import timedelta
from django_cfg.modules.django_logger import get_logger

logger = get_logger("view_base")


def superuser_required(function=None):
    """Decorator that checks if user is superuser."""
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated and u.is_superuser,
        login_url='/admin/login/'
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


class SuperuserRequiredMixin:
    """Mixin that requires superuser access for all views."""
    
    @method_decorator(superuser_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class PaymentFilterMixin:
    """Mixin that provides common payment filtering functionality."""
    
    def get_filtered_payments(self, request=None):
        """Get payments with common filters applied."""
        if request is None:
            request = self.request
            
        from ...models import UniversalPayment
        
        # Base queryset
        payments_qs = UniversalPayment.objects.select_related('user')
        
        # Apply filters from GET parameters
        status_filter = request.GET.get('status', '')
        provider_filter = request.GET.get('provider', '')
        search_query = request.GET.get('search', '')
        date_filter = request.GET.get('date', '')
        
        if status_filter:
            payments_qs = payments_qs.filter(status=status_filter)
        if provider_filter:
            payments_qs = payments_qs.filter(provider=provider_filter)
        if search_query:
            payments_qs = payments_qs.filter(
                Q(internal_payment_id__icontains=search_query) |
                Q(provider_payment_id__icontains=search_query) |
                Q(amount_usd__icontains=search_query) |
                Q(user__email__icontains=search_query)
            )
        if date_filter:
            try:
                filter_date = timezone.datetime.strptime(date_filter, '%Y-%m-%d').date()
                payments_qs = payments_qs.filter(created_at__date=filter_date)
            except ValueError:
                pass  # Invalid date format, ignore filter
        
        return payments_qs
    
    def get_filter_context(self, request=None):
        """Get filter values for template context."""
        if request is None:
            request = self.request
            
        return {
            'status': request.GET.get('status', ''),
            'provider': request.GET.get('provider', ''),
            'search': request.GET.get('search', ''),
            'date': request.GET.get('date', ''),
        }


class PaymentStatsMixin:
    """Mixin that provides payment statistics functionality."""
    
    def get_payment_stats(self, queryset=None):
        """Get payment statistics from queryset or all payments."""
        if queryset is None:
            from ...models import UniversalPayment
            queryset = UniversalPayment.objects.all()
        
        stats = queryset.aggregate(
            total_count=Count('id'),
            pending_count=Count('id', filter=Q(status='pending')),
            confirming_count=Count('id', filter=Q(status='confirming')),
            completed_count=Count('id', filter=Q(status='completed')),
            failed_count=Count('id', filter=Q(status='failed')),
            total_volume=Sum('amount_usd')
        )
        
        # Convert to template format
        return {
            'total_payments_count': stats['total_count'] or 0,
            'pending_payments_count': stats['pending_count'] or 0,
            'confirming_payments_count': stats['confirming_count'] or 0,
            'completed_payments_count': stats['completed_count'] or 0,
            'failed_payments_count': stats['failed_count'] or 0,
            'total_volume': float(stats['total_volume'] or 0),
        }
    
    def get_provider_stats(self, queryset=None):
        """Get provider-specific statistics."""
        if queryset is None:
            from ...models import UniversalPayment
            queryset = UniversalPayment.objects.all()
        
        provider_stats = queryset.values('provider').annotate(
            count=Count('id'),
            volume=Sum('amount_usd'),
            completed_count=Count('id', filter=Q(status='completed')),
        ).order_by('-volume')
        
        # Calculate success rate and convert to list of dicts
        stats_list = []
        for stat in provider_stats:
            if stat['count'] > 0:
                stat['success_rate'] = (stat['completed_count'] / stat['count']) * 100
            else:
                stat['success_rate'] = 0
            
            # Convert Decimal to float
            if stat['volume']:
                stat['volume'] = float(stat['volume'])
            else:
                stat['volume'] = 0.0
                
            stats_list.append(stat)
        
        return stats_list
    
    def get_time_range_stats(self, days=30):
        """Get statistics for a specific time range."""
        from ...models import UniversalPayment
        
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        queryset = UniversalPayment.objects.filter(
            created_at__gte=start_date,
            created_at__lte=end_date
        )
        
        return self.get_payment_stats(queryset)


class PaymentContextMixin:
    """Mixin that provides common context data for payment views."""
    
    def get_common_context(self):
        """Get common context data used across multiple views."""
        from ...models import PaymentEvent
        
        # Get recent events for activity feed (if any exist)
        try:
            recent_events = PaymentEvent.objects.order_by('-created_at')[:10]
        except Exception:
            recent_events = []
        
        return {
            'recent_events': recent_events,
            'page_title': self.get_page_title(),
            'breadcrumbs': self.get_breadcrumbs(),
        }
    
    def get_page_title(self):
        """Get page title for the view."""
        return getattr(self, 'page_title', 'Payment Dashboard')
    
    def get_breadcrumbs(self):
        """Get breadcrumb navigation for the view."""
        return getattr(self, 'breadcrumbs', [
            {'name': 'Payment Dashboard', 'url': '/payments/admin/'},
        ])


def get_progress_percentage(status):
    """Helper function to calculate progress percentage."""
    progress_map = {
        'pending': 10,
        'confirming': 40,
        'confirmed': 70,
        'completed': 100,
        'failed': 0,
        'expired': 0,
        'cancelled': 0,
        'refunded': 50,
    }
    return progress_map.get(status, 0)


def log_view_access(view_name, user, **kwargs):
    """Log access to payment views for audit purposes."""
    extra_info = ', '.join([f"{k}={v}" for k, v in kwargs.items()])
    logger.info(
        f"Payment dashboard access: {view_name} by {user.email} "
        f"(superuser={user.is_superuser}) {extra_info}"
    )
