"""
💰 Payments Overview Dashboard Serializers

DRF serializers for payments dashboard data with drf-spectacular integration.
"""
from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from typing import Dict, Any


class BalanceOverviewSerializer(serializers.Serializer):
    """
    User balance overview metrics
    """
    current_balance = serializers.FloatField(help_text="Current balance in USD")
    balance_display = serializers.CharField(help_text="Formatted balance display")
    total_deposited = serializers.FloatField(help_text="Total amount deposited (lifetime)")
    total_spent = serializers.FloatField(help_text="Total amount spent (lifetime)")
    last_transaction_at = serializers.DateTimeField(allow_null=True, help_text="Last transaction timestamp")
    has_transactions = serializers.BooleanField(help_text="Whether user has any transactions")
    is_empty = serializers.BooleanField(help_text="Whether balance is zero")


class SubscriptionOverviewSerializer(serializers.Serializer):
    """
    Current subscription overview
    """
    tier = serializers.CharField(help_text="Subscription tier")
    tier_display = serializers.CharField(help_text="Human-readable tier name")
    status = serializers.CharField(help_text="Subscription status")
    status_display = serializers.CharField(help_text="Human-readable status")
    status_color = serializers.CharField(help_text="Color for status display")
    is_active = serializers.BooleanField(help_text="Whether subscription is active")
    is_expired = serializers.BooleanField(help_text="Whether subscription is expired")
    days_remaining = serializers.IntegerField(help_text="Days until expiration")
    
    # Limits and usage
    requests_per_hour = serializers.IntegerField(help_text="Hourly request limit")
    requests_per_day = serializers.IntegerField(help_text="Daily request limit")
    total_requests = serializers.IntegerField(help_text="Total requests made")
    usage_percentage = serializers.FloatField(help_text="Usage percentage for current period")
    
    # Billing
    monthly_cost_usd = serializers.FloatField(help_text="Monthly cost in USD")
    cost_display = serializers.CharField(help_text="Formatted cost display")
    
    # Dates
    starts_at = serializers.DateTimeField(help_text="Subscription start date")
    expires_at = serializers.DateTimeField(help_text="Subscription expiration date")
    last_request_at = serializers.DateTimeField(allow_null=True, help_text="Last API request timestamp")
    
    # Access
    endpoint_groups_count = serializers.IntegerField(help_text="Number of accessible endpoint groups")
    endpoint_groups = serializers.ListField(
        child=serializers.CharField(),
        help_text="List of accessible endpoint group names"
    )


class APIKeysOverviewSerializer(serializers.Serializer):
    """
    API keys overview metrics
    """
    total_keys = serializers.IntegerField(help_text="Total number of API keys")
    active_keys = serializers.IntegerField(help_text="Number of active API keys")
    expired_keys = serializers.IntegerField(help_text="Number of expired API keys")
    total_requests = serializers.IntegerField(help_text="Total requests across all keys")
    last_used_at = serializers.DateTimeField(allow_null=True, help_text="When any key was last used")
    
    # Recent keys info
    most_used_key_name = serializers.CharField(allow_null=True, help_text="Name of most used API key")
    most_used_key_requests = serializers.IntegerField(help_text="Requests count for most used key")
    
    # Expiring keys warning
    expiring_soon_count = serializers.IntegerField(help_text="Number of keys expiring within 7 days")


class PaymentOverviewSerializer(serializers.Serializer):
    """
    Payments overview metrics
    """
    total_payments = serializers.IntegerField(help_text="Total number of payments")
    completed_payments = serializers.IntegerField(help_text="Number of completed payments")
    pending_payments = serializers.IntegerField(help_text="Number of pending payments")
    failed_payments = serializers.IntegerField(help_text="Number of failed payments")
    
    # Amounts
    total_amount_usd = serializers.FloatField(help_text="Total payment amount in USD")
    completed_amount_usd = serializers.FloatField(help_text="Total completed amount in USD")
    average_payment_usd = serializers.FloatField(help_text="Average payment amount in USD")
    
    # Success rate
    success_rate = serializers.FloatField(help_text="Payment success rate percentage")
    
    # Recent activity
    last_payment_at = serializers.DateTimeField(allow_null=True, help_text="Last payment timestamp")
    payments_this_month = serializers.IntegerField(help_text="Number of payments this month")
    amount_this_month = serializers.FloatField(help_text="Total amount this month")
    
    # Popular currencies
    top_currency = serializers.CharField(allow_null=True, help_text="Most used currency")
    top_currency_count = serializers.IntegerField(help_text="Usage count for top currency")


class PaymentsMetricsSerializer(serializers.Serializer):
    """
    Complete payments dashboard metrics
    """
    balance = BalanceOverviewSerializer(help_text="Balance overview")
    subscription = SubscriptionOverviewSerializer(allow_null=True, help_text="Subscription overview")
    api_keys = APIKeysOverviewSerializer(help_text="API keys overview")
    payments = PaymentOverviewSerializer(help_text="Payments overview")


class RecentPaymentSerializer(serializers.Serializer):
    """
    Recent payment item
    """
    id = serializers.UUIDField(help_text="Payment ID")
    internal_payment_id = serializers.CharField(help_text="Internal payment ID")
    amount_usd = serializers.FloatField(help_text="Payment amount in USD")
    amount_display = serializers.CharField(help_text="Formatted amount display")
    currency_code = serializers.CharField(help_text="Currency code")
    status = serializers.CharField(help_text="Payment status")
    status_display = serializers.CharField(help_text="Human-readable status")
    status_color = serializers.CharField(help_text="Color for status display")
    provider = serializers.CharField(help_text="Payment provider")
    created_at = serializers.DateTimeField(help_text="Payment creation timestamp")
    completed_at = serializers.DateTimeField(allow_null=True, help_text="Payment completion timestamp")
    
    # Status flags
    is_pending = serializers.BooleanField(help_text="Whether payment is pending")
    is_completed = serializers.BooleanField(help_text="Whether payment is completed")
    is_failed = serializers.BooleanField(help_text="Whether payment failed")


class RecentTransactionSerializer(serializers.Serializer):
    """
    Recent transaction item
    """
    id = serializers.UUIDField(help_text="Transaction ID")
    transaction_type = serializers.CharField(help_text="Transaction type")
    amount_usd = serializers.FloatField(help_text="Transaction amount in USD")
    amount_display = serializers.CharField(help_text="Formatted amount display")
    balance_after = serializers.FloatField(help_text="Balance after transaction")
    description = serializers.CharField(help_text="Transaction description")
    created_at = serializers.DateTimeField(help_text="Transaction timestamp")
    payment_id = serializers.CharField(allow_null=True, help_text="Related payment ID")
    
    # Type info
    is_credit = serializers.BooleanField(help_text="Whether this is a credit transaction")
    is_debit = serializers.BooleanField(help_text="Whether this is a debit transaction")
    type_color = serializers.CharField(help_text="Color for transaction type display")


class ChartDataPointSerializer(serializers.Serializer):
    """
    Chart data point for payments analytics
    """
    x = serializers.CharField(help_text="X-axis value (date)")
    y = serializers.FloatField(help_text="Y-axis value (amount or count)")


class ChartSeriesSerializer(serializers.Serializer):
    """
    Chart series data for payments visualization
    """
    name = serializers.CharField(help_text="Series name")
    data = ChartDataPointSerializer(many=True, help_text="Data points")
    color = serializers.CharField(help_text="Series color")


class PaymentsChartResponseSerializer(serializers.Serializer):
    """
    Complete chart response for payments analytics
    """
    series = ChartSeriesSerializer(many=True, help_text="Chart series data")
    period = serializers.CharField(help_text="Time period")
    total_amount = serializers.FloatField(help_text="Total amount for period")
    total_payments = serializers.IntegerField(help_text="Total payments for period")
    success_rate = serializers.FloatField(help_text="Success rate for period")


class PaymentsDashboardOverviewSerializer(serializers.Serializer):
    """
    Complete payments dashboard overview response
    """
    metrics = PaymentsMetricsSerializer(help_text="Dashboard metrics")
    recent_payments = RecentPaymentSerializer(many=True, help_text="Recent payments")
    recent_transactions = RecentTransactionSerializer(many=True, help_text="Recent transactions")
    chart_data = PaymentsChartResponseSerializer(help_text="Chart data for analytics")


class TimePeriodSerializer(serializers.Serializer):
    """
    Time period filter for charts and analytics
    """
    PERIOD_CHOICES = [
        ('7d', 'Last 7 days'),
        ('30d', 'Last 30 days'),
        ('90d', 'Last 90 days'),
        ('1y', 'Last year'),
    ]
    
    period = serializers.ChoiceField(choices=PERIOD_CHOICES, default='30d')
