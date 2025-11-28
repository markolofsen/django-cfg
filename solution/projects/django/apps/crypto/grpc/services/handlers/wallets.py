"""
Wallet operations handlers for Crypto gRPC service.

Handles GetWallet, ListWallets operations.
"""
import logging
from decimal import Decimal

from apps.crypto.models import Wallet
from ..proto.converters import ProtobufConverter
from ..generated import crypto_service_pb2


logger = logging.getLogger(__name__)


def handle_get_wallet(
    user_id: int,
    coin_id: int = None,
    symbol: str = None
) -> crypto_service_pb2.WalletResponse:
    """
    Get user's wallet for specific coin.

    Args:
        user_id: User ID
        coin_id: Coin ID (optional)
        symbol: Coin symbol (optional)

    Returns:
        WalletResponse with wallet data

    Raises:
        ValueError: If no coin identifier provided
        Wallet.DoesNotExist: If wallet not found
    """
    # Determine coin lookup
    coin_lookup = {}
    if coin_id is not None:
        coin_lookup['coin__id'] = coin_id
    elif symbol:
        coin_lookup['coin__symbol'] = symbol.upper()
    else:
        raise ValueError("Must provide coin_id or symbol")

    # Get wallet
    wallet = Wallet.objects.select_related('coin').get(
        user_id=user_id,
        **coin_lookup
    )

    logger.info(f"💰 GetWallet: user={user_id}, coin={wallet.coin.symbol}")

    return crypto_service_pb2.WalletResponse(
        success=True,
        message="Wallet retrieved successfully",
        wallet=ProtobufConverter.wallet_to_protobuf(wallet)
    )


def handle_list_wallets(
    user_id: int,
    exclude_zero_balance: bool = False
) -> crypto_service_pb2.ListWalletsResponse:
    """
    List all user wallets.

    Args:
        user_id: User ID
        exclude_zero_balance: Exclude wallets with zero balance

    Returns:
        ListWalletsResponse with all wallets and total value
    """
    # Build queryset
    queryset = Wallet.objects.select_related('coin').filter(user_id=user_id)

    # Exclude zero balances if requested
    if exclude_zero_balance:
        queryset = queryset.filter(balance__gt=0)

    wallets = list(queryset.order_by('-balance'))

    # Calculate total portfolio value
    total_value_usd = sum(wallet.value_usd for wallet in wallets)

    # Convert to protobuf
    pb_wallets = [ProtobufConverter.wallet_to_protobuf(w) for w in wallets]

    logger.info(
        f"💼 ListWallets: user={user_id}, "
        f"count={len(pb_wallets)}, total=${total_value_usd}"
    )

    return crypto_service_pb2.ListWalletsResponse(
        success=True,
        message=f"Found {len(pb_wallets)} wallets",
        wallets=pb_wallets,
        total_value_usd=ProtobufConverter.decimal_to_string(total_value_usd),
    )

