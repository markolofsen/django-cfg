"""
Currency Cache Management for django_currency.

Handles file-based and memory caching of currency rates with TTL support.
Uses YAML format for better readability and human-friendly configuration.
"""

import logging
import yaml
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional, Any
from cachetools import TTLCache

logger = logging.getLogger(__name__)


class CurrencyCache:
    """
    Currency cache manager with file and memory caching.
    
    Features:
    - TTL-based memory cache (24 hours default)
    - File-based persistent cache
    - Automatic cache invalidation
    - Thread-safe operations
    """
    
    DEFAULT_TTL = 86400  # 24 hours in seconds
    DEFAULT_CACHE_SIZE = 1000
    CACHE_FILENAME = "currency_rates.yaml"
    
    def __init__(
        self, 
        cache_dir: Optional[Path] = None,
        ttl: int = DEFAULT_TTL,
        max_size: int = DEFAULT_CACHE_SIZE
    ):
        """
        Initialize currency cache.
        
        Args:
            cache_dir: Directory for file cache
            ttl: Time-to-live for memory cache in seconds
            max_size: Maximum number of items in memory cache
        """
        # Default cache directory inside django-cfg structure
        if cache_dir is None:
            def make_cache_dir(cache_dir=Path.cwd()):
                return Path(cache_dir) / ".cache" / "currency"
            default_cache_dir = make_cache_dir()

            try:
                from django.conf import settings
                # Check if Django is configured before accessing settings
                if settings.configured and hasattr(settings, 'BASE_DIR'):
                    default_cache_dir = make_cache_dir(settings.BASE_DIR)
            except (ImportError, Exception):
                pass
        else:
            default_cache_dir = Path(cache_dir)
            
        self.cache_dir = default_cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_file = self.cache_dir / self.CACHE_FILENAME
        
        # TTL Cache for in-memory storage
        self._memory_cache = TTLCache(maxsize=max_size, ttl=ttl)
        
        # File cache metadata
        self._file_cache_data = None
        self._file_cache_timestamp = None
        
        logger.info(f"Currency cache initialized: {self.cache_dir}")
    
    def get_rates(self, source: str = "cbr") -> Optional[Dict[str, float]]:
        """
        Get currency rates from cache.
        
        Args:
            source: Rate source identifier (e.g., 'cbr', 'ecb')
            
        Returns:
            Dictionary of currency rates or None if not cached
        """
        cache_key = f"rates_{source}"
        
        # Try memory cache first
        if cache_key in self._memory_cache:
            logger.debug(f"Retrieved rates from memory cache: {source}")
            return self._memory_cache[cache_key]
        
        # Try file cache
        file_rates = self._load_from_file(source)
        if file_rates:
            # Update memory cache
            self._memory_cache[cache_key] = file_rates
            logger.debug(f"Retrieved rates from file cache: {source}")
            return file_rates
        
        logger.debug(f"No cached rates found for source: {source}")
        return None
    
    def set_rates(
        self, 
        rates: Dict[str, float], 
        source: str = "cbr",
        save_to_file: bool = True
    ) -> bool:
        """
        Store currency rates in cache.
        
        Args:
            rates: Dictionary of currency rates
            source: Rate source identifier
            save_to_file: Whether to persist to file
            
        Returns:
            True if successfully cached, False otherwise
        """
        try:
            cache_key = f"rates_{source}"
            
            # Store in memory cache
            self._memory_cache[cache_key] = rates
            
            # Store in file cache if requested
            if save_to_file:
                self._save_to_file(rates, source)
            
            logger.info(f"Cached {len(rates)} rates for source: {source}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to cache rates for {source}: {e}")
            return False
    
    def _load_from_file(self, source: str) -> Optional[Dict[str, float]]:
        """Load rates from file cache."""
        try:
            if not self.cache_file.exists():
                return None
            
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            # Check if data is for the requested source
            if data.get('source') != source:
                return None
            
            # Check if data is still valid (not expired)
            timestamp_str = data.get('timestamp')
            if timestamp_str:
                timestamp = datetime.fromisoformat(timestamp_str)
                if datetime.now() - timestamp > timedelta(seconds=self.DEFAULT_TTL):
                    logger.debug(f"File cache expired for source: {source}")
                    return None
            
            rates = data.get('rates', {})
            if rates:
                self._file_cache_data = data
                self._file_cache_timestamp = timestamp if timestamp_str else None
                return rates
            
        except Exception as e:
            logger.error(f"Failed to load file cache for {source}: {e}")
        
        return None
    
    def _save_to_file(self, rates: Dict[str, float], source: str) -> bool:
        """Save rates to file cache."""
        try:
            now = datetime.now()
            data = {
                'source': source,
                'timestamp': now.isoformat(),
                'rates': rates,
                'metadata': {
                    'count': len(rates),
                    'cache_version': '1.0',
                    'format': 'YAML',
                    'description': f'Currency rates from {source.upper()} API',
                    'updated_at': now.strftime('%Y-%m-%d %H:%M:%S UTC'),
                    'ttl_hours': self.DEFAULT_TTL // 3600,
                    'next_update': (now + timedelta(seconds=self.DEFAULT_TTL)).strftime('%Y-%m-%d %H:%M:%S UTC')
                }
            }
            
            # Atomic write using temporary file
            temp_file = self.cache_file.with_suffix('.tmp')
            with open(temp_file, 'w', encoding='utf-8') as f:
                # Write header comment
                f.write(f"# Currency Rates Cache - Django CFG\n")
                f.write(f"# Generated: {now.strftime('%Y-%m-%d %H:%M:%S UTC')}\n")
                f.write(f"# Source: {source.upper()} API\n")
                f.write(f"# Rates count: {len(rates)}\n")
                f.write(f"# TTL: {self.DEFAULT_TTL // 3600} hours\n")
                f.write(f"# Auto-generated - do not edit manually\n\n")
                
                yaml.safe_dump(
                    data, 
                    f, 
                    default_flow_style=False,
                    allow_unicode=True,
                    sort_keys=False,
                    indent=2,
                    width=120
                )
            
            # Move temp file to final location
            temp_file.replace(self.cache_file)
            
            self._file_cache_data = data
            self._file_cache_timestamp = datetime.now()
            
            logger.debug(f"Saved {len(rates)} rates to file cache: {source}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save file cache for {source}: {e}")
            return False
    
    def clear_cache(self, source: Optional[str] = None) -> bool:
        """
        Clear cache for specific source or all sources.
        
        Args:
            source: Source to clear (None for all)
            
        Returns:
            True if successfully cleared
        """
        try:
            if source:
                # Clear specific source from memory
                cache_key = f"rates_{source}"
                self._memory_cache.pop(cache_key, None)
                
                # Clear file cache if it matches the source
                if (self._file_cache_data and 
                    self._file_cache_data.get('source') == source):
                    if self.cache_file.exists():
                        self.cache_file.unlink()
                    self._file_cache_data = None
                    self._file_cache_timestamp = None
                
                logger.info(f"Cleared cache for source: {source}")
            else:
                # Clear all caches
                self._memory_cache.clear()
                if self.cache_file.exists():
                    self.cache_file.unlink()
                self._file_cache_data = None
                self._file_cache_timestamp = None
                
                logger.info("Cleared all currency caches")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")
            return False
    
    def get_cache_info(self) -> Dict[str, Any]:
        """Get information about cache status."""
        try:
            memory_info = {
                'size': len(self._memory_cache),
                'max_size': self._memory_cache.maxsize,
                'ttl': self._memory_cache.ttl,
                'keys': list(self._memory_cache.keys())
            }
            
            file_info = {
                'exists': self.cache_file.exists(),
                'path': str(self.cache_file),
                'size_bytes': self.cache_file.stat().st_size if self.cache_file.exists() else 0,
            }
            
            if self._file_cache_data:
                file_info.update({
                    'source': self._file_cache_data.get('source'),
                    'timestamp': self._file_cache_data.get('timestamp'),
                    'rates_count': len(self._file_cache_data.get('rates', {}))
                })
            
            return {
                'cache_directory': str(self.cache_dir),
                'memory_cache': memory_info,
                'file_cache': file_info,
                'status': 'active'
            }
            
        except Exception as e:
            logger.error(f"Failed to get cache info: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def is_cache_valid(self, source: str = "cbr") -> bool:
        """Check if cache is valid and not expired."""
        cache_key = f"rates_{source}"
        
        # Check memory cache
        if cache_key in self._memory_cache:
            return True
        
        # Check file cache
        if self._file_cache_timestamp:
            age = datetime.now() - self._file_cache_timestamp
            return age.total_seconds() < self.DEFAULT_TTL
        
        return False
    
    def get_cache_age(self, source: str = "cbr") -> Optional[timedelta]:
        """Get age of cached data."""
        if self._file_cache_timestamp:
            return datetime.now() - self._file_cache_timestamp
        return None
    
    def _get_currency_description(self, currency_code: str) -> str:
        """Get human-readable description for currency code."""
        currency_names = {
            'USD': 'US Dollar',
            'EUR': 'Euro',
            'GBP': 'British Pound',
            'JPY': 'Japanese Yen',
            'CNY': 'Chinese Yuan',
            'KRW': 'South Korean Won',
            'RUB': 'Russian Ruble',
            'CAD': 'Canadian Dollar',
            'AUD': 'Australian Dollar',
            'CHF': 'Swiss Franc',
            'SEK': 'Swedish Krona',
            'NOK': 'Norwegian Krone',
            'DKK': 'Danish Krone',
            'PLN': 'Polish Zloty',
            'CZK': 'Czech Koruna',
            'HUF': 'Hungarian Forint',
            'TRY': 'Turkish Lira',
            'BRL': 'Brazilian Real',
            'MXN': 'Mexican Peso',
            'INR': 'Indian Rupee',
            'SGD': 'Singapore Dollar',
            'HKD': 'Hong Kong Dollar',
            'NZD': 'New Zealand Dollar',
            'ZAR': 'South African Rand',
            'THB': 'Thai Baht',
            'MYR': 'Malaysian Ringgit',
            'PHP': 'Philippine Peso',
            'IDR': 'Indonesian Rupiah',
            'VND': 'Vietnamese Dong',
        }
        return currency_names.get(currency_code, currency_code)
    
    def export_rates_yaml(self, source: str = "cbr", output_file: Optional[Path] = None) -> str:
        """
        Export rates to a formatted YAML file with comments.
        
        Args:
            source: Rate source to export
            output_file: Optional output file path
            
        Returns:
            YAML content as string
        """
        rates = self.get_rates(source)
        if not rates:
            return "# No rates available for export"
        
        now = datetime.now()
        
        # Create structured data with comments
        yaml_content = f"""# Currency Exchange Rates - Django CFG
# Source: {source.upper()} API
# Generated: {now.strftime('%Y-%m-%d %H:%M:%S UTC')}
# Total currencies: {len(rates)}
# Cache TTL: {self.DEFAULT_TTL // 3600} hours
# 
# Format: currency_code: rate_to_base_currency
# Base currency for CBR: RUB (Russian Ruble)
# Base currency for ECB: EUR (Euro)

source: {source}
timestamp: {now.isoformat()}

metadata:
  count: {len(rates)}
  cache_version: '1.0'
  format: 'YAML'
  description: 'Currency rates from {source.upper()} API'
  updated_at: '{now.strftime('%Y-%m-%d %H:%M:%S UTC')}'
  ttl_hours: {self.DEFAULT_TTL // 3600}
  next_update: '{(now + timedelta(seconds=self.DEFAULT_TTL)).strftime('%Y-%m-%d %H:%M:%S UTC')}'

# Currency Rates
rates:
"""
        
        # Sort currencies: major currencies first, then alphabetically
        major_currencies = ['USD', 'EUR', 'GBP', 'JPY', 'CNY', 'KRW', 'RUB', 'CAD', 'AUD', 'CHF']
        sorted_currencies = []
        
        # Add major currencies first (if they exist)
        for curr in major_currencies:
            if curr in rates:
                sorted_currencies.append(curr)
        
        # Add remaining currencies alphabetically
        remaining = sorted([curr for curr in rates.keys() if curr not in major_currencies])
        sorted_currencies.extend(remaining)
        
        # Add rates with comments
        for currency in sorted_currencies:
            rate = rates[currency]
            description = self._get_currency_description(currency)
            yaml_content += f"  {currency}: {rate:<12.6f}  # {description}\n"
        
        # Save to file if requested
        if output_file:
            try:
                output_file.parent.mkdir(parents=True, exist_ok=True)
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(yaml_content)
                logger.info(f"Exported rates to: {output_file}")
            except Exception as e:
                logger.error(f"Failed to export rates to file: {e}")
        
        return yaml_content
