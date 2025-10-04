"""
Security settings builder for Django-CFG.

Single Responsibility: Build security-related Django settings (ALLOWED_HOSTS, CORS, etc.).
Extracted from original config.py for better maintainability.

Size: ~100 lines (focused on security)
"""

from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from ..base.config_model import DjangoConfig


class SecurityBuilder:
    """
    Builds security-related settings from DjangoConfig.

    Responsibilities:
    - Generate ALLOWED_HOSTS from security_domains
    - Add localhost/127.0.0.1 in development
    - Prepare CORS settings
    - Handle SSL redirect configuration

    Example:
        ```python
        builder = SecurityBuilder(config)
        allowed_hosts = builder.build_allowed_hosts()
        ```
    """

    def __init__(self, config: "DjangoConfig"):
        """
        Initialize builder with configuration.

        Args:
            config: DjangoConfig instance
        """
        self.config = config

    def build_allowed_hosts(self) -> List[str]:
        """
        Build ALLOWED_HOSTS from security_domains.

        In development:
        - Adds localhost, 127.0.0.1, [::1]
        - Adds security_domains if provided

        In production:
        - Uses only security_domains
        - Warning if security_domains is empty

        Returns:
            List of allowed host patterns

        Example:
            >>> config = DjangoConfig(
            ...     env_mode=EnvironmentMode.PRODUCTION,
            ...     security_domains=["example.com", "api.example.com"]
            ... )
            >>> builder = SecurityBuilder(config)
            >>> hosts = builder.build_allowed_hosts()
            >>> "example.com" in hosts
            True
        """
        allowed_hosts = []

        # Development mode: add localhost by default
        if self.config.is_development:
            allowed_hosts.extend([
                "localhost",
                "127.0.0.1",
                "[::1]",  # IPv6 localhost
            ])

        # Add security domains (both dev and prod)
        allowed_hosts.extend(self.config.security_domains)

        # Production warning if no domains configured
        if self.config.is_production and not self.config.security_domains:
            import warnings
            warnings.warn(
                "No security_domains configured in production mode. "
                "Add domains to security_domains field for proper security.",
                UserWarning,
                stacklevel=2,
            )
            # In production without domains, allow all (not recommended)
            allowed_hosts = ["*"]

        return allowed_hosts


# Export builder
__all__ = ["SecurityBuilder"]
