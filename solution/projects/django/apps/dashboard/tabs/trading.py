from django.db.models import Sum
from django.http import HttpRequest


def callback(request: HttpRequest) -> dict:
    """Trading overview.

    This tab was written against `apps.trading` (Portfolio, Order) — an app that
    does not exist in this project, so every render raised ModuleNotFoundError
    and the tab 500'd. There is nothing to restore it from.

    Rather than delete a tab someone may still want, it now degrades: if the app
    is absent it reports "unavailable" and the template renders an empty state.
    A dashboard tab must never take the admin page down.
    """
    try:
        from apps.trading.models import Order, Portfolio  # type: ignore[import-not-found]
    except ModuleNotFoundError:
        return {"available": False}

    orders = Order.objects.filter(status="filled")

    return {
        "available": True,
        "portfolios": Portfolio.objects.select_related("user").order_by("-total_balance_usd")[:10],
        "total_volume": orders.aggregate(total=Sum("total_usd"))["total"] or 0,
        "orders_count": orders.count(),
        "buy_orders": orders.filter(side="buy").count(),
        "sell_orders": orders.filter(side="sell").count(),
        "recent_orders": Order.objects.select_related("portfolio__user").order_by("-created_at")[:15],
    }
