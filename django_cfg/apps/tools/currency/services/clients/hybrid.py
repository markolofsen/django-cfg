"""
Hybrid Currency Client - Multi-source fiat rate fetcher.

Sources (priority order):
1. Fawaz Currency API (200+ currencies via CDN)
2. Frankfurter API (EUR-based fiat)
3. ExchangeRate-API (USD-based)
4. CBR API (RUB rates)
"""

import logging
import random
import time
from datetime import datetime
from typing import Dict, Set

import requests

from ..exceptions import RateFetchError
from ..schemas import Rate

logger = logging.getLogger(__name__)


class HybridCurrencyClient:
    """Multi-source fiat currency client with fallback."""

    def __init__(self):
        """Initialize with multiple data sources."""
        self._session = requests.Session()

        self._user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "curl/7.68.0",
            "python-requests/2.31.0"
        ]

        self._sources = {
            "fawaz_currency": {
                "url": "https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies",
                "priority": 1,
                "rate_limit": 0.5,
            },
            "frankfurter": {
                "url": "https://api.frankfurter.app/latest",
                "priority": 2,
                "rate_limit": 1.0,
            },
            "exchangerate_api": {
                "url": "https://open.er-api.com/v6/latest",
                "priority": 3,
                "rate_limit": 1.5,
            },
            "cbr": {
                "url": "https://www.cbr-xml-daily.ru/daily_json.js",
                "priority": 4,
                "rate_limit": 1.0,
            }
        }

        self._last_request_times: Dict[str, float] = {}
        self._max_retries = 2

    def _get_random_user_agent(self) -> str:
        return random.choice(self._user_agents)

    def _make_request(self, url: str, source: str) -> requests.Response:
        """Make HTTP request with rate limiting and retry."""
        config = self._sources[source]
        rate_limit = config["rate_limit"]

        # Rate limiting
        last_request = self._last_request_times.get(source, 0)
        time_since = time.time() - last_request
        if time_since < rate_limit:
            time.sleep(rate_limit - time_since + random.uniform(0, 0.3))

        for attempt in range(self._max_retries + 1):
            try:
                headers = {
                    "User-Agent": self._get_random_user_agent(),
                    "Accept": "application/json",
                }
                response = self._session.get(url, headers=headers, timeout=10)
                self._last_request_times[source] = time.time()

                if response.status_code == 429:
                    if attempt < self._max_retries:
                        backoff = (2 ** attempt) * 3 + random.uniform(1, 2)
                        logger.warning(f"{source}: Rate limited, retry in {backoff:.1f}s")
                        time.sleep(backoff)
                        continue
                    raise RateFetchError(f"429 Too Many Requests from {source}")

                response.raise_for_status()
                return response

            except requests.exceptions.RequestException as e:
                if attempt < self._max_retries:
                    backoff = (2 ** attempt) * 2 + random.uniform(0.5, 1)
                    logger.warning(f"{source}: Failed, retry in {backoff:.1f}s - {e}")
                    time.sleep(backoff)
                    continue
                raise RateFetchError(f"{source} request failed: {e}")

        raise RateFetchError(f"{source}: Failed after {self._max_retries + 1} attempts")

    # ========== FAWAZ CURRENCY API ==========

    def _fetch_from_fawaz(self, base: str, quote: str) -> Rate:
        base_lower = base.lower()
        url = f"{self._sources['fawaz_currency']['url']}/{base_lower}.json"
        response = self._make_request(url, "fawaz_currency")
        data = response.json()

        if base_lower not in data:
            raise RateFetchError(f"Fawaz: no base currency {base}")

        rates = data[base_lower]
        quote_lower = quote.lower()

        if quote_lower not in rates:
            raise RateFetchError(f"Fawaz: no rate for {base}/{quote}")

        return Rate(
            source="fawaz_currency",
            base_currency=base.upper(),
            quote_currency=quote.upper(),
            rate=float(rates[quote_lower]),
            timestamp=datetime.now()
        )

    # ========== FRANKFURTER API ==========

    def _fetch_from_frankfurter(self, base: str, quote: str) -> Rate:
        url = f"{self._sources['frankfurter']['url']}?from={base}&to={quote}"
        response = self._make_request(url, "frankfurter")
        data = response.json()

        if "rates" not in data or quote.upper() not in data["rates"]:
            raise RateFetchError(f"Frankfurter: no rate for {base}/{quote}")

        return Rate(
            source="frankfurter",
            base_currency=base.upper(),
            quote_currency=quote.upper(),
            rate=float(data["rates"][quote.upper()]),
            timestamp=datetime.now()
        )

    # ========== EXCHANGERATE API ==========

    def _fetch_from_exchangerate(self, base: str, quote: str) -> Rate:
        url = f"{self._sources['exchangerate_api']['url']}/{base.upper()}"
        response = self._make_request(url, "exchangerate_api")
        data = response.json()

        if data.get("result") != "success":
            raise RateFetchError(f"ExchangeRate-API error: {data.get('error-type')}")

        rates = data.get("rates", {})
        if quote.upper() not in rates:
            raise RateFetchError(f"ExchangeRate-API: no rate for {quote}")

        return Rate(
            source="exchangerate_api",
            base_currency=base.upper(),
            quote_currency=quote.upper(),
            rate=float(rates[quote.upper()]),
            timestamp=datetime.now()
        )

    # ========== CBR API (Russian Central Bank) ==========

    def _fetch_from_cbr(self, base: str, quote: str) -> Rate:
        url = self._sources["cbr"]["url"]
        response = self._make_request(url, "cbr")
        data = response.json()

        base, quote = base.upper(), quote.upper()

        if base == "RUB" and quote in data.get("Valute", {}):
            currency_data = data["Valute"][quote]
            rate_value = 1.0 / (currency_data["Value"] / currency_data["Nominal"])
        elif quote == "RUB" and base in data.get("Valute", {}):
            currency_data = data["Valute"][base]
            rate_value = currency_data["Value"] / currency_data["Nominal"]
        else:
            raise RateFetchError(f"CBR: doesn't support {base}/{quote}")

        return Rate(
            source="cbr",
            base_currency=base,
            quote_currency=quote,
            rate=rate_value,
            timestamp=datetime.now()
        )

    # ========== MAIN API ==========

    def fetch_rate(self, base: str, quote: str) -> Rate:
        """
        Fetch rate using priority fallback.

        Tries sources in order until one succeeds.
        """
        base, quote = base.upper(), quote.upper()

        # Try each source in priority order
        sources_order = [
            ("fawaz_currency", self._fetch_from_fawaz),
            ("frankfurter", self._fetch_from_frankfurter),
            ("exchangerate_api", self._fetch_from_exchangerate),
            ("cbr", self._fetch_from_cbr),
        ]

        last_error = None
        for source_name, fetch_method in sources_order:
            try:
                logger.debug(f"Trying {source_name} for {base}/{quote}")
                rate = fetch_method(base, quote)
                logger.info(f"Fetched {base}/{quote} = {rate.rate} from {source_name}")
                return rate
            except Exception as e:
                logger.warning(f"{source_name} failed: {e}")
                last_error = e
                continue

        raise RateFetchError(f"All sources failed for {base}/{quote}: {last_error}")

    def supports_pair(self, base: str, quote: str) -> bool:
        """Check if any source can handle this pair."""
        # Fawaz supports most fiat pairs
        # We assume it can handle common currencies
        common = {"USD", "EUR", "GBP", "JPY", "CHF", "CAD", "AUD", "KRW", "CNY", "RUB"}
        return base.upper() in common or quote.upper() in common

    # ========== BATCH FETCH (ONE REQUEST FOR ALL RATES) ==========

    def fetch_all_rates(self, target_currency: str = "USD") -> Dict[str, Rate]:
        """
        Fetch ALL rates to target currency in ONE request.

        This is much more efficient than fetching individual rates.
        Makes 1 API call instead of N calls.

        Args:
            target_currency: The quote currency (e.g., "USD").
                            All rates will be X→target_currency.

        Returns:
            Dict mapping base currency code to Rate object.
            Example: {"KRW": Rate(KRW→USD), "EUR": Rate(EUR→USD), ...}

        Raises:
            RateFetchError: If all sources fail.
        """
        target = target_currency.upper()

        # Try sources in priority order
        sources = [
            ("fawaz_currency", self._fetch_all_from_fawaz),
            ("exchangerate_api", self._fetch_all_from_exchangerate),
            ("frankfurter", self._fetch_all_from_frankfurter),
        ]

        last_error = None
        for source_name, fetch_method in sources:
            try:
                logger.info(f"Batch fetching all rates to {target} from {source_name}")
                rates = fetch_method(target)
                logger.info(f"Fetched {len(rates)} rates from {source_name}")
                return rates
            except Exception as e:
                logger.warning(f"Batch fetch from {source_name} failed: {e}")
                last_error = e
                continue

        raise RateFetchError(f"All batch sources failed: {last_error}")

    def _fetch_all_from_fawaz(self, target: str) -> Dict[str, Rate]:
        """
        Fetch all rates from Fawaz API in one request.

        Fawaz returns rates FROM base TO all quotes.
        We request target.json and INVERT to get X→target.
        """
        target_lower = target.lower()
        url = f"{self._sources['fawaz_currency']['url']}/{target_lower}.json"
        response = self._make_request(url, "fawaz_currency")
        data = response.json()

        if target_lower not in data:
            raise RateFetchError(f"Fawaz: no data for {target}")

        rates_data = data[target_lower]
        now = datetime.now()
        result = {}

        for currency_code, rate_value in rates_data.items():
            if not isinstance(rate_value, (int, float)) or rate_value <= 0:
                continue

            base = currency_code.upper()
            if base == target:
                continue

            # INVERT: Fawaz gives target→X, we need X→target
            # target→X = rate_value means 1 target = rate_value X
            # X→target = 1/rate_value means 1 X = 1/rate_value target
            inverted_rate = 1.0 / float(rate_value)

            result[base] = Rate(
                source="fawaz_currency",
                base_currency=base,
                quote_currency=target,
                rate=inverted_rate,
                timestamp=now,
            )

        return result

    def _fetch_all_from_exchangerate(self, target: str) -> Dict[str, Rate]:
        """
        Fetch all rates from ExchangeRate-API in one request.
        """
        url = f"{self._sources['exchangerate_api']['url']}/{target.upper()}"
        response = self._make_request(url, "exchangerate_api")
        data = response.json()

        if data.get("result") != "success":
            raise RateFetchError(f"ExchangeRate-API error: {data.get('error-type')}")

        rates_data = data.get("rates", {})
        now = datetime.now()
        result = {}

        for currency_code, rate_value in rates_data.items():
            base = currency_code.upper()
            if base == target.upper():
                continue

            # INVERT: API gives target→X, we need X→target
            inverted_rate = 1.0 / float(rate_value)

            result[base] = Rate(
                source="exchangerate_api",
                base_currency=base,
                quote_currency=target.upper(),
                rate=inverted_rate,
                timestamp=now,
            )

        return result

    def _fetch_all_from_frankfurter(self, target: str) -> Dict[str, Rate]:
        """
        Fetch all rates from Frankfurter API in one request.
        """
        url = f"{self._sources['frankfurter']['url']}?from={target.upper()}"
        response = self._make_request(url, "frankfurter")
        data = response.json()

        if "rates" not in data:
            raise RateFetchError("Frankfurter: no rates in response")

        rates_data = data["rates"]
        now = datetime.now()
        result = {}

        for currency_code, rate_value in rates_data.items():
            base = currency_code.upper()
            if base == target.upper():
                continue

            # INVERT: API gives target→X, we need X→target
            inverted_rate = 1.0 / float(rate_value)

            result[base] = Rate(
                source="frankfurter",
                base_currency=base,
                quote_currency=target.upper(),
                rate=inverted_rate,
                timestamp=now,
            )

        return result
