from django.db.models import Count, Sum
from django.http import HttpRequest


def callback(request: HttpRequest) -> dict:
    """Market overview, from the CoinListing table.

    This used to import `apps.crypto.models.coin.Coin` and query `is_active`,
    `rank` and `price_change_24h_percent` — a model that does not exist in this
    project. `apps.crypto.models` is a MODULE, not a package, and the model it
    defines is `CoinListing`, which has none of those fields. Every render raised
    ModuleNotFoundError.
    """
    from apps.crypto.models import CoinListing

    coins = CoinListing.objects.order_by("-market_cap")[:20]

    agg = CoinListing.objects.aggregate(
        total=Count("id"),
        market_cap=Sum("market_cap"),
    )

    return {
        "coins": coins,
        "total_coins": agg["total"] or 0,
        "total_market_cap": agg["market_cap"] or 0,
    }
