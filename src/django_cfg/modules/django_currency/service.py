"""
Django Currency Service for django_cfg.

Auto-configuring currency conversion service that integrates with DjangoConfig.
"""

import logging
from typing import Optional, Dict, Any, Union, List
from datetime import datetime, date
from pathlib import Path

from django_cfg.modules import BaseModule
from .converter import CurrencyConverter
from .cache import CurrencyCache

logger = logging.getLogger(__name__)


class CurrencyError(Exception):
    """Base exception for currency-related errors."""
    pass


class CurrencyConfigError(CurrencyError):
    """Raised when configuration is missing or invalid."""
    pass


class CurrencyConversionError(CurrencyError):
    """Raised when currency conversion fails."""
    pass


class DjangoCurrency(BaseModule):
    """
    Currency Service for django_cfg, configured via DjangoConfig.

    Provides currency conversion functionality with automatic configuration
    from the main DjangoConfig instance.
    """

    def __init__(self):
        self._converter = None
        self._is_configured = None

    @property
    def config(self):
        """Get the DjangoConfig instance."""
        return self.get_config()

    @property
    def is_configured(self) -> bool:
        """Check if currency service is properly configured."""
        if self._is_configured is None:
            try:
                # Currency service is always available with fallback
                self._is_configured = True
            except Exception:
                self._is_configured = False

        return self._is_configured

    @property
    def converter(self) -> CurrencyConverter:
        """Get currency converter instance."""
        if self._converter is None:
            # Let CurrencyConverter handle its own cache
            cache_dir = None
            try:
                # Only override if explicitly configured
                if hasattr(self.config, 'currency_cache_dir'):
                    cache_dir = Path(self.config.currency_cache_dir)
            except Exception:
                pass
            
            self._converter = CurrencyConverter(cache_dir=cache_dir)
        return self._converter

    @property
    def cache(self) -> CurrencyCache:
        """Get currency cache instance from converter."""
        return self.converter.cache


    def convert(
        self,
        amount: float,
        from_currency: str,
        to_currency: str,
        date_obj: Optional[Union[datetime, date]] = None,
        round_to: Optional[int] = 2,
        fail_silently: bool = False,
    ) -> float:
        """
        Convert amount from one currency to another.

        Args:
            amount: Amount to convert
            from_currency: Source currency code (e.g., 'USD')
            to_currency: Target currency code (e.g., 'EUR')
            date_obj: Optional date for historical rates
            round_to: Number of decimal places to round to
            fail_silently: Don't raise exceptions on failure

        Returns:
            Converted amount

        Raises:
            CurrencyConversionError: If conversion fails and fail_silently is False
        """
        try:
            if not self.is_configured:
                error_msg = "Currency service is not configured"
                logger.error(error_msg)
                if not fail_silently:
                    raise CurrencyConfigError(error_msg)
                return 0.0

            result = self.converter.convert(
                amount=amount,
                from_currency=from_currency,
                to_currency=to_currency,
                date_obj=date_obj,
                round_to=round_to
            )

            logger.debug(f"Converted {amount} {from_currency} to {result} {to_currency}")
            return result

        except Exception as e:
            error_msg = f"Failed to convert {amount} {from_currency} to {to_currency}: {e}"
            logger.error(error_msg)
            if not fail_silently:
                raise CurrencyConversionError(error_msg) from e
            return 0.0

    def get_rate(
        self,
        from_currency: str,
        to_currency: str,
        date_obj: Optional[Union[datetime, date]] = None,
        fail_silently: bool = False,
    ) -> float:
        """
        Get exchange rate between two currencies.

        Args:
            from_currency: Source currency code
            to_currency: Target currency code
            date_obj: Optional date for historical rates
            fail_silently: Don't raise exceptions on failure

        Returns:
            Exchange rate (1 unit of from_currency = X units of to_currency)
        """
        return self.convert(
            amount=1.0,
            from_currency=from_currency,
            to_currency=to_currency,
            date_obj=date_obj,
            fail_silently=fail_silently
        )

    def get_available_currencies(self) -> set:
        """
        Get set of available currency codes.

        Returns:
            Set of available currency codes
        """
        try:
            return self.converter.get_available_currencies()
        except Exception as e:
            logger.error(f"Failed to get available currencies: {e}")
            return set()

    def refresh_rates(self, fail_silently: bool = False) -> bool:
        """
        Force refresh currency rates from external APIs.

        Args:
            fail_silently: Don't raise exceptions on failure

        Returns:
            True if refresh was successful, False otherwise
        """
        try:
            success = self.converter.refresh_rates()
            if success:
                logger.info("Currency rates refreshed successfully")
            else:
                logger.warning("Failed to refresh currency rates")
            return success

        except Exception as e:
            error_msg = f"Failed to refresh currency rates: {e}"
            logger.error(error_msg)
            if not fail_silently:
                raise CurrencyError(error_msg) from e
            return False

    def get_config_info(self) -> Dict[str, Any]:
        """Get currency service configuration information."""
        try:
            cache_info = self.cache.get_cache_info()
            converter_info = self.converter.get_converter_info()
            
            return {
                "configured": self.is_configured,
                "cache_directory": str(self.cache.cache_dir),
                "cache_info": cache_info,
                "converter_info": converter_info,
                "available_currencies_count": len(self.get_available_currencies()),
            }
        except Exception as e:
            logger.error(f"Failed to get config info: {e}")
            return {
                "configured": False,
                "error": str(e)
            }

    def convert_multiple(
        self,
        amounts: List[float],
        from_currencies: List[str],
        to_currencies: List[str],
        fail_silently: bool = True,
    ) -> List[float]:
        """
        Convert multiple currency amounts in batch.

        Args:
            amounts: List of amounts to convert
            from_currencies: List of source currency codes
            to_currencies: List of target currency codes
            fail_silently: Don't raise exceptions on individual failures

        Returns:
            List of converted amounts (0.0 for failed conversions)
        """
        if not (len(amounts) == len(from_currencies) == len(to_currencies)):
            raise ValueError("All input lists must have the same length")

        results = []
        for amount, from_curr, to_curr in zip(amounts, from_currencies, to_currencies):
            try:
                result = self.convert(
                    amount=amount,
                    from_currency=from_curr,
                    to_currency=to_curr,
                    fail_silently=fail_silently
                )
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to convert {amount} {from_curr} to {to_curr}: {e}")
                results.append(0.0)

        return results

    @classmethod
    def send_currency_alert(cls, message: str, rates: Optional[Dict[str, float]] = None) -> None:
        """Send currency alert via configured notification services."""
        try:
            # Try to send via Telegram if available
            from django_cfg.modules.django_telegram import DjangoTelegram
            telegram = DjangoTelegram()
            
            text = f"💱 <b>Currency Alert</b>\n\n{message}"
            if rates:
                text += "\n\n<b>Current Rates:</b>\n"
                for pair, rate in rates.items():
                    text += f"• {pair}: {rate:.4f}\n"
            
            telegram.send_message(text, parse_mode="HTML", fail_silently=True)
            
        except Exception as e:
            logger.error(f"Failed to send currency alert: {e}")
