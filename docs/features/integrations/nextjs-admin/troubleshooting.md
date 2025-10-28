---
id: troubleshooting
title: Troubleshooting
description: Solutions to common issues with Next.js admin integration
sidebar_label: Troubleshooting
tags:
  - nextjs
  - admin
  - troubleshooting
---

# Troubleshooting

Solutions to common issues and error messages.

## Configuration Issues

### Tab Not Showing

**Problem**: Only the built-in admin tab appears, no Next.js admin tab.

**Solution**: Verify `NextJsAdminConfig` is set:

```python title="api/config.py"
# ❌ Wrong - nextjs_admin not configured
config = DjangoConfig(
    project_name="My Project",
    # Missing nextjs_admin configuration
)

# ✅ Correct
config = DjangoConfig(
    project_name="My Project",
    nextjs_admin=NextJsAdminConfig(
        project_path="../django_admin",
    ),
)
```

**Check**: Verify module is registered:

```bash
python manage.py shell
>>> from django.conf import settings
>>> print('django_cfg.modules.nextjs_admin' in settings.INSTALLED_APPS)
True  # Should be True
```

### Invalid project_path

**Problem**: `ValueError: project_path cannot be empty`

**Solution**: Ensure path is set and valid:

```python
# ❌ Empty path
nextjs_admin=NextJsAdminConfig(
    project_path="",  # Invalid
)

# ✅ Valid relative path
nextjs_admin=NextJsAdminConfig(
    project_path="../django_admin",
)

# ✅ Valid absolute path
nextjs_admin=NextJsAdminConfig(
    project_path="/home/user/projects/django_admin",
)
```

## iframe Loading Issues

### Blank iframe

**Problem**: iframe appears but shows blank white page.

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs groupId="mode">
  <TabItem value="dev" label="Development Mode" default>

**Check 1**: Is Next.js dev server running?

```bash
# Should be running on correct port
pnpm dev --port 3001

# Or check config
python manage.py shell
>>> from django_cfg import get_config
>>> print(get_config().nextjs_admin.get_dev_url())
http://localhost:3001  # Should match your dev server
```

**Check 2**: Check dev server output

```bash
# Next.js should show
> Local: http://localhost:3001
> Ready in 2.3s
```

**Check 3**: Test dev server directly

```bash
curl http://localhost:3001/private
# Should return HTML
```

  </TabItem>
  <TabItem value="prod" label="Production Mode">

**Check 1**: Does ZIP archive exist?

```bash
ls -lh static/nextjs_admin.zip
# Should show file ~5-10MB
```

**Check 2**: Check Django logs for extraction

```bash
python manage.py runserver
# Look for:
# INFO: Extracting nextjs_admin.zip...
# INFO: Successfully extracted nextjs_admin.zip
```

**Check 3**: Check if directory was created

```bash
ls -la static/
# Should see extracted directory
```

**Check 4**: Permissions

```bash
# Ensure Django can write to static/
chmod 755 static/
```

  </TabItem>
</Tabs>

### CORS Errors

**Problem**: Console shows CORS errors:

```
Access to fetch at 'http://localhost:8000/api/...' from origin
'http://localhost:3001' has been blocked by CORS policy
```

**Solution**: Add Next.js dev URL to CORS allowed origins:

```python title="api/config.py"
config = DjangoConfig(
    # ... other settings

    cors_allowed_origins=[
        "http://localhost:3001",  # Next.js dev server
        "http://127.0.0.1:3001",
    ],
)
```

**Verify**:

```bash
python manage.py shell
>>> from django.conf import settings
>>> print(settings.CORS_ALLOWED_ORIGINS)
['http://localhost:3001', 'http://127.0.0.1:3001']
```

### Mixed Content Errors

**Problem**: iframe won't load in production HTTPS site.

```
Mixed Content: The page at 'https://yourdomain.com/admin/' was loaded
over HTTPS, but requested an insecure resource 'http://...'. This
request has been blocked.
```

**Solution**: Ensure all URLs use HTTPS in production:

```python title="api/config.py"
import os

config = DjangoConfig(
    # Force HTTPS in production
    secure_ssl_redirect=os.getenv("ENV_MODE") == "production",
)
```

## API Issues

### Token Not Found

**Problem**: Next.js can't find JWT tokens:

```javascript
console.error('Token not found in localStorage');
```

**Solution 1**: Check if user is authenticated:

```python
# User must be logged into Django admin first
# Visit http://localhost:8000/admin/ and login
```

**Solution 2**: Check token injection in Django:

```bash
# Enable debug logging
python manage.py runserver --verbosity=2

# Look for logs like:
# DEBUG: JWT tokens injected before </head> for user 1
```

**Solution 3**: Check HTML response:

```bash
# View source of iframe page
curl http://localhost:8000/cfg/admin/ | grep auth_token

# Should see script tag with:
# localStorage.setItem('auth_token', '...');
```

### API Calls Failing

**Problem**: API calls return 401 Unauthorized.

**Check 1**: Token exists

```javascript
// In browser console (iframe context)
console.log(localStorage.getItem('auth_token'));
// Should show token
```

**Check 2**: Token format

```javascript
// Token should be sent as Bearer token
const token = localStorage.getItem('auth_token');
console.log(`Bearer ${token}`);
```

**Check 3**: Token expiry

```javascript
// Decode JWT token (client-side)
const token = localStorage.getItem('auth_token');
const payload = JSON.parse(atob(token.split('.')[1]));
console.log('Token expires at:', new Date(payload.exp * 1000));
```

**Solution**: Implement token refresh:

```typescript
// Check if token is expired
function isTokenExpired(token: string): boolean {
  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    return payload.exp * 1000 < Date.now();
  } catch {
    return true;
  }
}

// Refresh if needed
if (isTokenExpired(token)) {
  await refreshToken();
}
```

### CSRF Token Issues

**Problem**: POST requests fail with CSRF token missing.

**Solution**: Django-cfg handles CSRF automatically, but ensure:

```typescript
// Include CSRF token from cookies
function getCsrfToken(): string | null {
  const cookies = document.cookie.split(';');
  for (const cookie of cookies) {
    const [name, value] = cookie.trim().split('=');
    if (name === 'csrftoken') {
      return value;
    }
  }
  return null;
}

// Use in fetch
fetch('/api/endpoint/', {
  method: 'POST',
  headers: {
    'X-CSRFToken': getCsrfToken() || '',
    'Authorization': `Bearer ${token}`,
  },
  body: JSON.stringify(data),
});
```

## Build Issues

### ZIP Not Created

**Problem**: `static/nextjs_admin.zip` doesn't exist after `generate_clients`.

**Check 1**: Did build complete successfully?

```bash
python manage.py generate_clients --typescript
# Should show:
# ✅ Built Next.js static export
# ✅ Created static/nextjs_admin.zip
```

**Check 2**: Check Next.js build errors

```bash
cd ../django_admin/apps/admin
pnpm build
# Look for build errors
```

**Check 3**: Verify `auto_build` setting

```python
nextjs_admin=NextJsAdminConfig(
    project_path="../django_admin",
    auto_build=True,  # Must be True (default)
)
```

**Check 4**: Manual build if needed

```bash
# Build manually
cd ../django_admin/apps/admin
pnpm build

# Create ZIP manually
cd out/
zip -r ../../../static/nextjs_admin.zip .
```

### Build Fails with TypeScript Errors

**Problem**: Next.js build fails with TypeScript errors in generated clients.

**Solution**: Regenerate clients:

```bash
# Clean generated files
rm -rf openapi/clients/typescript/

# Regenerate
python manage.py generate_clients --typescript

# Verify no errors
cd ../django_admin/apps/admin
pnpm typecheck
```

### Out of Memory Error

**Problem**: Next.js build fails with:

```
FATAL ERROR: Ineffective mark-compacts near heap limit
Allocation failed - JavaScript heap out of memory
```

**Solution**: Increase Node.js memory:

```bash
# Temporary
export NODE_OPTIONS="--max-old-space-size=4096"
pnpm build

# Permanent (package.json)
{
  "scripts": {
    "build": "NODE_OPTIONS='--max-old-space-size=4096' next build"
  }
}
```

## Production Issues

### 404 on Production

**Problem**: Next.js admin works locally but 404 in production.

**Check 1**: Is ZIP file copied to production?

```bash
# In Docker container
docker exec myapp ls -lh /app/static/nextjs_admin.zip
```

**Check 2**: Check extraction logs

```bash
docker logs myapp | grep "Extracting"
# Should see: Successfully extracted nextjs_admin.zip
```

**Check 3**: Check URL configuration

```python
# Verify static_url matches your nginx/ingress config
nextjs_admin=NextJsAdminConfig(
    static_url="/cfg/admin/",  # Must match production URL
)
```

### Slow First Request

**Problem**: First request to Next.js admin is very slow (~10 seconds).

**Explanation**: This is ZIP extraction happening on first request.

**Solutions**:

<Tabs>
  <TabItem value="accept" label="Accept One-Time Cost" default>

```python
# This is expected and optimal
# - ~100ms extraction time
# - Only happens once
# - Subsequent requests are instant
```

  </TabItem>
  <TabItem value="persistent" label="Use Persistent Volume">

```yaml
# docker-compose.yml
volumes:
  - static_cache:/app/static_extracted

# Extraction persists across container restarts
```

  </TabItem>
  <TabItem value="preextract" label="Pre-extract in Docker Build">

```dockerfile
# Not recommended (increases image size)
RUN unzip /app/static/nextjs_admin.zip -d /app/static/nextjs_admin/
```

  </TabItem>
</Tabs>

### Assets Not Loading

**Problem**: HTML loads but CSS/JS/images return 404.

**Check 1**: Check Next.js asset path configuration

```javascript title="next.config.js"
module.exports = {
  // Ensure basePath matches your static_url
  basePath: process.env.NEXT_PUBLIC_STATIC_BUILD === 'true'
    ? '/cfg/admin'
    : '',
  assetPrefix: process.env.NEXT_PUBLIC_STATIC_BUILD === 'true'
    ? '/cfg/admin'
    : '',
};
```

**Check 2**: Check WhiteNoise configuration

```python
# Verify WhiteNoise is serving static files
python manage.py shell
>>> from django.conf import settings
>>> print(settings.MIDDLEWARE)
# Should include: 'whitenoise.middleware.WhiteNoiseMiddleware'
```

**Check 3**: Test asset URL directly

```bash
curl http://localhost:8000/cfg/admin/_next/static/chunks/main.js
# Should return JavaScript
```

## Development Issues

### Hot Reload Not Working

**Problem**: Changes to Next.js code don't appear without full page refresh.

**Solution**: Ensure Next.js dev server is running (not static build):

```bash
# ✅ Correct - dev server
cd ../django_admin/apps/admin && pnpm dev

# ❌ Wrong - static build
# Don't build for development, use dev server
```

**Check**: Django should proxy to dev server:

```python
# Development config should use dev_url
nextjs_admin=NextJsAdminConfig(
    dev_url="http://localhost:3001",  # Must point to dev server
)
```

### Port Already in Use

**Problem**: Can't start Next.js dev server:

```
Error: listen EADDRINUSE: address already in use :::3001
```

**Solution 1**: Kill process using port

```bash
# Find process
lsof -i :3001

# Kill it
kill -9 <PID>
```

**Solution 2**: Use different port

```bash
# Start on different port
pnpm dev --port 3002

# Update Django config
nextjs_admin=NextJsAdminConfig(
    dev_url="http://localhost:3002",
)
```

### Module Not Found Errors

**Problem**: Next.js can't find generated API modules:

```
Module not found: Can't resolve '@/api/generated/profiles/client'
```

**Solution**: Verify API clients were copied:

```bash
ls -la ../django_admin/apps/admin/src/api/generated/
# Should show profiles/, trading/, etc.
```

**Regenerate if missing**:

```bash
python manage.py generate_clients --typescript
```

**Check path alias**:

```json title="tsconfig.json"
{
  "compilerOptions": {
    "paths": {
      "@/*": ["./src/*"]  // Ensure this is set
    }
  }
}
```

## Debugging Tips

### Enable Debug Logging

```python title="api/config.py"
config = DjangoConfig(
    # ... other settings

    logging={
        "version": 1,
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
            },
        },
        "loggers": {
            "django_cfg.apps.frontend": {
                "handlers": ["console"],
                "level": "DEBUG",  # Enable debug logs
            },
            "django_cfg.modules.nextjs_admin": {
                "handlers": ["console"],
                "level": "DEBUG",
            },
        },
    },
)
```

### Check Configuration at Runtime

```python
# In Django shell
python manage.py shell

from django_cfg import get_config

config = get_config()
print("Next.js Admin configured:", config.nextjs_admin is not None)

if config.nextjs_admin:
    print("Project path:", config.nextjs_admin.project_path)
    print("Static URL:", config.nextjs_admin.get_static_url())
    print("Dev URL:", config.nextjs_admin.get_dev_url())
```

### Browser DevTools

**Check iframe context:**

```javascript
// In browser console, switch to iframe context
// (Use dropdown in DevTools console)

// Check tokens
console.log('Access token:', localStorage.getItem('auth_token'));
console.log('Refresh token:', localStorage.getItem('refresh_token'));

// Check API calls
// Network tab → Filter by 'api' → Check request headers
```

### Network Inspection

```bash
# Use curl to debug
curl -v http://localhost:8000/cfg/admin/

# Check response headers
# Check if HTML contains JWT injection script
```

## Common Error Messages

### "Module 'django_cfg.modules.nextjs_admin' not found"

**Cause**: Module not registered in INSTALLED_APPS.

**Solution**: Ensure `nextjs_admin` is configured:

```python
nextjs_admin=NextJsAdminConfig(
    project_path="../django_admin",
)
```

### "Failed to extract nextjs_admin.zip"

**Cause**: Insufficient permissions or disk space.

**Solutions**:

```bash
# Check permissions
ls -ld static/
chmod 755 static/

# Check disk space
df -h

# Check ZIP file integrity
unzip -t static/nextjs_admin.zip
```

### "CSRF token missing or incorrect"

**Cause**: CSRF token not included in POST request.

**Solution**: Include CSRF token in headers:

```typescript
fetch('/api/endpoint/', {
  method: 'POST',
  headers: {
    'X-CSRFToken': getCsrfToken(),
    'Authorization': `Bearer ${token}`,
  },
  body: JSON.stringify(data),
});
```

## Getting Help

If you're still stuck:

1. **Check Logs**: Look for error messages in Django and Next.js logs
2. **GitHub Issues**: Search existing issues or open a new one
3. **Discord Community**: Join our Discord for real-time help
4. **Documentation**: Review the [How It Works](./how-it-works) section

### Reporting Issues

When reporting issues, include:

- Django-CFG version
- Next.js version
- Full error message and stack trace
- Minimal reproduction steps
- Configuration (sanitized)

```bash
# Get version info
pip show django-cfg
pnpm list next

# Get Django settings
python manage.py diffsettings

# Get logs
python manage.py runserver --verbosity=2 2>&1 | tee django.log
```

## Next Steps

- [Configuration Reference](./configuration) - Review all settings
- [Examples](./examples) - See working examples
- [How It Works](./how-it-works) - Understand internals

:::tip Still Need Help?
Join our [Discord community](https://discord.gg/django-cfg) or open an issue on [GitHub](https://github.com/django-cfg/django-cfg/issues).
:::
