---
title: DjangoConfig Base Class
description: Complete reference for DjangoConfig base configuration class
sidebar_label: DjangoConfig
sidebar_position: 2
---

# DjangoConfig Base Class

The `DjangoConfig` base class is the foundation of Django-CFG's type-safe configuration system.

## Overview

`DjangoConfig` extends Pydantic's `BaseModel` to provide:

- ✅ **Type-safe** configuration with Pydantic v2 validation
- ✅ **Environment detection** (development, staging, production)
- ✅ **Smart defaults** based on environment
- ✅ **Django settings generation** from configuration models
- ✅ **YAML configuration** support
- ✅ **Path resolution** for project structure

## Complete Class Definition

```python
from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Dict, List, Any, Optional, Union
from pathlib import Path

class DjangoConfig(BaseModel):
    """
    Base configuration class for Django projects.
    Handles all Django settings generation and validation.
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="allow",
        env_prefix="DJANGO_",
        populate_by_name=True,
        validate_default=True,
    )

    # === Core Django Settings ===
    secret_key: str = Field(
        ...,
        description="Django SECRET_KEY",
        min_length=50
    )
    debug: bool = Field(
        default=False,
        description="Django DEBUG setting"
    )
    debug_warnings: bool = Field(
        default=False,
        description="Enable detailed warnings traceback (shows full stack trace for RuntimeWarnings)"
    )

    # Note: ALLOWED_HOSTS is auto-generated from security_domains
    # See get_allowed_hosts() method and security_domains field

    # === Project Structure ===
    project_name: str = Field(
        ...,
        description="Project name for identification"
    )
    project_apps: List[str] = Field(
        default_factory=list,
        description="List of project-specific Django apps"
    )

    # === URL Configuration ===
    root_urlconf: str = Field(
        default="",
        description="Django ROOT_URLCONF setting"
    )
    wsgi_application: str = Field(
        default="",
        description="Django WSGI_APPLICATION setting"
    )

    # === Custom User Model ===
    auth_user_model: Optional[str] = Field(
        default=None,
        description="Custom user model (AUTH_USER_MODEL)"
    )

    # === Database Configuration ===
    databases: Dict[str, "DatabaseConfig"] = Field(
        default_factory=dict,
        description="Database connections"
    )
    database_routing: List["DatabaseRoutingRule"] = Field(
        default_factory=list,
        description="Database routing rules"
    )

    # === Cache Configuration ===
    cache_default: Optional["CacheConfig"] = Field(
        default=None,
        description="Default cache backend"
    )
    cache_sessions: Optional["CacheConfig"] = Field(
        default=None,
        description="Sessions cache backend"
    )

    # === Security Configuration ===
    security_domains: List[str] = Field(
        default_factory=list,
        description="Domains for automatic security configuration (optional in development)"
    )
    ssl_redirect: Optional[bool] = Field(
        default=None,
        description="Force SSL redirect (None = disabled, assumes reverse proxy handles SSL)"
    )
    cors_allow_headers: List[str] = Field(
        default_factory=list,
        description="CORS allowed headers"
    )

    # === Services Configuration ===
    email: Optional["EmailConfig"] = Field(
        default=None,
        description="Email service configuration"
    )
    telegram: Optional["TelegramConfig"] = Field(
        default=None,
        description="Telegram service configuration"
    )

    # === Third-Party Integrations ===
    openapi_client: Optional[OpenAPIClientConfig] = Field(
        default=None,
        description="Django-CFG API Client Generation API zones configuration"
    )
    unfold: Optional["UnfoldConfig"] = Field(
        default=None,
        description="Unfold dashboard configuration"
    )
    dashboard: Optional["DashboardConfig"] = Field(
        default=None,
        description="Dashboard configuration with callbacks"
    )

    # === Built-in Apps Configuration ===
    enable_accounts: bool = Field(
        default=False,
        description="Enable django_cfg.apps.accounts"
    )
    enable_agents: bool = Field(
        default=False,
        description="Enable django_cfg.apps.agents"
    )
    enable_knowbase: bool = Field(
        default=False,
        description="Enable django_cfg.apps.knowbase"
    )
    enable_leads: bool = Field(
        default=False,
        description="Enable django_cfg.apps.leads"
    )
    enable_maintenance: bool = Field(
        default=False,
        description="Enable django_cfg.apps.maintenance"
    )
    enable_newsletter: bool = Field(
        default=False,
        description="Enable django_cfg.apps.newsletter"
    )
    enable_support: bool = Field(
        default=False,
        description="Enable django_cfg.apps.support"
    )

    # === Environment Configuration ===
    environments: Optional["EnvironmentConfig"] = Field(
        default=None,
        description="Environment-specific configuration files"
    )

    # === Middleware Configuration ===
    custom_middleware: List[str] = Field(
        default_factory=list,
        description="Custom middleware classes"
    )

    # === Logging Configuration ===
    logging: Optional["LoggingConfig"] = Field(
        default=None,
        description="Logging configuration"
    )

    # === Internal State ===
    _environment: Optional[str] = Field(
        default=None,
        description="Detected environment",
        exclude=True
    )
    _base_dir: Optional[Path] = Field(
        default=None,
        description="Project base directory",
        exclude=True
    )
    _django_settings: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Generated Django settings cache",
        exclude=True
    )
```

## Initialization Methods

### __init__

```python
def __init__(self, **data):
    """Initialize configuration with environment detection"""
    super().__init__(**data)
    self._detect_environment()
    self._resolve_paths()
    self._apply_smart_defaults()
    self._load_environment_config()
```

**Initialization flow:**

1. **Environment Detection** - Detects current environment (dev/staging/prod)
2. **Path Resolution** - Finds project root, detects URLs/WSGI
3. **Smart Defaults** - Applies environment-aware defaults
4. **YAML Loading** - Loads environment-specific YAML configuration

### _detect_environment

```python
def _detect_environment(self) -> None:
    """Detect current environment"""
    from django_cfg.core.environment import EnvironmentDetector
    self._environment = EnvironmentDetector.detect_environment()
```

Detects environment based on:
- Environment variables (`DJANGO_ENV`, `ENV`)
- Hostname patterns
- File existence (`.env.production`, `.env.development`)

### _resolve_paths

```python
def _resolve_paths(self) -> None:
    """Resolve project paths"""
    from django_cfg.utils.path_resolution import PathResolver
    self._base_dir = PathResolver.find_project_root()

    # Auto-detect URL configuration if not set
    if not self.root_urlconf:
        self.root_urlconf = PathResolver.detect_root_urlconf()

    if not self.wsgi_application:
        self.wsgi_application = PathResolver.detect_wsgi_application()
```

Automatically detects:
- **BASE_DIR** - Project root directory
- **ROOT_URLCONF** - URL configuration module
- **WSGI_APPLICATION** - WSGI application path

### _apply_smart_defaults

```python
def _apply_smart_defaults(self) -> None:
    """Apply environment-aware defaults"""
    from django_cfg.utils.smart_defaults import SmartDefaults

    # Apply cache defaults
    if self.cache_default:
        self.cache_default = SmartDefaults.configure_cache_backend(
            self.cache_default, self._environment, self.debug
        )

    if self.cache_sessions:
        self.cache_sessions = SmartDefaults.configure_cache_backend(
            self.cache_sessions, self._environment, self.debug
        )
```

Smart defaults based on environment:

**Development:**
- Cache: LocMem (in-memory)
- Debug: True
- SSL: Disabled

**Production:**
- Cache: Redis (if configured)
- Debug: False
- SSL: Enabled

## Settings Generation Methods

### get_all_settings

```python
def get_all_settings(self) -> Dict[str, Any]:
    """Generate complete Django settings dictionary"""
    if self._django_settings is None:
        from django_cfg.core.generation import SettingsGenerator
        self._django_settings = SettingsGenerator.generate(self)

    return self._django_settings
```

**Example usage:**

```python
# config.py
config = MyConfig(secret_key="...", debug=True)

# settings.py
from config import config
globals().update(config.get_all_settings())
```

### get_installed_apps

```python
def get_installed_apps(self) -> List[str]:
    """Get complete list of installed apps"""
    apps = [
        # Django core apps
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
    ]

    # Add third-party apps based on configuration
    if self.openapi_client:
        apps.append('django_cfg.client')

    if self.unfold:
        apps.append('unfold')

    # Add project apps
    apps.extend(self.project_apps)

    return apps
```

### get_middleware

```python
def get_middleware(self) -> List[str]:
    """Get complete middleware stack"""
    middleware = [
        'django.middleware.security.SecurityMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
    ]

    # Add CORS middleware if domains are configured
    if self.security_domains:
        middleware.insert(1, 'corsheaders.middleware.CorsMiddleware')

    # Add custom middleware
    middleware.extend(self.custom_middleware)

    return middleware
```

### get_allowed_hosts

```python
def get_allowed_hosts(self) -> List[str]:
    """
    Get ALLOWED_HOSTS auto-generated from security_domains.

    Automatically includes:
    - All domains from security_domains
    - www subdomain for each domain
    - localhost, 127.0.0.1, 0.0.0.0 for development

    Returns:
        List of allowed host names

    Example:
        >>> config = DjangoConfig(security_domains=["myapp.com"])
        >>> config.get_allowed_hosts()
        ['myapp.com', 'www.myapp.com', 'localhost', '127.0.0.1', '0.0.0.0']
    """
    allowed_hosts = []

    # Add domains from security_domains
    for domain in self.security_domains:
        # Remove protocol if present
        if "://" in domain:
            domain = domain.split("://")[1]

        # Remove path if present
        if "/" in domain:
            domain = domain.split("/")[0]

        # Add domain
        allowed_hosts.append(domain)

        # Add www subdomain
        if not domain.startswith("www."):
            allowed_hosts.append(f"www.{domain}")

    # Always include localhost for development and health checks
    for local_host in ["localhost", "127.0.0.1", "0.0.0.0"]:
        if local_host not in allowed_hosts:
            allowed_hosts.append(local_host)

    return allowed_hosts
```

## Validation

### validate_configuration

```python
def validate_configuration(self) -> List[str]:
    """Validate configuration and return list of errors"""
    from django_cfg.core.validation import ConfigurationValidator
    return ConfigurationValidator.validate(self)
```

**Example usage:**

```python
config = MyConfig(secret_key="short")
errors = config.validate_configuration()
if errors:
    for error in errors:
        print(f"Error: {error}")
```

## Usage Examples

### Basic Configuration

```python
# config.py
from django_cfg import DjangoConfig
from pydantic import BaseModel

class DatabaseConfig(BaseModel):
    url: str = "postgresql://localhost/mydb"

class MyConfig(DjangoConfig):
    secret_key: str = "your-secret-key-here-minimum-50-characters-long-string"
    debug: bool = True
    project_name: str = "My Project"
    project_apps: list = ["apps.blog", "apps.shop"]

    database: DatabaseConfig = DatabaseConfig()
```

### With Environment Detection

```python
class MyConfig(DjangoConfig):
    @property
    def debug(self) -> bool:
        return self._environment == "development"

    @property
    def database_url(self) -> str:
        if self._environment == "production":
            return "postgresql://prod-server/main"
        return "sqlite:///db/dev.sqlite3"
```

### With Services

```python
from django_cfg.models import EmailConfig, TelegramConfig, CacheConfig

class MyConfig(DjangoConfig):
    secret_key: str = "your-secret-key-here-minimum-50-characters-long-string"
    debug: bool = False
    project_name: str = "My Project"

    # Services
    email: EmailConfig = EmailConfig(
        backend="smtp",
        host="smtp.gmail.com",
        port=587,
        username="your-email@gmail.com",
        password="your-app-password"
    )

    telegram: TelegramConfig = TelegramConfig(
        bot_token="your-bot-token",
        allowed_user_ids=[123456789]
    )

    # Cache
    cache_default: CacheConfig = CacheConfig(
        redis_url="redis://localhost:6379/0"
    )
```

### With Built-in Apps

```python
class MyConfig(DjangoConfig):
    secret_key: str = "your-secret-key-here-minimum-50-characters-long-string"
    debug: bool = True
    project_name: str = "My Project"

    # Enable built-in apps
    enable_accounts: bool = True
    enable_agents: bool = True
    enable_knowbase: bool = True
```

## Model Configuration

The `model_config` dict controls Pydantic behavior:

```python
model_config = ConfigDict(
    validate_assignment=True,  # Validate on attribute assignment
    extra="allow",             # Allow extra fields
    env_prefix="DJANGO_",      # Environment variable prefix
    populate_by_name=True,     # Allow field name or alias
    validate_default=True,     # Validate default values
)
```

### Environment Variables

With `env_prefix="DJANGO_"`, you can override any field:

```bash
export DJANGO_SECRET_KEY="new-secret-key"
export DJANGO_DEBUG=false
export DJANGO_PROJECT_NAME="My App"
```

### Extra Fields

With `extra="allow"`, you can add custom fields:

```python
config = MyConfig(
    secret_key="...",
    debug=True,
    custom_field="custom_value"  # Allowed
)
```

## See Also

- [**Configuration Overview**](./) - Configuration system overview
- [**Security Settings**](./security) - Security configuration
- [**Database Models**](./database) - Database configuration
- [**Cache Models**](./cache) - Cache configuration
- [**Email Models**](./email) - Email configuration
