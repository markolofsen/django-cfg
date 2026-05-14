from django.http import HttpRequest
from django.db.models import Avg, Count, Sum


def callback(request: HttpRequest) -> dict:
    from apps.crypto.models.coin import Coin

    coins = Coin.objects.filter(is_active=True).order_by('rank')[:20]
    total = Coin.objects.count()
    active = Coin.objects.filter(is_active=True).count()
    gainers = Coin.objects.filter(price_change_24h_percent__gt=0).count()
    losers = Coin.objects.filter(price_change_24h_percent__lt=0).count()
    avg_change = Coin.objects.aggregate(avg=Avg('price_change_24h_percent'))['avg'] or 0

    return {
        'coins': coins,
        'total_coins': total,
        'active_coins': active,
        'gainers': gainers,
        'losers': losers,
        'avg_change_24h': round(float(avg_change), 2),
    }
