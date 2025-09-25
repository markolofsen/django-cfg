"""
Provider Health Monitoring System.

Monitors the health of all payment providers and provides
fallback mechanisms when providers are unavailable.
"""

from django_cfg.modules.django_logger import get_logger
import time
import asyncio
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

from django.utils import timezone
from django.core.cache import cache
from pydantic import BaseModel, Field

from ..providers.registry import ProviderRegistry
from ...models.events import PaymentEvent
from .api_schemas import parse_provider_response

logger = get_logger("provider_health")


class HealthStatus(Enum):
    """Provider health status levels."""
    HEALTHY = "healthy"
    DEGRADED = "degraded" 
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class ProviderHealthCheck(BaseModel):
    """Provider health check result."""
    provider_name: str = Field(..., description="Provider name")
    status: HealthStatus = Field(..., description="Health status")
    response_time_ms: float = Field(..., description="Response time in milliseconds")
    status_code: Optional[int] = Field(None, description="HTTP status code")
    error_message: Optional[str] = Field(None, description="Error message if unhealthy")
    checked_at: datetime = Field(default_factory=timezone.now, description="Check timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class ProviderHealthSummary(BaseModel):
    """Summary of all provider health statuses."""
    total_providers: int = Field(..., description="Total number of providers")
    healthy_count: int = Field(..., description="Number of healthy providers")
    degraded_count: int = Field(..., description="Number of degraded providers")
    unhealthy_count: int = Field(..., description="Number of unhealthy providers")
    providers: List[ProviderHealthCheck] = Field(..., description="Individual provider health checks")
    last_updated: datetime = Field(default_factory=timezone.now, description="Last update timestamp")


class ProviderHealthMonitor:
    """
    Monitor the health of all payment providers.
    
    Features:
    - Real-time health checks
    - Provider availability tracking
    - Automatic fallback recommendations
    - Health history and trends
    - Alert system integration
    """
    
    def __init__(self):
        """Initialize health monitor."""
        self.provider_registry = ProviderRegistry()
        self.cache_timeout = 300  # 5 minutes
        self.health_check_timeout = 10  # 10 seconds
        
        # Health check endpoints for each provider
        self.health_endpoints = {
            'cryptapi': 'https://api.cryptapi.io/btc/info/',
            'cryptomus': 'https://api.cryptomus.com',  # Base URL check (returns 204 No Content = healthy)
            'nowpayments': 'https://api.nowpayments.io/v1/status',
            'stripe': 'https://api.stripe.com/v1/account'  # Will return auth error = healthy
        }
    
    def check_all_providers(self) -> ProviderHealthSummary:
        """
        Check health of all registered providers.
        
        Returns:
            ProviderHealthSummary with all provider statuses
        """
        providers = self.provider_registry.get_all_providers()
        health_checks = []
        
        for provider_name, provider_instance in providers.items():
            try:
                health_check = self.check_provider_health(provider_name)
                health_checks.append(health_check)
            except Exception as e:
                logger.error(f"Failed to check health for {provider_name}: {e}")
                health_checks.append(ProviderHealthCheck(
                    provider_name=provider_name,
                    status=HealthStatus.UNKNOWN,
                    response_time_ms=0.0,
                    error_message=str(e)
                ))
        
        # Calculate summary
        healthy_count = sum(1 for check in health_checks if check.status == HealthStatus.HEALTHY)
        degraded_count = sum(1 for check in health_checks if check.status == HealthStatus.DEGRADED)
        unhealthy_count = sum(1 for check in health_checks if check.status == HealthStatus.UNHEALTHY)
        
        summary = ProviderHealthSummary(
            total_providers=len(health_checks),
            healthy_count=healthy_count,
            degraded_count=degraded_count,
            unhealthy_count=unhealthy_count,
            providers=health_checks
        )
        
        # Cache summary
        cache.set('provider_health_summary', summary.dict(), self.cache_timeout)
        
        # Log health summary
        logger.info(f"Provider health check completed: {healthy_count}/{len(health_checks)} healthy")
        
        return summary
    
    def check_provider_health(self, provider_name: str) -> ProviderHealthCheck:
        """
        Check health of a specific provider.
        
        Args:
            provider_name: Name of the provider to check
            
        Returns:
            ProviderHealthCheck with health status
        """
        # Check cache first
        cache_key = f'provider_health_{provider_name}'
        cached_result = cache.get(cache_key)
        if cached_result:
            return ProviderHealthCheck(**cached_result)
        
        start_time = time.time()
        health_check = None
        
        try:
            # Get health endpoint for provider
            endpoint = self.health_endpoints.get(provider_name)
            if not endpoint:
                raise ValueError(f"No health endpoint configured for {provider_name}")
            
            # Make health check request
            response = requests.get(
                endpoint,
                timeout=self.health_check_timeout,
                headers={'User-Agent': 'DjangoCFG-PaymentMonitor/1.0'}
            )
            
            response_time = (time.time() - start_time) * 1000
            
            # Parse response using Pydantic schemas
            response_body = response.text if response.text else ""
            parsed_health = parse_provider_response(
                provider_name=provider_name,
                status_code=response.status_code,
                response_body=response_body,
                response_time_ms=response_time
            )
            
            # Convert to our HealthStatus enum
            if parsed_health.is_healthy:
                status = HealthStatus.HEALTHY
            elif 400 <= response.status_code < 500:
                status = HealthStatus.DEGRADED
            else:
                status = HealthStatus.UNHEALTHY
            
            health_check = ProviderHealthCheck(
                provider_name=provider_name,
                status=status,
                response_time_ms=round(response_time, 2),
                status_code=response.status_code,
                error_message=parsed_health.error_message,
                metadata={
                    'endpoint': endpoint,
                    'response_size': len(response.content) if response.content else 0,
                    'parsed_response': parsed_health.parsed_response,
                    'pydantic_validated': True
                }
            )
            
        except requests.exceptions.Timeout:
            response_time = (time.time() - start_time) * 1000
            health_check = ProviderHealthCheck(
                provider_name=provider_name,
                status=HealthStatus.UNHEALTHY,
                response_time_ms=round(response_time, 2),
                error_message="Request timeout"
            )
            
        except requests.exceptions.ConnectionError:
            response_time = (time.time() - start_time) * 1000
            health_check = ProviderHealthCheck(
                provider_name=provider_name,
                status=HealthStatus.UNHEALTHY,
                response_time_ms=round(response_time, 2),
                error_message="Connection error"
            )
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            health_check = ProviderHealthCheck(
                provider_name=provider_name,
                status=HealthStatus.UNKNOWN,
                response_time_ms=round(response_time, 2),
                error_message=str(e)
            )
        
        # Cache result
        cache.set(cache_key, health_check.dict(), self.cache_timeout // 2)  # Shorter cache for individual checks
        
        # Log health check
        logger.info(f"Health check for {provider_name}: {health_check.status.value} ({health_check.response_time_ms}ms)")
        
        return health_check
    
    def get_healthy_providers(self) -> List[str]:
        """
        Get list of currently healthy provider names.
        
        Returns:
            List of healthy provider names
        """
        summary = self.check_all_providers()
        return [
            provider.provider_name 
            for provider in summary.providers 
            if provider.status == HealthStatus.HEALTHY
        ]
    
    def get_fallback_provider(self, preferred_provider: str) -> Optional[str]:
        """
        Get fallback provider when preferred provider is unhealthy.
        
        Args:
            preferred_provider: Name of preferred provider
            
        Returns:
            Name of healthy fallback provider or None
        """
        healthy_providers = self.get_healthy_providers()
        
        # Remove preferred provider from list
        fallback_providers = [p for p in healthy_providers if p != preferred_provider]
        
        if not fallback_providers:
            logger.warning(f"No healthy fallback providers available for {preferred_provider}")
            return None
        
        # Return first healthy provider as fallback
        fallback = fallback_providers[0]
        logger.info(f"Fallback provider for {preferred_provider}: {fallback}")
        
        return fallback
    
    def record_provider_incident(self, provider_name: str, incident_type: str, details: Dict[str, Any]):
        """
        Record provider incident for tracking.
        
        Args:
            provider_name: Name of the provider
            incident_type: Type of incident (outage, degradation, etc.)
            details: Incident details
        """
        try:
            PaymentEvent.objects.create(
                payment_id=f"health_monitor_{timezone.now().timestamp()}",
                event_type='provider_incident',
                sequence_number=1,
                event_data={
                    'provider_name': provider_name,
                    'incident_type': incident_type,
                    'details': details,
                    'timestamp': timezone.now().isoformat()
                },
                processed_by='health_monitor',
                idempotency_key=f"incident_{provider_name}_{timezone.now().timestamp()}"
            )
            
            logger.warning(f"Provider incident recorded: {provider_name} - {incident_type}")
            
        except Exception as e:
            logger.error(f"Failed to record provider incident: {e}")
    
    def get_provider_uptime(self, provider_name: str, days: int = 7) -> float:
        """
        Calculate provider uptime percentage over specified period.
        
        Args:
            provider_name: Name of the provider
            days: Number of days to calculate uptime for
            
        Returns:
            Uptime percentage (0.0 to 100.0)
        """
        try:
            # Get provider incidents from last N days
            since_date = timezone.now() - timedelta(days=days)
            
            incidents = PaymentEvent.objects.filter(
                event_type='provider_incident',
                event_data__provider_name=provider_name,
                created_at__gte=since_date
            ).count()
            
            # Simple uptime calculation (this could be more sophisticated)
            total_checks = days * 24 * 12  # Assume checks every 5 minutes
            uptime_percentage = max(0.0, ((total_checks - incidents) / total_checks) * 100.0)
            
            return round(uptime_percentage, 2)
            
        except Exception as e:
            logger.error(f"Failed to calculate uptime for {provider_name}: {e}")
            return 0.0
    
    def generate_health_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive health report.
        
        Returns:
            Dict with health report data
        """
        summary = self.check_all_providers()
        
        report = {
            'summary': summary.dict(),
            'uptime_stats': {},
            'recommendations': [],
            'generated_at': timezone.now().isoformat()
        }
        
        # Calculate uptime for each provider
        for provider in summary.providers:
            uptime = self.get_provider_uptime(provider.provider_name)
            report['uptime_stats'][provider.provider_name] = uptime
        
        # Generate recommendations
        if summary.unhealthy_count > 0:
            unhealthy_providers = [p.provider_name for p in summary.providers if p.status == HealthStatus.UNHEALTHY]
            report['recommendations'].append({
                'type': 'critical',
                'message': f"Unhealthy providers detected: {', '.join(unhealthy_providers)}",
                'action': 'Check provider API status and credentials'
            })
        
        if summary.healthy_count < 2:
            report['recommendations'].append({
                'type': 'warning',
                'message': 'Low number of healthy providers',
                'action': 'Consider adding additional payment provider integrations'
            })
        
        return report


# Global health monitor instance
health_monitor = ProviderHealthMonitor()


def get_health_monitor() -> ProviderHealthMonitor:
    """Get global health monitor instance."""
    return health_monitor
