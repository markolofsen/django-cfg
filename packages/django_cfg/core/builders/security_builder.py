"""
Security settings builder for Django-CFG.

Single Responsibility: Build security-related Django settings (ALLOWED_HOSTS, CORS, etc.).
Universal logic for Docker + bare metal in dev and prod.

Size: ~250 lines (focused on security with Docker awareness)
"""

from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List
from urllib.parse import urlparse

if TYPE_CHECKING:
    from ..base.config_model import DjangoConfig


class SecurityBuilder:
    """
    Builds security-related settings from DjangoConfig.

    Universal logic for Docker and bare metal in both dev and prod environments.

    Responsibilities:
    - Generate ALLOWED_HOSTS from security_domains
    - Configure CORS settings (open in dev, strict in prod)
    - Configure CSRF trusted origins
    - Handle SSL redirect configuration
    - Auto-detect Docker environment
    - Normalize domain formats (with/without protocol)

    Example:
        ```python
        builder = SecurityBuilder(config)
        settings = builder.build_security_settings()
        ```
    """

    def __init__(self, config: "DjangoConfig"):
        """
        Initialize builder with configuration.

        Args:
            config: DjangoConfig instance
        """
        self.config = config

    def build_security_settings(self) -> Dict[str, Any]:
        """
        Build complete security settings dictionary.

        Returns:
            Dictionary with all security-related Django settings

        Example:
            >>> config = DjangoConfig(project_name="Test", ...)
            >>> builder = SecurityBuilder(config)
            >>> settings = builder.build_security_settings()
            >>> 'ALLOWED_HOSTS' in settings
            True
        """
        if self.config.is_development or self.config.debug:
            return self._dev_mode_universal()
        else:
            return self._prod_mode_universal(self.config.security_domains)

    def build_allowed_hosts(self) -> List[str]:
        """
        Build ALLOWED_HOSTS from security_domains.

        DEPRECATED: Use build_security_settings() instead.
        Kept for backward compatibility.

        Returns:
            List of allowed host patterns
        """
        settings = self.build_security_settings()
        return settings.get('ALLOWED_HOSTS', ['*'])

    def _dev_mode_universal(self) -> Dict[str, Any]:
        """
        DEVELOPMENT mode: Fully open (Docker + bare metal).

        Covers:
        - localhost any port (bare metal)
        - Docker internal IPs (172.x.x.x, 192.168.x.x, 10.x.x.x)
        - Kubernetes IPs
        - Health checks
        - Any test domains

        Returns:
            Dictionary with dev security settings
        """
        normalized = self._normalize_domains(self.config.security_domains)

        # Get all dev CORS origins (popular ports + security_domains)
        dev_cors_origins = self._get_dev_csrf_origins() + normalized['cors_origins']

        return {
            # === CORS: Whitelist mode with credentials support ===
            # Use whitelist instead of wildcard to support credentials: 'include'
            'CORS_ALLOW_ALL_ORIGINS': False,
            'CORS_ALLOW_CREDENTIALS': True,
            'CORS_ALLOWED_ORIGINS': dev_cors_origins,
            'CORS_ALLOW_HEADERS': self.config.cors_allow_headers,

            # === ALLOWED_HOSTS: Accept everything ===
            # Docker health checks, internal IPs, localhost, all!
            'ALLOWED_HOSTS': ['*'],

            # === CSRF: Popular origins + security_domains ===
            # CSRF only checks browser requests
            # Docker-to-Docker requests don't have Referer
            'CSRF_TRUSTED_ORIGINS': dev_cors_origins,

            # === Security: All disabled ===
            'SECURE_SSL_REDIRECT': False,
            'SESSION_COOKIE_SECURE': False,
            'CSRF_COOKIE_SECURE': False,
            'SECURE_HSTS_SECONDS': 0,
            'SECURE_HSTS_INCLUDE_SUBDOMAINS': False,
            'SECURE_HSTS_PRELOAD': False,
            'SECURE_CONTENT_TYPE_NOSNIFF': False,
            'SECURE_BROWSER_XSS_FILTER': False,
            'X_FRAME_OPTIONS': 'SAMEORIGIN',
        }

    def _prod_mode_universal(self, security_domains: List[str]) -> Dict[str, Any]:
        """
        PRODUCTION mode: Strict whitelist + Docker support.

        In production Docker is also used, but:
        - Public requests go through domains (nginx/traefik)
        - Internal Docker-to-Docker requests don't check CORS
        - Health checks must work (ALLOWED_HOSTS)

        Args:
            security_domains: List of production domains

        Returns:
            Dictionary with prod security settings

        Raises:
            ConfigurationError: If security_domains is empty
        """
        if not security_domains:
            from ..exceptions import ConfigurationError
            raise ConfigurationError(
                "security_domains REQUIRED in production!",
                suggestions=[
                    "Add domains: security_domains: ['example.com', 'api.example.com']"
                ]
            )

        normalized = self._normalize_domains(security_domains)

        return {
            # === CORS: Only security_domains ===
            # Docker-to-Docker requests don't have Origin header - CORS doesn't apply
            'CORS_ALLOW_ALL_ORIGINS': False,
            'CORS_ALLOW_CREDENTIALS': True,
            'CORS_ALLOWED_ORIGINS': normalized['cors_origins'],
            'CORS_ALLOW_HEADERS': self.config.cors_allow_headers,

            # === ALLOWED_HOSTS: security_domains + Docker patterns ===
            # Need to allow internal health checks, but safely
            'ALLOWED_HOSTS': self._get_prod_allowed_hosts(normalized['allowed_hosts']),

            # === CSRF: Only security_domains ===
            'CSRF_TRUSTED_ORIGINS': normalized['csrf_origins'],

            # === Security: All enabled ===
            'SECURE_SSL_REDIRECT': self._should_enable_ssl_redirect(),
            'SESSION_COOKIE_SECURE': True,
            'CSRF_COOKIE_SECURE': True,
            'SECURE_HSTS_SECONDS': 31536000,
            'SECURE_HSTS_INCLUDE_SUBDOMAINS': True,
            'SECURE_HSTS_PRELOAD': True,
            'SECURE_CONTENT_TYPE_NOSNIFF': True,
            'SECURE_BROWSER_XSS_FILTER': True,
            'X_FRAME_OPTIONS': 'DENY',
        }

    def _get_prod_allowed_hosts(self, domain_hosts: List[str]) -> List[str]:
        """
        Production ALLOWED_HOSTS with Docker support.

        In production we're strict, but need to allow:
        - Public domains (security_domains)
        - Docker health checks (internal IPs, if needed)

        Problem: If we allow all IPs - insecure!
        Solution: Allow only private IP ranges (RFC 1918).

        Args:
            domain_hosts: List of normalized domain hostnames

        Returns:
            List of allowed hosts including Docker support
        """
        allowed_hosts = domain_hosts.copy()

        # Check if running in Docker
        if self._is_running_in_docker():
            # Allow Docker/Kubernetes health checks
            # Use regex for private IPs (RFC 1918)
            allowed_hosts.extend([
                # Docker bridge networks (172.16.0.0/12)
                r'^172\.(1[6-9]|2[0-9]|3[0-1])\.\d{1,3}\.\d{1,3}$',
                # Private networks (192.168.0.0/16)
                r'^192\.168\.\d{1,3}\.\d{1,3}$',
                # Private networks (10.0.0.0/8)
                r'^10\.\d{1,3}\.\d{1,3}\.\d{1,3}$',
                # Kubernetes service names (optional)
                '.cluster.local',
                '.svc',
            ])

        return allowed_hosts

    def _is_running_in_docker(self) -> bool:
        """
        Detect if application is running in Docker.

        Checks:
        1. File /.dockerenv exists
        2. /proc/1/cgroup contains "docker"
        3. Environment variable DOCKER=true or KUBERNETES_SERVICE_HOST exists

        Returns:
            True if running in Docker/Kubernetes, False otherwise
        """
        import os

        # Method 1: /.dockerenv file
        if Path('/.dockerenv').exists():
            return True

        # Method 2: cgroup contains docker/kubepods
        try:
            with open('/proc/1/cgroup', 'r') as f:
                content = f.read()
                if 'docker' in content or 'kubepods' in content:
                    return True
        except (FileNotFoundError, PermissionError):
            pass

        # Method 3: Environment variables
        if os.getenv('DOCKER') == 'true' or os.getenv('KUBERNETES_SERVICE_HOST'):
            return True

        return False

    def _should_enable_ssl_redirect(self) -> bool:
        """
        Determine if SSL redirect should be enabled.

        By default: DISABLED (most common case - behind reverse proxy).

        In 99% of cases, SSL termination happens at:
        - Reverse proxy (nginx/traefik/caddy)
        - Cloud provider (Cloudflare/AWS ALB/GCP Load Balancer)
        - Docker/Kubernetes ingress

        Enable explicitly with ssl_redirect=True only if Django handles SSL directly
        (rare case: bare metal without proxy).

        Returns:
            True if SSL redirect explicitly enabled, False otherwise (default)
        """
        # Use explicit config value if provided
        if self.config.ssl_redirect is not None:
            return self.config.ssl_redirect

        # Default: DISABLED (assume reverse proxy handles SSL)
        # This works for: Docker, nginx, Cloudflare, AWS ALB, etc.
        return False

    def _get_dev_csrf_origins(self) -> List[str]:
        """
        Smart list of dev CSRF origins.

        Covers:
        - Popular dev ports
        - localhost and 127.0.0.1

        Docker IPs NOT needed - CSRF checks Referer from browser!

        Returns:
            List of dev CSRF origins
        """
        popular_ports = [
            3000,  # React/Next.js default
            5173,  # Vite default
            5174,  # Vite preview
            8080,  # Vue/Spring Boot
            4200,  # Angular
            8000,  # Django default
            8001,  # Django alternative
        ]

        origins = []
        for port in popular_ports:
            origins.extend([
                f"http://localhost:{port}",
                f"http://127.0.0.1:{port}",
            ])

        return origins

    def _normalize_domains(self, domains: List[str]) -> Dict[str, List[str]]:
        """
        Normalize domains in ANY format.

        Accepts domains in any format:
        - "example.com" → https://example.com (CORS), example.com (ALLOWED_HOSTS)
        - "https://api.example.com" → https://api.example.com (as is)
        - "http://staging.com:8080" → http://staging.com:8080 (as is)
        - "192.168.1.10" → http://192.168.1.10

        Args:
            domains: List of domains in any format

        Returns:
            Dictionary with normalized domains for different settings:
            - 'allowed_hosts': Without protocol/port
            - 'cors_origins': With protocol
            - 'csrf_origins': With protocol
        """
        allowed_hosts = []
        cors_origins = []
        csrf_origins = []

        # Default protocol
        default_protocol = "https" if self.config.is_production else "http"

        for domain in domains:
            if not domain or not domain.strip():
                continue

            domain = domain.strip()

            # Add protocol if missing
            if not domain.startswith(("http://", "https://")):
                full_url = f"{default_protocol}://{domain}"
            else:
                full_url = domain

            try:
                parsed = urlparse(full_url)

                # ALLOWED_HOSTS - only hostname (no protocol, no port)
                hostname = parsed.hostname or parsed.netloc.split(':')[0]
                if hostname:
                    allowed_hosts.append(hostname)

                # CORS/CSRF - full URL with protocol
                if parsed.port:
                    origin = f"{parsed.scheme}://{parsed.hostname}:{parsed.port}"
                else:
                    origin = f"{parsed.scheme}://{parsed.hostname}"

                cors_origins.append(origin)
                csrf_origins.append(origin)

            except Exception as e:
                import warnings
                warnings.warn(
                    f"Failed to parse domain '{domain}': {e}",
                    UserWarning,
                    stacklevel=2
                )
                continue

        return {
            'allowed_hosts': list(set(filter(None, allowed_hosts))),
            'cors_origins': list(set(filter(None, cors_origins))),
            'csrf_origins': list(set(filter(None, csrf_origins))),
        }


# Export builder
__all__ = ["SecurityBuilder"]
