# 🛡️ Django CFG Middleware

Custom Django middleware components for Django CFG applications.

## 📋 Contents

- [UserActivityMiddleware](#useractivitymiddleware) - User activity tracking
- [Admin Login Notifications](#admin-login-notifications) - Real-time Telegram alerts for admin access

## JWT Token Injection for Next.js Apps

**Note:** JWT token injection is now handled by `NextJSStaticView` in `apps/frontend/views.py`, not by middleware.

This provides better security by limiting JWT injection scope to Next.js applications only.

### 📖 Full Documentation

See [`/apps/frontend/JWT_AUTO_INJECTION.md`](../apps/frontend/JWT_AUTO_INJECTION.md) for complete JWT injection documentation.

---

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
   - Django Client API: `/{api_prefix}/` (from config)
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

---

## Admin Login Notifications

Real-time Telegram notifications for admin panel access monitoring. Automatically sends alerts for successful logins, failed attempts, and account lockouts.

### ✨ Features

- ✅ **Successful admin logins** - Info notifications with user details
- ✅ **Failed login attempts** - Warning notifications (django-axes integration)
- ✅ **Account lockouts** - Error alerts for brute-force protection
- ✅ **Real IP detection** - Cloudflare/nginx/traefik support
- ✅ **Role identification** - Superuser vs staff differentiation
- ✅ **Zero configuration** - Works automatically when Telegram is configured

### 🚀 Automatic Integration

Admin login notifications activate automatically when Telegram is configured:

```python
# config.py
class MyConfig(DjangoConfig):
    # Configure Telegram
    telegram: TelegramConfig = TelegramConfig(
        bot_token="your-bot-token",
        chat_id=123456789,
    )

    # That's it! Admin login notifications are now active
```

### 📱 Notification Types

#### 1. Successful Login (Info)

**Superuser login:**
```
👑 Admin Login (Superuser)

user: admin@example.com
username: admin
role: Superuser
is_superuser: true
login_time: 2025-10-21 15:30:45 UTC
ip_address: 192.168.1.100
user_agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)...
user_id: 1
```

**Staff login:**
```
🔐 Admin Login (Staff)

user: staff@example.com
username: staff_user
role: Staff
is_superuser: false
login_time: 2025-10-21 15:32:10 UTC
ip_address: 192.168.1.101
user_agent: Mozilla/5.0...
user_id: 5
```

#### 2. Failed Login Attempt (Warning)

```
⚠️ Failed Admin Login Attempt

username: admin
ip_address: 203.0.113.45
time: 2025-10-21 15:35:22 UTC
user_agent: Mozilla/5.0...
path: /admin/login/
```

#### 3. Account Lockout (Error)

```
🚨 Admin Account LOCKED OUT

username: admin
ip_address: 203.0.113.45
time: 2025-10-21 15:36:10 UTC
reason: Too many failed login attempts
action_required: Manual unlock required in admin panel or via axes_reset command
```

### 🔧 How It Works

The module uses **Django signals** (not traditional middleware):

1. **`user_logged_in` signal** - Catches all successful logins
   - Filters for `/admin/` paths only
   - Checks `is_staff` or `is_superuser` permissions
   - Sends Telegram info notification

2. **`user_login_failed` signal** - Catches failed attempts (django-axes)
   - Only for admin panel paths
   - Sends warning notification

3. **`user_locked_out` signal** - Catches lockouts (django-axes)
   - Critical security alert
   - Sends error notification

### 🌐 Proxy Support

Automatically extracts real client IP through proxies:

**Header precedence** (matches AxesConfig):
1. `HTTP_CF_CONNECTING_IP` - Cloudflare real IP
2. `HTTP_X_FORWARDED_FOR` - Nginx/Traefik proxy
3. `HTTP_X_REAL_IP` - Alternative proxy header
4. `REMOTE_ADDR` - Direct connection

**Example with Cloudflare:**
```
Client (203.0.113.45) → Cloudflare → nginx → Django

Headers received:
- HTTP_CF_CONNECTING_IP: 203.0.113.45  ← Real client IP
- HTTP_X_FORWARDED_FOR: 203.0.113.45, 104.21.1.1
- REMOTE_ADDR: 172.18.0.1

Detected IP: 203.0.113.45 ✅
```

### 🔒 Security Benefits

1. **Immediate attack detection** - Real-time alerts for suspicious activity
2. **Brute-force monitoring** - Track failed login patterns
3. **Lockout notifications** - Know when accounts are locked
4. **IP tracking** - Identify attack sources
5. **Role awareness** - Monitor superuser vs staff access

### 📊 Integration with Django-Axes

Works seamlessly with django-axes brute-force protection:

```python
# config.py
class MyConfig(DjangoConfig):
    # Django-Axes configuration
    axes: AxesConfig = AxesConfig(
        failure_limit=5,      # 5 failed attempts
        cooloff_time=24,      # 24 hour lockout
    )

    # Telegram configuration
    telegram: TelegramConfig = TelegramConfig(
        bot_token="your-token",
        chat_id=123456789,
    )

    # Notifications work automatically:
    # 1. Failed attempt → Telegram warning
    # 2. 5th failed attempt → Account locked
    # 3. Lockout → Telegram error alert
```

### 🎯 Admin Panel Only

Notifications are **only sent for admin panel access**:

✅ **Monitored paths:**
- `/admin/login/`
- `/admin/`
- `/admin/accounts/customuser/`
- Any path starting with `/admin/`

❌ **Not monitored:**
- `/api/auth/login/` - API login
- `/cfg/accounts/otp/` - OTP login
- Regular user logins

### 🔕 Disabling Notifications

To disable admin login notifications:

```python
# Option 1: Disable Telegram entirely
telegram: Optional[TelegramConfig] = None

# Option 2: Set bot_token to empty
telegram: TelegramConfig = TelegramConfig(
    bot_token="",  # Notifications disabled
    chat_id=0,
)
```

### 🧪 Testing

Test admin login notifications:

```bash
# 1. Test successful login
# - Login to admin panel at /admin/
# - Check Telegram for "🔐 Admin Login" or "👑 Admin Login (Superuser)"

# 2. Test failed login
# - Try wrong password at /admin/login/
# - Check Telegram for "⚠️ Failed Admin Login Attempt"

# 3. Test lockout
# - Fail login 5 times (default AXES_FAILURE_LIMIT)
# - Check Telegram for "🚨 Admin Account LOCKED OUT"

# 4. Test unlock
python manage.py axes_reset username admin
# Login again - should get success notification
```

### 📝 Logging

All notifications are logged:

```python
# settings.py or configure logging
LOGGING = {
    'loggers': {
        'django_cfg.middleware.admin_notifications': {
            'level': 'INFO',
            'handlers': ['console'],
        },
    },
}
```

**Log output:**
```
INFO Admin login notification sent for admin@example.com from 192.168.1.100
WARNING Failed admin login attempt: admin from 203.0.113.45
ERROR Admin account locked out: admin from 203.0.113.45
```

### 🚨 Important Notes

1. **Requires Telegram** - Only works when TelegramConfig is configured
2. **Django-Axes optional** - Failed login/lockout notifications require django-axes
3. **Signal-based** - Not a traditional middleware class, uses Django signals
4. **Auto-registers** - Signals register automatically on import
5. **Fail-safe** - Notification errors don't break login flow

### 💡 Usage Examples

**Example 1: Basic setup**
```python
# config.py
class MyConfig(DjangoConfig):
    telegram: TelegramConfig = TelegramConfig(
        bot_token=env.telegram.bot_token,
        chat_id=env.telegram.chat_id,
    )

# Done! Admin logins now send Telegram notifications
```

**Example 2: With django-axes**
```python
# config.py
class MyConfig(DjangoConfig):
    # Brute-force protection
    axes: AxesConfig = AxesConfig(
        failure_limit=3,
        cooloff_time=48,
    )

    # Telegram notifications
    telegram: TelegramConfig = TelegramConfig(
        bot_token=env.telegram.bot_token,
        chat_id=env.telegram.chat_id,
    )

# Get notifications for:
# ✅ Successful logins
# ✅ Failed attempts
# ✅ Lockouts
```

**Example 3: Production monitoring**
```python
# config.py
class ProdConfig(DjangoConfig):
    debug: bool = False
    security_domains: list = ["myapp.com"]

    # Strict brute-force protection
    axes: AxesConfig = AxesConfig(
        failure_limit=3,      # Only 3 attempts
        cooloff_time=72,      # 72 hour lockout
        allowed_ips=[         # Whitelist office IPs
            '192.168.1.0/24',
        ],
    )

    # Telegram security monitoring
    telegram: TelegramConfig = TelegramConfig(
        bot_token=env.telegram.bot_token,
        chat_id=env.telegram.security_chat_id,  # Dedicated security channel
    )

# Production security monitoring:
# 🔐 Know who accesses admin panel
# ⚠️ Track suspicious login attempts
# 🚨 Get immediate lockout alerts
```

### 🔍 Troubleshooting

**Problem: No notifications sent**

1. Check Telegram configuration:
```python
from django_cfg.modules.django_telegram import DjangoTelegram

telegram = DjangoTelegram()
print(telegram.is_configured)  # Should be True
print(telegram.get_config_info())
```

2. Test Telegram manually:
```python
from django_cfg.modules.django_telegram import DjangoTelegram

DjangoTelegram.send_info("Test", {"message": "Testing admin notifications"})
```

3. Check logs:
```bash
# Enable DEBUG logging
tail -f logs/django.log | grep admin_notifications
```

**Problem: Wrong IP address**

Configure proxy settings:
```python
# config.py
axes: AxesConfig = AxesConfig(
    ipware_proxy_count=1,  # Adjust based on proxy layers
    ipware_meta_precedence_order=[
        'HTTP_CF_CONNECTING_IP',  # Add your proxy header
        'HTTP_X_FORWARDED_FOR',
        'REMOTE_ADDR',
    ],
)
```

**Problem: Too many notifications**

Notifications are sent once per login. If you're getting duplicates:
- Check for multiple middleware/signal registrations
- Verify django-axes is not sending duplicate signals

### 📚 See Also

- [Django-Axes Configuration](../fundamentals/configuration/security.md#django-axes-brute-force-protection)
- [Telegram Module](../modules/django_telegram)
- [Security Settings](../fundamentals/configuration/security.md)
