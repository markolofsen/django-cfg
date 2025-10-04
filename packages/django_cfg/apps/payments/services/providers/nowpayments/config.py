"""
NowPayments provider configuration.

Simple configuration constants for NowPayments provider.
"""

from decimal import Decimal

# NowPayments configuration constants
class NowPaymentsConfig:
    """Simple NowPayments configuration."""
    
    # Fees
    FEE_PERCENTAGE = Decimal('0.005')  # 0.5%
    FIXED_FEE_USD = Decimal('0.0')     # No fixed fee
    
    # Limits
    MIN_AMOUNT_USD = Decimal('0.000001')  # Minimum for all crypto
    MAX_AMOUNT_USD = Decimal('1000000.0')
    
    # Network names
    NETWORK_NAMES = {
        'eth': 'Ethereum',
        'bsc': 'Binance Smart Chain', 
        'matic': 'Polygon',
        'trx': 'TRON',
        'btc': 'Bitcoin',
        'ltc': 'Litecoin',
        'sol': 'Solana',
        'avaxc': 'Avalanche C-Chain',
        'arbitrum': 'Arbitrum',
        'op': 'Optimism',
        'base': 'Base',
        'ton': 'TON',
        'near': 'NEAR',
        'algo': 'Algorand',
        'xtz': 'Tezos',
        'dot': 'Polkadot',
        'ada': 'Cardano',
        'xlm': 'Stellar',
        'xrp': 'Ripple',
        'atom': 'Cosmos',
        'luna': 'Terra',
        'neo': 'Neo',
        'waves': 'Waves',
    }
    
    # Confirmation blocks
    CONFIRMATION_BLOCKS = {
        'btc': 1,
        'eth': 12,
        'bsc': 3,
        'matic': 20,
        'trx': 19,
    }
    
    @classmethod
    def get_network_name(cls, network_code: str) -> str:
        """Get human-readable network name."""
        return cls.NETWORK_NAMES.get(network_code.lower(), network_code.upper())
    
    @classmethod
    def get_confirmation_blocks(cls, network_code: str) -> int:
        """Get confirmation blocks for network."""
        return cls.CONFIRMATION_BLOCKS.get(network_code.lower(), 1)
    
    @classmethod
    def get_min_amount(cls) -> Decimal:
        """Get minimum amount for all currencies."""
        return cls.MIN_AMOUNT_USD
