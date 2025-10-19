---
title: Health Monitoring Overview
description: Django-CFG overview feature guide. Production-ready health monitoring overview with built-in validation, type safety, and seamless Django integration.
sidebar_label: Overview & Philosophy
sidebar_position: 1
keywords:
  - django-cfg overview
  - django overview
  - overview django-cfg
---

# Health Check Module

Django-CFG includes a **comprehensive health check system** that provides real-time monitoring of your application's critical components including databases, cache, system resources, and configuration status.

## Overview

The Django Health module provides:
- **Database Connectivity** - Multi-database connection monitoring
- **Cache Availability** - Redis, Memcached, and database cache checks
- **System Resources** - CPU, memory, disk usage monitoring
- **Configuration Validation** - Settings and environment validation
- **Custom Health Checks** - Extensible health check framework
- **API Endpoints** - RESTful health check endpoints

## Quick Start

### Direct Import (Recommended)

> **Note**: Health checks are view classes, not auto-configured services. Import directly from `django_cfg.modules.django_health`.

```python
# urls.py
from django.urls import path
from django_cfg.modules.django_health import HealthCheckView

urlpatterns = [
    path('health/', HealthCheckView.as_view(), name='health_check'),
]
```

### Basic Health Check

```python
from django_cfg.modules.django_health import HealthCheckView, get_health_status
from django.urls import path

# Configure URLs manually
urlpatterns = [
    path('health/', HealthCheckView.as_view(), name='health_check'),
]

# Or use programmatically
from django_cfg.modules.django_health import get_health_status

health_data = get_health_status()
print(health_data)
# {
#     "status": "healthy",
#     "timestamp": "2023-12-01T10:30:00Z",
#     "checks": {
#         "database": {"status": "ok", "response_time": 0.023},
#         "cache": {"status": "ok", "response_time": 0.001},
#         "system": {"cpu": 45.2, "memory": 62.8, "disk": 78.1}
#     }
# }
```

## Health Check Components

### Database Health Checks

```python
from django_cfg.modules.django_health import DatabaseHealthChecker

# Check all configured databases
db_checker = DatabaseHealthChecker()
db_status = db_checker.check_all_databases()

print(db_status)
# {
#     "default": {
#         "status": "ok",
#         "engine": "postgresql",
#         "response_time": 0.023,
#         "connection_count": 5,
#         "max_connections": 100
#     },
#     "analytics": {
#         "status": "ok", 
#         "engine": "mysql",
#         "response_time": 0.045,
#         "connection_count": 2,
#         "max_connections": 50
#     }
# }

# Check specific database
default_db_status = db_checker.check_database('default')
print(default_db_status)
# {
#     "status": "ok",
#     "response_time": 0.023,
#     "queries_executed": 1,
#     "connection_info": {
#         "host": "localhost",
#         "port": 5432,
#         "database": "myapp_db"
#     }
# }
```

### Cache Health Checks

```python
from django_cfg.modules.django_health import CacheHealthChecker

# Check all cache backends
cache_checker = CacheHealthChecker()
cache_status = cache_checker.check_all_caches()

print(cache_status)
# {
#     "default": {
#         "status": "ok",
#         "backend": "redis",
#         "response_time": 0.001,
#         "memory_usage": "45.2MB",
#         "hit_rate": 94.5
#     },
#     "sessions": {
#         "status": "ok",
#         "backend": "database",
#         "response_time": 0.012
#     }
# }

# Test cache operations
cache_test = cache_checker.test_cache_operations('default')
print(cache_test)
# {
#     "set_operation": {"status": "ok", "time": 0.001},
#     "get_operation": {"status": "ok", "time": 0.0005},
#     "delete_operation": {"status": "ok", "time": 0.0008},
#     "overall_status": "ok"
# }
```

### System Resource Monitoring

```python
from django_cfg.modules.django_health import SystemHealthChecker

# Get system metrics
system_checker = SystemHealthChecker()
system_status = system_checker.get_system_metrics()

print(system_status)
# {
#     "cpu": {
#         "usage_percent": 45.2,
#         "load_average": [1.23, 1.45, 1.67],
#         "core_count": 8
#     },
#     "memory": {
#         "usage_percent": 62.8,
#         "total_gb": 16.0,
#         "available_gb": 5.95,
#         "used_gb": 10.05
#     },
#     "disk": {
#         "usage_percent": 78.1,
#         "total_gb": 500.0,
#         "free_gb": 109.5,
#         "used_gb": 390.5
#     },
#     "network": {
#         "bytes_sent": 1024000,
#         "bytes_recv": 2048000,
#         "packets_sent": 1500,
#         "packets_recv": 2000
#     }
# }

# Check system thresholds
thresholds = system_checker.check_thresholds()
print(thresholds)
# {
#     "cpu_ok": True,      # < 80%
#     "memory_ok": True,   # < 85%
#     "disk_ok": False,    # > 75% (warning)
#     "overall_status": "warning"
# }
```

## Advanced Health Checks

### Custom Health Checks

```python
from django_cfg.modules.django_health import BaseHealthCheck

class CustomServiceHealthCheck(BaseHealthCheck):
    """Custom health check for external service"""
    
    name = "external_api"
    description = "External API service connectivity"
    
    def check(self) -> dict:
        """Perform health check"""
        try:
            import requests
            response = requests.get(
                'https://api.external-service.com/health',
                timeout=5
            )
            
            if response.status_code == 200:
                return {
                    "status": "ok",
                    "response_time": response.elapsed.total_seconds(),
                    "api_version": response.json().get('version', 'unknown')
                }
            else:
                return {
                    "status": "error",
                    "error": f"HTTP {response.status_code}",
                    "response_time": response.elapsed.total_seconds()
                }
                
        except requests.RequestException as e:
            return {
                "status": "error",
                "error": str(e),
                "response_time": None
            }

# Register custom health check
from django_cfg.modules.django_health import register_health_check

register_health_check(CustomServiceHealthCheck())
```

### Application-Specific Health Checks

```python
class DatabaseMigrationHealthCheck(BaseHealthCheck):
    """Check if database migrations are up to date"""
    
    name = "migrations"
    description = "Database migration status"
    
    def check(self) -> dict:
        """Check migration status"""
        from django.core.management import execute_from_command_line
        from django.db.migrations.executor import MigrationExecutor
        from django.db import connections
        
        try:
            connection = connections['default']
            executor = MigrationExecutor(connection)
            plan = executor.migration_plan(executor.loader.graph.leaf_nodes())
            
            if plan:
                return {
                    "status": "warning",
                    "pending_migrations": len(plan),
                    "migrations": [f"{migration[0]}.{migration[1]}" for migration in plan]
                }
            else:
                return {
                    "status": "ok",
                    "pending_migrations": 0,
                    "message": "All migrations applied"
                }
                
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }

class CeleryHealthCheck(BaseHealthCheck):
    """Check Celery worker status"""
    
    name = "celery"
    description = "Celery worker connectivity"
    
    def check(self) -> dict:
        """Check Celery workers"""
        try:
            from celery import current_app
            
            # Get active workers
            inspect = current_app.control.inspect()
            active_workers = inspect.active()
            
            if active_workers:
                worker_count = len(active_workers)
                return {
                    "status": "ok",
                    "active_workers": worker_count,
                    "workers": list(active_workers.keys())
                }
            else:
                return {
                    "status": "error",
                    "error": "No active Celery workers found",
                    "active_workers": 0
                }
                
        except ImportError:
            return {
                "status": "skipped",
                "message": "Celery not installed"
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
```

## Health Check Endpoints

### RESTful API

```python
# GET /health/ - Basic health check
{
    "status": "healthy",
    "timestamp": "2023-12-01T10:30:00Z",
    "response_time": 0.045
}

# GET /health/detailed/ - Detailed health information
{
    "status": "healthy",
    "timestamp": "2023-12-01T10:30:00Z",
    "checks": {
        "database": {
            "status": "ok",
            "response_time": 0.023,
            "connections": 5
        },
        "cache": {
            "status": "ok", 
            "response_time": 0.001,
            "hit_rate": 94.5
        },
        "system": {
            "status": "ok",
            "cpu_usage": 45.2,
            "memory_usage": 62.8,
            "disk_usage": 78.1
        },
        "external_api": {
            "status": "ok",
            "response_time": 0.234,
            "api_version": "v2.1"
        }
    },
    "overall_response_time": 0.045
}

# GET /health/system/ - System metrics only
{
    "status": "ok",
    "timestamp": "2023-12-01T10:30:00Z",
    "system": {
        "cpu": {"usage": 45.2, "cores": 8},
        "memory": {"usage": 62.8, "total_gb": 16.0},
        "disk": {"usage": 78.1, "total_gb": 500.0},
        "uptime": "5 days, 14:32:15"
    }
}
```

### Custom Endpoints

```python
from django_cfg.modules.django_health import HealthCheckView
from django.http import JsonResponse

class CustomHealthView(HealthCheckView):
    """Custom health check with additional metrics"""
    
    def get_custom_checks(self):
        """Add custom health checks"""
        return {
            'application': self.check_application_health(),
            'integrations': self.check_integrations(),
            'performance': self.check_performance_metrics()
        }
    
    def check_application_health(self):
        """Check application-specific health"""
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        
        return {
            'status': 'ok',
            'total_users': User.objects.count(),
            'active_sessions': self.get_active_sessions_count(),
            'recent_errors': self.get_recent_error_count()
        }
    
    def check_integrations(self):
        """Check external integrations"""
        integrations = {}
        
        # Check payment gateway
        integrations['payment'] = self.check_payment_gateway()
        
        # Check email service
        integrations['email'] = self.check_email_service()
        
        # Check file storage
        integrations['storage'] = self.check_file_storage()
        
        return integrations
    
    def check_performance_metrics(self):
        """Check performance metrics"""
        return {
            'avg_response_time': self.get_avg_response_time(),
            'error_rate': self.get_error_rate(),
            'throughput': self.get_throughput()
        }
```

## Configuration Options

### Health Check Configuration

Health checks are configured via view arguments or environment variables:

```python
# urls.py - Configure via view arguments
from django_cfg.modules.django_health import HealthCheckView

urlpatterns = [
    path('health/', HealthCheckView.as_view(
        auth_required=False,
        include_detailed=True,
    ), name='health_check'),
]

# Or configure via environment
# ENV variables:
# HEALTH_CPU_THRESHOLD=80.0
# HEALTH_MEMORY_THRESHOLD=85.0
# HEALTH_DISK_THRESHOLD=90.0
# HEALTH_DB_TIMEOUT=5.0
# HEALTH_CACHE_TIMEOUT=2.0

    # Custom checks
    health_custom_checks: list = [
        'myapp.health.CustomServiceHealthCheck',
        'myapp.health.DatabaseMigrationHealthCheck'
    ]
```

### Django Settings Integration

```python
# settings.py
HEALTH_CHECK = {
    'ENABLED': True,
    'PATH': '/health/',
    'DETAILED_PATH': '/health/detailed/',
    'SYSTEM_PATH': '/health/system/',
    
    # Authentication
    'REQUIRE_AUTH': False,
    'ALLOWED_IPS': ['127.0.0.1', '::1'],
    'REQUIRE_STAFF': False,
    
    # Checks configuration
    'CHECKS': {
        'database': True,
        'cache': True,
        'system': True,
        'migrations': True,
        'custom': True
    },
    
    # Thresholds
    'THRESHOLDS': {
        'cpu_warning': 70.0,
        'cpu_critical': 90.0,
        'memory_warning': 80.0,
        'memory_critical': 95.0,
        'disk_warning': 85.0,
        'disk_critical': 95.0
    },
    
    # Timeouts (seconds)
    'TIMEOUTS': {
        'database': 5.0,
        'cache': 2.0,
        'external': 10.0
    }
}
```

## Monitoring Integration

### Prometheus Metrics

```python
from django_cfg.modules.django_health import HealthMetricsCollector

# Export health metrics for Prometheus
collector = HealthMetricsCollector()

# Register metrics
from prometheus_client import CollectorRegistry, generate_latest

registry = CollectorRegistry()
registry.register(collector)

# Generate metrics
metrics_data = generate_latest(registry)
print(metrics_data.decode())
# # HELP django_health_check_status Health check status (1=ok, 0=error)
# # TYPE django_health_check_status gauge
# django_health_check_status{check="database"} 1.0
# django_health_check_status{check="cache"} 1.0
# django_health_check_status{check="system"} 1.0
```

### Alerting Integration

```python
from django_cfg.modules.django_health import HealthAlerting

class HealthAlerting:
    def __init__(self):
        self.alert_channels = []
    
    def add_alert_channel(self, channel):
        """Add alert channel (email, webhook, telegram)"""
        self.alert_channels.append(channel)
    
    def check_and_alert(self):
        """Check health and send alerts if needed"""
        health_data = get_health_status()
        
        if health_data['status'] != 'healthy':
            self.send_alerts(health_data)
    
    def send_alerts(self, health_data):
        """Send alerts through configured channels"""
        for channel in self.alert_channels:
            channel.send_alert(health_data)

# Usage
alerting = HealthAlerting()
alerting.add_alert_channel(EmailAlertChannel('admin@company.com'))
alerting.add_alert_channel(WebhookAlertChannel('https://hooks.zapier.com/hooks/catch/alerts'))
alerting.check_and_alert()
```

## 🧪 Testing Health Checks

### Unit Tests

```python
from django.test import TestCase, Client
from django_cfg.modules.django_health import get_health_status

class HealthCheckTest(TestCase):
    def setUp(self):
        self.client = Client()
    
    def test_basic_health_check(self):
        """Test basic health check endpoint"""
        response = self.client.get('/health/')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('status', data)
        self.assertIn('timestamp', data)
    
    def test_detailed_health_check(self):
        """Test detailed health check"""
        response = self.client.get('/health/detailed/')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('checks', data)
        self.assertIn('database', data['checks'])
        self.assertIn('cache', data['checks'])
    
    def test_health_status_function(self):
        """Test health status function"""
        health_data = get_health_status()
        
        self.assertIn('status', health_data)
        self.assertIn('checks', health_data)
        self.assertTrue(health_data['status'] in ['healthy', 'unhealthy', 'warning'])
```

## Related Documentation

- [**System Monitoring**](/deployment/monitoring) - Production monitoring
- [**Configuration Guide**](/fundamentals/configuration) - Health check configuration
- [**API Documentation**](/api/intro) - Health check API reference
- [**Deployment Guide**](/guides/docker/overview) - Docker health checks

The Health Check module provides comprehensive system monitoring for your Django applications! 🏥

TAGS: health-check, monitoring, system-metrics, database-check, cache-check, alerting
DEPENDS_ON: [configuration, monitoring, database, cache]
USED_BY: [deployment, monitoring, alerting, devops]
