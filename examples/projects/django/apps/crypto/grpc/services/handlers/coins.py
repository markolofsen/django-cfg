"""
Coin operations handlers for Crypto gRPC service.

Handles GetCoin, ListCoins, SearchCoins, GetTopCoins operations.
"""
import logging

from django.db.models import Q

from apps.crypto.models import Coin
from ..proto.converters import ProtobufConverter
from ..generated import crypto_service_pb2


logger = logging.getLogger(__name__)


def handle_get_coin(
    coin_id: int = None,
    symbol: str = None,
    slug: str = None
) -> crypto_service_pb2.CoinResponse:
    """
    Get single coin by ID, symbol, or slug.

    Args:
        coin_id: Coin ID (optional)
        symbol: Coin symbol (optional)
        slug: Coin slug (optional)

    Returns:
        CoinResponse with coin data

    Raises:
        ValueError: If no identifier provided
        Coin.DoesNotExist: If coin not found
    """
    # Determine lookup field
    lookup = {}
    if coin_id is not None:
        lookup['id'] = coin_id
    elif symbol:
        lookup['symbol'] = symbol.upper()
    elif slug:
        lookup['slug'] = slug.lower()
    else:
        raise ValueError("Must provide id, symbol, or slug")

    # Get coin
    coin = Coin.objects.get(**lookup)

    logger.info(f"📊 GetCoin: {coin.symbol}")

    return crypto_service_pb2.CoinResponse(
        success=True,
        message="Coin retrieved successfully",
        coin=ProtobufConverter.coin_to_protobuf(coin)
    )


def handle_list_coins(
    page: int = 1,
    page_size: int = 20,
    active_only: bool = False,
    tradeable_only: bool = False,
    sort_by: int = None,
    sort_order: int = None
) -> crypto_service_pb2.ListCoinsResponse:
    """
    List all coins with pagination and filtering.

    Args:
        page: Page number (default: 1)
        page_size: Items per page (default: 20, max: 100)
        active_only: Filter only active coins
        tradeable_only: Filter only tradeable coins
        sort_by: Sort field (enum)
        sort_order: Sort order (ASC/DESC)

    Returns:
        ListCoinsResponse with paginated coins
    """
    # Pagination
    page = max(page, 1)
    page_size = min(page_size, 100)
    offset = (page - 1) * page_size

    # Build queryset
    queryset = Coin.objects.all()

    # Apply filters
    if active_only:
        queryset = queryset.filter(is_active=True)
    if tradeable_only:
        queryset = queryset.filter(is_tradeable=True)

    # Apply sorting
    sort_map = {
        crypto_service_pb2.RANK: 'rank',
        crypto_service_pb2.PRICE: 'current_price_usd',
        crypto_service_pb2.MARKET_CAP: 'market_cap_usd',
        crypto_service_pb2.VOLUME_24H: 'volume_24h_usd',
        crypto_service_pb2.CHANGE_24H: 'price_change_24h_percent',
        crypto_service_pb2.NAME: 'name',
        crypto_service_pb2.SYMBOL: 'symbol',
    }
    sort_field = sort_map.get(sort_by, 'rank')
    if sort_order == crypto_service_pb2.DESC:
        sort_field = f'-{sort_field}'

    queryset = queryset.order_by(sort_field)

    # Get total count
    total_count = queryset.count()
    total_pages = (total_count + page_size - 1) // page_size

    # Paginate
    coins = list(queryset[offset:offset + page_size])

    # Convert to protobuf
    pb_coins = [ProtobufConverter.coin_to_protobuf(coin) for coin in coins]

    logger.info(f"📋 ListCoins: page={page}, count={len(pb_coins)}, total={total_count}")

    return crypto_service_pb2.ListCoinsResponse(
        success=True,
        message=f"Found {total_count} coins",
        coins=pb_coins,
        total_count=total_count,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


def handle_search_coins(query: str) -> crypto_service_pb2.ListCoinsResponse:
    """
    Search coins by name or symbol.

    Args:
        query: Search query

    Returns:
        ListCoinsResponse with matching coins

    Raises:
        ValueError: If query is empty
    """
    query = query.strip()
    if not query:
        raise ValueError("Search query cannot be empty")

    # Search in name and symbol
    coins = Coin.objects.filter(
        Q(name__icontains=query) | Q(symbol__icontains=query),
        is_active=True
    ).order_by('rank')[:50]  # Limit to 50 results

    pb_coins = [ProtobufConverter.coin_to_protobuf(coin) for coin in coins]

    logger.info(f"🔍 SearchCoins: query='{query}', found={len(pb_coins)}")

    return crypto_service_pb2.ListCoinsResponse(
        success=True,
        message=f"Found {len(pb_coins)} coins matching '{query}'",
        coins=pb_coins,
        total_count=len(pb_coins),
        page=1,
        page_size=len(pb_coins),
        total_pages=1,
    )


def handle_get_top_coins(limit: int = 10) -> crypto_service_pb2.ListCoinsResponse:
    """
    Get top coins by market cap.

    Args:
        limit: Number of coins to return (default: 10, max: 100)

    Returns:
        ListCoinsResponse with top coins
    """
    limit = min(limit, 100)

    coins = Coin.objects.filter(is_active=True).order_by('rank')[:limit]
    pb_coins = [ProtobufConverter.coin_to_protobuf(coin) for coin in coins]

    logger.info(f"🏆 GetTopCoins: limit={limit}, found={len(pb_coins)}")

    return crypto_service_pb2.ListCoinsResponse(
        success=True,
        message=f"Top {len(pb_coins)} coins by market cap",
        coins=pb_coins,
        total_count=len(pb_coins),
        page=1,
        page_size=limit,
        total_pages=1,
    )

