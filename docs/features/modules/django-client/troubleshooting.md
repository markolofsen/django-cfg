---
title: Troubleshooting
sidebar_position: 5
keywords:
  - django client troubleshooting
  - django client errors
  - openapi client issues
  - api client debugging
description: Troubleshooting guide for Django Client. Common issues, solutions, and debugging tips.
---

# Troubleshooting

Common issues and solutions when using Django Client.

---

## Generation Issues

### No Operations Found

**Problem:**
```
✅ Generated 0 operations
```

**Causes:**
1. No ViewSets registered in URL router
2. drf-spectacular not properly configured
3. Apps not included in group configuration

**Solutions:**

**1. Check ViewSets are registered:**

```python
# users/api/views.py
from rest_framework import viewsets

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
```

**2. Verify URL patterns:**

```python
# users/urls.py
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('users', UserViewSet)
urlpatterns = router.urls
```

**3. Check Django-CFG configuration:**

```python
groups=[
    OpenAPIGroupConfig(
        name="core",
        apps=["users"],  # ✅ Make sure app is included
    ),
]
```

**4. Validate OpenAPI schema:**

```bash
python manage.py spectacular --validate --format openapi --file openapi.yaml
```

---

### Empty Generated Files

**Problem:**
Generated client has no models or operations.

**Solution:**

Check OpenAPI schema has content:

```bash
# Generate schema
python manage.py spectacular --file openapi.yaml

# Check file size
ls -lh openapi.yaml

# View content
cat openapi.yaml
```

If schema is empty:
- Ensure `drf-spectacular` is in `INSTALLED_APPS`
- Check `REST_FRAMEWORK` has `DEFAULT_SCHEMA_CLASS`
- Verify ViewSets have serializers

---

## TypeScript Issues

### Module Not Found

**Problem:**
```
Module 'zod' not found
Module 'swr' not found
```

**Solution:**

Install dependencies:

```bash
cd frontend
npm install zod swr
# or
pnpm install zod swr
# or
yarn add zod swr
```

---

### Type Errors

**Problem:**
```
error TS2345: Argument of type 'string' is not assignable to parameter of type 'number'
```

**Solutions:**

**1. Regenerate with latest version:**

```bash
pip install --upgrade django-cfg
python manage.py generate_api
```

**2. Check OpenAPI schema:**

Ensure field types are correct in Django serializers:

```python
# ❌ Wrong
class UserSerializer(serializers.Serializer):
    id = serializers.CharField()  # Should be IntegerField

# ✅ Correct
class UserSerializer(serializers.Serializer):
    id = serializers.IntegerField()
```

**3. Clear TypeScript cache:**

```bash
cd frontend
rm -rf node_modules/.cache
rm -rf .next  # for Next.js
pnpm tsc --noEmit  # Check for errors
```

---

### Import Errors

**Problem:**
```
Cannot find module '@/api/generated/users'
```

**Solution:**

**1. Check tsconfig.json paths:**

```json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"]
    }
  }
}
```

**2. Verify generated files exist:**

```bash
ls -la src/api/generated
```

**3. Restart TypeScript server:**

In VS Code: `Cmd+Shift+P` → "TypeScript: Restart TS Server"

---

## Python Issues

### ModuleNotFoundError

**Problem:**
```
ModuleNotFoundError: No module named 'api_client'
```

**Solutions:**

**1. Add to Python path:**

```python
import sys
sys.path.insert(0, '/path/to/api_client')

from api_client import APIClient
```

**2. Install as editable package:**

```bash
cd api_client
pip install -e .
```

**3. Check PYTHONPATH:**

```bash
export PYTHONPATH="${PYTHONPATH}:/path/to/backend"
python -c "from api_client import APIClient"
```

---

### ValidationError

**Problem:**
```
pydantic.error_wrappers.ValidationError: 1 validation error for User
```

**Solutions:**

**1. Check request data matches schema:**

```python
# ❌ Wrong
await client.users.create(data={
    "id": 1,  # Read-only field!
    "username": "john"
})

# ✅ Correct
await client.users.create(data={
    "username": "john",
    "email": "john@example.com"
})
```

**2. Use Pydantic models for validation:**

```python
from api_client.models import UserRequest

# Validate before sending
user_data = UserRequest.model_validate({
    "username": "john",
    "email": "john@example.com"
})

await client.users.create(data=user_data)
```

---

## Runtime Issues

### Authentication Not Working

**Problem:**
API returns 401 Unauthorized.

**Solutions:**

**TypeScript:**

```typescript
import { configureAPI } from '@/api/generated/api-instance'

configureAPI({
  baseUrl: 'https://api.example.com',
  getAuthToken: () => {
    // ✅ Get token from storage
    return localStorage.getItem('auth_token')
  },
})
```

**Python:**

```python
client = APIClient(
    base_url="https://api.example.com",
    headers={
        "Authorization": f"Bearer {get_auth_token()}"
    }
)
```

---

### CORS Errors

**Problem:**
```
Access to fetch at 'https://api.example.com' from origin 'http://localhost:3000'
has been blocked by CORS
```

**Solution:**

Configure CORS in Django:

```python
# settings.py
INSTALLED_APPS += ['corsheaders']

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # ✅ Add this
    'django.middleware.common.CommonMiddleware',
    ...
]

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:3001",
]

# ⚠️ Development only
CORS_ALLOW_ALL_ORIGINS = True  # Don't use in production!
```

---

### File Upload Not Working

**Problem:**
```
TypeError: file is not a File or Blob
```

**Solutions:**

**1. Browser (correct):**

```typescript
// ✅ Correct
const file = event.target.files[0]  // File object
await uploadDocument({ title: "Doc", file: file })

// ❌ Wrong
await uploadDocument({ title: "Doc", file: "path/to/file" })
```

**2. React Native:**

```typescript
import { launchImageLibrary } from 'react-native-image-picker'

const result = await launchImageLibrary({ mediaType: 'photo' })
const file = {
  uri: result.assets[0].uri,
  type: result.assets[0].type,
  name: result.assets[0].fileName,
}

// Use FormData
const formData = new FormData()
formData.append('file', file)
await uploadDocument({ title: "Doc", file: formData })
```

---

### Network Errors

**Problem:**
```
TypeError: Failed to fetch
```

**Solutions:**

**1. Check API is running:**

```bash
curl https://api.example.com/health
```

**2. Check baseUrl configuration:**

```typescript
configureAPI({
  baseUrl: 'https://api.example.com',  // ✅ No trailing slash
})
```

**3. Check network connectivity:**

```bash
ping api.example.com
```

---

## Configuration Issues

### Schema Generation Fails

**Problem:**
```
CommandError: Error generating schema
```

**Solutions:**

**1. Install drf-spectacular:**

```bash
pip install drf-spectacular>=0.26.5
```

**2. Configure Django settings:**

```python
INSTALLED_APPS = [
    'rest_framework',
    'drf_spectacular',
]

REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}
```

**3. Validate configuration:**

```bash
python manage.py spectacular --validate
```

---

### Rate Limiting Blocks Generation

**Problem:**
Schema endpoints return 429 Too Many Requests.

**Solution:**

Exempt schema endpoints from rate limiting:

```python
# Django-CFG configuration
RATE_LIMIT_EXEMPT_PATHS = [
    '/schema/',
    '/api/schema/',
]
```

---

## Performance Issues

### Slow Generation

**Problem:**
Generation takes too long (>30 seconds).

**Solutions:**

**1. Use groups to split APIs:**

```python
# Split into smaller groups
groups=[
    OpenAPIGroupConfig(name="core", apps=["users", "auth"]),
    OpenAPIGroupConfig(name="billing", apps=["payments"]),
]
```

**2. Generate specific groups only:**

```bash
# Only regenerate core
python manage.py generate_api --groups core
```

**3. Check for circular imports:**

Ensure no circular dependencies in Django models.

---

### Large Bundle Size

**Problem:**
Generated TypeScript client is too large.

**Solutions:**

**1. Use groups to split code:**

```python
# Generate separate clients
groups=[
    OpenAPIGroupConfig(name="web", apps=["users", "content"]),
    OpenAPIGroupConfig(name="admin", apps=["admin", "analytics"]),
]
```

**2. Import only what you need:**

```typescript
// ✅ Specific imports
import { getUsers } from '@/api/generated/core/_utils/fetchers/users'

// ❌ Import everything
import * as api from '@/api/generated/core'
```

---

## Debugging Tips

### Enable Verbose Logging

```bash
# Django-CFG debug mode
DJANGO_CFG_DEBUG=1 python manage.py generate_api
```

### Check Generated Code

Inspect generated files:

```bash
# TypeScript
cat frontend/src/api/generated/client.ts

# Python
cat backend/api_client/client.py
```

### Validate OpenAPI Schema

```bash
# Validate schema
python manage.py spectacular --validate

# Generate and view schema
python manage.py spectacular --file openapi.yaml
cat openapi.yaml
```

### Test API Manually

```bash
# Test API endpoint
curl -X GET https://api.example.com/api/users/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## Getting Help

If you encounter issues not covered here:

1. **Check documentation**: [Overview](./overview), [Examples](./examples)
2. **Search issues**: [GitHub Issues](https://github.com/your-org/django-cfg/issues)
3. **Ask community**: [Discord](https://discord.gg/django-cfg)
4. **Report bug**: Open a new issue with:
   - Django-CFG version
   - OpenAPI schema (if possible)
   - Error messages
   - Steps to reproduce

---

## Next Steps

- **[Examples](./examples)** - Usage examples
- **[Advanced Topics](./advanced)** - Groups, CI/CD
- **[Overview](./overview)** - Feature overview
