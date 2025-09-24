"""
Pydantic schemas for provider API responses.

Type-safe models for validating and parsing responses
from payment provider health check endpoints.
"""

from typing import Dict, Optional, Any
from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel, Field, validator


class CryptAPIInfoResponse(BaseModel):
    """CryptAPI /btc/info/ response schema."""
    
    coin: str = Field(..., description="Cryptocurrency name")
    logo: str = Field(..., description="Logo URL")
    ticker: str = Field(..., description="Currency ticker")
    minimum_transaction: int = Field(..., description="Minimum transaction in satoshis")
    minimum_transaction_coin: str = Field(..., description="Minimum transaction in coin units")
    minimum_fee: int = Field(..., description="Minimum fee in satoshis")
    minimum_fee_coin: str = Field(..., description="Minimum fee in coin units")
    fee_percent: str = Field(..., description="Fee percentage")
    network_fee_estimation: str = Field(..., description="Network fee estimation")
    status: str = Field(..., description="API status")
    prices: Dict[str, str] = Field(..., description="Prices in various fiat currencies")
    prices_updated: str = Field(..., description="Prices last updated timestamp")
    
    @validator('status')
    def validate_status(cls, v):
        """Validate that status is success."""
        if v != 'success':
            raise ValueError(f"Expected status 'success', got '{v}'")
        return v
    
    @validator('prices')
    def validate_prices_not_empty(cls, v):
        """Validate that prices dict is not empty."""
        if not v:
            raise ValueError("Prices dictionary cannot be empty")
        return v
    
    def get_usd_price(self) -> Optional[Decimal]:
        """Get USD price as Decimal."""
        usd_price = self.prices.get('USD')
        if usd_price:
            try:
                return Decimal(usd_price)
            except:
                return None
        return None


class NowPaymentsStatusResponse(BaseModel):
    """NowPayments /v1/status response schema."""
    
    message: str = Field(..., description="Status message")
    
    @validator('message')
    def validate_message_ok(cls, v):
        """Validate that message is OK."""
        if v.upper() != 'OK':
            raise ValueError(f"Expected message 'OK', got '{v}'")
        return v


class StripeErrorResponse(BaseModel):
    """Stripe API error response schema."""
    
    class StripeError(BaseModel):
        message: str = Field(..., description="Error message")
        type: str = Field(..., description="Error type")
        
    error: StripeError = Field(..., description="Error details")
    
    @validator('error')
    def validate_auth_error(cls, v):
        """Validate this is an authentication error (meaning API is healthy)."""
        if v.type != 'invalid_request_error':
            raise ValueError(f"Expected auth error, got '{v.type}'")
        return v


class CryptomusErrorResponse(BaseModel):
    """Cryptomus API error response schema."""
    
    error: str = Field(..., description="Error message")
    
    @validator('error')
    def validate_not_found_error(cls, v):
        """Validate this is a not found error (meaning API is responding)."""
        if v.lower() not in ['not found', 'unauthorized', 'forbidden']:
            raise ValueError(f"Unexpected error: {v}")
        return v


class GenericAPIHealthResponse(BaseModel):
    """Generic API health response for unknown formats."""
    
    status_code: int = Field(..., description="HTTP status code")
    response_body: str = Field(..., description="Raw response body")
    response_time_ms: float = Field(..., description="Response time in milliseconds")
    
    def is_healthy(self) -> bool:
        """Determine if API is healthy based on status code."""
        # 2xx = healthy, 401/403 = healthy (auth required), 4xx = degraded, 5xx = unhealthy
        if 200 <= self.status_code < 300:
            return True
        elif self.status_code in [401, 403]:
            return True  # Auth required but API responding
        else:
            return False


class ProviderHealthResponse(BaseModel):
    """Unified health response model for all providers."""
    
    provider_name: str = Field(..., description="Provider name")
    is_healthy: bool = Field(..., description="Is provider healthy")
    status_code: int = Field(..., description="HTTP status code")
    response_time_ms: float = Field(..., description="Response time in milliseconds")
    error_message: Optional[str] = Field(None, description="Error message if unhealthy")
    parsed_response: Optional[Dict[str, Any]] = Field(None, description="Parsed API response")
    raw_response: Optional[str] = Field(None, description="Raw response body")
    checked_at: datetime = Field(default_factory=datetime.now, description="Check timestamp")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


def parse_provider_response(provider_name: str, status_code: int, response_body: str, response_time_ms: float) -> ProviderHealthResponse:
    """
    Parse provider API response using appropriate schema.
    
    Args:
        provider_name: Name of the provider
        status_code: HTTP status code
        response_body: Raw response body
        response_time_ms: Response time in milliseconds
        
    Returns:
        ProviderHealthResponse with parsed data
    """
    parsed_response = None
    error_message = None
    is_healthy = False
    
    try:
        import json
        response_json = json.loads(response_body) if response_body else {}
        
        if provider_name == 'cryptapi':
            if status_code == 200:
                cryptapi_response = CryptAPIInfoResponse(**response_json)
                parsed_response = cryptapi_response.dict()
                is_healthy = True
            else:
                error_message = f"CryptAPI returned status {status_code}"
                
        elif provider_name == 'nowpayments':
            if status_code == 200:
                nowpayments_response = NowPaymentsStatusResponse(**response_json)
                parsed_response = nowpayments_response.dict()
                is_healthy = True
            else:
                error_message = f"NowPayments returned status {status_code}"
                
        elif provider_name == 'stripe':
            if status_code == 401:
                stripe_response = StripeErrorResponse(**response_json)
                parsed_response = stripe_response.dict()
                is_healthy = True  # Auth error = API responding
            elif 200 <= status_code < 300:
                parsed_response = response_json
                is_healthy = True
            else:
                error_message = f"Stripe returned unexpected status {status_code}"
                
        elif provider_name == 'cryptomus':
            if status_code == 404 and response_json.get('error') == 'Not found':
                cryptomus_response = CryptomusErrorResponse(**response_json)
                parsed_response = cryptomus_response.dict()
                is_healthy = True  # Not found = API responding
            elif status_code == 204:
                # No Content = API responding and healthy
                parsed_response = {'status': 'no_content', 'message': 'API responding correctly'}
                is_healthy = True
            elif status_code in [401, 403]:
                is_healthy = True  # Auth required = API responding
                parsed_response = response_json
            elif 200 <= status_code < 300:
                parsed_response = response_json
                is_healthy = True
            else:
                error_message = f"Cryptomus returned status {status_code}"
        
        else:
            # Generic handling for unknown providers
            generic_response = GenericAPIHealthResponse(
                status_code=status_code,
                response_body=response_body,
                response_time_ms=response_time_ms
            )
            parsed_response = generic_response.dict()
            is_healthy = generic_response.is_healthy()
            
    except Exception as e:
        error_message = f"Failed to parse {provider_name} response: {str(e)}"
        is_healthy = False
    
    return ProviderHealthResponse(
        provider_name=provider_name,
        is_healthy=is_healthy,
        status_code=status_code,
        response_time_ms=response_time_ms,
        error_message=error_message,
        parsed_response=parsed_response,
        raw_response=response_body
    )
