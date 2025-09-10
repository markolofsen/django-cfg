"""
🧪 Tests for Django Currency Module

Tests the django_currency module functionality including:
- Currency conversion
- YAML caching
- Multiple data sources (CBR, ECB, fallback)
- Error handling
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
from django_cfg.modules.django_currency import DjangoCurrency, convert_currency, get_exchange_rate
from django_cfg.modules.django_currency.cache import CurrencyCache
from django_cfg.modules.django_currency.converter import CurrencyConverter
from django_cfg.modules.django_currency.service import CurrencyError, CurrencyConfigError


class TestCurrencyCache:
    """Test YAML currency cache functionality."""
    
    def test_cache_initialization(self, temp_dir):
        """Test cache initialization with custom directory."""
        cache = CurrencyCache(cache_dir=temp_dir)
        assert cache.cache_dir == temp_dir
        assert cache.cache_file.name == "currency_rates.yaml"
        assert cache.cache_dir.exists()
    
    def test_set_and_get_rates(self, temp_dir):
        """Test storing and retrieving rates from cache."""
        cache = CurrencyCache(cache_dir=temp_dir)
        
        test_rates = {
            'USD': 80.5,
            'EUR': 85.2,
            'GBP': 95.1,
            'JPY': 0.55,
        }
        
        # Store rates
        success = cache.set_rates(test_rates, 'test')
        assert success is True
        
        # Retrieve rates
        retrieved_rates = cache.get_rates('test')
        assert retrieved_rates == test_rates
    
    def test_yaml_file_format(self, temp_dir):
        """Test that cache file is properly formatted YAML."""
        cache = CurrencyCache(cache_dir=temp_dir)
        
        test_rates = {'USD': 80.5, 'EUR': 85.2}
        cache.set_rates(test_rates, 'test')
        
        # Check file exists and is YAML
        assert cache.cache_file.exists()
        
        # Read and verify YAML content
        with open(cache.cache_file, 'r') as f:
            content = f.read()
        
        assert '# Currency Rates Cache - Django CFG' in content
        assert 'source: test' in content
        assert 'USD: 80.5' in content or 'USD: 80.500000' in content
        assert 'format: YAML' in content
    
    def test_cache_expiration(self, temp_dir):
        """Test cache TTL functionality."""
        # Create cache with very short TTL for testing
        cache = CurrencyCache(cache_dir=temp_dir, ttl=1)  # 1 second TTL
        
        test_rates = {'USD': 80.5}
        cache.set_rates(test_rates, 'test')
        
        # Should be available immediately
        assert cache.get_rates('test') == test_rates
        
        # Wait for expiration (in real test, we'd mock time)
        import time
        time.sleep(2)
        
        # Should be expired from memory cache, but file cache might still work
        # This is a simplified test - in practice we'd mock datetime
    
    def test_clear_cache(self, temp_dir):
        """Test cache clearing functionality."""
        cache = CurrencyCache(cache_dir=temp_dir)
        
        test_rates = {'USD': 80.5}
        cache.set_rates(test_rates, 'test')
        
        # Verify data is cached
        assert cache.get_rates('test') == test_rates
        
        # Clear cache
        success = cache.clear_cache('test')
        assert success is True
        
        # Verify data is cleared
        assert cache.get_rates('test') is None
    
    def test_export_rates_yaml(self, temp_dir):
        """Test YAML export functionality."""
        cache = CurrencyCache(cache_dir=temp_dir)
        
        test_rates = {
            'USD': 80.5,
            'EUR': 85.2,
            'GBP': 95.1,
            'JPY': 0.55,
            'CNY': 11.2,
        }
        cache.set_rates(test_rates, 'test')
        
        # Export to YAML
        yaml_content = cache.export_rates_yaml('test')
        
        assert '# Currency Exchange Rates - Django CFG' in yaml_content
        assert 'USD: 80.500000' in yaml_content and '# US Dollar' in yaml_content
        assert 'EUR: 85.200000' in yaml_content and '# Euro' in yaml_content
        assert 'source: test' in yaml_content
    
    def test_currency_descriptions(self, temp_dir):
        """Test currency description mapping."""
        cache = CurrencyCache(cache_dir=temp_dir)
        
        # Test known currencies
        assert cache._get_currency_description('USD') == 'US Dollar'
        assert cache._get_currency_description('EUR') == 'Euro'
        assert cache._get_currency_description('GBP') == 'British Pound'
        assert cache._get_currency_description('KRW') == 'South Korean Won'
        
        # Test unknown currency
        assert cache._get_currency_description('XYZ') == 'XYZ'


class TestCurrencyConverter:
    """Test currency converter functionality."""
    
    def test_converter_initialization(self, temp_dir):
        """Test converter initialization."""
        cache = CurrencyCache(cache_dir=temp_dir)
        converter = CurrencyConverter(cache=cache)
        
        assert converter.cache == cache
        assert hasattr(converter, '_fallback_converter')
    
    @patch('requests.get')
    def test_cbr_rates_fetch(self, mock_get, temp_dir):
        """Test fetching rates from CBR API."""
        # Mock CBR API response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'Valute': {
                'USD': {'Value': 80.5, 'Nominal': 1},
                'EUR': {'Value': 85.2, 'Nominal': 1},
            }
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        cache = CurrencyCache(cache_dir=temp_dir)
        converter = CurrencyConverter(cache=cache)
        
        # Fetch CBR rates
        rates = converter._get_cbr_rates()
        
        assert 'USD' in rates
        assert 'EUR' in rates
        assert 'RUB' in rates  # Should be added as base currency
        assert rates['USD'] == 80.5
        assert rates['EUR'] == 85.2
        assert rates['RUB'] == 1.0
    
    @patch('requests.get')
    def test_ecb_rates_fetch(self, mock_get, temp_dir):
        """Test fetching rates from ECB API."""
        # Mock ECB API response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'rates': {
                'USD': 1.1,
                'GBP': 0.85,
                'JPY': 130.0,
            }
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        cache = CurrencyCache(cache_dir=temp_dir)
        converter = CurrencyConverter(cache=cache)
        
        # Fetch ECB rates
        rates = converter._get_ecb_rates()
        
        assert 'USD' in rates
        assert 'GBP' in rates
        assert 'EUR' in rates  # Should be added as base currency
        assert rates['USD'] == 1.1
        assert rates['EUR'] == 1.0
    
    def test_same_currency_conversion(self, temp_dir):
        """Test conversion between same currencies."""
        cache = CurrencyCache(cache_dir=temp_dir)
        converter = CurrencyConverter(cache=cache)
        
        result = converter.convert(100, 'USD', 'USD')
        assert result == 100.0
    
    @patch('requests.get')
    def test_cbr_conversion(self, mock_get, temp_dir):
        """Test conversion using CBR rates."""
        # Mock CBR API response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'Valute': {
                'USD': {'Value': 80.0, 'Nominal': 1},
                'EUR': {'Value': 90.0, 'Nominal': 1},
            }
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        cache = CurrencyCache(cache_dir=temp_dir)
        converter = CurrencyConverter(cache=cache)
        
        # Convert USD to EUR via RUB
        # 100 USD = 8000 RUB, 8000 RUB = 88.89 EUR (8000/90)
        result = converter.convert(100, 'USD', 'EUR')
        expected = 100 * (80.0 / 90.0)  # 88.89
        assert abs(result - expected) < 0.01
    
    def test_get_available_currencies(self, temp_dir):
        """Test getting available currencies."""
        cache = CurrencyCache(cache_dir=temp_dir)
        converter = CurrencyConverter(cache=cache)
        
        currencies = converter.get_available_currencies()
        assert isinstance(currencies, set)
        # Should have at least some currencies even if APIs fail


class TestDjangoCurrencyService:
    """Test main Django Currency service."""
    
    def test_service_initialization(self):
        """Test service initialization."""
        service = DjangoCurrency()
        
        assert hasattr(service, '_converter')
        assert hasattr(service, '_cache')
        assert hasattr(service, '_is_configured')
    
    def test_is_configured(self):
        """Test configuration check."""
        service = DjangoCurrency()
        
        # Currency service should always be configured (has fallbacks)
        assert service.is_configured is True
    
    @patch('django_cfg.modules.django_currency.converter.CurrencyConverter.convert')
    def test_convert_method(self, mock_convert):
        """Test currency conversion method."""
        mock_convert.return_value = 85.5
        
        service = DjangoCurrency()
        result = service.convert(100, 'USD', 'EUR')
        
        assert result == 85.5
        mock_convert.assert_called_once_with(
            amount=100,
            from_currency='USD',
            to_currency='EUR',
            date_obj=None,
            round_to=2
        )
    
    def test_get_rate_method(self):
        """Test exchange rate method."""
        service = DjangoCurrency()
        
        with patch.object(service, 'convert', return_value=80.5) as mock_convert:
            rate = service.get_rate('USD', 'RUB')
            
            assert rate == 80.5
            mock_convert.assert_called_once_with(
                amount=1.0,
                from_currency='USD',
                to_currency='RUB',
                date_obj=None,
                fail_silently=False
            )
    
    def test_convert_multiple(self):
        """Test multiple currency conversions."""
        service = DjangoCurrency()
        
        with patch.object(service, 'convert', side_effect=[80.5, 85.2, 95.1]) as mock_convert:
            amounts = [100, 200, 300]
            from_currencies = ['USD', 'EUR', 'GBP']
            to_currencies = ['RUB', 'RUB', 'RUB']
            
            results = service.convert_multiple(amounts, from_currencies, to_currencies)
            
            assert results == [80.5, 85.2, 95.1]
            assert mock_convert.call_count == 3
    
    def test_convert_multiple_invalid_input(self):
        """Test multiple conversions with invalid input."""
        service = DjangoCurrency()
        
        with pytest.raises(ValueError, match="All input lists must have the same length"):
            service.convert_multiple([100], ['USD', 'EUR'], ['RUB'])
    
    def test_error_handling_fail_silently(self):
        """Test error handling with fail_silently=True."""
        service = DjangoCurrency()
        
        with patch.object(service.converter, 'convert', side_effect=Exception("API Error")):
            result = service.convert(100, 'USD', 'EUR', fail_silently=True)
            assert result == 0.0
    
    def test_error_handling_raise_exception(self):
        """Test error handling with fail_silently=False."""
        service = DjangoCurrency()
        
        with patch.object(service.converter, 'convert', side_effect=Exception("API Error")):
            with pytest.raises(Exception):
                service.convert(100, 'USD', 'EUR', fail_silently=False)
    
    def test_get_config_info(self):
        """Test configuration info retrieval."""
        service = DjangoCurrency()
        
        config_info = service.get_config_info()
        
        assert isinstance(config_info, dict)
        assert 'configured' in config_info
        assert 'cache_directory' in config_info
        assert config_info['configured'] is True


class TestConvenienceFunctions:
    """Test convenience functions."""
    
    @patch('django_cfg.modules.django_currency.DjangoCurrency')
    def test_convert_currency_function(self, mock_service_class):
        """Test convert_currency convenience function."""
        mock_service = MagicMock()
        mock_service.convert.return_value = 85.5
        mock_service_class.return_value = mock_service
        
        result = convert_currency(100, 'USD', 'EUR')
        
        assert result == 85.5
        mock_service.convert.assert_called_once_with(
            amount=100,
            from_currency='USD',
            to_currency='EUR',
            fail_silently=False
        )
    
    @patch('django_cfg.modules.django_currency.DjangoCurrency')
    def test_get_exchange_rate_function(self, mock_service_class):
        """Test get_exchange_rate convenience function."""
        mock_service = MagicMock()
        mock_service.get_rate.return_value = 80.5
        mock_service_class.return_value = mock_service
        
        result = get_exchange_rate('USD', 'RUB')
        
        assert result == 80.5
        mock_service.get_rate.assert_called_once_with('USD', 'RUB')


@pytest.mark.integration
class TestCurrencyIntegration:
    """Integration tests for currency module."""
    
    def test_full_conversion_flow(self, temp_dir):
        """Test complete conversion flow with real components."""
        # This test uses real components but mocked API calls
        with patch('requests.get') as mock_get:
            # Mock CBR response
            mock_response = MagicMock()
            mock_response.json.return_value = {
                'Valute': {
                    'USD': {'Value': 80.0, 'Nominal': 1},
                    'EUR': {'Value': 90.0, 'Nominal': 1},
                }
            }
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            
            # Create service with custom cache directory
            service = DjangoCurrency()
            service._cache = CurrencyCache(cache_dir=temp_dir)
            service._converter = CurrencyConverter(cache=service._cache)
            
            # Test conversion
            result = service.convert(100, 'USD', 'EUR')
            
            # Should get reasonable result
            assert isinstance(result, float)
            assert result > 0
            
            # Test that cache was populated
            cache_info = service.cache.get_cache_info()
            assert cache_info['status'] == 'active'
    
    def test_yaml_cache_persistence(self, temp_dir):
        """Test that YAML cache persists between service instances."""
        # First service instance
        service1 = DjangoCurrency()
        service1._cache = CurrencyCache(cache_dir=temp_dir)
        
        test_rates = {'USD': 80.5, 'EUR': 85.2}
        service1.cache.set_rates(test_rates, 'test')
        
        # Second service instance
        service2 = DjangoCurrency()
        service2._cache = CurrencyCache(cache_dir=temp_dir)
        
        # Should load from file cache
        loaded_rates = service2.cache.get_rates('test')
        assert loaded_rates == test_rates


# Pytest markers for test organization
pytestmark = [
    pytest.mark.unit,  # Most tests are unit tests
]
