"""
Currency list sync service.

Sync currencies from predefined list or external API.
"""

from typing import Any

from django_cfg.modules.django_logging import get_logger

logger = get_logger(__name__)


# Complete currency list with metadata
CURRENCIES = [
    # Major fiat
    {"code": "USD", "name": "US Dollar", "symbol": "$", "currency_type": "fiat", "decimals": 2},
    {"code": "EUR", "name": "Euro", "symbol": "€", "currency_type": "fiat", "decimals": 2},
    {"code": "GBP", "name": "British Pound", "symbol": "£", "currency_type": "fiat", "decimals": 2},
    {"code": "JPY", "name": "Japanese Yen", "symbol": "¥", "currency_type": "fiat", "decimals": 0},
    {"code": "CNY", "name": "Chinese Yuan", "symbol": "¥", "currency_type": "fiat", "decimals": 2},
    {"code": "CHF", "name": "Swiss Franc", "symbol": "Fr", "currency_type": "fiat", "decimals": 2},
    # Asian
    {"code": "KRW", "name": "South Korean Won", "symbol": "₩", "currency_type": "fiat", "decimals": 0},
    {"code": "INR", "name": "Indian Rupee", "symbol": "₹", "currency_type": "fiat", "decimals": 2},
    {"code": "THB", "name": "Thai Baht", "symbol": "฿", "currency_type": "fiat", "decimals": 2},
    {"code": "VND", "name": "Vietnamese Dong", "symbol": "₫", "currency_type": "fiat", "decimals": 0},
    {"code": "IDR", "name": "Indonesian Rupiah", "symbol": "Rp", "currency_type": "fiat", "decimals": 0},
    {"code": "SGD", "name": "Singapore Dollar", "symbol": "S$", "currency_type": "fiat", "decimals": 2},
    {"code": "HKD", "name": "Hong Kong Dollar", "symbol": "HK$", "currency_type": "fiat", "decimals": 2},
    {"code": "TWD", "name": "Taiwan Dollar", "symbol": "NT$", "currency_type": "fiat", "decimals": 2},
    {"code": "MYR", "name": "Malaysian Ringgit", "symbol": "RM", "currency_type": "fiat", "decimals": 2},
    {"code": "PHP", "name": "Philippine Peso", "symbol": "₱", "currency_type": "fiat", "decimals": 2},
    # European
    {"code": "RUB", "name": "Russian Ruble", "symbol": "₽", "currency_type": "fiat", "decimals": 2},
    {"code": "UAH", "name": "Ukrainian Hryvnia", "symbol": "₴", "currency_type": "fiat", "decimals": 2},
    {"code": "PLN", "name": "Polish Zloty", "symbol": "zł", "currency_type": "fiat", "decimals": 2},
    {"code": "CZK", "name": "Czech Koruna", "symbol": "Kč", "currency_type": "fiat", "decimals": 2},
    {"code": "TRY", "name": "Turkish Lira", "symbol": "₺", "currency_type": "fiat", "decimals": 2},
    {"code": "SEK", "name": "Swedish Krona", "symbol": "kr", "currency_type": "fiat", "decimals": 2},
    {"code": "NOK", "name": "Norwegian Krone", "symbol": "kr", "currency_type": "fiat", "decimals": 2},
    {"code": "DKK", "name": "Danish Krone", "symbol": "kr", "currency_type": "fiat", "decimals": 2},
    {"code": "HUF", "name": "Hungarian Forint", "symbol": "Ft", "currency_type": "fiat", "decimals": 0},
    {"code": "RON", "name": "Romanian Leu", "symbol": "lei", "currency_type": "fiat", "decimals": 2},
    {"code": "BGN", "name": "Bulgarian Lev", "symbol": "лв", "currency_type": "fiat", "decimals": 2},
    {"code": "HRK", "name": "Croatian Kuna", "symbol": "kn", "currency_type": "fiat", "decimals": 2},
    {"code": "ISK", "name": "Icelandic Krona", "symbol": "kr", "currency_type": "fiat", "decimals": 0},
    # Americas
    {"code": "CAD", "name": "Canadian Dollar", "symbol": "C$", "currency_type": "fiat", "decimals": 2},
    {"code": "AUD", "name": "Australian Dollar", "symbol": "A$", "currency_type": "fiat", "decimals": 2},
    {"code": "NZD", "name": "New Zealand Dollar", "symbol": "NZ$", "currency_type": "fiat", "decimals": 2},
    {"code": "BRL", "name": "Brazilian Real", "symbol": "R$", "currency_type": "fiat", "decimals": 2},
    {"code": "MXN", "name": "Mexican Peso", "symbol": "$", "currency_type": "fiat", "decimals": 2},
    {"code": "ARS", "name": "Argentine Peso", "symbol": "$", "currency_type": "fiat", "decimals": 2},
    {"code": "CLP", "name": "Chilean Peso", "symbol": "$", "currency_type": "fiat", "decimals": 0},
    {"code": "COP", "name": "Colombian Peso", "symbol": "$", "currency_type": "fiat", "decimals": 0},
    {"code": "PEN", "name": "Peruvian Sol", "symbol": "S/", "currency_type": "fiat", "decimals": 2},
    # Middle East & Africa
    {"code": "AED", "name": "UAE Dirham", "symbol": "د.إ", "currency_type": "fiat", "decimals": 2},
    {"code": "SAR", "name": "Saudi Riyal", "symbol": "﷼", "currency_type": "fiat", "decimals": 2},
    {"code": "ILS", "name": "Israeli Shekel", "symbol": "₪", "currency_type": "fiat", "decimals": 2},
    {"code": "ZAR", "name": "South African Rand", "symbol": "R", "currency_type": "fiat", "decimals": 2},
    {"code": "EGP", "name": "Egyptian Pound", "symbol": "£", "currency_type": "fiat", "decimals": 2},
    {"code": "NGN", "name": "Nigerian Naira", "symbol": "₦", "currency_type": "fiat", "decimals": 2},
    {"code": "KES", "name": "Kenyan Shilling", "symbol": "KSh", "currency_type": "fiat", "decimals": 2},
    {"code": "MAD", "name": "Moroccan Dirham", "symbol": "د.م.", "currency_type": "fiat", "decimals": 2},
    {"code": "QAR", "name": "Qatari Riyal", "symbol": "﷼", "currency_type": "fiat", "decimals": 2},
    {"code": "KWD", "name": "Kuwaiti Dinar", "symbol": "د.ك", "currency_type": "fiat", "decimals": 3},
    {"code": "BHD", "name": "Bahraini Dinar", "symbol": "ب.د", "currency_type": "fiat", "decimals": 3},
    {"code": "OMR", "name": "Omani Rial", "symbol": "ر.ع.", "currency_type": "fiat", "decimals": 3},
    # Crypto
    {"code": "BTC", "name": "Bitcoin", "symbol": "₿", "currency_type": "crypto", "decimals": 8},
    {"code": "ETH", "name": "Ethereum", "symbol": "Ξ", "currency_type": "crypto", "decimals": 8},
    {"code": "USDT", "name": "Tether", "symbol": "₮", "currency_type": "crypto", "decimals": 6},
    {"code": "USDC", "name": "USD Coin", "symbol": "$", "currency_type": "crypto", "decimals": 6},
    {"code": "BNB", "name": "Binance Coin", "symbol": "BNB", "currency_type": "crypto", "decimals": 8},
    {"code": "SOL", "name": "Solana", "symbol": "◎", "currency_type": "crypto", "decimals": 9},
    {"code": "XRP", "name": "Ripple", "symbol": "✕", "currency_type": "crypto", "decimals": 6},
    {"code": "ADA", "name": "Cardano", "symbol": "₳", "currency_type": "crypto", "decimals": 6},
    {"code": "DOGE", "name": "Dogecoin", "symbol": "Ð", "currency_type": "crypto", "decimals": 8},
    {"code": "LTC", "name": "Litecoin", "symbol": "Ł", "currency_type": "crypto", "decimals": 8},
    {"code": "DOT", "name": "Polkadot", "symbol": "DOT", "currency_type": "crypto", "decimals": 10},
    {"code": "MATIC", "name": "Polygon", "symbol": "MATIC", "currency_type": "crypto", "decimals": 18},
    {"code": "AVAX", "name": "Avalanche", "symbol": "AVAX", "currency_type": "crypto", "decimals": 18},
    {"code": "LINK", "name": "Chainlink", "symbol": "LINK", "currency_type": "crypto", "decimals": 18},
    {"code": "UNI", "name": "Uniswap", "symbol": "UNI", "currency_type": "crypto", "decimals": 18},
    {"code": "ATOM", "name": "Cosmos", "symbol": "ATOM", "currency_type": "crypto", "decimals": 6},
    {"code": "XLM", "name": "Stellar", "symbol": "XLM", "currency_type": "crypto", "decimals": 7},
    {"code": "TRX", "name": "Tron", "symbol": "TRX", "currency_type": "crypto", "decimals": 6},
]

# Pre-computed sets from static list (fallback)
_STATIC_CURRENCY_CODES: set[str] = {c["code"] for c in CURRENCIES}
_STATIC_FIAT_CODES: set[str] = {c["code"] for c in CURRENCIES if c["currency_type"] == "fiat"}
_STATIC_CRYPTO_CODES: set[str] = {c["code"] for c in CURRENCIES if c["currency_type"] == "crypto"}

# Cache for DB codes
_db_codes_cache: set[str] | None = None


def get_currency_codes(from_db: bool = True) -> set[str]:
    """
    Get valid currency codes.

    Args:
        from_db: If True, fetch from database (cached). If False, use static list.

    Returns:
        Set of valid currency codes.
    """
    global _db_codes_cache

    if not from_db:
        return _STATIC_CURRENCY_CODES

    if _db_codes_cache is not None:
        return _db_codes_cache

    try:
        from ..models import Currency
        _db_codes_cache = set(Currency.objects.filter(is_active=True).values_list("code", flat=True))
        return _db_codes_cache
    except Exception:
        # Fallback to static if DB not ready
        return _STATIC_CURRENCY_CODES


def clear_currency_cache() -> None:
    """Clear the currency codes cache (call after adding new currencies)."""
    global _db_codes_cache
    _db_codes_cache = None


def is_valid_currency(code: str) -> bool:
    """Check if currency code is valid (from DB)."""
    return code.upper() in get_currency_codes()


# Aliases for backward compatibility
CURRENCY_CODES = _STATIC_CURRENCY_CODES
FIAT_CODES = _STATIC_FIAT_CODES
CRYPTO_CODES = _STATIC_CRYPTO_CODES


def sync_currencies(
    update_existing: bool = False,
    deactivate_missing: bool = False,
) -> dict[str, Any]:
    """
    Sync currencies from predefined list to database.

    Args:
        update_existing: Update name/symbol for existing currencies
        deactivate_missing: Deactivate currencies not in the list

    Returns:
        Dict with sync statistics
    """
    from ..models import Currency

    created = []
    updated = []
    skipped = []

    existing_codes = set(Currency.objects.values_list("code", flat=True))
    new_codes = {c["code"] for c in CURRENCIES}

    for data in CURRENCIES:
        code = data["code"]

        if code in existing_codes:
            if update_existing:
                Currency.objects.filter(code=code).update(
                    name=data["name"],
                    symbol=data["symbol"],
                    currency_type=data["currency_type"],
                    decimals=data["decimals"],
                    is_active=True,
                )
                updated.append(code)
            else:
                skipped.append(code)
        else:
            Currency.objects.create(**data)
            created.append(code)

    deactivated = []
    if deactivate_missing:
        missing = existing_codes - new_codes
        if missing:
            deactivated = list(missing)
            Currency.objects.filter(code__in=missing).update(is_active=False)

    result = {
        "created": len(created),
        "updated": len(updated),
        "skipped": len(skipped),
        "deactivated": len(deactivated),
        "total": len(CURRENCIES),
        "created_codes": created,
        "updated_codes": updated,
        "deactivated_codes": deactivated,
    }

    logger.info(
        f"Currency sync: {result['created']} created, "
        f"{result['updated']} updated, {result['deactivated']} deactivated"
    )

    return result


def sync_currencies_if_needed(min_count: int = 40) -> dict[str, Any] | None:
    """
    Sync currencies only if needed (empty or too few).

    Args:
        min_count: Minimum expected currencies. Sync if below this.

    Returns:
        Sync result or None if skipped.
    """
    from ..models import Currency

    current_count = Currency.objects.filter(is_active=True).count()

    if current_count >= min_count:
        logger.debug(f"Currencies OK: {current_count} >= {min_count}, skipping sync")
        return None

    logger.info(f"Currencies low: {current_count} < {min_count}, syncing...")
    return sync_currencies()


def get_currency_stats() -> dict[str, Any]:
    """Get currency statistics."""
    from ..models import Currency, CurrencyRate

    total = Currency.objects.count()
    active = Currency.objects.filter(is_active=True).count()
    fiat = Currency.objects.filter(currency_type="fiat", is_active=True).count()
    crypto = Currency.objects.filter(currency_type="crypto", is_active=True).count()
    rates_count = CurrencyRate.objects.count()

    return {
        "total": total,
        "active": active,
        "inactive": total - active,
        "fiat": fiat,
        "crypto": crypto,
        "rates": rates_count,
    }


def sync_all(
    sync_currencies_flag: bool = True,
    update_rates_flag: bool = True,
    target_currency: str = "USD",
    force_currencies: bool = False,
    force_rates: bool = False,
) -> dict[str, Any]:
    """
    Sync currencies and update rates in one call.

    Args:
        sync_currencies_flag: Sync currency list
        update_rates_flag: Update exchange rates
        target_currency: Target currency for rates
        force_currencies: Force sync even if enough currencies exist
        force_rates: Force update even if rates are fresh

    Returns:
        Combined result dict
    """
    from .update import update_rates, should_update_rates

    result = {
        "currencies": None,
        "rates": None,
    }

    # Sync currencies
    if sync_currencies_flag:
        if force_currencies:
            result["currencies"] = sync_currencies()
        else:
            result["currencies"] = sync_currencies_if_needed()

    # Update rates
    if update_rates_flag:
        if force_rates or should_update_rates():
            result["rates"] = update_rates(target_currency=target_currency)

    # Summary
    curr = result["currencies"]
    rates = result["rates"]

    logger.info(
        f"Sync all: currencies={curr['created'] if curr else 'skipped'}, "
        f"rates={rates['updated'] if rates else 'skipped'}"
    )

    return result


def add_currency(
    code: str,
    name: str,
    symbol: str = "",
    currency_type: str = "fiat",
    decimals: int = 2,
) -> dict[str, Any]:
    """
    Add a single currency.

    Args:
        code: Currency code (e.g., "USD")
        name: Currency name
        symbol: Currency symbol
        currency_type: "fiat" or "crypto"
        decimals: Decimal places

    Returns:
        Dict with result
    """
    from ..models import Currency

    code = code.upper()

    obj, created = Currency.objects.get_or_create(
        code=code,
        defaults={
            "name": name,
            "symbol": symbol,
            "currency_type": currency_type,
            "decimals": decimals,
        },
    )

    if created:
        logger.info(f"Created currency: {code}")
    else:
        logger.info(f"Currency already exists: {code}")

    return {
        "code": code,
        "created": created,
        "currency": {
            "code": obj.code,
            "name": obj.name,
            "symbol": obj.symbol,
            "type": obj.currency_type,
        },
    }
