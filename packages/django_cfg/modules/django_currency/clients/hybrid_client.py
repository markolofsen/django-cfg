"""
Hybrid Currency Client - Multi-source currency rate fetcher with full caching
Combines multiple data sources for maximum reliability and performance:
1. Fawaz Currency API (primary - 200+ currencies via CDN)
2. Frankfurter API (reliable fiat currencies)
3. ExchangeRate-API (fallback)
4. CBR API (for RUB rates)

All supported currencies are dynamically fetched and cached.
"""

import logging
import random
import time
from datetime import datetime
from typing import Dict, Set

import requests
from cachetools import TTLCache

from ..core.exceptions import RateFetchError
from ..core.models import Rate

logger = logging.getLogger(__name__)


class HybridCurrencyClient:
    """Multi-source currency client with intelligent fallback and full caching."""

    def __init__(self, cache_ttl: int = 3600):
        """Initialize hybrid client with multiple data sources."""
        self._rate_cache = TTLCache(maxsize=1000, ttl=cache_ttl)
        self._session = requests.Session()

        # User-Agent rotation for better reliability
        self._user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'curl/7.68.0',
            'python-requests/2.31.0'
        ]

        # Data sources configuration (ordered by priority)
        self._sources = {
            'fawaz_currency': {
                'url': 'https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies',
                'priority': 1,
                'rate_limit': 0.5,
                'supports_check': self._fawaz_supports_pair,
                'fetch_method': self._fetch_from_fawaz_currency,
                'get_supported': self._get_fawaz_supported_currencies
            },
            'prebid_currency': {
                'url': 'https://cdn.jsdelivr.net/gh/prebid/currency-file@1/latest.json',
                'priority': 2,
                'rate_limit': 0.5,
                'supports_check': self._prebid_supports_pair,
                'fetch_method': self._fetch_from_prebid_currency,
                'get_supported': self._get_prebid_supported_currencies
            },
            'frankfurter': {
                'url': 'https://api.frankfurter.app/latest',
                'priority': 3,
                'rate_limit': 1.0,
                'supports_check': self._frankfurter_supports_pair,
                'fetch_method': self._fetch_from_frankfurter,
                'get_supported': self._get_frankfurter_supported_currencies
            },
            'exchangerate_api': {
                'url': 'https://open.er-api.com/v6/latest',
                'priority': 4,
                'rate_limit': 1.5,
                'supports_check': self._exchangerate_supports_pair,
                'fetch_method': self._fetch_from_exchangerate_api,
                'get_supported': self._get_exchangerate_supported_currencies
            },
            'cbr': {
                'url': 'https://www.cbr-xml-daily.ru/daily_json.js',
                'priority': 5,
                'rate_limit': 1.0,
                'supports_check': self._cbr_supports_pair,
                'fetch_method': self._fetch_from_cbr,
                'get_supported': self._get_cbr_supported_currencies
            }
        }

        self._last_request_times = {}
        self._max_retries = 2

    def _get_random_user_agent(self) -> str:
        """Get random User-Agent for better request reliability."""
        return random.choice(self._user_agents)

    def _make_request_with_retry(self, url: str, source: str, headers: dict = None) -> requests.Response:
        """Make HTTP request with exponential backoff retry logic."""
        source_config = self._sources[source]
        rate_limit = source_config['rate_limit']

        # Rate limiting
        last_request = self._last_request_times.get(source, 0)
        time_since_last = time.time() - last_request
        if time_since_last < rate_limit:
            sleep_time = rate_limit - time_since_last + random.uniform(0, 0.5)
            time.sleep(sleep_time)

        for attempt in range(self._max_retries + 1):
            try:
                request_headers = {
                    'User-Agent': self._get_random_user_agent(),
                    'Accept': 'application/json',
                    'Accept-Language': 'en-US,en;q=0.9'
                }
                if headers:
                    request_headers.update(headers)

                response = self._session.get(url, headers=request_headers, timeout=10)
                self._last_request_times[source] = time.time()

                if response.status_code == 429:
                    if attempt < self._max_retries:
                        backoff = (2 ** attempt) * 3 + random.uniform(1, 2)
                        logger.warning(f"{source}: Rate limited, retrying in {backoff:.1f}s")
                        time.sleep(backoff)
                        continue
                    else:
                        raise requests.exceptions.HTTPError(f"429 Too Many Requests from {source}")

                response.raise_for_status()
                return response

            except requests.exceptions.RequestException as e:
                if attempt < self._max_retries:
                    backoff = (2 ** attempt) * 2 + random.uniform(0.5, 1)
                    logger.warning(f"{source}: Request failed, retrying in {backoff:.1f}s - {e}")
                    time.sleep(backoff)
                    continue
                else:
                    raise RateFetchError(f"{source} request failed: {e}")

        raise RateFetchError(f"{source}: Failed after {self._max_retries + 1} attempts")

    # ============================================================================
    # FAWAZ CURRENCY API
    # ============================================================================

    def _get_fawaz_supported_currencies(self) -> Set[str]:
        """Get list of supported currencies from Fawaz API with caching."""
        cache_key = "fawaz_supported_currencies"

        if cache_key in self._rate_cache:
            return self._rate_cache[cache_key]

        try:
            url = f"{self._sources['fawaz_currency']['url']}/usd.json"
            response = self._make_request_with_retry(url, 'fawaz_currency')
            data = response.json()

            if 'usd' in data:
                supported = set(data['usd'].keys())
                supported.add('usd')  # Add USD itself
                logger.info(f"Fawaz API supports {len(supported)} currencies")

                self._rate_cache[cache_key] = supported
                return supported
            else:
                logger.warning("Fawaz API response format unexpected")
                return set()

        except Exception as e:
            logger.warning(f"Failed to get Fawaz supported currencies: {e}")
            # Minimal fallback
            fallback = {'usd', 'eur', 'btc', 'eth'}
            self._rate_cache[cache_key] = fallback
            return fallback

    def _fawaz_supports_pair(self, base: str, quote: str) -> bool:
        """Check if Fawaz Currency API supports the currency pair."""
        supported_currencies = self._get_fawaz_supported_currencies()
        base_lower = base.lower()
        quote_lower = quote.lower()
        return base_lower in supported_currencies and quote_lower in supported_currencies

    def _fetch_from_fawaz_currency(self, base: str, quote: str) -> Rate:
        """Fetch rate from Fawaz Currency API via jsDelivr CDN."""
        base_lower = base.lower()
        url = f"{self._sources['fawaz_currency']['url']}/{base_lower}.json"
        response = self._make_request_with_retry(url, 'fawaz_currency')
        data = response.json()

        if base_lower not in data:
            raise RateFetchError(f"Fawaz API doesn't have base currency {base}")

        rates = data[base_lower]
        quote_lower = quote.lower()

        if quote_lower not in rates:
            raise RateFetchError(f"Fawaz API doesn't have {base}/{quote} rate")

        return Rate(
            source="fawaz_currency",
            base_currency=base.upper(),
            quote_currency=quote.upper(),
            rate=float(rates[quote_lower]),
            timestamp=datetime.now()
        )

    # ============================================================================
    # PREBID CURRENCY API
    # ============================================================================

    def _get_prebid_supported_currencies(self) -> Set[str]:
        """Get list of supported currencies from Prebid Currency API with caching."""
        cache_key = "prebid_supported_currencies"

        if cache_key in self._rate_cache:
            return self._rate_cache[cache_key]

        try:
            url = self._sources['prebid_currency']['url']
            response = self._make_request_with_retry(url, 'prebid_currency')
            data = response.json()

            if 'conversions' in data:
                supported = set()
                # Prebid has conversions from multiple base currencies
                for base_currency, rates in data['conversions'].items():
                    supported.add(base_currency.upper())
                    supported.update(rate.upper() for rate in rates.keys())

                logger.info(f"Prebid Currency API supports {len(supported)} currencies")

                self._rate_cache[cache_key] = supported
                return supported
            else:
                logger.warning("Prebid Currency API response format unexpected")
                return set()

        except Exception as e:
            logger.warning(f"Failed to get Prebid supported currencies: {e}")
            # Fallback to major currencies
            fallback = {'USD', 'EUR', 'GBP', 'JPY', 'CHF', 'CAD', 'AUD'}
            self._rate_cache[cache_key] = fallback
            return fallback

    def _prebid_supports_pair(self, base: str, quote: str) -> bool:
        """Check if Prebid Currency API supports the currency pair."""
        supported_currencies = self._get_prebid_supported_currencies()
        return base.upper() in supported_currencies and quote.upper() in supported_currencies

    def _fetch_from_prebid_currency(self, base: str, quote: str) -> Rate:
        """Fetch rate from Prebid Currency API."""
        url = self._sources['prebid_currency']['url']
        response = self._make_request_with_retry(url, 'prebid_currency')
        data = response.json()

        base_upper = base.upper()
        quote_upper = quote.upper()

        # Check if we have direct conversion from base to quote
        if 'conversions' in data and base_upper in data['conversions']:
            rates = data['conversions'][base_upper]
            if quote_upper in rates:
                return Rate(
                    source="prebid_currency",
                    base_currency=base_upper,
                    quote_currency=quote_upper,
                    rate=float(rates[quote_upper]),
                    timestamp=datetime.now()
                )

        # Try reverse conversion (quote to base)
        if 'conversions' in data and quote_upper in data['conversions']:
            rates = data['conversions'][quote_upper]
            if base_upper in rates:
                reverse_rate = float(rates[base_upper])
                if reverse_rate > 0:
                    return Rate(
                        source="prebid_currency",
                        base_currency=base_upper,
                        quote_currency=quote_upper,
                        rate=1.0 / reverse_rate,
                        timestamp=datetime.now()
                    )

        raise RateFetchError(f"Prebid Currency API doesn't have {base}/{quote} rate")

    # ============================================================================
    # FRANKFURTER API
    # ============================================================================

    def _get_frankfurter_supported_currencies(self) -> Set[str]:
        """Get list of supported currencies from Frankfurter API with caching."""
        cache_key = "frankfurter_supported_currencies"

        if cache_key in self._rate_cache:
            return self._rate_cache[cache_key]

        try:
            url = f"{self._sources['frankfurter']['url']}"
            response = self._make_request_with_retry(url, 'frankfurter')
            data = response.json()

            if 'rates' in data:
                supported = set(data['rates'].keys())
                supported.add('EUR')  # Add EUR itself (base currency)
                logger.info(f"Frankfurter API supports {len(supported)} currencies")

                self._rate_cache[cache_key] = supported
                return supported
            else:
                logger.warning("Frankfurter API response format unexpected")
                return set()

        except Exception as e:
            logger.warning(f"Failed to get Frankfurter supported currencies: {e}")
            # Fallback to major fiat currencies
            fallback = {'EUR', 'USD', 'GBP', 'JPY', 'CHF', 'CAD', 'AUD'}
            self._rate_cache[cache_key] = fallback
            return fallback

    def _frankfurter_supports_pair(self, base: str, quote: str) -> bool:
        """Check if Frankfurter supports the currency pair."""
        supported_currencies = self._get_frankfurter_supported_currencies()
        return base.upper() in supported_currencies and quote.upper() in supported_currencies

    def _fetch_from_frankfurter(self, base: str, quote: str) -> Rate:
        """Fetch rate from Frankfurter API."""
        url = f"{self._sources['frankfurter']['url']}?from={base}&to={quote}"
        response = self._make_request_with_retry(url, 'frankfurter')
        data = response.json()

        if 'rates' not in data or quote.upper() not in data['rates']:
            raise RateFetchError(f"Frankfurter doesn't have {base}/{quote} rate")

        return Rate(
            source="frankfurter",
            base_currency=base.upper(),
            quote_currency=quote.upper(),
            rate=float(data['rates'][quote.upper()]),
            timestamp=datetime.now()
        )

    # ============================================================================
    # EXCHANGERATE-API
    # ============================================================================

    def _get_exchangerate_supported_currencies(self) -> Set[str]:
        """Get list of supported currencies from ExchangeRate-API with caching."""
        cache_key = "exchangerate_supported_currencies"

        if cache_key in self._rate_cache:
            return self._rate_cache[cache_key]

        try:
            url = f"{self._sources['exchangerate_api']['url']}/USD"
            response = self._make_request_with_retry(url, 'exchangerate_api')
            data = response.json()

            if data.get('result') == 'success' and 'rates' in data:
                supported = set(data['rates'].keys())
                supported.add('USD')  # Add USD itself (base currency)
                logger.info(f"ExchangeRate-API supports {len(supported)} currencies")

                self._rate_cache[cache_key] = supported
                return supported
            else:
                logger.warning("ExchangeRate-API response format unexpected")
                return set()

        except Exception as e:
            logger.warning(f"Failed to get ExchangeRate-API supported currencies: {e}")
            # Fallback to major currencies
            fallback = {'USD', 'EUR', 'GBP', 'JPY', 'CHF', 'CAD', 'AUD', 'RUB'}
            self._rate_cache[cache_key] = fallback
            return fallback

    def _exchangerate_supports_pair(self, base: str, quote: str) -> bool:
        """Check if ExchangeRate-API supports the currency pair."""
        supported_currencies = self._get_exchangerate_supported_currencies()
        return base.upper() in supported_currencies and quote.upper() in supported_currencies

    def _fetch_from_exchangerate_api(self, base: str, quote: str) -> Rate:
        """Fetch rate from ExchangeRate-API."""
        url = f"{self._sources['exchangerate_api']['url']}/{base.upper()}"
        response = self._make_request_with_retry(url, 'exchangerate_api')
        data = response.json()

        if data.get('result') != 'success':
            raise RateFetchError(f"ExchangeRate-API error: {data.get('error-type', 'Unknown error')}")

        rates = data.get('rates', {})
        if quote.upper() not in rates:
            raise RateFetchError(f"ExchangeRate-API doesn't have {quote} rate")

        return Rate(
            source="exchangerate_api",
            base_currency=base.upper(),
            quote_currency=quote.upper(),
            rate=float(rates[quote.upper()]),
            timestamp=datetime.now()
        )

    # ============================================================================
    # CBR API (Russian Central Bank)
    # ============================================================================

    def _get_cbr_supported_currencies(self) -> Set[str]:
        """Get list of supported currencies from CBR API with caching."""
        cache_key = "cbr_supported_currencies"

        if cache_key in self._rate_cache:
            return self._rate_cache[cache_key]

        try:
            url = self._sources['cbr']['url']
            response = self._make_request_with_retry(url, 'cbr')
            data = response.json()

            if 'Valute' in data:
                supported = set(data['Valute'].keys())
                supported.add('RUB')  # Add RUB itself
                logger.info(f"CBR API supports {len(supported)} currencies")

                self._rate_cache[cache_key] = supported
                return supported
            else:
                logger.warning("CBR API response format unexpected")
                return set()

        except Exception as e:
            logger.warning(f"Failed to get CBR supported currencies: {e}")
            # Fallback to major currencies that CBR typically supports
            fallback = {'RUB', 'USD', 'EUR', 'GBP', 'JPY', 'CHF', 'CNY'}
            self._rate_cache[cache_key] = fallback
            return fallback

    def _cbr_supports_pair(self, base: str, quote: str) -> bool:
        """CBR supports conversions to/from RUB."""
        if 'RUB' not in [base.upper(), quote.upper()]:
            return False

        supported_currencies = self._get_cbr_supported_currencies()
        return base.upper() in supported_currencies and quote.upper() in supported_currencies

    def _fetch_from_cbr(self, base: str, quote: str) -> Rate:
        """Fetch rate from CBR API (Russian Central Bank)."""
        url = self._sources['cbr']['url']
        response = self._make_request_with_retry(url, 'cbr')
        data = response.json()

        base, quote = base.upper(), quote.upper()

        if base == 'RUB' and quote in data.get('Valute', {}):
            # RUB to other currency
            currency_data = data['Valute'][quote]
            rate_value = 1.0 / (currency_data['Value'] / currency_data['Nominal'])
        elif quote == 'RUB' and base in data.get('Valute', {}):
            # Other currency to RUB
            currency_data = data['Valute'][base]
            rate_value = currency_data['Value'] / currency_data['Nominal']
        else:
            raise RateFetchError(f"CBR doesn't support {base}/{quote}")

        return Rate(
            source="cbr",
            base_currency=base,
            quote_currency=quote,
            rate=rate_value,
            timestamp=datetime.now()
        )

    # ============================================================================
    # MAIN API METHODS
    # ============================================================================

    def fetch_rate(self, base: str, quote: str) -> Rate:
        """
        Fetch exchange rate using hybrid approach with priority fallback.
        
        Tries sources in priority order:
        1. Fawaz Currency API (200+ currencies, unlimited, CDN-fast)
        2. Prebid Currency API (major fiat currencies, CDN-fast)
        3. Frankfurter (reliable, free, no limits)
        4. ExchangeRate-API (good fallback)
        5. CBR (best for RUB pairs)
        """
        base, quote = base.upper(), quote.upper()
        cache_key = f"{base}_{quote}"

        # Check cache first
        if cache_key in self._rate_cache:
            logger.debug(f"Retrieved rate {base}/{quote} from cache")
            return self._rate_cache[cache_key]

        # Try sources in priority order
        sources_to_try = []
        for source_name, config in self._sources.items():
            if config['supports_check'](base, quote):
                sources_to_try.append((config['priority'], source_name))

        sources_to_try.sort(key=lambda x: x[0])  # Sort by priority

        last_error = None
        for priority, source_name in sources_to_try:
            try:
                logger.debug(f"Trying {source_name} for {base}/{quote}")

                config = self._sources[source_name]
                rate = config['fetch_method'](base, quote)

                # Cache successful result
                self._rate_cache[cache_key] = rate
                logger.info(f"Fetched {base}/{quote} = {rate.rate} from {source_name}")
                return rate

            except Exception as e:
                logger.warning(f"{source_name} failed for {base}/{quote}: {e}")
                last_error = e
                continue

        raise RateFetchError(f"All sources failed for {base}/{quote}. Last error: {last_error}")

    def supports_pair(self, base: str, quote: str) -> bool:
        """Check if any source supports the currency pair."""
        base, quote = base.upper(), quote.upper()
        return any(
            config['supports_check'](base, quote)
            for config in self._sources.values()
        )

    def get_all_supported_currencies(self) -> Dict[str, str]:
        """Get all supported currencies across all sources dynamically."""
        cache_key = "all_supported_currencies"

        # Check cache first
        if cache_key in self._rate_cache:
            return self._rate_cache[cache_key]

        # Collect all currencies from all sources
        all_currencies = set()
        for source_name, config in self._sources.items():
            try:
                supported = config['get_supported']()
                all_currencies.update(supported)
                logger.debug(f"Added {len(supported)} currencies from {source_name}")
            except Exception as e:
                logger.warning(f"Failed to get supported currencies from {source_name}: {e}")

        # Currency names mapping
        currency_names = {
            # Major Fiat
            'USD': 'US Dollar', 'EUR': 'Euro', 'GBP': 'British Pound',
            'JPY': 'Japanese Yen', 'CHF': 'Swiss Franc', 'CAD': 'Canadian Dollar',
            'AUD': 'Australian Dollar', 'NZD': 'New Zealand Dollar',
            'SEK': 'Swedish Krona', 'NOK': 'Norwegian Krone', 'DKK': 'Danish Krone',
            'PLN': 'Polish Zloty', 'CZK': 'Czech Koruna', 'HUF': 'Hungarian Forint',
            'RUB': 'Russian Ruble', 'CNY': 'Chinese Yuan', 'INR': 'Indian Rupee',
            'KRW': 'South Korean Won', 'SGD': 'Singapore Dollar', 'HKD': 'Hong Kong Dollar',
            'THB': 'Thai Baht', 'MXN': 'Mexican Peso', 'BRL': 'Brazilian Real',
            'ZAR': 'South African Rand', 'TRY': 'Turkish Lira', 'ILS': 'Israeli Shekel',

            # Cryptocurrencies
            'BTC': 'Bitcoin', 'ETH': 'Ethereum', 'BNB': 'Binance Coin',
            'XRP': 'Ripple', 'ADA': 'Cardano', 'SOL': 'Solana',
            'DOT': 'Polkadot', 'MATIC': 'Polygon', 'LTC': 'Litecoin',
            'BCH': 'Bitcoin Cash', 'LINK': 'Chainlink', 'UNI': 'Uniswap',
            'ATOM': 'Cosmos', 'XLM': 'Stellar', 'VET': 'VeChain',
            'USDT': 'Tether USD', 'USDC': 'USD Coin', 'DAI': 'Dai Stablecoin',

            # Precious Metals
            'XAU': 'Gold Ounce', 'XAG': 'Silver Ounce',
            'XPT': 'Platinum Ounce', 'XPD': 'Palladium Ounce'
        }

        # Create result with proper names
        result = {}
        for currency in sorted(all_currencies):
            currency_upper = currency.upper()
            # Test if currency actually works with USD (basic validation)
            if self.supports_pair(currency_upper, 'USD'):
                result[currency_upper] = currency_names.get(currency_upper, f"{currency_upper} Currency")

        # Cache the result
        self._rate_cache[cache_key] = result
        logger.info(f"Collected {len(result)} supported currencies from all sources")

        return result
