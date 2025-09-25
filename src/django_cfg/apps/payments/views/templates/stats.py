"""
Payment statistics and analytics views.

Provides comprehensive analytics for payment performance and trends.
"""

from django.views.generic import TemplateView
from django.utils import timezone
from django.db.models import Q
from datetime import timedelta
from .base import (
    SuperuserRequiredMixin,
    PaymentStatsMixin,
    PaymentContextMixin,
    log_view_access
)


class PaymentStatsView(
    SuperuserRequiredMixin,
    PaymentStatsMixin,
    PaymentContextMixin,
    TemplateView
):
    """Analytics and statistics view."""
    
    template_name = 'payments/stats.html'
    page_title = 'Payment Analytics'
    
    def get_breadcrumbs(self):
        return [
            {'name': 'Dashboard', 'url': '/payments/admin/'},
            {'name': 'Analytics', 'url': ''},
        ]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Log access for audit
        log_view_access('payment_stats', self.request.user)
        
        # Get time period from request (default to 30 days)
        days = int(self.request.GET.get('days', 30))
        
        # Calculate date ranges
        now = timezone.now()
        ranges = self._get_date_ranges(now, days)
        
        # Get comprehensive statistics
        stats = {
            'overview': self._get_overview_stats(),
            'time_periods': self._get_time_period_stats(ranges),
            'providers': self._get_detailed_provider_stats(),
            'status_distribution': self._get_status_distribution(),
            'trends': self._get_trend_data(days),
            'performance': self._get_performance_metrics(),
        }
        
        # Get common context
        common_context = self.get_common_context()
        
        context.update({
            'stats': stats,
            'selected_days': days,
            'available_periods': [7, 30, 90, 365],
            'date_ranges': ranges,
            **common_context
        })
        
        return context
    
    def _get_date_ranges(self, now, days):
        """Calculate various date ranges for statistics."""
        return {
            'current_period_start': now - timedelta(days=days),
            'current_period_end': now,
            'previous_period_start': now - timedelta(days=days * 2),
            'previous_period_end': now - timedelta(days=days),
            'last_7_days': now - timedelta(days=7),
            'last_30_days': now - timedelta(days=30),
            'last_year': now - timedelta(days=365),
        }
    
    def _get_overview_stats(self):
        """Get overall payment statistics."""
        return self.get_payment_stats()
    
    def _get_time_period_stats(self, ranges):
        """Get statistics for different time periods."""
        from ...models import UniversalPayment
        
        periods = {}
        
        # Current period
        current_qs = UniversalPayment.objects.filter(
            created_at__gte=ranges['current_period_start'],
            created_at__lte=ranges['current_period_end']
        )
        periods['current'] = self.get_payment_stats(current_qs)
        
        # Previous period for comparison
        previous_qs = UniversalPayment.objects.filter(
            created_at__gte=ranges['previous_period_start'],
            created_at__lte=ranges['previous_period_end']
        )
        periods['previous'] = self.get_payment_stats(previous_qs)
        
        # Calculate growth rates
        periods['growth'] = self._calculate_growth_rates(
            periods['current'], 
            periods['previous']
        )
        
        # Last 7 days
        last_7_qs = UniversalPayment.objects.filter(created_at__gte=ranges['last_7_days'])
        periods['last_7_days'] = self.get_payment_stats(last_7_qs)
        
        # Last 30 days
        last_30_qs = UniversalPayment.objects.filter(created_at__gte=ranges['last_30_days'])
        periods['last_30_days'] = self.get_payment_stats(last_30_qs)
        
        return periods
    
    def _get_detailed_provider_stats(self):
        """Get detailed provider statistics."""
        provider_stats = self.get_provider_stats()
        
        # Add additional metrics for each provider
        for stat in provider_stats:
            stat['avg_amount'] = stat['volume'] / stat['count'] if stat['count'] > 0 else 0
            stat['failure_rate'] = 100 - stat['success_rate']
            
        return provider_stats
    
    def _get_status_distribution(self):
        """Get payment status distribution."""
        from ...models import UniversalPayment
        from django.db.models import Count
        
        distribution = UniversalPayment.objects.values('status').annotate(
            count=Count('id')
        ).order_by('-count')
        
        total = sum(item['count'] for item in distribution)
        
        # Add percentage
        for item in distribution:
            item['percentage'] = (item['count'] / total * 100) if total > 0 else 0
        
        return distribution
    
    def _get_trend_data(self, days):
        """Get trend data for charts."""
        from ...models import UniversalPayment
        from django.db.models import Count, Sum
        from django.db.models.functions import TruncDate
        
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        # Daily trends
        daily_trends = UniversalPayment.objects.filter(
            created_at__gte=start_date,
            created_at__lte=end_date
        ).annotate(
            date=TruncDate('created_at')
        ).values('date').annotate(
            count=Count('id'),
            volume=Sum('amount_usd'),
            completed=Count('id', filter=Q(status='completed'))
        ).order_by('date')
        
        # Convert to list and add calculated fields
        trends = []
        for item in daily_trends:
            trends.append({
                'date': item['date'].isoformat(),
                'count': item['count'],
                'volume': float(item['volume'] or 0),
                'completed': item['completed'],
                'success_rate': (item['completed'] / item['count'] * 100) if item['count'] > 0 else 0
            })
        
        return trends
    
    def _get_performance_metrics(self):
        """Get performance metrics."""
        from ...models import UniversalPayment, PaymentEvent
        from django.db.models import Avg, Min, Max
        
        # Average processing time (from created to completed)
        completed_payments = UniversalPayment.objects.filter(
            status='completed',
            completed_at__isnull=False
        )
        
        processing_times = []
        for payment in completed_payments[:100]:  # Sample for performance
            if payment.completed_at and payment.created_at:
                duration = payment.completed_at - payment.created_at
                processing_times.append(duration.total_seconds())
        
        metrics = {
            'avg_processing_time': sum(processing_times) / len(processing_times) if processing_times else 0,
            'min_processing_time': min(processing_times) if processing_times else 0,
            'max_processing_time': max(processing_times) if processing_times else 0,
        }
        
        # Convert seconds to human readable format
        formatted_metrics = {}
        for key, value in metrics.items():
            if value > 0:
                formatted_metrics[f"{key}_formatted"] = self._format_duration(value)
            else:
                formatted_metrics[f"{key}_formatted"] = "N/A"
        
        # Add formatted metrics to the original metrics
        metrics.update(formatted_metrics)
        
        return metrics
    
    def _calculate_growth_rates(self, current, previous):
        """Calculate growth rates between two periods."""
        growth = {}
        
        for key in ['total_count', 'total_volume', 'completed_count']:
            current_val = current.get(key, 0)
            previous_val = previous.get(key, 0)
            
            if previous_val > 0:
                growth[f"{key}_rate"] = ((current_val - previous_val) / previous_val) * 100
            else:
                growth[f"{key}_rate"] = 100 if current_val > 0 else 0
        
        return growth
    
    def _format_duration(self, seconds):
        """Format duration in seconds to human readable format."""
        if seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            return f"{seconds/60:.1f}m"
        else:
            return f"{seconds/3600:.1f}h"
