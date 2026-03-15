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

        Security mode priority:
        1. Production mode (is_production=True) → strict security (whitelist only)
        2. Development mode (is_development=True) → relaxed security (wide port ranges)

        IMPORTANT: Production mode always uses strict security regardless of debug flag.
        The debug flag should only affect logging/error pages, NOT security settings.

        Returns:
            Dictionary with all security-related Django settings

        Example:
            >>> config = DjangoConfig(project_name="Test", ...)
            >>> builder = SecurityBuilder(config)
            >>> settings = builder.build_security_settings()
            >>> 'ALLOWED_HOSTS' in settings
            True
        """
        # Get all security domains including auto-extracted from api_url and site_url
        all_domains = self._get_all_security_domains()

        # Production mode has highest priority for security settings
        # Debug flag should NOT weaken security in production
        if self.config.is_production:
            return self._prod_mode_universal(all_domains)
        else:
            return self._dev_mode_universal()

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
        # Get all security domains including auto-extracted from api_url and site_url
        all_domains = self._get_all_security_domains()
        normalized = self._normalize_domains(all_domains)

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

            # === Django-Axes: Brute-force protection ===
            **self._get_axes_settings(is_dev=True),

            # === Authentication backends (django-axes + default) ===
            'AUTHENTICATION_BACKENDS': [
                'axes.backends.AxesStandaloneBackend',  # django-axes must be first
                'django.contrib.auth.backends.ModelBackend',  # Default Django auth
            ],
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

        # Check if localhost is in security_domains for universal CORS regex
        has_localhost = any(
            domain in ('localhost', '127.0.0.1')
            for domain in security_domains
        )

        return {
            # === CORS: Only security_domains ===
            # Docker-to-Docker requests don't have Origin header - CORS doesn't apply
            'CORS_ALLOW_ALL_ORIGINS': False,
            'CORS_ALLOW_CREDENTIALS': True,
            'CORS_ALLOWED_ORIGINS': normalized['cors_origins'],
            'CORS_ALLOWED_ORIGIN_REGEXES': self._get_localhost_cors_regexes() if has_localhost else [],
            'CORS_ALLOW_HEADERS': self.config.cors_allow_headers,

            # === ALLOWED_HOSTS: security_domains + Docker patterns ===
            # Need to allow internal health checks, but safely
            'ALLOWED_HOSTS': self._get_prod_allowed_hosts(normalized['allowed_hosts']),

            # === CSRF: Only security_domains ===
            'CSRF_TRUSTED_ORIGINS': normalized['csrf_origins'] + (
                self._get_localhost_csrf_origins() if has_localhost else []
            ),

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

            # === Django-Axes: Brute-force protection ===
            **self._get_axes_settings(is_dev=False),

            # === Authentication backends (django-axes + default) ===
            'AUTHENTICATION_BACKENDS': [
                'axes.backends.AxesStandaloneBackend',  # django-axes must be first
                'django.contrib.auth.backends.ModelBackend',  # Default Django auth
            ],
        }

    def _get_prod_allowed_hosts(self, domain_hosts: List[str]) -> List[str]:
        """
        Production ALLOWED_HOSTS with Docker support.

        In production we're strict, but need to allow:
        - Public domains (security_domains)
        - Docker internal service names (auto-detected)
        - Docker health checks (internal IPs, if needed)

        Problem: If we allow all IPs - insecure!
        Solution: Allow only private IP ranges (RFC 1918) + internal service names.

        Args:
            domain_hosts: List of normalized domain hostnames

        Returns:
            List of allowed hosts including Docker support
        """
        allowed_hosts = domain_hosts.copy()

        # Check if running in Docker
        if self._is_running_in_docker():
            # Auto-detect internal service names from configuration
            internal_services = self._get_internal_service_names()
            allowed_hosts.extend(internal_services)

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

    def _get_internal_service_names(self) -> List[str]:
        """
        Auto-detect Docker internal service names from configuration.

        Extracts service hostnames from internal URLs:
        - Centrifugo API URL (centrifugo_api_url)
        - gRPC internal URL (grpc.internal_url if available)
        - Any other internal service URLs

        Example:
            centrifugo_api_url = "http://djangocfg-centrifugo:8000/api"
            → Extracts: "djangocfg-centrifugo"

        Returns:
            List of internal service hostnames (without port)
        """
        service_names = []

        # Extract from Centrifugo config
        if hasattr(self.config, 'centrifugo') and self.config.centrifugo:
            centrifugo_cfg = self.config.centrifugo

            # Extract from centrifugo_api_url (for Django → Centrifugo publishing)
            if hasattr(centrifugo_cfg, 'centrifugo_api_url'):
                api_url = centrifugo_cfg.centrifugo_api_url
                hostname = self._extract_hostname_from_url(api_url)
                if hostname and self._is_internal_service_name(hostname):
                    service_names.append(hostname)

        # Extract from gRPC config
        if hasattr(self.config, 'grpc') and self.config.grpc:
            grpc_cfg = self.config.grpc

            # Extract from internal_url (for container-to-container gRPC)
            if hasattr(grpc_cfg, 'internal_url'):
                internal_url = grpc_cfg.internal_url
                # Handle formats: "djangocfg-grpc:50051" or "http://djangocfg-grpc:50051"
                hostname = self._extract_hostname_from_url(internal_url, allow_no_protocol=True)
                if hostname and self._is_internal_service_name(hostname):
                    service_names.append(hostname)

        # Deduplicate while preserving order
        return list(dict.fromkeys(service_names))

    def _extract_hostname_from_url(self, url: str, allow_no_protocol: bool = False) -> str:
        """
        Extract hostname from URL.

        Args:
            url: URL string (e.g., "http://djangocfg-api:8000/path" or "djangocfg-grpc:50051")
            allow_no_protocol: Allow URLs without protocol (for gRPC addresses)

        Returns:
            Hostname without port (e.g., "djangocfg-api")
        """
        if not url:
            return ""

        try:
            # Handle URLs without protocol (e.g., "djangocfg-grpc:50051")
            if allow_no_protocol and not url.startswith(("http://", "https://")):
                # Split by : to get hostname:port
                hostname_port = url.split('/')[0]  # Remove path if any
                hostname = hostname_port.split(':')[0]  # Remove port
                return hostname.strip()

            # Standard URL parsing
            parsed = urlparse(url if url.startswith(("http://", "https://")) else f"http://{url}")
            hostname = parsed.hostname or parsed.netloc.split(':')[0]
            return hostname.strip() if hostname else ""
        except Exception:
            return ""

    def _is_internal_service_name(self, hostname: str) -> bool:
        """
        Check if hostname is an internal Docker/Kubernetes service name.

        Internal service names typically:
        - Don't contain dots (unlike domains: example.com)
        - Are not IPs (172.x.x.x, 192.168.x.x)
        - Are not localhost/127.0.0.1

        Examples:
            "djangocfg-api" → True (internal service)
            "djangocfg-grpc" → True (internal service)
            "api.example.com" → False (external domain)
            "192.168.1.10" → False (IP address)
            "localhost" → False (localhost)

        Args:
            hostname: Hostname to check

        Returns:
            True if internal service name, False otherwise
        """
        if not hostname:
            return False

        hostname = hostname.lower().strip()

        # Exclude localhost
        if hostname in ('localhost', '127.0.0.1'):
            return False

        # Exclude IP addresses (simple check)
        if hostname.replace('.', '').isdigit():
            return False

        # Exclude domains with dots (external domains like api.example.com)
        # Keep Kubernetes service names like service.namespace.svc.cluster.local
        if '.' in hostname:
            # Allow .cluster.local and .svc (Kubernetes)
            if hostname.endswith(('.cluster.local', '.svc')):
                return True
            # Otherwise it's an external domain
            return False

        # If no dots and not excluded - it's an internal service name
        # Examples: djangocfg-api, djangocfg-grpc, postgres, redis
        return True

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
        - All dev ports from 3000 to 10000 (covers all common dev servers)
        - localhost and 127.0.0.1

        Docker IPs NOT needed - CSRF checks Referer from browser!

        Returns:
            List of dev CSRF origins
        """
        # Wide port range for development (3000-10000)
        # Covers: Next.js, React, Vite, Angular, Vue, Django, Flask, etc.
        dev_ports = range(3000, 10001)

        origins = []
        for port in dev_ports:
            origins.extend([
                f"http://localhost:{port}",
                f"http://127.0.0.1:{port}",
            ])

        return origins

    def _get_localhost_cors_regexes(self) -> List[str]:
        """
        Universal localhost CORS regex for ANY port.

        When localhost/127.0.0.1 is in security_domains, allow all ports via regex.
        This is much simpler than maintaining a list of specific ports.

        Matches:
        - http://localhost:3000
        - http://localhost:8000
        - http://127.0.0.1:7301
        - Any other localhost port

        Returns:
            List of regex patterns for CORS_ALLOWED_ORIGIN_REGEXES
        """
        return [
            r'^http://localhost:\d+$',      # localhost with any port
            r'^http://127\.0\.0\.1:\d+$',   # 127.0.0.1 with any port
        ]

    def _get_localhost_csrf_origins(self) -> List[str]:
        """
        Localhost CSRF origins with wide port range for development.

        CSRF doesn't support regex, so we need to list specific ports.
        Covers all development ports from 3000 to 10000.

        Note: CORS uses regex for ALL ports via CORS_ALLOWED_ORIGIN_REGEXES.
        CSRF needs explicit port list - using same range as dev mode (3000-10000).

        Returns:
            List of localhost origins with development ports for CSRF
        """
        # Wide port range for development (3000-10000)
        # Covers: Next.js, React, Vite, Angular, Vue, Django, Flask, etc.
        dev_ports = range(3000, 10001)

        origins = []
        for port in dev_ports:
            origins.extend([
                f"http://localhost:{port}",
                f"http://127.0.0.1:{port}",
            ])

        return origins

    def _get_axes_settings(self, is_dev: bool) -> Dict[str, Any]:
        """
        Get Django-Axes settings (custom config or smart defaults).

        Args:
            is_dev: Whether running in development mode

        Returns:
            Dictionary with Django-Axes settings
        """
        # If user provided custom AxesConfig, use it
        if self.config.axes:
            return self.config.axes.to_django_settings(
                is_production=self.config.is_production,
                debug=self.config.debug
            )

        # Otherwise, use smart defaults
        return self._get_default_axes_settings(is_dev)

    def _get_default_axes_settings(self, is_dev: bool) -> Dict[str, Any]:
        """
        Get default Django-Axes settings based on environment.

        Args:
            is_dev: Whether running in development mode

        Returns:
            Dictionary with default Django-Axes settings
        """
        if is_dev:
            return {
                'AXES_ENABLED': True,
                'AXES_FAILURE_LIMIT': 10,  # More attempts in dev
                'AXES_COOLOFF_TIME': 1,  # 1 hour lockout
                'AXES_LOCK_OUT_AT_FAILURE': True,
                'AXES_RESET_ON_SUCCESS': True,
                # AXES_ONLY_USER_FAILURES deprecated in 8.0
                'AXES_LOCKOUT_TEMPLATE': None,  # Use default lockout response
                'AXES_LOCKOUT_URL': None,  # No custom lockout URL
                'AXES_VERBOSE': True,  # Log lockout events in dev
                'AXES_ENABLE_ACCESS_FAILURE_LOG': True,
                'AXES_IPWARE_PROXY_COUNT': 1,
                'AXES_IPWARE_META_PRECEDENCE_ORDER': [
                    'HTTP_X_FORWARDED_FOR',
                    'HTTP_X_REAL_IP',
                    'REMOTE_ADDR',
                ],
            }
        else:
            return {
                'AXES_ENABLED': True,
                'AXES_FAILURE_LIMIT': 5,  # Stricter limit in production
                'AXES_COOLOFF_TIME': 24,  # 24 hours lockout in production
                'AXES_LOCK_OUT_AT_FAILURE': True,
                'AXES_RESET_ON_SUCCESS': True,
                # AXES_ONLY_USER_FAILURES deprecated in 8.0
                'AXES_LOCKOUT_TEMPLATE': None,  # Use default lockout response
                'AXES_LOCKOUT_URL': None,  # No custom lockout URL
                'AXES_VERBOSE': False,  # Less verbose logging in production
                'AXES_ENABLE_ACCESS_FAILURE_LOG': True,  # Log failures for security audit
                # Proxy/Cloudflare support - get real IP from X-Forwarded-For
                'AXES_IPWARE_PROXY_COUNT': 1,  # Number of proxies between client and server
                'AXES_IPWARE_META_PRECEDENCE_ORDER': [
                    'HTTP_X_FORWARDED_FOR',  # Cloudflare, nginx, traefik
                    'HTTP_X_REAL_IP',        # Alternative proxy header
                    'REMOTE_ADDR',           # Fallback to direct connection
                ],
            }

    def _get_all_security_domains(self) -> List[str]:
        """
        Get all security domains including auto-extracted from api_url and site_url.

        Automatically extracts domains from:
        - config.security_domains (user-defined)
        - config.api_url (backend URL)
        - config.site_url (frontend URL)

        Smart deduplication by hostname:port (ignoring protocol differences).

        Returns:
            List of all unique security domains

        Example:
            >>> config = DjangoConfig(
            ...     api_url="https://api.example.com",
            ...     site_url="https://example.com",
            ...     security_domains=["localhost"]
            ... )
            >>> builder = SecurityBuilder(config)
            >>> domains = builder._get_all_security_domains()
            >>> len([d for d in domains if 'api.example.com' in d])
            1
            >>> len([d for d in domains if 'example.com' in d and 'api' not in d])
            1
        """
        domains = list(self.config.security_domains)

        # Extract domain from api_url
        if self.config.api_url:
            try:
                parsed = urlparse(self.config.api_url)
                if parsed.netloc:
                    # Add full URL with protocol and port if present
                    if parsed.port:
                        domains.append(f"{parsed.scheme}://{parsed.hostname}:{parsed.port}")
                    else:
                        domains.append(f"{parsed.scheme}://{parsed.hostname}")
            except Exception:
                pass  # Ignore parsing errors

        # Extract domain from site_url
        if self.config.site_url:
            try:
                parsed = urlparse(self.config.site_url)
                if parsed.netloc:
                    # Add full URL with protocol and port if present
                    if parsed.port:
                        domains.append(f"{parsed.scheme}://{parsed.hostname}:{parsed.port}")
                    else:
                        domains.append(f"{parsed.scheme}://{parsed.hostname}")
            except Exception:
                pass  # Ignore parsing errors

        # Smart deduplication: track by hostname:port, keep first occurrence with protocol
        seen_hostports = {}  # hostname:port -> full domain string
        unique_domains = []

        for domain in domains:
            if not domain or not domain.strip():
                continue

            domain = domain.strip()

            # Normalize for comparison: parse to get hostname:port key
            try:
                # Add protocol if missing for parsing
                if not domain.startswith(("http://", "https://")):
                    parse_domain = f"http://{domain}"
                else:
                    parse_domain = domain

                parsed = urlparse(parse_domain)
                hostname = (parsed.hostname or parsed.netloc.split(':')[0]).lower()  # Lowercase for case-insensitive comparison
                port = parsed.port

                # Create unique key: hostname:port or just hostname (lowercase for case-insensitivity)
                if port:
                    hostport_key = f"{hostname}:{port}"
                else:
                    hostport_key = hostname

                # Only add if we haven't seen this hostname:port combination
                if hostport_key not in seen_hostports:
                    # Normalize domain to lowercase but preserve original format (with/without protocol)
                    # Reconstruct normalized domain
                    if domain.startswith(("http://", "https://")):
                        # Has protocol - normalize hostname part only
                        if port:
                            normalized_domain = f"{parsed.scheme}://{hostname}:{port}"
                        else:
                            normalized_domain = f"{parsed.scheme}://{hostname}"
                    else:
                        # No protocol - just lowercase the whole thing
                        normalized_domain = domain.lower()

                    seen_hostports[hostport_key] = normalized_domain
                    unique_domains.append(normalized_domain)

            except Exception:
                # If parsing fails, use simple string deduplication with lowercase
                domain_lower = domain.lower()
                if domain_lower not in seen_hostports.values():
                    seen_hostports[domain_lower] = domain_lower
                    unique_domains.append(domain_lower)

        return unique_domains

    def _normalize_domains(self, domains: List[str]) -> Dict[str, List[str]]:
        """
        Normalize domains in ANY format.

        Accepts domains in any format:
        - "example.com" → https://example.com (CORS), example.com (ALLOWED_HOSTS)
        - "https://api.example.com" → https://api.example.com (as is)
        - "http://staging.com:8080" → http://staging.com:8080 (as is)
        - "192.168.1.10" → http://192.168.1.10
        - "localhost" → http://localhost (regex handles all ports via CORS_ALLOWED_ORIGIN_REGEXES)

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
