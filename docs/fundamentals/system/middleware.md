---
title: Middleware System
description: Django-CFG middleware fundamentals. Comprehensive guide to middleware system with Pydantic validation, type safety, and enterprise patterns.
sidebar_label: Middleware
sidebar_position: 8
keywords:
  - django-cfg middleware
  - django middleware configuration
  - type-safe middleware django
---

# Middleware System

Django-CFG includes a **comprehensive middleware system** that provides automatic user activity tracking, public endpoint management, and enhanced request processing.

## Overview

The Django-CFG middleware system provides:
- **User Activity Tracking** - Automatic last_login updates for API requests
- **Public Endpoints Management** - Bypass authentication for specific endpoints
- **Performance Optimization** - Smart caching and batch operations
- **Automatic Integration** - Zero-configuration setup with Django-CFG apps

## User Activity Middleware

### Automatic User Activity Tracking

The `UserActivityMiddleware` automatically tracks user activity by updating the `last_login` field on API requests.

```python
# Automatically enabled when accounts app is active
class MyConfig(DjangoConfig):
    enable_accounts: bool = True  # UserActivityMiddleware auto-included
```

### Features

- ✅ **Smart API Detection** - Identifies API requests vs web requests
- ✅ **5-minute Intervals** - Prevents database spam with intelligent caching
- ✅ **Performance Optimized** - In-memory caching and batch updates
- ✅ **Zero Configuration** - Works automatically with accounts app
- ✅ **Error Resilient** - Never breaks request processing

### API Request Detection

The middleware intelligently detects API requests using multiple criteria:

```python
# 1. JSON Content-Type or Accept headers
Content-Type: application/json
Accept: application/json

# 2. DRF format parameters
GET /api/users/?format=json
GET /api/data/?format=api

# 3. REST methods on non-admin paths
POST /api/users/
PUT /api/profile/
PATCH /api/settings/
DELETE /api/items/123/

# 4. Configured API prefixes
GET /api/v1/data/        # Django-CFG API Client Generation API
GET /cfg/accounts/       # Django CFG API (always active)
```

### Usage Statistics

```python
from django_cfg.middleware import UserActivityMiddleware

# Get middleware statistics
middleware = UserActivityMiddleware()
stats = middleware.get_activity_stats()

print(stats)
# Output:
# {
#     'tracked_users': 42,
#     'update_interval': 300,  # 5 minutes
#     'api_only': True,
#     'accounts_enabled': True,
#     'middleware_active': True,
#     'cache_size': 15,
#     'total_updates': 1247
# }
```

### Performance Monitoring

```python
# Monitor user activity in real-time
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

# User activity dashboard
def get_activity_dashboard():
    now = timezone.now()
    
    return {
        'online_now': User.objects.filter(
            last_login__gte=now - timedelta(minutes=5)
        ).count(),
        'active_today': User.objects.filter(
            last_login__gte=now - timedelta(days=1)
        ).count(),
        'active_this_week': User.objects.filter(
            last_login__gte=now - timedelta(days=7)
        ).count(),
        'total_users': User.objects.count()
    }
```

## Public Endpoints Middleware

### Bypass Authentication for Public APIs

The `PublicEndpointsMiddleware` allows specific endpoints to bypass authentication requirements.

```python
from django_cfg.middleware import PublicEndpointsMiddleware

class PublicAPIMiddleware(PublicEndpointsMiddleware):
    """Custom public endpoints configuration"""
    
    public_patterns = [
        r'^/api/public/',           # All public API endpoints
        r'^/api/auth/login/$',      # Login endpoint
        r'^/api/auth/register/$',   # Registration endpoint
        r'^/api/health/$',          # Health check
        r'^/cfg/newsletter/subscribe/$',  # Newsletter subscription
    ]
    
    def is_public_endpoint(self, request):
        """Override for custom logic"""
        path = request.path_info
        
        # Custom logic for public endpoints
        if path.startswith('/api/public/'):
            return True
            
        # Check if it's a health check
        if path.endswith('/health/') and request.method == 'GET':
            return True
            
        return super().is_public_endpoint(request)
```

### Configuration

```python
# settings.py - Manual configuration
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    
    # Django-CFG middleware
    'django_cfg.middleware.PublicEndpointsMiddleware',
    'django_cfg.middleware.UserActivityMiddleware',
    
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Public endpoints configuration
PUBLIC_ENDPOINTS = [
    '/api/public/',
    '/api/auth/login/',
    '/api/auth/register/',
    '/api/health/',
    '/cfg/newsletter/subscribe/',
]
```

## Advanced Middleware Configuration

### Custom User Activity Tracking

```python
from django_cfg.middleware.user_activity import UserActivityMiddleware

class CustomUserActivityMiddleware(UserActivityMiddleware):
    """Extended user activity tracking"""
    
    def __init__(self, get_response):
        super().__init__(get_response)
        self.update_interval = 180  # 3 minutes instead of 5
        self.track_anonymous = True  # Track anonymous users too
    
    def should_update_activity(self, request, user):
        """Custom logic for when to update activity"""
        # Always update for admin users
        if user.is_staff:
            return True
            
        # Skip updates for bot requests
        user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
        if any(bot in user_agent for bot in ['bot', 'crawler', 'spider']):
            return False
            
        return super().should_update_activity(request, user)
    
    def get_client_info(self, request):
        """Extract additional client information"""
        return {
            'ip_address': self.get_client_ip(request),
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            'referer': request.META.get('HTTP_REFERER', ''),
            'method': request.method,
            'path': request.path_info
        }
    
    def get_client_ip(self, request):
        """Get real client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
```

### Middleware Integration with Django-CFG Apps

```python
# Automatic integration with Django-CFG configuration
class MyConfig(DjangoConfig):
    enable_accounts: bool = True     # Enables UserActivityMiddleware
    enable_support: bool = True      # Enables support-specific middleware
    enable_newsletter: bool = True   # Enables newsletter public endpoints
    
    # Custom middleware settings
    user_activity_interval: int = 300  # 5 minutes
    track_anonymous_users: bool = False
    public_api_endpoints: list = [
        '/api/public/',
        '/api/health/',
        '/cfg/newsletter/subscribe/'
    ]
```

## Middleware Analytics

### Activity Analytics

```python
from django_cfg.middleware.analytics import MiddlewareAnalytics

class ActivityAnalytics:
    def __init__(self):
        self.analytics = MiddlewareAnalytics()
    
    def get_user_activity_report(self, days=7):
        """Generate user activity report"""
        from django.contrib.auth import get_user_model
        from django.utils import timezone
        from datetime import timedelta
        
        User = get_user_model()
        cutoff_date = timezone.now() - timedelta(days=days)
        
        # Activity metrics
        total_users = User.objects.count()
        active_users = User.objects.filter(
            last_login__gte=cutoff_date
        ).count()
        
        # Daily breakdown
        daily_activity = []
        for i in range(days):
            day_start = cutoff_date + timedelta(days=i)
            day_end = day_start + timedelta(days=1)
            
            daily_active = User.objects.filter(
                last_login__gte=day_start,
                last_login__lt=day_end
            ).count()
            
            daily_activity.append({
                'date': day_start.date(),
                'active_users': daily_active
            })
        
        return {
            'total_users': total_users,
            'active_users': active_users,
            'activity_rate': (active_users / total_users * 100) if total_users > 0 else 0,
            'daily_breakdown': daily_activity
        }
    
    def get_api_usage_stats(self):
        """Get API usage statistics from middleware"""
        return {
            'total_api_requests': self.analytics.get_api_request_count(),
            'authenticated_requests': self.analytics.get_auth_request_count(),
            'public_requests': self.analytics.get_public_request_count(),
            'top_endpoints': self.analytics.get_top_endpoints(),
            'user_agents': self.analytics.get_user_agents()
        }
```

### Real-time Monitoring

```python
# Management command for real-time monitoring
from django.core.management.base import BaseCommand
from django_cfg.middleware import UserActivityMiddleware

class Command(BaseCommand):
    help = 'Monitor user activity in real-time'
    
    def handle(self, *args, **options):
        middleware = UserActivityMiddleware()
        
        while True:
            stats = middleware.get_activity_stats()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f"Active users: {stats['tracked_users']} | "
                    f"Cache size: {stats['cache_size']} | "
                    f"Updates: {stats['total_updates']}"
                )
            )
            
            time.sleep(10)  # Update every 10 seconds
```

## Middleware Configuration

### Django Settings Integration

```python
# settings.py
MIDDLEWARE = [
    # Standard Django middleware
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # If using CORS
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    
    # Django-CFG middleware (auto-configured)
    'django_cfg.middleware.PublicEndpointsMiddleware',
    'django_cfg.middleware.UserActivityMiddleware',
    
    # Standard Django middleware (continued)
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Django-CFG middleware settings
DJANGO_CFG_MIDDLEWARE = {
    'USER_ACTIVITY': {
        'UPDATE_INTERVAL': 300,  # 5 minutes
        'TRACK_ANONYMOUS': False,
        'CACHE_SIZE_LIMIT': 1000,
    },
    'PUBLIC_ENDPOINTS': {
        'PATTERNS': [
            r'^/api/public/',
            r'^/api/health/$',
            r'^/cfg/newsletter/subscribe/$',
        ],
        'METHODS': ['GET', 'POST'],  # Allowed methods for public endpoints
    }
}
```

### Logging Configuration

```python
# settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'middleware.log',
        },
    },
    'loggers': {
        'django_cfg.middleware': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'django_cfg.middleware.user_activity': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
```

## 🧪 Testing Middleware

### Unit Tests

```python
from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django_cfg.middleware import UserActivityMiddleware

User = get_user_model()

class UserActivityMiddlewareTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = UserActivityMiddleware(lambda r: None)
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com'
        )
    
    def test_api_request_detection(self):
        """Test API request detection"""
        # JSON request
        request = self.factory.post(
            '/api/users/',
            content_type='application/json'
        )
        self.assertTrue(self.middleware.is_api_request(request))
        
        # DRF format parameter
        request = self.factory.get('/api/users/?format=json')
        self.assertTrue(self.middleware.is_api_request(request))
        
        # Regular web request
        request = self.factory.get('/admin/')
        self.assertFalse(self.middleware.is_api_request(request))
    
    def test_activity_update_interval(self):
        """Test update interval logic"""
        request = self.factory.post(
            '/api/test/',
            content_type='application/json'
        )
        request.user = self.user
        
        # First request should update
        self.assertTrue(
            self.middleware.should_update_activity(request, self.user)
        )
        
        # Immediate second request should not update
        self.middleware.last_updates[self.user.id] = timezone.now()
        self.assertFalse(
            self.middleware.should_update_activity(request, self.user)
        )
```

## Related Documentation

- [**User Management**](/features/built-in-apps/user-management/accounts) - Accounts app integration
- [**Configuration Guide**](/fundamentals/configuration) - Middleware configuration
- [**Security Guide**](/deployment/security) - Security considerations
- [**Performance Guide**](/deployment/monitoring) - Performance monitoring

The Middleware system provides seamless request processing enhancements for your Django applications! 🛡️

TAGS: middleware, user-activity, public-endpoints, performance, authentication
DEPENDS_ON: [accounts, configuration, security]
USED_BY: [all-apps, authentication, monitoring]
