"""
NowPayments currency parser for Payments v2.0.

Simplified parser for NowPayments currency codes (token+network combined).
"""

from typing import Optional, Tuple


class NowPaymentsCurrencyParser:
    """
    Parser for NowPayments currency codes.

    NowPayments combines token + network in one code:
    - USDTTRC20 → token=USDT, network=TRC20
    - USDTERC20 → token=USDT, network=ERC20
    - BTC → token=BTC, network=Bitcoin
    """

    # Common network suffixes
    NETWORK_SUFFIXES = [
        'TRC20', 'ERC20', 'BEP20', 'POLYGON', 'BSC',
        'ARBITRUM', 'OPTIMISM', 'AVALANCHE', 'SOLANA',
        'MATIC', 'ARB', 'OP', 'SOL', 'AVAX'
    ]

    # Known currency full names
    CURRENCY_NAMES = {
        'USDT': 'Tether USD',
        'USDC': 'USD Coin',
        'BTC': 'Bitcoin',
        'ETH': 'Ethereum',
        'BNB': 'Binance Coin',
        'MATIC': 'Polygon',
        'TRX': 'TRON',
        'LTC': 'Litecoin',
        'DOGE': 'Dogecoin',
        'BUSD': 'Binance USD',
        'DAI': 'Dai',
        'SHIB': 'Shiba Inu',
        'UNI': 'Uniswap',
        'LINK': 'Chainlink',
        'XRP': 'Ripple',
    }

    # Network display names
    NETWORK_NAMES = {
        'trc20': 'TRC20',
        'erc20': 'ERC20',
        'bep20': 'BEP20',
        'polygon': 'Polygon',
        'matic': 'Polygon',
        'bsc': 'BSC',
        'arbitrum': 'Arbitrum',
        'arb': 'Arbitrum',
        'optimism': 'Optimism',
        'op': 'Optimism',
        'avalanche': 'Avalanche',
        'avax': 'Avalanche',
        'solana': 'Solana',
        'sol': 'Solana',
        'eth': 'Ethereum',
        'btc': 'Bitcoin',
        'trx': 'TRON',
        'ltc': 'Litecoin',
    }

    def parse_currency_code(
        self,
        provider_code: str,
        currency_name: str = '',
        network_from_api: Optional[str] = None,
        ticker: str = ''
    ) -> Tuple[str, Optional[str]]:
        """
        Parse NowPayments currency code into token and network.

        Args:
            provider_code: Provider code (e.g., "USDTTRC20", "BTC")
            currency_name: Human-readable name (e.g., "Tether USD")
            network_from_api: Network code from API (e.g., "trx")
            ticker: Ticker symbol from API (e.g., "usdt")

        Returns:
            Tuple of (token, network) or (token, None) for native currencies

        Examples:
            >>> parser.parse_currency_code("USDTTRC20", network_from_api="trx")
            ("USDT", "TRC20")
            >>> parser.parse_currency_code("BTC", network_from_api="btc")
            ("BTC", "Bitcoin")
            >>> parser.parse_currency_code("USDTERC20", network_from_api="eth")
            ("USDT", "ERC20")
        """
        if not provider_code:
            return provider_code, None

        code_upper = provider_code.upper()

        # Priority 1: Use ticker from API if available
        if ticker and len(ticker.strip()) > 0:
            token = ticker.upper().strip()
            network = self._determine_network(code_upper, network_from_api)
            return token, network

        # Priority 2: Try to extract token + network from provider code
        token, network = self._extract_from_provider_code(code_upper)

        # Priority 3: Use network from API if available
        if network_from_api:
            network = self._normalize_network_name(network_from_api)

        return token, network

    def _extract_from_provider_code(self, code: str) -> Tuple[str, Optional[str]]:
        """
        Extract token and network from provider code.

        Examples:
            USDTTRC20 → (USDT, TRC20)
            USDTERC20 → (USDT, ERC20)
            BTC → (BTC, None)
        """
        # Check for known network suffixes
        for suffix in self.NETWORK_SUFFIXES:
            if code.endswith(suffix):
                token = code[:-len(suffix)]
                network = suffix
                if len(token) >= 2:  # Ensure valid token
                    return token, network

        # No network suffix found - it's a native currency
        return code, None

    def _determine_network(self, code: str, network_from_api: Optional[str]) -> Optional[str]:
        """
        Determine network from provider code and API data.
        """
        # Try to extract from code first
        _, network_from_code = self._extract_from_provider_code(code)

        if network_from_code:
            return network_from_code

        # Use API network if available
        if network_from_api:
            return self._normalize_network_name(network_from_api)

        return None

    def _normalize_network_name(self, network: str) -> str:
        """
        Normalize network name to standard format.

        Examples:
            "trx" → "TRC20"
            "eth" → "Ethereum"
            "bsc" → "BSC"
        """
        network_lower = network.lower()
        return self.NETWORK_NAMES.get(network_lower, network.upper())

    def generate_currency_name(
        self,
        token: str,
        network: Optional[str],
        original_name: str = ''
    ) -> str:
        """
        Generate display name for currency.

        Args:
            token: Token symbol (e.g., "USDT")
            network: Network name (e.g., "TRC20")
            original_name: Original name from API as fallback

        Returns:
            Formatted name (e.g., "Tether USD (TRC20)")

        Examples:
            >>> parser.generate_currency_name("USDT", "TRC20")
            "Tether USD (TRC20)"
            >>> parser.generate_currency_name("BTC", "Bitcoin")
            "Bitcoin"
            >>> parser.generate_currency_name("ETH", "Ethereum")
            "Ethereum"
        """
        # Get base currency name
        base_name = self.CURRENCY_NAMES.get(token, original_name or token)

        # If no network or network matches token, just return base name
        if not network or network.lower() == token.lower():
            return base_name

        # If network is the native network name (Bitcoin, Ethereum, etc.)
        # and matches base name, return just the base name
        if network.lower() in ['bitcoin', 'ethereum', 'litecoin', 'dogecoin']:
            if network.lower() == base_name.lower():
                return base_name

        # Otherwise, combine with network
        return f"{base_name} ({network})"

    def get_full_currency_name(self, token: str) -> str:
        """Get full currency name by token symbol."""
        return self.CURRENCY_NAMES.get(token, token)
