---
title: Security Hardening
description: Deploy Django-CFG with security. Complete deployment guide for security hardening with Docker, environment configuration, and production best practices.
sidebar_label: Security
sidebar_position: 3
keywords:
  - django-cfg security
  - deploy django-cfg
  - django security deployment
---

# 🔒 Security Guide

Django-CFG provides automatic security configuration that adapts to your environment—open in development, strict in production.

---

## Core Security Principles

### Environment-Aware Security
Django-CFG automatically configures security based on environment:

**Development Mode (`debug=True`):**
- CORS: Whitelist mode with common dev ports
- CSRF: Wide port range for local development
- SSL: Disabled (local development)
- Credentials: Allowed for frontend testing

**Production Mode (`debug=False`):**
- CORS: Strict domain whitelist only
- CSRF: Production domains only
- SSL: Enabled with HSTS
- Credentials: Secure cookie transmission

### Docker-Aware Configuration
Security works seamlessly in Docker:
- Auto-detects Docker environment
- Allows internal health checks
- Supports private IP ranges (RFC 1918)
- Works with reverse proxies (nginx/traefik)

---

## Security Domains

The foundation of Django-CFG security is `security_domains`—a single list that configures all security settings.

### Basic Configuration

```yaml
# config.yaml
security_domains:
  - example.com
  - api.example.com
  - admin.example.com
```

**What this configures automatically:**
- ✅ `ALLOWED_HOSTS` (host-only format)
- ✅ `CORS_ALLOWED_ORIGINS` (with protocol)
- ✅ `CSRF_TRUSTED_ORIGINS` (with protocol)

### Format Support

Django-CFG accepts domains in any format:

```yaml
security_domains:
  # Simple domain (auto-adds https://)
  - example.com

  # With protocol
  - https://api.example.com

  # With custom port
  - http://staging.example.com:8080

  # IP addresses (auto-adds http://)
  - 192.168.1.10
```

**Automatic normalization:**
```python
# Input: "example.com"
ALLOWED_HOSTS = ["example.com"]
CORS_ALLOWED_ORIGINS = ["https://example.com"]
CSRF_TRUSTED_ORIGINS = ["https://example.com"]

# Input: "http://staging.com:8080"
ALLOWED_HOSTS = ["staging.com"]
CORS_ALLOWED_ORIGINS = ["http://staging.com:8080"]
CSRF_TRUSTED_ORIGINS = ["http://staging.com:8080"]
```

---

## CORS (Cross-Origin Resource Sharing)

### How CORS Works in Django-CFG

**Development Mode:**
```python
# Whitelist mode with common dev ports
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",   # React
    "http://localhost:5173",   # Vite
    "http://localhost:8080",   # Vue
    # ... + your security_domains
]
```

**Production Mode:**
```python
# Only security_domains allowed
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = [
    "https://example.com",
    "https://api.example.com",
]
```

### Why Whitelist Mode?

Django-CFG uses **whitelist mode** instead of wildcard `*` to support credentials:

```javascript
// Frontend can use credentials: 'include'
fetch('https://api.example.com/user/', {
  method: 'GET',
  credentials: 'include',  // ✅ Works with whitelist mode
  headers: {
    'Authorization': 'Bearer token',
  }
})
```

> **Note:** `CORS_ALLOW_ALL_ORIGINS = True` doesn't support credentials. Django-CFG uses whitelist for maximum flexibility.

### Custom CORS Headers

Default headers cover most use cases:

```yaml
# Automatic defaults
cors_allow_headers:
  - accept
  - authorization
  - content-type
  - x-csrftoken
  - x-requested-with
```

---

## CSRF Protection

### How CSRF Works in Django-CFG

CSRF protection checks the `Referer` header from browsers.

**Development Mode:**
```python
# Wide range of local ports
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:3001",
    # ... ports 3000-5000 and 8000-9000
]
```

**Production Mode:**
```python
# Only security_domains
CSRF_TRUSTED_ORIGINS = [
    "https://example.com",
    "https://api.example.com",
]
```

### CSRF vs CORS

Important distinction:

| Feature | CORS | CSRF |
|---------|------|------|
| **Checks** | `Origin` header | `Referer` header |
| **When** | Browser cross-origin requests | Form submissions |
| **Docker API** | Not checked (no Origin) | Not checked (no Referer) |
| **Frontend SPA** | ✅ Checked | ✅ Checked |

**Why both are needed:**
- CORS: Allows frontend SPA to make API requests
- CSRF: Protects form submissions from malicious sites

---

## SSL/HTTPS Configuration

### Reverse Proxy Mode (Default)

**Most common setup:** SSL handled by reverse proxy

```yaml
# Default behavior - SSL redirect DISABLED
ssl_redirect: null  # or omit
```

**Architecture:**
```
Internet → Cloudflare/ALB → nginx/traefik (SSL termination) → Django (HTTP)
```

Django receives plain HTTP from reverse proxy. This is **correct and secure**.

### Direct SSL Mode (Rare)

**Only use if Django directly handles SSL:**

```yaml
# Enable SSL redirect
ssl_redirect: true
```

This is rare. Only needed when:
- No reverse proxy
- Django serves HTTPS directly
- Bare metal deployment without nginx

### Production SSL Settings

When `debug=False`, Django-CFG automatically enables:

```python
# Automatic in production
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'
```

**HSTS (HTTP Strict Transport Security):**
```python
# When ssl_redirect=True
SECURE_HSTS_SECONDS = 31536000        # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
```

---

## Docker Security

### Private IP Ranges

In production Docker, Django-CFG allows health checks from private IPs:

```python
# Automatic in Docker production
ALLOWED_HOSTS = [
    "example.com",
    "api.example.com",
    # + Docker private IPs (regex patterns)
    r'^172\.(1[6-9]|2[0-9]|3[0-1])\.\d{1,3}\.\d{1,3}$',  # Docker bridge
    r'^192\.168\.\d{1,3}\.\d{1,3}$',                      # Private network
    r'^10\.\d{1,3}\.\d{1,3}\.\d{1,3}$',                   # Private network
    '.cluster.local',                                      # Kubernetes
]
```

**Why this is secure:**
- Only private RFC 1918 ranges allowed
- Public IPs still blocked
- Health checks work internally

### Docker Detection

Django-CFG auto-detects Docker:

1. Checks for `/.dockerenv` file
2. Reads `/proc/1/cgroup` for "docker"
3. Checks `DOCKER=true` or `KUBERNETES_SERVICE_HOST` env vars

---

## Security Checklist

### Production Requirements

Before deploying, verify:

**Environment:**
- [ ] `debug = false` in config.yaml
- [ ] `environment = "production"`
- [ ] Strong `secret_key` (50+ characters)

**Domains:**
- [ ] `security_domains` configured with production domains
- [ ] No wildcard `*` in security_domains
- [ ] HTTPS enabled on all domains

**SSL/HTTPS:**
- [ ] SSL certificate configured (Cloudflare/Let's Encrypt)
- [ ] HSTS configured (if Django handles SSL)
- [ ] Secure cookies enabled

**Database:**
- [ ] Database password strong and unique
- [ ] Database not exposed to public internet
- [ ] Database backups configured

**Secrets:**
- [ ] All secrets in environment variables (not in code)
- [ ] `.env` file in `.gitignore`
- [ ] API keys rotated regularly

### Development Best Practices

**Local Development:**
```yaml
# config.dev.yaml
debug: true
environment: development
secret_key: "dev-secret-key-at-least-50-chars-long-xxxxxxxxxxxxxxxxx"
security_domains: []  # Auto-configured for localhost
```

**Never commit:**
- Production `.env` files
- Secret keys
- Database passwords
- API keys

---

## Common Security Patterns

### Multiple Frontends

```yaml
# API + multiple frontend apps
security_domains:
  - api.example.com        # Backend API
  - app.example.com        # Main web app
  - admin.example.com      # Admin panel
  - mobile.example.com     # Mobile web app
```

All domains automatically configured for CORS and CSRF.

### Staging Environment

```yaml
# Staging with custom port
security_domains:
  - staging.example.com
  - staging-api.example.com:8443
```

### Multi-Region Setup

```yaml
# Multiple regions
security_domains:
  - api-us.example.com
  - api-eu.example.com
  - api-asia.example.com
```

---

## Troubleshooting

### CORS Errors in Browser

**Error:** `Access-Control-Allow-Origin header is missing`

**Solution:**
```yaml
# Add your frontend domain to security_domains
security_domains:
  - example.com
  - app.example.com  # ← Add frontend domain
```

**Verify configuration:**
```bash
# Check CORS origins
python manage.py shell
>>> from django.conf import settings
>>> print(settings.CORS_ALLOWED_ORIGINS)
```

### CSRF Token Mismatch

**Error:** `CSRF verification failed`

**Solution:**
```yaml
# Ensure frontend domain in security_domains
security_domains:
  - app.example.com  # Frontend domain must be here
```

**For API-only (no CSRF needed):**
```python
# In your API views
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def api_view(request):
    # API endpoint without CSRF check
    pass
```

### Health Checks Failing in Docker

**Error:** `Invalid HTTP_HOST header`

**Solution:**

1. Check Docker environment detection:
```python
# In Django shell
from django_cfg.core.builders.security_builder import SecurityBuilder
builder = SecurityBuilder(config)
print(builder._is_running_in_docker())  # Should be True
```

2. Manually enable Docker mode:
```bash
# Set environment variable
export DOCKER=true
```

### "Insecure Secret Key" Warning

**Error:** `Secret key is too short or not set`

**Solution:**
```bash
# Generate secure secret key (50+ chars)
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Add to .env
SECRET_KEY="your-generated-secret-key-here"
```

---

## See Also

- **[Environment Setup](/deployment/environment-setup)** - Environment configuration
- **[Docker Guide](/guides/docker/overview)** - Docker deployment
- **[Production Config](/guides/production-config)** - Production best practices
- **[Configuration Reference](/fundamentals/configuration)** - Full configuration options

---

TAGS: security, cors, csrf, ssl, https, docker, production, domains
DEPENDS_ON: [django-cfg, docker, ssl-certificates]
USED_BY: [production, deployment, frontend, api]
