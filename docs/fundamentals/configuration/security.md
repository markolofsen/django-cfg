---
title: Security Settings
description: Security, CORS, and SSL configuration in Django-CFG
sidebar_label: Security Settings
sidebar_position: 3
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# Security Settings

:::danger[Production Security Critical]
Proper security configuration is **critical** for production deployments. Always use:
- ✅ Strong SECRET_KEY (50+ characters)
- ✅ Reverse proxy with SSL/TLS (nginx, Cloudflare, traefik)
- ✅ Specific `security_domains` for production (never use `['*']`)
- ✅ Environment variables for secrets
:::

Django-CFG provides **automatic security configuration** based on your domains and environment.

## Overview

:::tip[Environment-Aware Security]
Django-CFG provides **environment-aware security** - development is fully open for convenience, production is strict and secure.
:::

**How it works:**

**Development Mode** (`debug=True` or no `security_domains`):
- ✅ **CORS** - Fully open (`CORS_ALLOW_ALL_ORIGINS=True`)
- ✅ **ALLOWED_HOSTS** - Accepts all (`['*']`)
- ✅ **Docker** - Automatic Docker IP support
- ✅ **Localhost** - All ports allowed

**Production Mode** (when `security_domains` specified):
- ✅ **ALLOWED_HOSTS** - Generated from `security_domains`
- ✅ **CORS** - Strict whitelist with credentials
- ✅ **CSRF** - Trusted origins from domains
- ✅ **Security headers** - Automatic configuration
- ✅ **SSL** - Assumes reverse proxy (nginx/Cloudflare)

## security_domains Field

The `security_domains` field is the foundation of security configuration:

```python
from django_cfg import DjangoConfig

class MyConfig(DjangoConfig):
    secret_key: str = "your-secret-key"
    debug: bool = False

    # Production domains (flexible format - Django-CFG normalizes automatically)
    security_domains: list = [
        "myapp.com",              # ✅ No protocol
        "https://api.myapp.com",  # ✅ With protocol
        "admin.myapp.com:8443",   # ✅ With port
    ]

# Development: security_domains optional (CORS fully open by default)
class DevConfig(DjangoConfig):
    debug: bool = True
    # security_domains not needed - auto-configured for development
```

### Auto-Generated Settings

From `security_domains`, Django-CFG automatically generates:

**Development Mode (no security_domains):**
```python
# CORS fully open
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = False

# All hosts accepted
ALLOWED_HOSTS = ['*']

# CSRF only for popular dev ports
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:3000',
    'http://localhost:5173',
    # ... 7 popular dev ports
]
```

**Production Mode (security_domains specified):**
```python
# Strict CORS from security_domains
CORS_ALLOWED_ORIGINS = [
    'https://myapp.com',
    'https://api.myapp.com',
    'https://admin.myapp.com',
]
CORS_ALLOW_CREDENTIALS = True

# Hosts from security_domains + Docker IPs (if detected)
ALLOWED_HOSTS = [
    'myapp.com',
    'api.myapp.com',
    'admin.myapp.com',
    # Docker IPs added automatically if /.dockerenv detected
    'r"172\.(1[6-9]|2[0-9]|3[0-1])\..*',  # Docker range
]

# CSRF from security_domains
CSRF_TRUSTED_ORIGINS = [
    'https://myapp.com',
    'https://api.myapp.com',
    'https://admin.myapp.com',
]
```

## SSL/TLS Configuration

:::tip[Reverse Proxy Best Practice]
Django-CFG **assumes** SSL/TLS termination happens at the reverse proxy level (nginx, Cloudflare, traefik, AWS ALB). This is the industry-standard approach.
:::

### Default Behavior (Recommended)

```python
class MyConfig(DjangoConfig):
    secret_key: str = "your-secret-key"
    debug: bool = False
    security_domains: list = ["myapp.com"]

    # ssl_redirect not specified - Django-CFG defaults to None (disabled)
    # SSL handled by reverse proxy (nginx, Cloudflare, etc.)
```

**Default behavior:**
- ✅ `SECURE_SSL_REDIRECT = False` - Reverse proxy handles redirects
- ✅ `SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')` - Trust proxy headers
- ✅ `SESSION_COOKIE_SECURE = True` - Secure cookies in production
- ✅ `CSRF_COOKIE_SECURE = True` - Secure CSRF tokens

### Explicit SSL Redirect (Rare)

:::warning[Only for Bare Metal]
Set `ssl_redirect=True` **ONLY** if Django handles SSL directly without a reverse proxy. This is rare in modern deployments.
:::

```python
class MyConfig(DjangoConfig):
    secret_key: str = "your-secret-key"
    debug: bool = False
    security_domains: list = ["myapp.com"]

    # Explicit SSL redirect - ONLY if Django handles SSL directly
    ssl_redirect: bool = True
```

**When to use:**
- ❌ **Don't use** with nginx/Cloudflare/traefik (causes redirect loops)
- ✅ **Use only** for bare metal Django with direct SSL certificates
- ✅ **Use only** for testing SSL redirects in development

## CORS Configuration

### Automatic CORS

```python
class MyConfig(DjangoConfig):
    secret_key: str = "your-secret-key"
    debug: bool = False
    security_domains: list = ["myapp.com"]
```

**Automatic CORS headers:**
```python
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]
```

### Custom CORS Headers

```python
class MyConfig(DjangoConfig):
    secret_key: str = "your-secret-key"
    debug: bool = False
    security_domains: list = ["myapp.com"]

    # Add custom headers
    cors_allow_headers: list = [
        'x-api-key',
        'x-custom-header',
    ]
```

**Result:** Merges default headers + custom headers

### CORS for API

```python
class MyConfig(DjangoConfig):
    secret_key: str = "your-secret-key"
    debug: bool = False
    security_domains: list = ["api.myapp.com", "myapp.com"]

    cors_allow_headers: list = [
        'x-api-key',
        'authorization',
    ]
```

**Generated settings:**
```python
CORS_ALLOW_CREDENTIALS = True
CORS_ORIGIN_WHITELIST = [
    'https://api.myapp.com',
    'https://www.api.myapp.com',
    'https://myapp.com',
    'https://www.myapp.com',
    'http://localhost:3000',
]
```

## Complete Security Example

### Production Configuration

```python
# config.py
from django_cfg import DjangoConfig

class ProductionConfig(DjangoConfig):
    secret_key: str = "your-production-secret-key-minimum-50-characters"
    debug: bool = False
    project_name: str = "My Production App"

    # Security domains (flexible format - auto-normalized)
    security_domains: list = [
        "myapp.com",                # ✅ No protocol
        "https://api.myapp.com",    # ✅ With protocol
        "admin.myapp.com:8443",     # ✅ With port
    ]

    # ssl_redirect: Optional - defaults to None (reverse proxy handles SSL)
    # CORS auto-configured from domains
    # ALLOWED_HOSTS auto-generated
```

**Generated security settings:**

```python
# ALLOWED_HOSTS (from security_domains + Docker IPs if detected)
ALLOWED_HOSTS = [
    'myapp.com',
    'api.myapp.com',
    'admin.myapp.com',
    # Docker IPs added automatically if /.dockerenv exists:
    'r"172\.(1[6-9]|2[0-9]|3[0-1])\..*',  # Docker bridge
    'r"192\.168\..*',                      # Docker compose
]

# SSL/TLS (assumes reverse proxy)
SECURE_SSL_REDIRECT = False  # Reverse proxy handles redirect
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# CORS (strict whitelist with credentials)
CORS_ALLOWED_ORIGINS = [
    'https://myapp.com',
    'https://api.myapp.com',
    'https://admin.myapp.com',
]
CORS_ALLOW_CREDENTIALS = True

# CSRF (from security_domains)
CSRF_TRUSTED_ORIGINS = [
    'https://myapp.com',
    'https://api.myapp.com',
    'https://admin.myapp.com',
]

# Security headers
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'
```

### Development Configuration

```python
# config.py
from django_cfg import DjangoConfig

class DevelopmentConfig(DjangoConfig):
    secret_key: str = "dev-secret-key-minimum-50-characters-long-string"
    debug: bool = True
    project_name: str = "My Dev App"

    # security_domains: Optional - not needed in development
    # Django-CFG auto-configures for development convenience
```

**Generated security settings:**

```python
# CORS (fully open for development)
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = False  # Must be False with ALLOW_ALL

# ALLOWED_HOSTS (accept everything)
ALLOWED_HOSTS = ['*']

# CSRF (popular dev ports only)
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:3000',  # React/Next.js
    'http://localhost:5173',  # Vite
    'http://localhost:8080',  # Webpack
    'http://localhost:4200',  # Angular
    # ... 7 popular ports
]

# SSL/TLS (disabled in development)
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
```

## Environment-Specific Security

### Using Environment Detection

```python
from django_cfg import DjangoConfig

class MyConfig(DjangoConfig):
    secret_key: str = "your-secret-key"
    project_name: str = "My App"

    @property
    def debug(self) -> bool:
        return self._environment == "development"

    @property
    def security_domains(self) -> list:
        if self._environment == "production":
            return ["myapp.com", "api.myapp.com"]
        elif self._environment == "staging":
            return ["staging.myapp.com"]
        return []  # Development

    @property
    def ssl_redirect(self) -> bool:
        return self._environment in ["production", "staging"]
```

### Using YAML Configuration

```yaml
# config.production.yaml
secret_key: "${SECRET_KEY}"  # From environment
debug: false
security_domains:
  - myapp.com              # ✅ Flexible format
  - https://api.myapp.com  # ✅ With protocol
  - admin.myapp.com:8443   # ✅ With port

# ssl_redirect: Optional - not needed (defaults to reverse proxy mode)

# config.development.yaml
secret_key: "dev-secret-key-minimum-50-chars"
debug: true

# security_domains: Optional - not needed in development
# Django-CFG auto-configures CORS fully open for development
```

```python
# config.py
from django_cfg import load_config

config = load_config()  # Loads environment-specific YAML
```

## Security Best Practices

:::warning[Security Checklist]
Follow **all** these practices for production security. Skipping any can expose your application to attacks.
:::

<Tabs>
  <TabItem value="secret-key" label="SECRET_KEY" default>

### 1. Always Set Strong SECRET_KEY

:::danger[Weak SECRET_KEY]
**Never use:**
- Default values like "changeme" or "insecure-key"
- Short keys (< 50 characters)
- Predictable patterns or dictionary words
- Keys committed to version control

**Consequences:**
- Session hijacking
- CSRF token forgery
- Password reset token prediction
- Data tampering
:::

**❌ Bad:**
```python
secret_key: str = "changeme"  # ❌ NEVER DO THIS
secret_key: str = "django-insecure-key"  # ❌ Too weak
```

**✅ Good:**
```python
# Use environment variable
secret_key: str = os.environ["SECRET_KEY"]  # ✅ Secure

# Or generate new key:
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

:::tip[Key Generation]
Generate a cryptographically secure key:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```
:::

  </TabItem>
  <TabItem value="environment" label="Environment Variables">

### 2. Use Environment Variables for Secrets

:::warning[Never Hardcode Secrets]
Hardcoded secrets in code can be:
- Found in git history (even after deletion)
- Leaked through GitHub search
- Exposed in error messages
- Copied to forks and backups
:::

**❌ Bad:**
```python
class MyConfig(DjangoConfig):
    secret_key: str = "my-actual-secret-key-abc123"  # ❌ EXPOSED
    database_url: str = "postgresql://user:password@host/db"  # ❌ LEAKED
```

**✅ Good:**
```python
import os

class MyConfig(DjangoConfig):
    secret_key: str = os.environ["SECRET_KEY"]  # ✅ From environment
    database_url: str = os.environ["DATABASE_URL"]  # ✅ Secure

    # Optional: provide dev fallback
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
```

  </TabItem>
  <TabItem value="ssl" label="SSL/TLS">

### 3. Enable SSL at Reverse Proxy

:::tip[Reverse Proxy SSL Termination]
**Best practice:** Handle SSL/TLS at the reverse proxy level (nginx, Cloudflare, traefik, AWS ALB). This is more secure, performant, and flexible than Django-level SSL.
:::

**✅ Default (recommended):**
```python
class MyConfig(DjangoConfig):
    debug: bool = False
    security_domains: list = ["myapp.com"]
    # ssl_redirect not specified - Django-CFG assumes reverse proxy handles SSL
```

**Nginx example:**
```nginx
server {
    listen 443 ssl http2;
    server_name myapp.com;

    ssl_certificate /etc/ssl/myapp.com.crt;
    ssl_certificate_key /etc/ssl/myapp.com.key;

    location / {
        proxy_pass http://django:8000;
        proxy_set_header X-Forwarded-Proto https;  # Django trusts this
        proxy_set_header Host $host;
    }
}
```

:::danger[Only Set ssl_redirect=True for Bare Metal]
Set `ssl_redirect=True` **ONLY** if Django handles SSL certificates directly without a reverse proxy (rare: bare metal without nginx/traefik).

**Causes redirect loops with:**
- nginx/Apache
- Cloudflare
- AWS ALB/ELB
- traefik
- Any reverse proxy
:::

  </TabItem>
  <TabItem value="hosts" label="ALLOWED_HOSTS">

### 4. Restrict ALLOWED_HOSTS

:::danger[Wildcard ALLOWED_HOSTS]
Using `ALLOWED_HOSTS = ['*']` allows:
- HTTP Host header attacks
- Cache poisoning
- Email/password reset injection
- Subdomain takeover attacks
:::

**❌ Bad:**
```python
ALLOWED_HOSTS = ['*']  # ❌ DANGEROUS - allows any domain
```

**✅ Good:**
```python
class MyConfig(DjangoConfig):
    security_domains: list = [
        "myapp.com",
        "api.myapp.com",
    ]
    # ALLOWED_HOSTS auto-generated with www variants + localhost
```

  </TabItem>
  <TabItem value="cors" label="CORS">

### 5. Configure CORS Properly

:::danger[Permissive CORS]
Using `CORS_ALLOW_ALL_ORIGINS = True` exposes your API to:
- Cross-site request forgery
- Data theft from other domains
- Unauthorized API access
- Session hijacking
:::

**❌ Bad:**
```python
CORS_ALLOW_ALL_ORIGINS = True  # ❌ DANGEROUS
CORS_ALLOW_CREDENTIALS = True  # With wildcard origin = CRITICAL VULNERABILITY
```

**✅ Good:**
```python
class MyConfig(DjangoConfig):
    security_domains: list = [
        "myapp.com",
        "api.myapp.com",
    ]
    # CORS auto-configured with specific origins
```

:::warning[CORS + Credentials]
Never combine `CORS_ALLOW_ALL_ORIGINS = True` with `CORS_ALLOW_CREDENTIALS = True`. This is a **critical security vulnerability**.
:::

  </TabItem>
</Tabs>

## Security Headers Reference

Django-CFG automatically configures security headers based on environment:

### Production Headers

```python
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
```

### Development Headers

```python
SECURE_CONTENT_TYPE_NOSNIFF = False
SECURE_BROWSER_XSS_FILTER = False
X_FRAME_OPTIONS = 'SAMEORIGIN'
```

## Troubleshooting

### ALLOWED_HOSTS Error

**Error:**
```
DisallowedHost at /
Invalid HTTP_HOST header: 'newdomain.com'
```

**Solution:**
```python
class MyConfig(DjangoConfig):
    security_domains: list = [
        "myapp.com",
        "newdomain.com",  # Add new domain
    ]
```

### CORS Error

**Error:**
```
Access to fetch at 'https://api.myapp.com' from origin 'https://myapp.com'
has been blocked by CORS policy
```

**Solution:**
```python
class MyConfig(DjangoConfig):
    security_domains: list = [
        "myapp.com",
        "api.myapp.com",  # Add API domain
    ]
```

### SSL Redirect Loop

**Problem:** Infinite redirect loop in production

**Solution:**
```python
class MyConfig(DjangoConfig):
    security_domains: list = ["myapp.com"]
    ssl_redirect: bool = True

# Add to settings:
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
```

## See Also

- [**DjangoConfig**](./django-settings) - Base configuration class
- [**Configuration Overview**](./) - Configuration system overview
- [**Environment**](./environment) - Environment detection
