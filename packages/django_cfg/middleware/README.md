# 🛡️ Django CFG Middleware

Custom Django middleware components for Django CFG applications.

## 📋 Contents

- [UserActivityMiddleware](#useractivitymiddleware) - User activity tracking

## UserActivityMiddleware

Middleware for automatic user activity tracking by updating the `last_login` field on API requests.

### ✨ Features

- ✅ Automatic `last_login` update on API requests
- ✅ Smart API request detection (JSON, DRF, REST methods)
- ✅ 5-minute update interval to prevent database spam
- ✅ In-memory caching for performance optimization
- ✅ Only works when `accounts` app is enabled
- ✅ KISS principle - no configuration needed

### 🚀 Automatic Integration

The middleware is automatically included when `enable_accounts = True`:

```python
class MyConfig(DjangoConfig):
    enable_accounts = True  # UserActivityMiddleware will be auto-included
```

### 🎯 API Request Detection

The middleware intelligently detects API requests using:

1. **JSON Content-Type or Accept header**
   ```
   Content-Type: application/json
   Accept: application/json
   ```

2. **DRF format parameter**
   ```
   ?format=json
   ?format=api
   ```

3. **REST methods** (POST, PUT, PATCH, DELETE) on non-admin paths

4. **Configured API prefixes**
   - Django Revolution API: `/{api_prefix}/` (from config)
   - Django CFG API: `/cfg/` (always)

### 📊 Statistics

Get middleware statistics:

```python
from django_cfg.middleware import UserActivityMiddleware

# In view or management command
middleware = UserActivityMiddleware()
stats = middleware.get_activity_stats()

print(stats)
# {
#     'tracked_users': 42,
#     'update_interval': 300,
#     'api_only': True,
#     'accounts_enabled': True,
#     'middleware_active': True
# }
```

### 🔍 Logging

The middleware logs activity at DEBUG level:

```python
# settings.py
LOGGING = {
    'loggers': {
        'django_cfg.middleware.user_activity': {
            'level': 'DEBUG',
            'handlers': ['console'],
        },
    },
}
```

### 🎛️ Manual Integration

If you need to include the middleware manually:

```python
# settings.py
MIDDLEWARE = [
    # ... other middleware
    'django_cfg.middleware.UserActivityMiddleware',
]
```

### 🔧 Performance

- **Caching**: Last update times are cached in memory
- **Batch updates**: Uses `update()` instead of `save()` for optimization
- **Auto-cleanup**: Cache automatically cleans up when exceeding 1000 users
- **Graceful errors**: Errors don't break request processing

### 🎯 Admin Integration

The `last_login` field is automatically displayed in accounts admin:

- ✅ In user list view (`last_login_display`)
- ✅ In user detail view
- ✅ With human-readable time format

### 🚨 Important Notes

1. **Accounts only**: Middleware only works when `enable_accounts = True`
2. **Authentication**: Only tracks authenticated users
3. **Performance**: 5-minute interval prevents database spam
4. **Safety**: Middleware doesn't break requests on errors

### 📈 Monitoring

For user activity monitoring:

```python
# In Django admin or management command
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

# Active users in the last hour
active_users = User.objects.filter(
    last_login__gte=timezone.now() - timedelta(hours=1)
).count()

# Online users (last 5 minutes)
online_users = User.objects.filter(
    last_login__gte=timezone.now() - timedelta(minutes=5)
).count()
```

### 💡 Usage Examples

The middleware works automatically with no configuration needed:

```python
# Your DjangoConfig
class MyProjectConfig(DjangoConfig):
    enable_accounts = True  # That's it! Middleware is active

# API requests will automatically update last_login:
# POST /cfg/accounts/profile/
# GET /api/users/?format=json
# PUT /cfg/newsletter/subscribe/
```
