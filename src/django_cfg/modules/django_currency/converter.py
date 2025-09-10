"""
Currency Converter for django_currency.

Handles actual currency conversion using multiple data sources with fallback support.
"""

import logging
import requests
from datetime import datetime, date
from typing import Dict, Optional, Union, Any
from pathlib import Path

from .cache import CurrencyCache

logger = logging.getLogger(__name__)


class CurrencyConverter:
    """
    Currency converter with multiple data sources and caching.
    
    Data sources (in priority order):
    1. Central Bank of Russia (CBR) API - for RUB-based conversions
    2. European Central Bank (ECB) API - for EUR-based conversions  
    3. currency_converter library - fallback for other conversions
    """
    
    # API endpoints
    CBR_API_URL = "https://www.cbr-xml-daily.ru/daily_json.js"
    ECB_API_URL = "https://api.exchangerate-api.com/v4/latest/EUR"
    
    def __init__(self, cache_dir: Optional[Path] = None):
        """
        Initialize currency converter.
        
        Args:
            cache_dir: Optional cache directory path
        """
        self.cache = CurrencyCache(cache_dir=cache_dir)
        self._fallback_converter = None
        self._cbr_rates = {}
        self._ecb_rates = {}
        
        # Initialize fallback converter
        self._init_fallback_converter()
    
    def _init_fallback_converter(self):
        """Initialize fallback currency converter."""
        try:
            from currency_converter import CurrencyConverter as FallbackConverter
            self._fallback_converter = FallbackConverter(
                fallback_on_wrong_date=True,
                fallback_on_missing_rate=True
            )
            # Test the converter
            _ = self._fallback_converter.convert(1, 'USD', 'EUR')
            logger.info("Fallback currency converter initialized")
        except ImportError:
            logger.warning("currency_converter library not available - install with: pip install CurrencyConverter")
            self._fallback_converter = None
        except Exception as e:
            logger.error(f"Failed to initialize fallback converter: {e}")
            self._fallback_converter = None
    
    def convert(
        self,
        amount: float,
        from_currency: str,
        to_currency: str,
        date_obj: Optional[Union[datetime, date]] = None,
        round_to: Optional[int] = 2,
    ) -> float:
        """
        Convert amount from one currency to another.
        
        Args:
            amount: Amount to convert
            from_currency: Source currency code
            to_currency: Target currency code
            date_obj: Optional date for historical rates
            round_to: Number of decimal places to round to
            
        Returns:
            Converted amount
        """
        from_curr = from_currency.upper()
        to_curr = to_currency.upper()
        
        # Same currency - no conversion needed
        if from_curr == to_curr:
            return float(amount)
        
        result = 0.0
        conversion_successful = False
        
        # Try CBR rates first (best for RUB conversions)
        if not conversion_successful:
            try:
                result = self._convert_via_cbr(amount, from_curr, to_curr)
                if result > 0:
                    conversion_successful = True
                    logger.debug(f"Converted via CBR: {amount} {from_curr} = {result} {to_curr}")
            except Exception as e:
                logger.debug(f"CBR conversion failed: {e}")
        
        # Try ECB rates (good for EUR conversions)
        if not conversion_successful:
            try:
                result = self._convert_via_ecb(amount, from_curr, to_curr)
                if result > 0:
                    conversion_successful = True
                    logger.debug(f"Converted via ECB: {amount} {from_curr} = {result} {to_curr}")
            except Exception as e:
                logger.debug(f"ECB conversion failed: {e}")
        
        # Fallback to currency_converter library
        if not conversion_successful and self._fallback_converter:
            try:
                fallback_date = date_obj.date() if isinstance(date_obj, datetime) else date_obj
                result = float(self._fallback_converter.convert(
                    amount, from_curr, to_curr, date=fallback_date
                ))
                conversion_successful = True
                logger.debug(f"Converted via fallback: {amount} {from_curr} = {result} {to_curr}")
            except Exception as e:
                logger.debug(f"Fallback conversion failed: {e}")
        
        if not conversion_successful:
            raise ValueError(f"Unable to convert {from_curr} to {to_curr}")
        
        # Apply rounding
        if round_to is not None:
            result = round(result, round_to)
        
        return result
    
    def _convert_via_cbr(self, amount: float, from_curr: str, to_curr: str) -> float:
        """Convert using CBR (Central Bank of Russia) rates."""
        # Get CBR rates
        cbr_rates = self._get_cbr_rates()
        if not cbr_rates:
            raise ValueError("CBR rates not available")
        
        # Check if both currencies are available
        if from_curr not in cbr_rates or to_curr not in cbr_rates:
            raise ValueError(f"Currency pair {from_curr}/{to_curr} not available in CBR rates")
        
        # Convert via RUB
        from_rate = cbr_rates[from_curr]  # How many RUB for 1 unit of from_curr
        to_rate = cbr_rates[to_curr]      # How many RUB for 1 unit of to_curr
        
        # amount * from_rate = RUB amount
        # RUB amount / to_rate = to_curr amount
        result = amount * (from_rate / to_rate)
        return result
    
    def _convert_via_ecb(self, amount: float, from_curr: str, to_curr: str) -> float:
        """Convert using ECB (European Central Bank) rates."""
        # Get ECB rates
        ecb_rates = self._get_ecb_rates()
        if not ecb_rates:
            raise ValueError("ECB rates not available")
        
        # ECB rates are EUR-based
        if from_curr == 'EUR':
            if to_curr not in ecb_rates:
                raise ValueError(f"Currency {to_curr} not available in ECB rates")
            return amount * ecb_rates[to_curr]
        
        elif to_curr == 'EUR':
            if from_curr not in ecb_rates:
                raise ValueError(f"Currency {from_curr} not available in ECB rates")
            return amount / ecb_rates[from_curr]
        
        else:
            # Convert via EUR
            if from_curr not in ecb_rates or to_curr not in ecb_rates:
                raise ValueError(f"Currency pair {from_curr}/{to_curr} not available in ECB rates")
            
            # Convert to EUR first, then to target currency
            eur_amount = amount / ecb_rates[from_curr]
            result = eur_amount * ecb_rates[to_curr]
            return result
    
    def _get_cbr_rates(self) -> Dict[str, float]:
        """Get CBR rates from cache or API."""
        # Try cache first
        cached_rates = self.cache.get_rates("cbr")
        if cached_rates:
            self._cbr_rates = cached_rates
            return cached_rates
        
        # Fetch from API
        try:
            response = requests.get(self.CBR_API_URL, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            valutes = data.get("Valute", {})
            rates = {}
            
            # Add RUB as base currency
            rates["RUB"] = 1.0
            
            # Process other currencies
            for currency_code, item in valutes.items():
                if "Value" in item and "Nominal" in item:
                    # CBR gives rate as: Nominal units of currency = Value RUB
                    # We want: 1 unit of currency = X RUB
                    rate = float(item["Value"]) / float(item["Nominal"])
                    rates[currency_code] = rate
            
            # Cache the rates
            self.cache.set_rates(rates, "cbr")
            self._cbr_rates = rates
            
            logger.info(f"Fetched {len(rates)} CBR rates")
            return rates
            
        except Exception as e:
            logger.error(f"Failed to fetch CBR rates: {e}")
            return {}
    
    def _get_ecb_rates(self) -> Dict[str, float]:
        """Get ECB rates from cache or API."""
        # Try cache first
        cached_rates = self.cache.get_rates("ecb")
        if cached_rates:
            self._ecb_rates = cached_rates
            return cached_rates
        
        # Fetch from API
        try:
            response = requests.get(self.ECB_API_URL, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            rates = data.get("rates", {})
            if rates:
                # Add EUR as base currency
                rates["EUR"] = 1.0
                
                # Cache the rates
                self.cache.set_rates(rates, "ecb")
                self._ecb_rates = rates
                
                logger.info(f"Fetched {len(rates)} ECB rates")
                return rates
            
        except Exception as e:
            logger.error(f"Failed to fetch ECB rates: {e}")
        
        return {}
    
    def get_available_currencies(self) -> set:
        """Get set of all available currency codes."""
        currencies = set()
        
        # Add CBR currencies
        cbr_rates = self._get_cbr_rates()
        currencies.update(cbr_rates.keys())
        
        # Add ECB currencies
        ecb_rates = self._get_ecb_rates()
        currencies.update(ecb_rates.keys())
        
        # Add fallback currencies
        if self._fallback_converter:
            try:
                currencies.update(self._fallback_converter.currencies)
            except Exception as e:
                logger.error(f"Failed to get fallback currencies: {e}")
        
        return currencies
    
    def refresh_rates(self) -> bool:
        """Force refresh all currency rates."""
        success = True
        
        # Clear cache
        self.cache.clear_cache()
        
        # Refresh CBR rates
        try:
            cbr_rates = self._get_cbr_rates()
            if not cbr_rates:
                success = False
        except Exception as e:
            logger.error(f"Failed to refresh CBR rates: {e}")
            success = False
        
        # Refresh ECB rates
        try:
            ecb_rates = self._get_ecb_rates()
            if not ecb_rates:
                success = False
        except Exception as e:
            logger.error(f"Failed to refresh ECB rates: {e}")
            success = False
        
        logger.info(f"Currency rates refresh {'successful' if success else 'failed'}")
        return success
    
    def get_converter_info(self) -> Dict[str, Any]:
        """Get information about converter status."""
        return {
            "cbr_rates_count": len(self._cbr_rates),
            "ecb_rates_count": len(self._ecb_rates),
            "fallback_available": self._fallback_converter is not None,
            "total_currencies": len(self.get_available_currencies()),
            "data_sources": {
                "cbr": {
                    "url": self.CBR_API_URL,
                    "available": len(self._cbr_rates) > 0
                },
                "ecb": {
                    "url": self.ECB_API_URL,
                    "available": len(self._ecb_rates) > 0
                },
                "fallback": {
                    "available": self._fallback_converter is not None
                }
            }
        }
