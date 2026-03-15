"""
Rate limiting configuration models for django_cfg.

Following CRITICAL_REQUIREMENTS.md:
- No raw Dict/Any usage - everything through Pydantic models
- Proper validation and type safety
- Environment-aware defaults
- Redis-backed for production scalability
"""

import re
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field, field_validator, model_validator


class RateLimitRule(BaseModel):
    """
    Individual rate limit rule for specific endpoints.

    Example:
        RateLimitRule(
            path_pattern="/api/auth/login/",
            rate="10/minute",
            key="ip",
        )
    """

    model_config = {
        "str_strip_whitespace": True,
        "validate_assignment": True,
        "extra": "forbid",
    }

    path_pattern: str = Field(
        ...,
        description="URL path pattern to match (supports * wildcards)",
        min_length=1,
    )

    rate: str = Field(
        ...,
        description="Rate limit string (e.g., '10/minute', '100/hour')",
    )

    key: Literal["ip", "user", "user_or_ip"] = Field(
        default="user_or_ip",
        description="Rate limit key type",
    )

    methods: Optional[List[str]] = Field(
        default=None,
        description="HTTP methods to apply rule to. None = all methods.",
    )

    @field_validator('rate')
    @classmethod
    def validate_rate(cls, v: str) -> str:
        """Validate rate format."""
        pattern = r'^\d+/(second|sec|s|minute|min|m|hour|hr|h|day|d)$'
        if not re.match(pattern, v.lower()):
            raise ValueError(
                f"Invalid rate format: {v}. "
                "Expected format: 'limit/period' (e.g., '100/hour', '60/minute')"
            )
        return v.lower()

    @field_validator('methods')
    @classmethod
    def validate_methods(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        """Validate HTTP methods."""
        if v is None:
            return v

        valid_methods = {'GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'HEAD', 'OPTIONS'}
        normalized = [m.upper() for m in v]

        invalid = set(normalized) - valid_methods
        if invalid:
            raise ValueError(f"Invalid HTTP methods: {invalid}")

        return normalized


class RateLimitConfig(BaseModel):
    """
    Comprehensive rate limiting configuration.

    Features:
    - Global default rates for anonymous and authenticated users
    - Endpoint-specific custom rules
    - Redis backend for distributed rate limiting
    - DRF throttle integration

    Example:
        RateLimitConfig(
            enabled=True,
            default_anon_rate="100/hour",
            default_user_rate="1000/hour",
            custom_rules=[
                RateLimitRule(path_pattern="/api/auth/login/", rate="10/minute", key="ip"),
                RateLimitRule(path_pattern="/api/ai/*", rate="20/minute", key="user"),
            ],
        )
    """

    model_config = {
        "str_strip_whitespace": True,
        "validate_assignment": True,
        "extra": "forbid",
    }

    # Global enable/disable
    enabled: bool = Field(
        default=True,
        description="Enable rate limiting globally",
    )

    # Default rates
    default_anon_rate: str = Field(
        default="100/hour",
        description="Default rate limit for anonymous users",
    )

    default_user_rate: str = Field(
        default="1000/hour",
        description="Default rate limit for authenticated users",
    )

    # Backend configuration
    backend: Literal["redis", "cache", "memory"] = Field(
        default="redis",
        description=(
            "Rate limit storage backend. "
            "'redis' recommended for production, "
            "'memory' only for single-worker development."
        ),
    )

    # Cache key prefix
    key_prefix: str = Field(
        default="ratelimit",
        description="Prefix for rate limit cache keys",
        max_length=50,
    )

    # Custom endpoint rules
    custom_rules: List[RateLimitRule] = Field(
        default_factory=list,
        description="Endpoint-specific rate limit rules",
    )

    # Response behavior
    block_on_exceed: bool = Field(
        default=True,
        description="Return 429 response when limit exceeded. If False, just mark request.",
    )

    include_headers: bool = Field(
        default=True,
        description="Include X-RateLimit-* headers in responses",
    )

    # Logging
    log_exceeded: bool = Field(
        default=True,
        description="Log when rate limits are exceeded",
    )

    @field_validator('default_anon_rate', 'default_user_rate')
    @classmethod
    def validate_rate(cls, v: str) -> str:
        """Validate rate format."""
        pattern = r'^\d+/(second|sec|s|minute|min|m|hour|hr|h|day|d)$'
        if not re.match(pattern, v.lower()):
            raise ValueError(
                f"Invalid rate format: {v}. "
                "Expected format: 'limit/period' (e.g., '100/hour')"
            )
        return v.lower()

    @field_validator('key_prefix')
    @classmethod
    def validate_key_prefix(cls, v: str) -> str:
        """Validate cache key prefix."""
        if not v.replace('_', '').replace('-', '').replace(':', '').isalnum():
            raise ValueError(
                "Key prefix must contain only alphanumeric characters, "
                "underscores, hyphens, and colons"
            )
        return v

    @model_validator(mode='after')
    def validate_config(self) -> 'RateLimitConfig':
        """Validate configuration consistency."""
        # Warn about memory backend in production-like configs
        if self.backend == "memory" and len(self.custom_rules) > 10:
            # Many rules suggests production use - memory won't scale
            pass  # Just a note, not an error

        return self

    def to_django_settings(self) -> Dict[str, Any]:
        """
        Convert to Django settings.

        Returns:
            Dictionary of Django settings for rate limiting
        """
        if not self.enabled:
            return {}

        settings = {
            'RATE_LIMIT_ENABLED': True,
            'RATE_LIMIT_KEY_PREFIX': self.key_prefix,
            'RATE_LIMIT_BACKEND': self.backend,
            'RATE_LIMIT_BLOCK_ON_EXCEED': self.block_on_exceed,
            'RATE_LIMIT_INCLUDE_HEADERS': self.include_headers,
            'RATE_LIMIT_LOG_EXCEEDED': self.log_exceeded,
            'RATE_LIMIT_DEFAULT_ANON': self.default_anon_rate,
            'RATE_LIMIT_DEFAULT_USER': self.default_user_rate,
            'RATE_LIMIT_CUSTOM_RULES': [
                rule.model_dump() for rule in self.custom_rules
            ],
        }

        return settings

    def to_drf_throttle_settings(self) -> Dict[str, Any]:
        """
        Convert to DRF throttle settings.

        Returns:
            REST_FRAMEWORK throttle configuration
        """
        if not self.enabled:
            return {}

        return {
            'DEFAULT_THROTTLE_CLASSES': [
                'rest_framework.throttling.AnonRateThrottle',
                'rest_framework.throttling.UserRateThrottle',
            ],
            'DEFAULT_THROTTLE_RATES': {
                'anon': self.default_anon_rate,
                'user': self.default_user_rate,
            },
        }

    def get_rule_for_path(self, path: str, method: str = "GET") -> Optional[RateLimitRule]:
        """
        Find matching rate limit rule for a path.

        Args:
            path: URL path to match
            method: HTTP method

        Returns:
            Matching RateLimitRule or None
        """
        for rule in self.custom_rules:
            # Check method filter
            if rule.methods and method.upper() not in rule.methods:
                continue

            # Convert wildcard pattern to regex
            pattern = rule.path_pattern.replace('*', '.*')
            if re.match(f'^{pattern}$', path):
                return rule

        return None


# Export
__all__ = [
    "RateLimitConfig",
    "RateLimitRule",
]
