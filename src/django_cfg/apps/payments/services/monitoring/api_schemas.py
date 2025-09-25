"""
Provider API monitoring schemas.

Re-exports provider-specific monitoring models from their dedicated folders.
Universal monitoring models and utilities.
"""

# Re-export provider-specific health check models
from ..providers.cryptapi.models import CryptAPIInfoResponse
from ..providers.nowpayments.models import NowPaymentsStatusResponse  
from ..providers.cryptomus.models import CryptomusErrorResponse
from ..providers.stripe.models import StripeHealthErrorResponse

# Universal monitoring models - defined here
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from enum import Enum


class APIHealthStatus(str, Enum):
    """API health status enumeration."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class GenericAPIHealthResponse(BaseModel):
    """Generic API health check response."""
    status: APIHealthStatus = Field(description="API health status")
    response_time_ms: float = Field(description="Response time in milliseconds")
    error_message: Optional[str] = Field(None, description="Error message if unhealthy")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class ProviderHealthResponse(BaseModel):
    """Provider health check response wrapper."""
    provider_name: str = Field(description="Provider name")
    api_health: GenericAPIHealthResponse = Field(description="API health details")
    checked_at: str = Field(description="Check timestamp")


def parse_provider_response(provider_name: str, response_data: Dict[str, Any]) -> ProviderHealthResponse:
    """Parse provider API response into standardized health format."""
    # Simple implementation - can be enhanced per provider
    status = APIHealthStatus.HEALTHY if response_data.get('success', False) else APIHealthStatus.UNHEALTHY
    
    api_health = GenericAPIHealthResponse(
        status=status,
        response_time_ms=response_data.get('response_time', 0.0),
        error_message=response_data.get('error_message'),
        metadata=response_data.get('metadata', {})
    )
    
    return ProviderHealthResponse(
        provider_name=provider_name,
        api_health=api_health,
        checked_at=response_data.get('timestamp', '')
    )


# Backward compatibility exports
__all__ = [
    # Provider-specific models
    'CryptAPIInfoResponse',
    'NowPaymentsStatusResponse',
    'CryptomusErrorResponse', 
    'StripeHealthErrorResponse',
    
    # Universal models
    'GenericAPIHealthResponse',
    'ProviderHealthResponse',
    
    # Utility functions
    'parse_provider_response',
]