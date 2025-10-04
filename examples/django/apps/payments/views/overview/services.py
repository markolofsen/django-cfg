"""
💰 Payments Overview Dashboard Services

Services for aggregating payments dashboard data from existing models.
"""
from django.db.models import Count, Sum, Avg, Q, Max
from django.utils import timezone
from datetime import timedelta, date
from decimal import Decimal
from typing import Dict, List, Any, Optional

from ...models import (
    UniversalPayment,
    UserBalance,
    Transaction,
    Subscription,
    EndpointGroup,
    APIKey,
)


class PaymentsDashboardMetricsService:
    """
    Service for calculating payments dashboard metrics
    """
    
    def __init__(self, user):
        self.user = user
        self.now = timezone.now()
        self.today = self.now.date()
        self.month_start = self.today.replace(day=1)
        self.last_month_start = (self.month_start - timedelta(days=1)).replace(day=1)
        self.last_month_end = self.month_start - timedelta(days=1)
    
    def get_dashboard_metrics(self) -> Dict[str, Any]:
        """
        Get complete payments dashboard metrics
        """
        return {
            'balance': self.get_balance_overview(),
            'subscription': self.get_subscription_overview(),
            'api_keys': self.get_api_keys_overview(),
            'payments': self.get_payments_overview(),
        }
    
    def get_balance_overview(self) -> Dict[str, Any]:
        """
        Get user balance overview using manager methods
        """
        balance = UserBalance.objects.get_or_create_for_user(self.user)
        
        return {
            'current_balance': balance.balance_usd,
            'balance_display': balance.balance_display,
            'total_deposited': balance.total_deposited,
            'total_spent': balance.total_spent,
            'last_transaction_at': balance.last_transaction_at,
            'has_transactions': balance.has_transactions,
            'is_empty': balance.is_empty,
        }
    
    def get_subscription_overview(self) -> Optional[Dict[str, Any]]:
        """
        Get current subscription overview using manager methods
        """
        subscription = Subscription.objects.get_active_for_user(self.user)
        
        if not subscription:
            return None
        
        # Get endpoint groups info
        endpoint_groups = subscription.endpoint_groups.filter(is_enabled=True)
        endpoint_groups_names = list(endpoint_groups.values_list('name', flat=True))
        
        return {
            'tier': subscription.tier,
            'tier_display': subscription.tier_display,
            'status': subscription.status,
            'status_display': subscription.get_status_display(),
            'status_color': subscription.status_color,
            'is_active': subscription.is_active,
            'is_expired': subscription.is_expired,
            'days_remaining': subscription.days_remaining,
            
            # Limits and usage
            'requests_per_hour': subscription.requests_per_hour,
            'requests_per_day': subscription.requests_per_day,
            'total_requests': subscription.total_requests,
            'usage_percentage': subscription.usage_percentage,
            
            # Billing
            'monthly_cost_usd': subscription.monthly_cost_usd,
            'cost_display': f"${subscription.monthly_cost_usd:.2f}/month",
            
            # Dates
            'starts_at': subscription.starts_at,
            'expires_at': subscription.expires_at,
            'last_request_at': subscription.last_request_at,
            
            # Access
            'endpoint_groups_count': endpoint_groups.count(),
            'endpoint_groups': endpoint_groups_names,
        }
    
    def get_api_keys_overview(self) -> Dict[str, Any]:
        """
        Get API keys overview using manager methods
        """
        api_keys = APIKey.objects.by_user(self.user)
        
        total_keys = api_keys.count()
        active_keys = api_keys.active().count()
        expired_keys = api_keys.expired().count()
        
        # Total requests across all keys
        total_requests = api_keys.aggregate(
            total=Sum('total_requests')
        )['total'] or 0
        
        # Last used timestamp
        last_used_at = api_keys.aggregate(
            last_used=Max('last_used_at')
        )['last_used']
        
        # Most used key
        most_used_key = api_keys.order_by('-total_requests').first()
        most_used_key_name = most_used_key.name if most_used_key else None
        most_used_key_requests = most_used_key.total_requests if most_used_key else 0
        
        # Keys expiring soon (within 7 days)
        expiring_soon = api_keys.expiring_soon(7).count()
        
        return {
            'total_keys': total_keys,
            'active_keys': active_keys,
            'expired_keys': expired_keys,
            'total_requests': total_requests,
            'last_used_at': last_used_at,
            'most_used_key_name': most_used_key_name,
            'most_used_key_requests': most_used_key_requests,
            'expiring_soon_count': expiring_soon,
        }
    
    def get_payments_overview(self) -> Dict[str, Any]:
        """
        Get payments overview using manager methods
        """
        payments = UniversalPayment.objects.by_user(self.user)
        
        # Basic counts using manager methods
        total_payments = payments.count()
        completed_payments = payments.completed().count()
        pending_payments = payments.pending().count()
        failed_payments = payments.failed().count()
        
        # Amount calculations
        total_amount_usd = payments.total_amount()
        completed_amount_usd = payments.completed().total_amount()
        average_payment_usd = payments.average_amount()
        
        # Success rate
        success_rate = (completed_payments / total_payments * 100) if total_payments > 0 else 0.0
        
        # Recent activity
        last_payment = payments.order_by('-created_at').first()
        last_payment_at = last_payment.created_at if last_payment else None
        
        # This month stats using manager methods
        payments_this_month = payments.this_month().count()
        amount_this_month = payments.this_month().total_amount()
        
        # Top currency
        top_currency_data = payments.values('currency__code').annotate(
            count=Count('id')
        ).order_by('-count').first()
        
        top_currency = top_currency_data['currency__code'] if top_currency_data else None
        top_currency_count = top_currency_data['count'] if top_currency_data else 0
        
        return {
            'total_payments': total_payments,
            'completed_payments': completed_payments,
            'pending_payments': pending_payments,
            'failed_payments': failed_payments,
            
            'total_amount_usd': total_amount_usd,
            'completed_amount_usd': completed_amount_usd,
            'average_payment_usd': average_payment_usd,
            
            'success_rate': round(success_rate, 2),
            
            'last_payment_at': last_payment_at,
            'payments_this_month': payments_this_month,
            'amount_this_month': amount_this_month,
            
            'top_currency': top_currency,
            'top_currency_count': top_currency_count,
        }


class PaymentsUsageChartService:
    """
    Service for generating payments usage chart data
    """
    
    def __init__(self, user):
        self.user = user
    
    def get_chart_data(self, period: str = '30d') -> Dict[str, Any]:
        """
        Get chart data for payments analytics
        """
        days_map = {
            '7d': 7,
            '30d': 30,
            '90d': 90,
            '1y': 365
        }
        
        days = days_map.get(period, 30)
        start_date = timezone.now().date() - timedelta(days=days)
        
        # Get payments for the period using manager methods
        payments = UniversalPayment.objects.by_user(self.user).filter(
            created_at__date__gte=start_date
        ).values('created_at__date').annotate(
            total_amount=Sum('amount_usd'),
            completed_amount=Sum(
                'actual_amount_usd',
                filter=Q(status=UniversalPayment.PaymentStatus.COMPLETED)
            ),
            payment_count=Count('id'),
            completed_count=Count(
                'id',
                filter=Q(status=UniversalPayment.PaymentStatus.COMPLETED)
            ),
            failed_count=Count(
                'id',
                filter=Q(status__in=[
                    UniversalPayment.PaymentStatus.FAILED,
                    UniversalPayment.PaymentStatus.EXPIRED,
                    UniversalPayment.PaymentStatus.CANCELLED
                ])
            )
        ).order_by('created_at__date')
        
        # Generate chart series data
        amounts_data = []
        completed_data = []
        failed_data = []
        
        # Create data points for each day
        for i in range(days):
            current_date = start_date + timedelta(days=i)
            date_str = current_date.strftime('%Y-%m-%d')
            
            # Find payments for this date
            day_data = next(
                (p for p in payments if p['created_at__date'] == current_date),
                None
            )
            
            total_amount = day_data['total_amount'] if day_data and day_data['total_amount'] is not None else 0.0
            completed_amount = day_data['completed_amount'] if day_data and day_data['completed_amount'] is not None else 0.0
            failed_count = day_data['failed_count'] if day_data else 0
            
            amounts_data.append({'x': date_str, 'y': total_amount})
            completed_data.append({'x': date_str, 'y': completed_amount})
            failed_data.append({'x': date_str, 'y': failed_count})
        
        # Calculate totals
        total_amount = sum(p['y'] for p in amounts_data)
        total_payments = sum(1 for p in amounts_data if p['y'] > 0)
        completed_amount = sum(p['y'] for p in completed_data)
        success_rate = (completed_amount / total_amount * 100) if total_amount > 0 else 0.0
        
        return {
            'series': [
                {
                    'name': 'Total Amount',
                    'data': amounts_data,
                    'color': '#3B82F6'
                },
                {
                    'name': 'Completed Amount',
                    'data': completed_data,
                    'color': '#10B981'
                },
                {
                    'name': 'Failed Payments',
                    'data': failed_data,
                    'color': '#EF4444'
                }
            ],
            'period': period,
            'total_amount': total_amount,
            'total_payments': total_payments,
            'success_rate': round(success_rate, 2)
        }


class RecentPaymentsService:
    """
    Service for getting recent payments and transactions
    """
    
    def __init__(self, user):
        self.user = user
    
    def get_recent_payments(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent payments for the user using manager methods
        """
        payments = UniversalPayment.objects.by_user(self.user).optimized().order_by('-created_at')[:limit]
        
        result = []
        for payment in payments:
            result.append({
                'id': payment.id,
                'internal_payment_id': payment.internal_payment_id,
                'amount_usd': payment.amount_usd,
                'amount_display': payment.amount_display,
                'currency_code': payment.currency.code,
                'status': payment.status,
                'status_display': payment.get_status_display(),
                'status_color': payment.status_color,
                'provider': payment.provider,
                'created_at': payment.created_at,
                'completed_at': payment.completed_at,
                
                # Status flags
                'is_pending': payment.is_pending,
                'is_completed': payment.is_completed,
                'is_failed': payment.is_failed,
            })
        
        return result
    
    def get_recent_transactions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent transactions for the user using manager methods
        """
        transactions = Transaction.objects.by_user(self.user).optimized().order_by('-created_at')[:limit]
        
        result = []
        for transaction in transactions:
            result.append({
                'id': transaction.id,
                'transaction_type': transaction.transaction_type,
                'amount_usd': transaction.amount_usd,
                'amount_display': transaction.amount_display,
                'balance_after': transaction.balance_after,
                'description': transaction.description,
                'created_at': transaction.created_at,
                'payment_id': transaction.payment_id,
                
                # Type info
                'is_credit': transaction.is_credit,
                'is_debit': transaction.is_debit,
                'type_color': transaction.type_color,
            })
        
        return result


class PaymentsAnalyticsService:
    """
    Service for payments analytics and insights
    """
    
    def __init__(self, user):
        self.user = user
    
    def get_payment_analytics(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get payment analytics by currency, provider, etc.
        """
        # Analytics by currency using manager methods
        currency_stats = UniversalPayment.objects.by_user(self.user).values(
            'currency__code', 'currency__name'
        ).annotate(
            total_payments=Count('id'),
            total_amount=Sum('amount_usd'),
            completed_payments=Count(
                'id',
                filter=Q(status=UniversalPayment.PaymentStatus.COMPLETED)
            ),
            avg_amount=Avg('amount_usd'),
            success_rate=Count(
                'id',
                filter=Q(status=UniversalPayment.PaymentStatus.COMPLETED)
            ) * 100.0 / Count('id')
        ).order_by('-total_amount')[:limit]
        
        result = []
        for stat in currency_stats:
            result.append({
                'currency_code': stat['currency__code'],
                'currency_name': stat['currency__name'],
                'total_payments': stat['total_payments'],
                'total_amount': stat['total_amount'] or 0.0,
                'completed_payments': stat['completed_payments'],
                'average_amount': stat['avg_amount'] or 0.0,
                'success_rate': round(stat['success_rate'] or 0.0, 2),
            })
        
        return result
    
    def get_provider_analytics(self) -> List[Dict[str, Any]]:
        """
        Get analytics by payment provider
        """
        provider_stats = UniversalPayment.objects.by_user(self.user).values('provider').annotate(
            total_payments=Count('id'),
            total_amount=Sum('amount_usd'),
            completed_payments=Count(
                'id',
                filter=Q(status=UniversalPayment.PaymentStatus.COMPLETED)
            ),
            success_rate=Count(
                'id',
                filter=Q(status=UniversalPayment.PaymentStatus.COMPLETED)
            ) * 100.0 / Count('id')
        ).order_by('-total_payments')
        
        result = []
        for stat in provider_stats:
            result.append({
                'provider': stat['provider'],
                'provider_display': dict(UniversalPayment.PaymentProvider.choices).get(
                    stat['provider'], stat['provider']
                ),
                'total_payments': stat['total_payments'],
                'total_amount': stat['total_amount'] or 0.0,
                'completed_payments': stat['completed_payments'],
                'success_rate': round(stat['success_rate'] or 0.0, 2),
            })
        
        return result
