"""
Cache key generation utilities for the Universal Payment System v2.0.

Centralized cache key generation for consistency and testing.
"""


class CacheKeys:
    """Cache key generation utilities."""
    
    @staticmethod
    def user_balance(user_id: int) -> str:
        """Generate cache key for user balance."""
        return f"payments:user_balance:{user_id}"
    
    @staticmethod
    def payment(payment_id: str) -> str:
        """Generate cache key for payment data."""
        return f"payments:payment:{payment_id}"
    
    @staticmethod
    def payment_status(payment_id: str) -> str:
        """Generate cache key for payment status."""
        return f"payments:payment_status:{payment_id}"
    
    @staticmethod
    def currency_rates(from_currency: str, to_currency: str) -> str:
        """Generate cache key for currency exchange rates."""
        return f"payments:currency_rates:{from_currency}:{to_currency}"
    
    @staticmethod
    def provider_currencies(provider: str) -> str:
        """Generate cache key for provider supported currencies."""
        return f"payments:provider_currencies:{provider}"
    
    @staticmethod
    def api_key_validation(api_key: str) -> str:
        """Generate cache key for API key validation data."""
        return f"payments:api_key_validation:{api_key}"
    
    @staticmethod
    def user_subscription(user_id: int) -> str:
        """Generate cache key for user subscription data."""
        return f"payments:user_subscription:{user_id}"
    
    @staticmethod
    def rate_limit(user_id: int, action: str) -> str:
        """Generate cache key for rate limiting."""
        return f"payments:rate_limit:{user_id}:{action}"
