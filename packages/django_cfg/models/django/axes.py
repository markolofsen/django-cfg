"""
Django-Axes configuration model.

Brute-force protection settings with smart defaults for dev/prod.
"""

from typing import List, Optional

from pydantic import BaseModel, Field


class AxesConfig(BaseModel):
    """
    Django-Axes brute-force protection configuration.

    Provides type-safe configuration for django-axes with environment-aware defaults.

    Example:
        ```python
        # Custom configuration
        axes = AxesConfig(
            failure_limit=3,
            cooloff_time=48,
            only_user_failures=True
        )

        # Production-ready defaults
        axes = AxesConfig(enabled=True)
        ```
    """

    # === Basic Settings ===
    enabled: bool = Field(
        default=True,
        description="Enable/disable django-axes protection"
    )

    failure_limit: Optional[int] = Field(
        default=None,
        description="Number of failed attempts before lockout (None = auto: 10 dev, 5 prod)"
    )

    cooloff_time: Optional[int] = Field(
        default=None,
        description="Lockout duration in hours (None = auto: 1 dev, 24 prod)"
    )

    # === Lockout Behavior ===
    lock_out_at_failure: bool = Field(
        default=True,
        description="Lock out after reaching failure limit"
    )

    reset_on_success: bool = Field(
        default=True,
        description="Reset failure count after successful login"
    )

    only_user_failures: bool = Field(
        default=False,
        description="DEPRECATED in 8.0: Track only username (True) or IP+username (False). Use axes_handler instead."
    )

    # === UI/UX Settings ===
    lockout_template: Optional[str] = Field(
        default=None,
        description="Path to custom lockout template (e.g., 'lockout.html')"
    )

    lockout_url: Optional[str] = Field(
        default=None,
        description="URL to redirect to on lockout (e.g., '/account/locked/')"
    )

    # === Logging ===
    verbose: Optional[bool] = Field(
        default=None,
        description="Verbose logging (None = auto: True dev, False prod)"
    )

    enable_access_failure_log: bool = Field(
        default=True,
        description="Log access failures for security audit"
    )

    # === Proxy/Cloudflare Support ===
    ipware_proxy_count: int = Field(
        default=1,
        description="Number of proxies between client and server"
    )

    ipware_meta_precedence_order: List[str] = Field(
        default_factory=lambda: [
            'HTTP_X_FORWARDED_FOR',
            'HTTP_X_REAL_IP',
            'REMOTE_ADDR',
        ],
        description="Order of headers to extract real IP from proxy"
    )

    # === Whitelist/Blacklist ===
    allowed_ips: List[str] = Field(
        default_factory=list,
        description="IP addresses that bypass axes protection (e.g., ['192.168.1.100'])"
    )

    denied_ips: List[str] = Field(
        default_factory=list,
        description="IP addresses that are always blocked (e.g., ['10.0.0.2'])"
    )

    # === Advanced Settings ===
    cache_name: str = Field(
        default='default',
        description="Cache backend to use for axes (default or redis)"
    )

    use_user_agent: bool = Field(
        default=False,
        description="DEPRECATED in 8.0: Include user agent in lockout tracking"
    )

    username_form_field: str = Field(
        default='username',
        description="Form field name for username (default: 'username')"
    )

    def to_django_settings(self, is_production: bool, debug: bool) -> dict:
        """
        Convert to Django settings dictionary with environment-aware defaults.

        Args:
            is_production: Whether running in production mode
            debug: Whether debug mode is enabled

        Returns:
            Dictionary of Django-Axes settings
        """
        is_dev = debug or not is_production

        # Auto-configure failure_limit
        failure_limit = self.failure_limit if self.failure_limit is not None else (
            10 if is_dev else 5
        )

        # Auto-configure cooloff_time
        cooloff_time = self.cooloff_time if self.cooloff_time is not None else (
            1 if is_dev else 24
        )

        # Auto-configure verbose
        verbose = self.verbose if self.verbose is not None else is_dev

        settings = {
            'AXES_ENABLED': self.enabled,
            'AXES_FAILURE_LIMIT': failure_limit,
            'AXES_COOLOFF_TIME': cooloff_time,
            'AXES_LOCK_OUT_AT_FAILURE': self.lock_out_at_failure,
            'AXES_RESET_ON_SUCCESS': self.reset_on_success,
            # Skip deprecated settings in axes 8.0
            # 'AXES_ONLY_USER_FAILURES': self.only_user_failures,  # DEPRECATED
            # 'AXES_USE_USER_AGENT': self.use_user_agent,  # DEPRECATED
            'AXES_VERBOSE': verbose,
            'AXES_ENABLE_ACCESS_FAILURE_LOG': self.enable_access_failure_log,
            'AXES_IPWARE_PROXY_COUNT': self.ipware_proxy_count,
            'AXES_IPWARE_META_PRECEDENCE_ORDER': self.ipware_meta_precedence_order,
            'AXES_CACHE': self.cache_name,
            'AXES_USERNAME_FORM_FIELD': self.username_form_field,
        }

        # Add optional settings
        if self.lockout_template:
            settings['AXES_LOCKOUT_TEMPLATE'] = self.lockout_template

        if self.lockout_url:
            settings['AXES_LOCKOUT_URL'] = self.lockout_url

        if self.allowed_ips:
            settings['AXES_ALLOWED_IPS'] = self.allowed_ips

        if self.denied_ips:
            settings['AXES_DENIED_IPS'] = self.denied_ips

        return settings


__all__ = ["AxesConfig"]
