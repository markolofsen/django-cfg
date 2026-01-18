# Generated data migration for initial currencies

from django.db import migrations


INITIAL_CURRENCIES = [
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
    # Americas
    {"code": "CAD", "name": "Canadian Dollar", "symbol": "C$", "currency_type": "fiat", "decimals": 2},
    {"code": "AUD", "name": "Australian Dollar", "symbol": "A$", "currency_type": "fiat", "decimals": 2},
    {"code": "NZD", "name": "New Zealand Dollar", "symbol": "NZ$", "currency_type": "fiat", "decimals": 2},
    {"code": "BRL", "name": "Brazilian Real", "symbol": "R$", "currency_type": "fiat", "decimals": 2},
    {"code": "MXN", "name": "Mexican Peso", "symbol": "$", "currency_type": "fiat", "decimals": 2},
    {"code": "ARS", "name": "Argentine Peso", "symbol": "$", "currency_type": "fiat", "decimals": 2},
    # Middle East & Africa
    {"code": "AED", "name": "UAE Dirham", "symbol": "د.إ", "currency_type": "fiat", "decimals": 2},
    {"code": "SAR", "name": "Saudi Riyal", "symbol": "﷼", "currency_type": "fiat", "decimals": 2},
    {"code": "ILS", "name": "Israeli Shekel", "symbol": "₪", "currency_type": "fiat", "decimals": 2},
    {"code": "ZAR", "name": "South African Rand", "symbol": "R", "currency_type": "fiat", "decimals": 2},
    {"code": "EGP", "name": "Egyptian Pound", "symbol": "£", "currency_type": "fiat", "decimals": 2},
    # Crypto
    {"code": "BTC", "name": "Bitcoin", "symbol": "₿", "currency_type": "crypto", "decimals": 8},
    {"code": "ETH", "name": "Ethereum", "symbol": "Ξ", "currency_type": "crypto", "decimals": 8},
    {"code": "USDT", "name": "Tether", "symbol": "₮", "currency_type": "crypto", "decimals": 6},
    {"code": "USDC", "name": "USD Coin", "symbol": "$", "currency_type": "crypto", "decimals": 6},
    {"code": "SOL", "name": "Solana", "symbol": "◎", "currency_type": "crypto", "decimals": 9},
    {"code": "XRP", "name": "Ripple", "symbol": "✕", "currency_type": "crypto", "decimals": 6},
    {"code": "ADA", "name": "Cardano", "symbol": "₳", "currency_type": "crypto", "decimals": 6},
    {"code": "DOGE", "name": "Dogecoin", "symbol": "Ð", "currency_type": "crypto", "decimals": 8},
    {"code": "LTC", "name": "Litecoin", "symbol": "Ł", "currency_type": "crypto", "decimals": 8},
]


def populate_currencies(apps, schema_editor):
    """Add initial currencies to the database."""
    Currency = apps.get_model("cfg_currency", "Currency")

    for data in INITIAL_CURRENCIES:
        Currency.objects.get_or_create(
            code=data["code"],
            defaults=data,
        )


def remove_currencies(apps, schema_editor):
    """Remove initial currencies (reverse migration)."""
    Currency = apps.get_model("cfg_currency", "Currency")
    codes = [c["code"] for c in INITIAL_CURRENCIES]
    Currency.objects.filter(code__in=codes).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("cfg_currency", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(populate_currencies, remove_currencies),
    ]
