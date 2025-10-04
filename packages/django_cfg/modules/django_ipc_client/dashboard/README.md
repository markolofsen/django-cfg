# RPC Dashboard 📊

**Real-time WebSocket & RPC Activity Monitor**

Built-in dashboard for monitoring RPC requests, notifications, and WebSocket activity.

---

## ✨ Features

- ✅ **Real-time Monitoring** - Live updates every 5 seconds
- ✅ **Request Tracking** - View recent RPC calls with details
- ✅ **Notification Stats** - Track sent notifications by type
- ✅ **Method Analytics** - See which RPC methods are called most
- ✅ **Health Checks** - Monitor Redis and stream status
- ✅ **Tailwind CSS** - Beautiful dark mode UI
- ✅ **Zero Config** - Works out of the box
- ✅ **Django Cache** - 3-second cache reduces Redis load
- ✅ **XSS Protection** - Secure against injection attacks
- ✅ **Stream Validation** - Whitelist prevents Redis key injection
- ✅ **Error Handling** - Specific HTTP codes (400, 503, 500)

---

## 🚀 Quick Start

### ✨ Automatic Integration (Recommended)

Simply enable RPC in your django-cfg configuration:

```python
# config.py
from django_cfg import DjangoConfig
from django_cfg.modules.django_ipc_client.config import DjangoCfgRPCConfig

class MyProjectConfig(DjangoConfig):
    # Enable RPC Client
    django_ipc = DjangoCfgRPCConfig(
        enabled=True,
        redis_url="redis://localhost:6379/2",
    )

config = MyProjectConfig()
```

**That's it!** Django-cfg automatically:
- ✅ Adds dashboard app to `INSTALLED_APPS`
- ✅ Registers URL at `/admin/rpc/`
- ✅ Adds "Operations" section to Unfold navigation
- ✅ Generates `DJANGO_CFG_RPC` settings

### Access Dashboard

Navigate to: **http://localhost:8000/admin/rpc/**

(Requires staff user login - `is_staff=True`)

---

### Manual Integration (Advanced)

If not using django-cfg's automatic integration:

```python
# urls.py
from django.urls import path, include

urlpatterns = [
    # RPC Dashboard (requires staff login)
    path('admin/rpc/', include('django_cfg.modules.django_ipc_client.dashboard.urls')),
]
```

For Unfold navigation customization, see [UNFOLD_INTEGRATION.md](./UNFOLD_INTEGRATION.md)

---

## 📊 Dashboard Tabs

### Overview Tab

Shows key metrics:
- Total requests today
- Active RPC methods
- Average response time
- Success rate

### Recent Requests Tab

Live stream of RPC calls:
- Timestamp
- Method name
- Correlation ID
- Request parameters (expandable)

### Notifications Tab

Notification statistics:
- Total sent
- Delivery rate
- Breakdown by type
- Recent notifications

### Methods Tab

Analytics by RPC method:
- Call count
- Percentage of total
- Average response time

---

## 🔧 Configuration

### Default Settings

```python
# In your Django settings.py (auto-configured)
DJANGO_CFG_RPC = {
    'redis_url': 'redis://localhost:6379/2',  # RPC database
    'request_stream': 'stream:requests',
    # ... other settings
}
```

### URL Customization

Mount at custom path:

```python
urlpatterns = [
    path('my/custom/path/', include('django_cfg.modules.django_ipc_client.dashboard.urls')),
]
```

---

## 🧪 Testing

### Run Tests

```bash
# Run all dashboard tests
pytest django_cfg/modules/django_ipc_client/tests/

# Run monitor tests
pytest django_cfg/modules/django_ipc_client/tests/test_monitor.py -v

# Run view tests
pytest django_cfg/modules/django_ipc_client/tests/test_dashboard.py -v
```

### Test Coverage

- ✅ **RPCMonitor**: 15 tests
- ✅ **Dashboard Views**: 10 tests
- ✅ **Integration Tests**: Fakeredis support

---

## 📡 API Endpoints

Dashboard exposes JSON API endpoints:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/admin/rpc/api/overview/` | GET | Overview statistics |
| `/admin/rpc/api/requests/?count=50` | GET | Recent RPC requests |
| `/admin/rpc/api/notifications/` | GET | Notification stats |
| `/admin/rpc/api/methods/` | GET | Method statistics |
| `/admin/rpc/api/health/` | GET | Health check |

All endpoints return JSON:

```json
{
    "success": true,
    "data": { ... }
}
```

---

## 🏗️ Architecture

```
dashboard/
├── monitor.py          # RPCMonitor class (reads Redis)
├── views.py            # Django views + JSON API
├── urls.py             # URL routing
├── templates/          # Tailwind CSS templates
│   └── django_ipc_dashboard/
│       ├── base.html
│       └── dashboard.html
└── static/             # JavaScript
    └── django_ipc_dashboard/
        └── js/
            └── dashboard.js
```

### Data Flow

```
Redis DB 2 (stream:requests)
    ↓
RPCMonitor.get_overview_stats()
    ↓
Django View (dashboard_view)
    ↓
Template (dashboard.html)
    ↓
JavaScript (auto-refresh every 5s)
    ↓
API Endpoints (/api/overview/, etc.)
```

---

## 🎨 Customization

### Disable Auto-Refresh

Toggle "Auto-refresh" checkbox in dashboard header.

### Change Refresh Interval

Edit `dashboard.js`:

```javascript
class RPCDashboard {
    constructor() {
        this.refreshInterval = 10000; // 10 seconds instead of 5
        // ...
    }
}
```

### Custom Styling

Override Tailwind classes or add custom CSS to `base.html`.

---

## 🐛 Troubleshooting

### Dashboard shows "Redis not connected"

**Check:**
1. Redis running: `redis-cli ping`
2. Correct Redis URL in config
3. Using DB 2 for RPC: `redis://localhost:6379/2`

**Solution:**
```bash
# Check Redis is running
redis-cli -h localhost -p 6379 ping  # Should return "PONG"

# Check database 2 is accessible
redis-cli -h localhost -p 6379 -n 2 ping
```

### No requests showing up

**Check:**
1. RPC client actually making requests
2. Request stream exists: `redis-cli XLEN stream:requests`
3. Recent activity (last 5 minutes)

**Debug:**
```bash
# Check stream exists and has data
redis-cli -n 2 XLEN stream:requests

# View latest request
redis-cli -n 2 XREVRANGE stream:requests + - COUNT 1
```

### Permission denied

**Solution:** Dashboard requires staff user login (`is_staff=True`)

```python
user = User.objects.get(username='your_user')
user.is_staff = True
user.save()
```

### Dashboard is slow / High Redis load

**Solution:** Dashboard uses 3-second cache. If still slow:

1. Increase cache timeout in `monitor.py`:
```python
CACHE_TIMEOUT = 5  # Change from 3 to 5 seconds
```

2. Configure Django cache backend (default uses in-memory):
```python
# settings.py
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://localhost:6379/0',
    }
}
```

3. Reduce stream read count in `monitor.py`:
```python
recent_requests = self._get_recent_stream_entries(count=500)  # Down from 1000
```

### API returns 503 "Service Unavailable"

**Cause:** Redis connection lost or timeout

**Solution:**
```python
# Check Redis connection settings
config = DjangoCfgRPCConfig()
print(config.redis_url)  # Should be redis://localhost:6379/2

# Increase timeout in monitor.py _create_redis_client():
client = redis.Redis(
    socket_connect_timeout=10,  # Up from 5
    socket_timeout=10,           # Up from 5
)

---

## 📚 Related Documentation

- [RPC Client README](../README.md)
- [RPC Integration Guide](../../../../../../@docs/websocket2/RPC_DRAMATIQ_INTEGRATION.md)
- [Redis Database Allocation](../../../../../../@docs/websocket2/REDIS_DATABASES.md)

---

## 🎯 Example Use Cases

### 1. Monitor Notification Delivery

Track how many notifications are sent to users:

1. Go to "Notifications" tab
2. See total sent + delivery rate
3. Breakdown by notification type

### 2. Debug RPC Issues

When RPC calls fail:

1. Go to "Recent Requests" tab
2. Find failing request
3. Expand "View" to see parameters
4. Check correlation ID for tracing

### 3. Analyze Performance

Find slow RPC methods:

1. Go to "Methods" tab
2. Sort by "Avg Time"
3. Identify bottlenecks

---

## ✅ Summary

- **Location**: `django_cfg/modules/django_ipc_client/dashboard/`
- **URL**: `/admin/rpc/` (customizable)
- **Requirements**: Staff login, Redis DB 2
- **Tech Stack**: Django, Tailwind CSS, Vanilla JS
- **Tests**: 25+ tests with mocks + fakeredis

**Production Ready**: ✅

---

## 🚀 Production Deployment Checklist

### 1. Security
- [ ] Verify all views use `@staff_member_required`
- [ ] Configure HTTPS for dashboard URL
- [ ] Enable CSRF protection (Django default)
- [ ] Set strong `SECRET_KEY` in production

### 2. Redis Configuration
- [ ] Use dedicated Redis DB for RPC (DB 2)
- [ ] Configure Redis persistence (AOF or RDB)
- [ ] Set Redis `maxmemory-policy` to `allkeys-lru`
- [ ] Enable Redis password authentication

```python
# Production config
DJANGO_CFG_RPC = DjangoCfgRPCConfig(
    redis_url="redis://:strong_password@redis-server:6379/2",
    redis_max_connections=100,  # Increase for production
)
```

### 3. Django Cache
- [ ] Configure Redis cache backend (not in-memory)
- [ ] Set cache timeout appropriately

```python
# settings.py
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://localhost:6379/0',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}
```

### 4. Static Files
- [ ] Run `python manage.py collectstatic`
- [ ] Configure static files serving (nginx/whitenoise)
- [ ] Verify Tailwind CSS loads from CDN

### 5. Performance
- [ ] Monitor Redis memory usage
- [ ] Set stream MAXLEN to prevent unbounded growth
- [ ] Consider Redis eviction policy
- [ ] Enable connection pooling (default: enabled)

```bash
# Monitor Redis memory
redis-cli INFO memory

# Trim old stream entries (if needed)
redis-cli -n 2 XTRIM stream:requests MAXLEN 10000
```

### 6. Monitoring
- [ ] Set up logging for dashboard errors
- [ ] Monitor API endpoint response times
- [ ] Track Redis connection errors
- [ ] Set up alerts for 503 errors

```python
# settings.py - Enhanced logging
LOGGING = {
    'loggers': {
        'django_cfg.modules.django_ipc_client.dashboard': {
            'level': 'INFO',
            'handlers': ['file', 'sentry'],  # Add Sentry for production
        },
    },
}
```

### 7. Testing
- [ ] Run all tests: `pytest django_cfg/modules/django_ipc_client/tests/`
- [ ] Load test API endpoints
- [ ] Verify dashboard loads with production data
- [ ] Test with Redis connection failures

### 8. Documentation
- [ ] Document custom URL mounting path
- [ ] Document Redis DB allocation
- [ ] Document staff user creation process

---

## 🔧 Performance Optimization

### Redis Stream Management

Prevent unlimited stream growth:

```bash
# Add to cron (daily cleanup)
redis-cli -n 2 XTRIM stream:requests MAXLEN 50000

# Or use MAXLEN in stream writes (django-cfg-rpc server)
XADD stream:requests MAXLEN ~ 10000 * payload {...}
```

### Cache Configuration

Optimize cache for high traffic:

```python
# monitor.py - Adjust cache timeout based on traffic
CACHE_TIMEOUT = 5  # Higher for production (less Redis load)

# settings.py - Use connection pool
CACHES = {
    'default': {
        'LOCATION': 'redis://localhost:6379/0',
        'OPTIONS': {
            'CONNECTION_POOL_KWARGS': {
                'max_connections': 50
            }
        }
    }
}
```

---

## 🔒 Security Notes

1. **XSS Protection**: All user data sanitized via `textContent` (not `innerHTML`)
2. **Stream Key Validation**: Whitelist prevents Redis key injection
3. **Staff-Only Access**: All endpoints require `is_staff=True`
4. **Error Messages**: Generic messages in production (no stack traces to clients)
5. **CSRF**: Django CSRF protection enabled by default

---

**Last Updated**: 2025-10-03
**Version**: 2.0 (Security Hardened)
