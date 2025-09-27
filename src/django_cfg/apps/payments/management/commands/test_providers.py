"""
Test Providers Management Command for Universal Payment System v2.0.

Test payment provider connections, configurations, and functionality.
"""

from typing import List, Dict, Any, Optional
from decimal import Decimal
import time

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from django_cfg.modules.django_logger import get_logger
from django_cfg.apps.payments.services.providers.registry import get_provider_registry
from django_cfg.apps.payments.models import Currency, Network
from django_cfg.apps.payments.services.types.requests import PaymentCreateRequest

logger = get_logger("test_providers")


class Command(BaseCommand):
    """
    Test payment provider connections and functionality.
    
    Features:
    - Test provider connectivity
    - Validate configurations
    - Test currency support
    - Check API responses
    - Performance testing
    """
    
    help = 'Test payment provider connections and functionality'
    
    def add_arguments(self, parser):
        """Add command line arguments."""
        parser.add_argument(
            '--provider',
            type=str,
            help='Test specific provider only'
        )
        
        parser.add_argument(
            '--test-type',
            choices=['connectivity', 'currencies', 'payment', 'all'],
            default='all',
            help='Type of test to run (default: all)'
        )
        
        parser.add_argument(
            '--timeout',
            type=int,
            default=30,
            help='Request timeout in seconds (default: 30)'
        )
        
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed test information'
        )
        
        parser.add_argument(
            '--create-test-payment',
            action='store_true',
            help='Create actual test payment (use with caution!)'
        )
        
        parser.add_argument(
            '--test-amount',
            type=float,
            default=1.0,
            help='Test payment amount in USD (default: 1.0)'
        )
    
    def handle(self, *args, **options):
        """Execute the command."""
        try:
            self.options = options
            self.verbose = options['verbose']
            
            self.show_header()
            
            # Get provider registry
            self.provider_registry = get_provider_registry()
            
            # Initialize test results
            self.test_results = {}
            
            # Get providers to test
            if options['provider']:
                providers = [options['provider']]
            else:
                providers = self.provider_registry.get_available_providers()
            
            if not providers:
                self.stdout.write(self.style.WARNING("No providers available to test"))
                return
            
            # Run tests
            for provider_name in providers:
                self.test_provider(provider_name)
            
            self.show_summary()
            
        except Exception as e:
            logger.error(f"Test providers command failed: {e}")
            raise CommandError(f"Failed to test providers: {e}")
    
    def show_header(self):
        """Display command header."""
        self.stdout.write(
            self.style.SUCCESS("=" * 60)
        )
        self.stdout.write(
            self.style.SUCCESS("🧪 PAYMENT PROVIDER TESTING")
        )
        self.stdout.write(
            self.style.SUCCESS("=" * 60)
        )
        self.stdout.write(f"Started: {timezone.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
        self.stdout.write("")
    
    def test_provider(self, provider_name: str):
        """Test a specific provider."""
        self.stdout.write(self.style.SUCCESS(f"🔍 TESTING PROVIDER: {provider_name.upper()}"))
        self.stdout.write("-" * 50)
        
        # Initialize provider results
        self.test_results[provider_name] = {
            'connectivity': False,
            'currencies': False,
            'payment': False,
            'errors': [],
            'warnings': [],
            'performance': {}
        }
        
        try:
            # Get provider instance
            provider = self.provider_registry.get_provider(provider_name)
            if not provider:
                self.test_results[provider_name]['errors'].append("Provider not available")
                self.stdout.write(self.style.ERROR(f"❌ Provider {provider_name} not available"))
                return
            
            # Run selected tests
            test_type = self.options['test_type']
            
            if test_type in ['connectivity', 'all']:
                self.test_connectivity(provider_name, provider)
            
            if test_type in ['currencies', 'all']:
                self.test_currencies(provider_name, provider)
            
            if test_type in ['payment', 'all'] and self.options['create_test_payment']:
                self.test_payment_creation(provider_name, provider)
            
        except Exception as e:
            error_msg = f"Provider test failed: {e}"
            self.test_results[provider_name]['errors'].append(error_msg)
            logger.error(f"Error testing provider {provider_name}: {e}")
            self.stdout.write(self.style.ERROR(f"❌ {error_msg}"))
        
        self.stdout.write("")
    
    def test_connectivity(self, provider_name: str, provider):
        """Test provider connectivity."""
        self.stdout.write("  🌐 Testing connectivity...")
        
        try:
            start_time = time.time()
            
            # Test basic connectivity (health check or similar)
            if hasattr(provider, 'health_check'):
                result = provider.health_check()
                success = result.success if hasattr(result, 'success') else True
            elif hasattr(provider, 'get_supported_currencies'):
                # Fallback: try to get currencies as connectivity test
                result = provider.get_supported_currencies()
                success = len(result) > 0 if isinstance(result, list) else bool(result)
            else:
                # Last resort: assume connectivity is OK if provider exists
                success = True
            
            end_time = time.time()
            response_time = (end_time - start_time) * 1000  # Convert to milliseconds
            
            self.test_results[provider_name]['performance']['connectivity_ms'] = response_time
            
            if success:
                self.test_results[provider_name]['connectivity'] = True
                self.stdout.write(f"    ✅ Connectivity OK ({response_time:.0f}ms)")
            else:
                self.test_results[provider_name]['errors'].append("Connectivity test failed")
                self.stdout.write(f"    ❌ Connectivity failed")
                
        except Exception as e:
            error_msg = f"Connectivity test error: {e}"
            self.test_results[provider_name]['errors'].append(error_msg)
            self.stdout.write(f"    ❌ Connectivity error: {e}")
    
    def test_currencies(self, provider_name: str, provider):
        """Test provider currency support."""
        self.stdout.write("  💰 Testing currency support...")
        
        try:
            start_time = time.time()
            
            # Get supported currencies from provider
            if hasattr(provider, 'get_supported_currencies'):
                supported_currencies = provider.get_supported_currencies()
            else:
                self.test_results[provider_name]['warnings'].append("Provider doesn't support currency listing")
                self.stdout.write("    ⚠️  Provider doesn't support currency listing")
                return
            
            end_time = time.time()
            response_time = (end_time - start_time) * 1000
            
            self.test_results[provider_name]['performance']['currencies_ms'] = response_time
            
            if isinstance(supported_currencies, list) and len(supported_currencies) > 0:
                self.test_results[provider_name]['currencies'] = True
                currency_count = len(supported_currencies)
                self.stdout.write(f"    ✅ {currency_count} currencies supported ({response_time:.0f}ms)")
                
                if self.verbose:
                    # Show first few currencies
                    sample_currencies = supported_currencies[:5]
                    currency_codes = [c.get('code', str(c)) for c in sample_currencies]
                    self.stdout.write(f"    Sample: {', '.join(currency_codes)}")
                
                # Check if our database currencies are supported
                our_currencies = Currency.objects.filter(is_active=True)[:10]
                supported_codes = []
                
                if isinstance(supported_currencies[0], dict):
                    supported_codes = [c.get('code', '').upper() for c in supported_currencies]
                else:
                    supported_codes = [str(c).upper() for c in supported_currencies]
                
                matching_count = 0
                for currency in our_currencies:
                    if currency.code.upper() in supported_codes:
                        matching_count += 1
                
                if matching_count > 0:
                    self.stdout.write(f"    ✅ {matching_count}/{our_currencies.count()} of our currencies supported")
                else:
                    self.test_results[provider_name]['warnings'].append("No matching currencies found")
                    self.stdout.write("    ⚠️  No matching currencies found")
                    
            else:
                self.test_results[provider_name]['errors'].append("No currencies returned")
                self.stdout.write("    ❌ No currencies returned")
                
        except Exception as e:
            error_msg = f"Currency test error: {e}"
            self.test_results[provider_name]['errors'].append(error_msg)
            self.stdout.write(f"    ❌ Currency test error: {e}")
    
    def test_payment_creation(self, provider_name: str, provider):
        """Test payment creation (creates actual test payment!)."""
        self.stdout.write("  💳 Testing payment creation...")
        self.stdout.write("    ⚠️  WARNING: This creates an actual payment!")
        
        try:
            # Get a supported currency for testing
            test_currency = self.get_test_currency(provider)
            if not test_currency:
                self.test_results[provider_name]['warnings'].append("No suitable test currency found")
                self.stdout.write("    ⚠️  No suitable test currency found")
                return
            
            # Create test payment request
            payment_request = PaymentCreateRequest(
                amount_usd=self.options['test_amount'],
                currency_code=test_currency,
                description=f"Test payment from django-cfg ({timezone.now().isoformat()})",
                callback_url="https://example.com/webhook/test",
                success_url="https://example.com/success",
                cancel_url="https://example.com/cancel"
            )
            
            start_time = time.time()
            
            # Create payment
            result = provider.create_payment(payment_request)
            
            end_time = time.time()
            response_time = (end_time - start_time) * 1000
            
            self.test_results[provider_name]['performance']['payment_creation_ms'] = response_time
            
            if hasattr(result, 'success') and result.success:
                self.test_results[provider_name]['payment'] = True
                payment_id = getattr(result, 'provider_payment_id', 'Unknown')
                payment_url = getattr(result, 'payment_url', 'No URL')
                
                self.stdout.write(f"    ✅ Payment created ({response_time:.0f}ms)")
                self.stdout.write(f"    Payment ID: {payment_id}")
                
                if self.verbose and payment_url != 'No URL':
                    self.stdout.write(f"    Payment URL: {payment_url}")
                
                # Test payment status check
                if hasattr(provider, 'get_payment_status') and payment_id != 'Unknown':
                    try:
                        status_result = provider.get_payment_status(payment_id)
                        if hasattr(status_result, 'success') and status_result.success:
                            status = getattr(status_result, 'status', 'Unknown')
                            self.stdout.write(f"    ✅ Status check OK: {status}")
                        else:
                            self.test_results[provider_name]['warnings'].append("Status check failed")
                            self.stdout.write("    ⚠️  Status check failed")
                    except Exception as e:
                        self.test_results[provider_name]['warnings'].append(f"Status check error: {e}")
                        self.stdout.write(f"    ⚠️  Status check error: {e}")
                
            else:
                error = getattr(result, 'error', 'Unknown error')
                self.test_results[provider_name]['errors'].append(f"Payment creation failed: {error}")
                self.stdout.write(f"    ❌ Payment creation failed: {error}")
                
        except Exception as e:
            error_msg = f"Payment creation error: {e}"
            self.test_results[provider_name]['errors'].append(error_msg)
            self.stdout.write(f"    ❌ Payment creation error: {e}")
    
    def get_test_currency(self, provider) -> Optional[str]:
        """Get a suitable currency for testing."""
        # Common test currencies
        test_currencies = ['BTC', 'ETH', 'USDT', 'LTC', 'USD']
        
        try:
            # Get supported currencies from provider
            if hasattr(provider, 'get_supported_currencies'):
                supported = provider.get_supported_currencies()
                
                if isinstance(supported, list) and len(supported) > 0:
                    # Extract currency codes
                    if isinstance(supported[0], dict):
                        supported_codes = [c.get('code', '').upper() for c in supported]
                    else:
                        supported_codes = [str(c).upper() for c in supported]
                    
                    # Find first matching test currency
                    for currency in test_currencies:
                        if currency in supported_codes:
                            return currency
                    
                    # Fallback: return first supported currency
                    if supported_codes:
                        return supported_codes[0]
            
            # Last resort: try BTC
            return 'BTC'
            
        except Exception:
            return 'BTC'
    
    def show_summary(self):
        """Display test summary."""
        self.stdout.write(self.style.SUCCESS("📊 TEST SUMMARY"))
        self.stdout.write("-" * 40)
        
        total_providers = len(self.test_results)
        successful_providers = 0
        total_errors = 0
        total_warnings = 0
        
        for provider_name, results in self.test_results.items():
            errors = len(results['errors'])
            warnings = len(results['warnings'])
            
            total_errors += errors
            total_warnings += warnings
            
            # Count as successful if no errors and at least one test passed
            if errors == 0 and (results['connectivity'] or results['currencies']):
                successful_providers += 1
            
            # Show provider summary
            status_icon = "✅" if errors == 0 else "❌"
            self.stdout.write(f"{status_icon} {provider_name}:")
            
            if results['connectivity']:
                self.stdout.write("    ✅ Connectivity")
            if results['currencies']:
                self.stdout.write("    ✅ Currencies")
            if results['payment']:
                self.stdout.write("    ✅ Payment Creation")
            
            if errors > 0:
                self.stdout.write(f"    ❌ {errors} error(s)")
            if warnings > 0:
                self.stdout.write(f"    ⚠️  {warnings} warning(s)")
            
            # Show performance metrics
            if self.verbose and results['performance']:
                perf = results['performance']
                if 'connectivity_ms' in perf:
                    self.stdout.write(f"    ⏱️  Connectivity: {perf['connectivity_ms']:.0f}ms")
                if 'currencies_ms' in perf:
                    self.stdout.write(f"    ⏱️  Currencies: {perf['currencies_ms']:.0f}ms")
                if 'payment_creation_ms' in perf:
                    self.stdout.write(f"    ⏱️  Payment: {perf['payment_creation_ms']:.0f}ms")
        
        # Overall summary
        self.stdout.write("")
        self.stdout.write(f"Providers tested: {total_providers}")
        self.stdout.write(f"Successful: {self.style.SUCCESS(successful_providers)}")
        self.stdout.write(f"Failed: {self.style.ERROR(total_providers - successful_providers)}")
        self.stdout.write(f"Total errors: {self.style.ERROR(total_errors)}")
        self.stdout.write(f"Total warnings: {self.style.WARNING(total_warnings)}")
        
        # Show completion time
        self.stdout.write("")
        self.stdout.write(f"Completed: {timezone.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
        
        # Recommendations
        if total_errors > 0:
            self.stdout.write("")
            self.stdout.write(
                self.style.WARNING("⚠️  Some providers have errors. Check configurations and network connectivity.")
            )
        
        if successful_providers == total_providers and total_errors == 0:
            self.stdout.write("")
            self.stdout.write(
                self.style.SUCCESS("🎉 All providers tested successfully!")
            )
