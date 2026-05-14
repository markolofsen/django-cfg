from django.http import HttpRequest
from django.db.models import Sum, Count, Avg


def callback(request: HttpRequest) -> dict:
    from apps.trading.models import Portfolio, Order

    portfolios = Portfolio.objects.select_related('user').order_by('-total_balance_usd')[:10]
    total_volume = Order.objects.filter(status='filled').aggregate(total=Sum('total_usd'))['total'] or 0
    orders_today = Order.objects.filter(status='filled').count()
    buy_orders = Order.objects.filter(side='buy', status='filled').count()
    sell_orders = Order.objects.filter(side='sell', status='filled').count()
    recent_orders = Order.objects.select_related('portfolio__user').order_by('-created_at')[:15]

    return {
        'portfolios': portfolios,
        'total_volume': total_volume,
        'orders_count': orders_today,
        'buy_orders': buy_orders,
        'sell_orders': sell_orders,
        'recent_orders': recent_orders,
    }
