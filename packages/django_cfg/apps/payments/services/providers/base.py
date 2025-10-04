"""
Base provider class for the Universal Payment System v2.0.

Abstract base class for all payment providers with unified interface.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from decimal import Decimal
import requests
from django.utils import timezone
from django_cfg.modules.django_logging import get_logger
from ..types import ProviderResponse, ServiceOperationResult
from .models import ProviderConfig, PaymentRequest, WithdrawalRequest


class BaseProvider(ABC):
    """
    Abstract base class for payment providers.
    
    Defines the unified interface that all providers must implement.
    """
    
    def __init__(self, config: ProviderConfig):
        """
        Initialize provider with configuration.
        
        Args:
            config: Provider configuration
        """
        self.config = config
        self.logger = get_logger(f"providers.{config.provider_name}")
        self._session = None
    
    @property
    def name(self) -> str:
        """Get provider name."""
        return self.config.provider_name
    
    @property
    def is_sandbox(self) -> bool:
        """Check if provider is in sandbox mode."""
        return self.config.sandbox_mode
    
    # Provider configuration methods (to be overridden by specific providers)
    def get_fee_percentage(self, currency_code: str = None, currency_type: str = None) -> Decimal:
        """
        Get fee percentage for currency.
        
        Args:
            currency_code: Currency code (e.g., 'BTC', 'ETH')
            currency_type: Currency type ('fiat', 'crypto')
            
        Returns:
            Fee percentage as decimal (0.005 = 0.5%)
        """
        return Decimal('0.005')  # Default 0.5%
    
    def get_fixed_fee_usd(self, currency_code: str = None, currency_type: str = None) -> Decimal:
        """
        Get fixed fee in USD for currency.
        
        Args:
            currency_code: Currency code (e.g., 'BTC', 'ETH')
            currency_type: Currency type ('fiat', 'crypto')
            
        Returns:
            Fixed fee in USD
        """
        return Decimal('0.0')  # Default no fixed fee
    
    def get_min_amount_usd(self, currency_code: str = None, currency_type: str = None, is_stable: bool = False) -> Decimal:
        """
        Get minimum amount in USD for currency.
        
        Args:
            currency_code: Currency code (e.g., 'BTC', 'ETH')
            currency_type: Currency type ('fiat', 'crypto')
            is_stable: Whether currency is a stablecoin
            
        Returns:
            Minimum amount in USD
        """
        if currency_type == 'fiat':
            return Decimal('1.0')
        elif is_stable:
            return Decimal('0.01')
        else:
            return Decimal('0.000001')
    
    def get_max_amount_usd(self, currency_code: str = None, currency_type: str = None) -> Decimal:
        """
        Get maximum amount in USD for currency.
        
        Args:
            currency_code: Currency code (e.g., 'BTC', 'ETH')
            currency_type: Currency type ('fiat', 'crypto')
            
        Returns:
            Maximum amount in USD
        """
        return Decimal('1000000.0')  # Default 1M USD
    
    def get_confirmation_blocks(self, network_code: str) -> int:
        """
        Get confirmation blocks for network.
        
        Args:
            network_code: Network code (e.g., 'btc', 'eth')
            
        Returns:
            Number of confirmation blocks
        """
        return 1  # Default 1 confirmation
    
    def get_network_name(self, network_code: str) -> str:
        """
        Get human-readable network name.
        
        Args:
            network_code: Network code (e.g., 'btc', 'eth')
            
        Returns:
            Human-readable network name
        """
        return network_code.upper() if network_code else 'Unknown'
    
    @abstractmethod
    def create_payment(self, request: PaymentRequest) -> ProviderResponse:
        """
        Create payment with provider.
        
        Args:
            request: Payment creation request
            
        Returns:
            ProviderResponse: Provider response with payment details
        """
        pass
    
    @abstractmethod
    def get_payment_status(self, provider_payment_id: str) -> ProviderResponse:
        """
        Get payment status from provider.
        
        Args:
            provider_payment_id: Provider's payment ID
            
        Returns:
            ProviderResponse: Current payment status
        """
        pass
    
    def refresh_payment_status(self, provider_payment_id: str, force_update: bool = True) -> ProviderResponse:
        """
        Refresh payment status with enhanced error handling and caching control.
        
        This method provides additional functionality over get_payment_status:
        - Enhanced error handling
        - Optional caching control
        - Detailed logging
        
        Args:
            provider_payment_id: Provider's payment ID
            force_update: Whether to bypass cache and force fresh data
            
        Returns:
            ProviderResponse: Current payment status with enhanced metadata
        """
        self.logger.info(f"Refreshing payment status for {provider_payment_id}", extra={
            'provider': self.name,
            'payment_id': provider_payment_id,
            'force_update': force_update
        })
        
        try:
            # Call the provider-specific implementation
            result = self.get_payment_status(provider_payment_id)
            
            # Add refresh metadata
            if result.success and hasattr(result, 'raw_response') and result.raw_response:
                result.raw_response['_refresh_metadata'] = {
                    'refreshed_at': timezone.now().isoformat(),
                    'provider': self.name,
                    'force_update': force_update
                }
            
            self.logger.info(f"Payment status refreshed successfully", extra={
                'provider': self.name,
                'payment_id': provider_payment_id,
                'status': getattr(result, 'status', 'unknown')
            })
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to refresh payment status", extra={
                'provider': self.name,
                'payment_id': provider_payment_id,
                'error': str(e)
            })
            
            return ProviderResponse(
                success=False,
                error_message=f"Failed to refresh payment status: {str(e)}",
                raw_response={'error': str(e), 'provider': self.name}
            )
    
    @abstractmethod
    def get_supported_currencies(self) -> ServiceOperationResult:
        """
        Get list of supported currencies from provider.
        
        Returns:
            ServiceOperationResult: List of supported currencies
        """
        pass
    
    @abstractmethod
    def sync_currencies_to_db(self):
        """
        Sync currencies from provider API to database.
        
        Returns:
            CurrencySyncResult: Synchronization result
        """
        pass
    
    @abstractmethod
    def validate_webhook(self, payload: Dict[str, Any], signature: str = None) -> ServiceOperationResult:
        """
        Validate webhook from provider.
        
        Args:
            payload: Webhook payload
            signature: Webhook signature (if any)
            
        Returns:
            ServiceOperationResult: Validation result
        """
        pass
    
    # Withdrawal/Payout Methods
    
    def supports_withdrawals(self) -> bool:
        """
        Check if provider supports withdrawals/payouts.
        
        Returns:
            bool: True if provider supports withdrawals
        """
        return False  # Default: most payment processors don't support withdrawals
    
    def create_withdrawal(self, request: WithdrawalRequest) -> ProviderResponse:
        """
        Create withdrawal/payout request with provider.
        
        Args:
            request: Withdrawal creation request
            
        Returns:
            ProviderResponse: Provider response with withdrawal details
            
        Raises:
            NotImplementedError: If provider doesn't support withdrawals
        """
        if not self.supports_withdrawals():
            return ProviderResponse(
                success=False,
                error_message=f"Provider {self.name} does not support withdrawals",
                raw_response={'error': 'withdrawals_not_supported'}
            )
        
        raise NotImplementedError("Subclasses must implement create_withdrawal if they support withdrawals")
    
    def get_withdrawal_status(self, provider_withdrawal_id: str) -> ProviderResponse:
        """
        Get withdrawal status from provider.
        
        Args:
            provider_withdrawal_id: Provider's withdrawal ID
            
        Returns:
            ProviderResponse: Current withdrawal status
            
        Raises:
            NotImplementedError: If provider doesn't support withdrawals
        """
        if not self.supports_withdrawals():
            return ProviderResponse(
                success=False,
                error_message=f"Provider {self.name} does not support withdrawals",
                raw_response={'error': 'withdrawals_not_supported'}
            )
        
        raise NotImplementedError("Subclasses must implement get_withdrawal_status if they support withdrawals")
    
    def cancel_withdrawal(self, provider_withdrawal_id: str) -> ProviderResponse:
        """
        Cancel pending withdrawal.
        
        Args:
            provider_withdrawal_id: Provider's withdrawal ID
            
        Returns:
            ProviderResponse: Cancellation result
            
        Raises:
            NotImplementedError: If provider doesn't support withdrawal cancellation
        """
        if not self.supports_withdrawals():
            return ProviderResponse(
                success=False,
                error_message=f"Provider {self.name} does not support withdrawals",
                raw_response={'error': 'withdrawals_not_supported'}
            )
        
        return ProviderResponse(
            success=False,
            error_message=f"Provider {self.name} does not support withdrawal cancellation",
            raw_response={'error': 'withdrawal_cancellation_not_supported'}
        )
    
    def get_withdrawal_fees(self, currency_code: str) -> ServiceOperationResult:
        """
        Get withdrawal fees for specific currency.
        
        Args:
            currency_code: Currency code
            
        Returns:
            ServiceOperationResult: Fee information or not supported
        """
        if not self.supports_withdrawals():
            return ServiceOperationResult(
                success=False,
                message=f"Provider {self.name} does not support withdrawals"
            )
        
        return ServiceOperationResult(
            success=False,
            message="Withdrawal fee information not available"
        )
    
    def get_minimum_withdrawal_amount(self, currency_code: str) -> ServiceOperationResult:
        """
        Get minimum withdrawal amount for specific currency.
        
        Args:
            currency_code: Currency code
            
        Returns:
            ServiceOperationResult: Minimum amount or not supported
        """
        if not self.supports_withdrawals():
            return ServiceOperationResult(
                success=False,
                message=f"Provider {self.name} does not support withdrawals"
            )
        
        return ServiceOperationResult(
            success=False,
            message="Minimum withdrawal amount information not available"
        )
    
    def get_exchange_rate(self, from_currency: str, to_currency: str) -> ServiceOperationResult:
        """
        Get exchange rate from provider (optional).
        
        Args:
            from_currency: Source currency
            to_currency: Target currency
            
        Returns:
            ServiceOperationResult: Exchange rate or not supported
        """
        return ServiceOperationResult(
            success=False,
            message=f"Exchange rates not supported by {self.name}",
            error_code="not_supported"
        )
    
    def health_check(self) -> ServiceOperationResult:
        """
        Perform provider health check.
        
        Returns:
            ServiceOperationResult: Health check result
        """
        try:
            # Basic connectivity test - can be overridden by providers
            result = self.get_supported_currencies()
            
            if result.success:
                return ServiceOperationResult(
                    success=True,
                    message=f"{self.name} provider is healthy",
                    data={
                        'provider': self.name,
                        'sandbox': self.is_sandbox,
                        'api_url': self.config.api_url,
                        'supported_currencies_count': len(result.data.get('currencies', []))
                    }
                )
            else:
                return ServiceOperationResult(
                    success=False,
                    message=f"{self.name} provider health check failed",
                    error_code="health_check_failed",
                    data={'provider': self.name, 'error': result.message}
                )
                
        except Exception as e:
            self.logger.error(f"Health check failed for {self.name}: {e}")
            return ServiceOperationResult(
                success=False,
                message=f"{self.name} provider health check error: {e}",
                error_code="health_check_error",
                data={'provider': self.name}
            )
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Make HTTP request to provider API.
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            data: Request data
            headers: Request headers
            
        Returns:
            Dict[str, Any]: Response data
            
        Raises:
            Exception: If request fails
        """
        import requests
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry
        
        # Create session if not exists
        if self._session is None:
            self._session = requests.Session()
            
            # Configure retries
            retry_strategy = Retry(
                total=self.config.retry_attempts,
                backoff_factor=self.config.retry_delay,
                status_forcelist=[429, 500, 502, 503, 504],
            )
            adapter = HTTPAdapter(max_retries=retry_strategy)
            self._session.mount("http://", adapter)
            self._session.mount("https://", adapter)
        
        # Build URL
        url = f"{self.config.api_url.rstrip('/')}/{endpoint.lstrip('/')}"
        
        # Prepare headers
        request_headers = {
            'Content-Type': 'application/json',
            'User-Agent': f'django-cfg-payments/2.0 ({self.name})',
        }
        if headers:
            request_headers.update(headers)
        
        # Log request
        self.logger.debug(f"Making {method} request to {url}", extra={
            'method': method,
            'url': url,
            'has_data': bool(data)
        })
        
        # Make request
        response = self._session.request(
            method=method,
            url=url,
            json=data if data else None,
            headers=request_headers,
            timeout=self.config.timeout
        )
        
        # Log response
        self.logger.debug(f"Received response: {response.status_code}", extra={
            'status_code': response.status_code,
            'response_size': len(response.content)
        })
        
        # Handle response
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            # Log the error with response content for debugging
            error_content = response.text if response.text else "No response content"
            self.logger.error(f"HTTP {response.status_code} error from {self.name}", extra={
                'status_code': response.status_code,
                'error_content': error_content[:500],  # Limit content length
                'url': response.url
            })
            
            # Handle specific HTTP errors
            if response.status_code == 403:
                if "blocked" in error_content.lower() or "nowpayments.io" in error_content:
                    raise Exception(f"IP address blocked by {self.name}. Please contact {self.name} support or use a different IP/VPN.")
                else:
                    raise Exception(f"Access forbidden by {self.name}. Check API key and permissions.")
            elif response.status_code == 401:
                raise Exception(f"Authentication failed with {self.name}. Check API key.")
            elif response.status_code == 400:
                raise Exception(f"Bad request to {self.name}: {error_content[:200]}")
            elif response.status_code == 429:
                raise Exception(f"Rate limit exceeded for {self.name}. Please try again later.")
            elif response.status_code >= 500:
                raise Exception(f"{self.name} server error ({response.status_code}). Please try again later.")
            else:
                raise Exception(f"HTTP {response.status_code} error from {self.name}: {error_content[:200]}")
        
        try:
            return response.json()
        except ValueError:
            # Non-JSON response
            return {'raw_response': response.text, 'status_code': response.status_code}
    
    def _create_provider_response(
        self,
        success: bool,
        raw_response: Dict[str, Any],
        **kwargs
    ) -> ProviderResponse:
        """
        Create standardized provider response.
        
        Args:
            success: Operation success
            raw_response: Raw provider response
            **kwargs: Additional response fields
            
        Returns:
            ProviderResponse: Standardized response
        """
        return ProviderResponse(
            provider=self.name,
            success=success,
            raw_response=raw_response,
            **kwargs
        )
    
    def __str__(self) -> str:
        """String representation."""
        return f"{self.name}Provider(sandbox={self.is_sandbox})"
    
    def __repr__(self) -> str:
        """Detailed representation."""
        return f"{self.__class__.__name__}(name='{self.name}', sandbox={self.is_sandbox}, api_url='{self.config.api_url}')"
