"""
Transfer handlers for Crypto gRPC service.

Handles Deposit, Withdraw, and Transfer operations.
"""
import logging
import uuid
from decimal import Decimal

from django.db import transaction as db_transaction

from apps.crypto.models import Coin, Wallet
from ..proto.converters import ProtobufConverter
from ..generated import crypto_service_pb2


logger = logging.getLogger(__name__)


def handle_deposit(
    user_id: int,
    symbol: str,
    amount: str,
    transaction_id: str
) -> crypto_service_pb2.WalletResponse:
    """
    Deposit funds to wallet.

    Args:
        user_id: User ID
        symbol: Coin symbol (e.g., 'BTC')
        amount: Amount to deposit (as string for precision)
        transaction_id: External transaction ID

    Returns:
        WalletResponse with updated wallet

    Raises:
        ValueError: If amount is invalid
        Coin.DoesNotExist: If coin not found
    """
    amount_decimal = ProtobufConverter.string_to_decimal(amount)
    if amount_decimal <= 0:
        raise ValueError("Amount must be positive")

    # Get coin
    coin = Coin.objects.get(symbol=symbol.upper())

    # Get or create wallet
    with db_transaction.atomic():
        wallet, created = Wallet.objects.select_related('coin').get_or_create(
            user_id=user_id,
            coin=coin,
            defaults={'balance': Decimal('0')}
        )

        # Add deposit
        wallet.balance += amount_decimal
        wallet.save(update_fields=['balance', 'updated_at'])

    logger.info(
        f"💵 Deposit: user={user_id}, coin={coin.symbol}, "
        f"amount={amount_decimal}, tx={transaction_id}"
    )

    return crypto_service_pb2.WalletResponse(
        success=True,
        message=f"Deposited {amount_decimal} {coin.symbol} successfully",
        wallet=ProtobufConverter.wallet_to_protobuf(wallet)
    )


def handle_withdraw(
    user_id: int,
    symbol: str,
    amount: str,
    destination_address: str
) -> crypto_service_pb2.WalletResponse:
    """
    Withdraw funds from wallet.

    Args:
        user_id: User ID
        symbol: Coin symbol (e.g., 'BTC')
        amount: Amount to withdraw (as string for precision)
        destination_address: Destination wallet address

    Returns:
        WalletResponse with updated wallet

    Raises:
        ValueError: If amount is invalid or insufficient balance
        Wallet.DoesNotExist: If wallet not found
    """
    amount_decimal = ProtobufConverter.string_to_decimal(amount)
    if amount_decimal <= 0:
        raise ValueError("Amount must be positive")

    # Get wallet
    wallet = Wallet.objects.select_related('coin').get(
        user_id=user_id,
        coin__symbol=symbol.upper()
    )

    # Check balance
    if wallet.balance < amount_decimal:
        raise ValueError(
            f"Insufficient balance: {wallet.balance} < {amount_decimal}"
        )

    # Withdraw
    with db_transaction.atomic():
        wallet.balance -= amount_decimal
        wallet.save(update_fields=['balance', 'updated_at'])

    logger.info(
        f"💸 Withdraw: user={user_id}, coin={wallet.coin.symbol}, "
        f"amount={amount_decimal}, address={destination_address}"
    )

    return crypto_service_pb2.WalletResponse(
        success=True,
        message=f"Withdrew {amount_decimal} {wallet.coin.symbol} successfully",
        wallet=ProtobufConverter.wallet_to_protobuf(wallet)
    )


def handle_transfer(
    from_user_id: int,
    to_user_id: int,
    symbol: str,
    amount: str,
    note: str = ""
) -> crypto_service_pb2.TransferResponse:
    """
    Transfer funds between wallets.

    Args:
        from_user_id: Sender user ID
        to_user_id: Receiver user ID
        symbol: Coin symbol (e.g., 'BTC')
        amount: Amount to transfer (as string for precision)
        note: Optional transfer note

    Returns:
        TransferResponse with both wallets and transaction ID

    Raises:
        ValueError: If amount is invalid or insufficient balance
        Wallet.DoesNotExist: If sender wallet not found
    """
    amount_decimal = ProtobufConverter.string_to_decimal(amount)
    if amount_decimal <= 0:
        raise ValueError("Amount must be positive")

    if from_user_id == to_user_id:
        raise ValueError("Cannot transfer to yourself")

    # Get coin
    coin = Coin.objects.get(symbol=symbol.upper())

    # Transfer
    with db_transaction.atomic():
        # Get sender wallet
        from_wallet = Wallet.objects.select_related('coin').select_for_update().get(
            user_id=from_user_id,
            coin=coin
        )

        # Check balance
        if from_wallet.balance < amount_decimal:
            raise ValueError(
                f"Insufficient balance: {from_wallet.balance} < {amount_decimal}"
            )

        # Get or create receiver wallet
        to_wallet, created = Wallet.objects.select_related('coin').get_or_create(
            user_id=to_user_id,
            coin=coin,
            defaults={'balance': Decimal('0')}
        )

        # Perform transfer
        from_wallet.balance -= amount_decimal
        to_wallet.balance += amount_decimal

        from_wallet.save(update_fields=['balance', 'updated_at'])
        to_wallet.save(update_fields=['balance', 'updated_at'])

    transaction_id = str(uuid.uuid4())

    logger.info(
        f"🔄 Transfer: from={from_user_id} to={to_user_id}, "
        f"coin={coin.symbol}, amount={amount_decimal}, tx={transaction_id}"
    )

    return crypto_service_pb2.TransferResponse(
        success=True,
        message=f"Transferred {amount_decimal} {coin.symbol} successfully",
        from_wallet=ProtobufConverter.wallet_to_protobuf(from_wallet),
        to_wallet=ProtobufConverter.wallet_to_protobuf(to_wallet),
        transaction_id=transaction_id,
    )

