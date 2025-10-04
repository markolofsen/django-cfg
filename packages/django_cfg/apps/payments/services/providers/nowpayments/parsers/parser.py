"""
NowPayments currency parser.

Handles parsing and normalization of NowPayments currency data using
pattern matching and data-driven approach.
"""

from typing import Optional
from django_cfg.modules.django_logging import get_logger

from .data import (
    CURRENCY_NAMES,
    NETWORK_NAMES,
    PRECISE_PATTERNS,
    FALLBACK_PATTERNS,
    PROVIDER_CODE_PATTERNS,
    NETWORK_SUFFIXES,
)

logger = get_logger("nowpayments_parsers")


class NowPaymentsCurrencyParser:
    """Parser for NowPayments currency data."""

    def __init__(self):
        """Initialize currency parser with data from data module."""
        self.precise_patterns = PRECISE_PATTERNS
        self.fallback_patterns = FALLBACK_PATTERNS
        self.provider_code_patterns = PROVIDER_CODE_PATTERNS
        self.network_suffixes = NETWORK_SUFFIXES

    def parse_currency_code(
        self,
        provider_code: str,
        currency_name: str,
        network_code: Optional[str] = None,
        ticker: str = ''
    ) -> tuple[str, Optional[str]]:
        """
        Smart parsing using API data, prioritizing ticker field.

        Uses ticker as primary source for base currency, then falls back to name parsing.

        Args:
            provider_code: Provider's currency code (e.g., "USDTERC20")
            currency_name: Human-readable currency name (e.g., "Tether USD")
            network_code: Network code (e.g., "eth")
            ticker: Ticker symbol (e.g., "usdt")

        Returns:
            Tuple of (base_currency, network_code) or (None, None) if should skip

        Examples:
            >>> parser.parse_currency_code("1INCHBSC", "1Inch Network (BSC)", "bsc", "1inch")
            ("1INCH", "bsc")
            >>> parser.parse_currency_code("USDTERC20", "Tether USD (ERC-20)", "eth", "usdt")
            ("USDT", "eth")
            >>> parser.parse_currency_code("BTC", "Bitcoin", "btc", "btc")
            ("BTC", "btc")
        """
        # Skip currencies with empty network - they are duplicates
        if network_code is not None and network_code.strip() == "":
            return None, None

        # Priority 1: Use ticker if available and meaningful
        if ticker and len(ticker.strip()) > 0:
            base_currency = ticker.upper().strip()
            return base_currency, network_code

        # Priority 2: Extract from provider code patterns
        base_currency = self.extract_base_currency_from_provider_code(provider_code)
        if base_currency != provider_code:
            return base_currency, network_code

        # Priority 3: Extract from name using patterns
        base_currency = self.extract_base_currency_from_name(currency_name, provider_code)
        return base_currency, network_code

    def extract_base_currency_from_name(self, currency_name: str, fallback_code: str) -> str:
        """
        Extract base currency from human-readable name using real API patterns.

        Args:
            currency_name: Human-readable currency name
            fallback_code: Code to use if no pattern matches

        Returns:
            Base currency code (e.g., "USDT", "BTC")
        """
        if not currency_name:
            return fallback_code

        name_lower = currency_name.lower()

        # Check precise patterns first (most reliable)
        for pattern, base in self.precise_patterns.items():
            if pattern in name_lower:
                return base

        # Fallback patterns for edge cases
        for pattern, base in self.fallback_patterns.items():
            if pattern in name_lower:
                return base

        # Last resort: use the provider code as-is
        return fallback_code

    def extract_base_currency_from_provider_code(self, provider_code: str) -> str:
        """
        Extract base currency from NowPayments provider code patterns.

        Args:
            provider_code: Provider's currency code (e.g., "USDTERC20")

        Returns:
            Base currency code (e.g., "USDT")
        """
        if not provider_code:
            return provider_code

        code_upper = provider_code.upper()

        # Check exact matches first
        if code_upper in self.provider_code_patterns:
            return self.provider_code_patterns[code_upper]

        # Pattern matching for common suffixes
        for suffix in self.network_suffixes:
            if code_upper.endswith(suffix):
                base_part = code_upper[:-len(suffix)]
                if len(base_part) >= 2:  # Ensure we have a meaningful base
                    return base_part

        # Return original if no pattern matches
        return provider_code

    def generate_currency_name(
        self,
        base_currency_code: str,
        network_code: Optional[str],
        original_name: str
    ) -> str:
        """
        Generate proper currency name based on base currency and network.

        Args:
            base_currency_code: Base currency code (e.g., "USDT")
            network_code: Network code (e.g., "eth")
            original_name: Original name as fallback

        Returns:
            Formatted currency name (e.g., "Tether USD (Ethereum)")

        Examples:
            >>> parser.generate_currency_name("USDT", "eth", "Tether USD")
            "Tether USD (Ethereum)"
            >>> parser.generate_currency_name("BTC", "btc", "Bitcoin")
            "Bitcoin"
        """
        base_name = CURRENCY_NAMES.get(base_currency_code, original_name)

        if not network_code or network_code == base_currency_code.lower():
            # Native currency on its own network
            return base_name

        network_name = NETWORK_NAMES.get(network_code.lower(), network_code.title())
        return f"{base_name} ({network_name})"
