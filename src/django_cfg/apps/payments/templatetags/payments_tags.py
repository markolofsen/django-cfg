"""
Payment Template Tags

Custom template tags for payment functionality, status badges, progress bars,
and real-time payment tracking components.
"""

from django import template
from django.utils.safestring import mark_safe
from django.utils.html import format_html
from django.db.models import Count, Sum, Q
from decimal import Decimal
import json

register = template.Library()


@register.simple_tag
def payment_status_badge(payment):
    """Render payment status badge with icon and color."""
    status_config = {
        'pending': {'color': 'yellow', 'icon': 'pending', 'animate': True},
        'confirming': {'color': 'blue', 'icon': 'sync', 'animate': True},
        'confirmed': {'color': 'green', 'icon': 'check_circle', 'animate': False},
        'completed': {'color': 'green', 'icon': 'verified', 'animate': False},
        'failed': {'color': 'red', 'icon': 'error', 'animate': False},
        'expired': {'color': 'gray', 'icon': 'schedule', 'animate': False},
        'cancelled': {'color': 'gray', 'icon': 'cancel', 'animate': False},
        'refunded': {'color': 'purple', 'icon': 'undo', 'animate': False},
    }
    
    config = status_config.get(payment.status, {'color': 'gray', 'icon': 'help', 'animate': False})
    animate_class = 'animate-pulse' if config['animate'] else ''
    
    return format_html(
        '<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-{}-100 text-{}-800 dark:bg-{}-900 dark:text-{}-200">'
        '<span class="material-icons text-sm mr-1 {}">{}</span>'
        '<span class="status-text">{}</span>'
        '</span>',
        config['color'], config['color'], config['color'], config['color'],
        animate_class,
        config['icon'],
        payment.get_status_display()
    )


@register.filter
def payment_progress_percentage(payment):
    """Calculate payment progress percentage."""
    progress_map = {
        'pending': 10,
        'confirming': 40,
        'confirmed': 70,
        'completed': 100,
        'failed': 0,
        'expired': 0,
        'cancelled': 0,
        'refunded': 50,  # Partial progress for refunds
    }
    return progress_map.get(payment.status, 0)


@register.filter
def payment_progress_steps(payment):
    """Get payment progress steps with status."""
    steps = [
        {'label': 'Created', 'key': 'created'},
        {'label': 'Processing', 'key': 'processing'},
        {'label': 'Confirming', 'key': 'confirming'},
        {'label': 'Completed', 'key': 'completed'},
    ]
    
    status_order = ['pending', 'confirming', 'confirmed', 'completed']
    current_index = status_order.index(payment.status) if payment.status in status_order else -1
    
    for i, step in enumerate(steps):
        step['completed'] = i < current_index
        step['active'] = i == current_index
    
    return steps


@register.inclusion_tag('payments/components/payment_card.html')
def payment_card(payment, show_actions=True, compact=False):
    """Render payment card component."""
    return {
        'payment': payment,
        'show_actions': show_actions,
        'compact': compact
    }


@register.inclusion_tag('payments/components/status_badge.html')
def render_payment_status(payment):
    """Render payment status badge component."""
    return {'payment': payment}


@register.inclusion_tag('payments/components/progress_bar.html')
def payment_progress_bar(payment):
    """Render payment progress bar component."""
    return {
        'payment': payment,
        'percentage': payment_progress_percentage(payment),
        'steps': payment_progress_steps(payment)
    }


@register.inclusion_tag('payments/components/payment_tracker.html', takes_context=True)
def payment_tracker(context, payment_id):
    """Render real-time payment tracker."""
    try:
        from ..models import UniversalPayment
        payment = UniversalPayment.objects.get(id=payment_id)
        return {
            'payment': payment,
            'request': context.get('request'),
            'user': context.get('user'),
            'websocket_url': f"/ws/payments/{payment_id}/"
        }
    except UniversalPayment.DoesNotExist:
        return {'payment': None}


@register.simple_tag
def payment_websocket_url(payment_id):
    """Get WebSocket URL for real-time payment updates."""
    return f"/ws/payments/{payment_id}/"


@register.filter
def format_crypto_amount(amount, currency_code):
    """Format cryptocurrency amount with proper decimals."""
    if not amount:
        return "0"
    
    # Different currencies have different decimal places
    decimal_places = {
        'BTC': 8,
        'ETH': 6,
        'LTC': 8,
        'USDT': 6,
        'USDC': 6,
        'USD': 2,
        'EUR': 2,
    }
    
    places = decimal_places.get(currency_code.upper(), 6)
    formatted = f"{float(amount):.{places}f}".rstrip('0').rstrip('.')
    return formatted if formatted else "0"


@register.simple_tag
def get_payment_stats():
    """Get payment statistics for dashboard."""
    try:
        from ..models import UniversalPayment
        
        stats = UniversalPayment.objects.aggregate(
            total_count=Count('id'),
            pending_count=Count('id', filter=Q(status='pending')),
            confirming_count=Count('id', filter=Q(status='confirming')),
            completed_count=Count('id', filter=Q(status='completed')),
            failed_count=Count('id', filter=Q(status='failed')),
            total_volume=Sum('amount_usd')
        )
        
        return {
            'total_payments_count': stats['total_count'] or 0,
            'pending_payments_count': stats['pending_count'] or 0,
            'confirming_payments_count': stats['confirming_count'] or 0,
            'completed_payments_count': stats['completed_count'] or 0,
            'failed_payments_count': stats['failed_count'] or 0,
            'total_volume': float(stats['total_volume'] or 0),
        }
    except Exception:
        # Return default values if there's any error
        return {
            'total_payments_count': 0,
            'pending_payments_count': 0,
            'confirming_payments_count': 0,
            'completed_payments_count': 0,
            'failed_payments_count': 0,
            'total_volume': 0.0,
        }


@register.inclusion_tag('payments/components/provider_stats.html')
def provider_statistics():
    """Render provider statistics."""
    try:
        from ..models import UniversalPayment
        from django.db.models import Avg
        
        stats = UniversalPayment.objects.values('provider').annotate(
            count=Count('id'),
            volume=Sum('amount_usd'),
            avg_amount=Avg('amount_usd'),
            completed_count=Count('id', filter=Q(status='completed')),
        ).order_by('-volume')
        
        # Calculate success rate
        for stat in stats:
            if stat['count'] > 0:
                stat['success_rate'] = (stat['completed_count'] / stat['count']) * 100
            else:
                stat['success_rate'] = 0
        
        return {'provider_stats': stats}
    except Exception:
        return {'provider_stats': []}


@register.simple_tag
def payment_status_distribution():
    """Get payment status distribution for charts."""
    try:
        from ..models import UniversalPayment
        
        distribution = UniversalPayment.objects.values('status').annotate(
            count=Count('id')
        ).order_by('-count')
        
        return {item['status']: item['count'] for item in distribution}
    except Exception:
        return {}


@register.filter
def provider_display_name(provider_key):
    """Get display name for provider."""
    provider_names = {
        'nowpayments': 'NowPayments',
        'cryptapi': 'CryptAPI',
        'cryptomus': 'Cryptomus',
        'stripe': 'Stripe',
        'internal': 'Internal',
    }
    return provider_names.get(provider_key, provider_key.title())


@register.filter
def payment_method_icon(provider):
    """Get icon for payment method."""
    icons = {
        'nowpayments': 'currency_bitcoin',
        'cryptapi': 'currency_bitcoin',
        'cryptomus': 'currency_bitcoin',
        'stripe': 'credit_card',
        'internal': 'account_balance',
    }
    return icons.get(provider, 'payment')


@register.simple_tag
def payment_json_data(payment):
    """Convert payment to JSON for JavaScript use."""
    try:
        data = {
            'id': str(payment.id),
            'status': payment.status,
            'amount_usd': float(payment.amount_usd),
            'currency_code': payment.currency_code,
            'provider': payment.provider,
            'created_at': payment.created_at.isoformat(),
            'progress_percentage': payment_progress_percentage(payment),
        }
        return mark_safe(json.dumps(data))
    except Exception:
        return mark_safe('{}')


@register.filter
def time_since_created(payment):
    """Get human-readable time since payment was created."""
    from django.utils import timezone
    from django.utils.timesince import timesince
    
    if payment.created_at:
        return timesince(payment.created_at, timezone.now())
    return "Unknown"


@register.filter
def is_crypto_payment(payment):
    """Check if payment is cryptocurrency-based."""
    crypto_providers = ['nowpayments', 'cryptapi', 'cryptomus']
    return payment.provider in crypto_providers


@register.filter
def can_cancel_payment(payment):
    """Check if payment can be cancelled."""
    cancellable_statuses = ['pending', 'confirming']
    return payment.status in cancellable_statuses


@register.filter
def payment_qr_code_data(payment):
    """Get QR code data for payment."""
    if hasattr(payment, 'pay_address') and payment.pay_address:
        # For crypto payments, use address:amount format
        if payment.pay_amount:
            return f"{payment.pay_address}?amount={payment.pay_amount}"
        return payment.pay_address
    return None


@register.inclusion_tag('payments/components/payment_qr_code.html')
def payment_qr_code(payment):
    """Render QR code for payment."""
    return {
        'payment': payment,
        'qr_data': payment_qr_code_data(payment)
    }
