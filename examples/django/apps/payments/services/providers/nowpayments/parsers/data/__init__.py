"""
Data for NowPayments parsers.

All currency names, patterns, and constants for parsing NowPayments API data.
"""

from .currency_names import CURRENCY_NAMES, NETWORK_NAMES
from .patterns import PRECISE_PATTERNS, FALLBACK_PATTERNS, PROVIDER_CODE_PATTERNS
from .constants import NETWORK_SUFFIXES

__all__ = [
    # Currency and network names
    'CURRENCY_NAMES',
    'NETWORK_NAMES',

    # Parsing patterns
    'PRECISE_PATTERNS',
    'FALLBACK_PATTERNS',
    'PROVIDER_CODE_PATTERNS',

    # Constants
    'NETWORK_SUFFIXES',
]
