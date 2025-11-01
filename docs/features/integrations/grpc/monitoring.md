---
title: Monitoring & Logging
description: Monitor gRPC requests with database logging, Django admin, and REST API
sidebar_label: Monitoring
sidebar_position: 7
keywords:
  - grpc monitoring
  - grpc logging
  - grpc metrics
  - grpc admin
---

# gRPC Monitoring & Logging

Django-CFG provides comprehensive monitoring and logging for gRPC requests through database logging, beautiful Django admin interface, and REST API endpoints.

## 🎯 Overview

All gRPC requests are automatically logged to the database with:

- ✅ **Request Metadata** - Service, method, request ID, timestamp
- ✅ **Performance Metrics** - Duration, request/response sizes
- ✅ **Status Tracking** - Success, error, cancelled, timeout
- ✅ **User Context** - Authenticated user, client IP, user agent
- ✅ **Error Details** - gRPC status codes, error messages
- ✅ **Django Admin UI** - Beautiful interface with filtering
- ✅ **REST API** - Monitoring endpoints for integrations

## 📊 Request Logging Model

### GRPCRequestLog Model

Every gRPC request creates a log entry with these fields:

```python
class GRPCRequestLog(models.Model):
    # Request identification
    request_id = models.CharField(max_length=100, unique=True)  # UUID
    service_name = models.CharField(max_length=200)             # e.g., "UserService"
    method_name = models.CharField(max_length=200)              # e.g., "GetUser"
    full_method = models.CharField(max_length=400)              # e.g., "/api.users.UserService/GetUser"

    # Status tracking
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.PENDING,
    )
    grpc_status_code = models.CharField(max_length=50, null=True)  # e.g., "OK", "NOT_FOUND"

    # Performance metrics
    duration_ms = models.IntegerField(null=True)                # Request duration in milliseconds
    request_size = models.IntegerField(null=True)               # Request size in bytes
    response_size = models.IntegerField(null=True)              # Response size in bytes

    # User context
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
    )
    client_ip = models.GenericIPAddressField(null=True)
    user_agent = models.CharField(max_length=500, null=True)
    peer = models.CharField(max_length=200, null=True)          # gRPC peer info

    # Error tracking
    error_message = models.TextField(null=True)
    error_details = models.JSONField(null=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

### Status Choices

| Status | Description |
|--------|-------------|
| `pending` | Request received, processing started |
| `success` | Request completed successfully |
| `error` | Request failed with error |
| `cancelled` | Request was cancelled by client |
| `timeout` | Request exceeded deadline |

## 🎨 Django Admin Interface

### Overview

Access the admin interface at `/admin/grpc/grpcrequestlog/`:

**Features:**
- 🎨 **Color-coded badges** - Visual status indicators
- 🔍 **Advanced filtering** - By service, method, status, user, date
- 📊 **Statistics** - Success rate, average duration
- 📥 **Export** - Download logs as CSV
- 🔎 **Search** - Full-text search across fields

### Admin Configuration

The admin interface is automatically configured with:

```python
@admin.register(GRPCRequestLog)
class GRPCRequestLogAdmin(PydanticAdmin):
    list_display = [
        "request_id_display",
        "service_name",
        "method_name",
        "status_display",
        "duration_display",
        "user_display",
        "created_at",
    ]

    list_filter = [
        "status",
        "service_name",
        "method_name",
        ("created_at", DateRangeFilter),
        "user",
    ]

    search_fields = [
        "request_id",
        "service_name",
        "method_name",
        "user__username",
        "client_ip",
    ]
```

### Color-Coded Badges

**Status badges:**
- 🟢 **Success** - Green badge
- 🔴 **Error** - Red badge
- ⏳ **Pending** - Gray badge
- 🚫 **Cancelled** - Orange badge
- ⏱️ **Timeout** - Yellow badge

**Duration badges:**
- 🟢 **< 100ms** - Green (Fast)
- 🟡 **100-1000ms** - Yellow (Moderate)
- 🔴 **> 1000ms** - Red (Slow)

**Size badges:**
- Request/Response sizes displayed in KB/MB

### Filtering

Filter logs by:

- **Service** - Filter by service name
- **Method** - Filter by method name
- **Status** - Success/Error/Pending/Cancelled/Timeout
- **User** - Filter by authenticated user
- **Date Range** - Custom date range picker
- **Client IP** - Filter by IP address

## 📈 Statistics & Metrics

### Request Statistics

Get aggregated statistics via the manager:

```python
from django_cfg.apps.grpc.models import GRPCRequestLog

# Get statistics for last 24 hours
stats = GRPCRequestLog.objects.get_statistics(hours=24)

# Returns:
{
    "total": 1543,              # Total requests
    "successful": 1489,         # Successful requests
    "errors": 54,               # Failed requests
    "success_rate": 96.5,       # Success rate percentage
    "avg_duration_ms": 125.3,   # Average duration
    "p95_duration_ms": 450.2,   # 95th percentile
}
```

### Filter Methods

Use built-in filter methods:

```python
# Recent requests (last 24 hours by default)
recent_logs = GRPCRequestLog.objects.recent(hours=24)

# Successful requests only
successful = GRPCRequestLog.objects.successful()

# Error requests only
errors = GRPCRequestLog.objects.error()

# By service
user_service_logs = GRPCRequestLog.objects.by_service("UserService")

# By method
get_user_logs = GRPCRequestLog.objects.by_method("GetUser")

# By user
user_logs = GRPCRequestLog.objects.by_user(request.user)

# Combine filters
recent_errors = GRPCRequestLog.objects.recent(hours=1).error()
```

## 🔌 REST API Monitoring

### API Endpoints

Access monitoring data via REST API at `/cfg/grpc/monitor/`:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/cfg/grpc/monitor/overview/` | GET | Overall statistics and health |
| `/cfg/grpc/monitor/requests/` | GET | Recent request logs (paginated) |
| `/cfg/grpc/monitor/services/` | GET | Per-service statistics |
| `/cfg/grpc/monitor/methods/` | GET | Per-method statistics |
| `/cfg/grpc/monitor/timeline/` | GET | Timeline data (hourly breakdown) |
| `/cfg/grpc/monitor/health/` | GET | Health check status |

### 1. Overview Endpoint

**GET** `/cfg/grpc/monitor/overview/`

Returns overall statistics:

```json
{
  "total_requests": 1543,
  "successful_requests": 1489,
  "error_requests": 54,
  "success_rate": 96.5,
  "avg_duration_ms": 125.3,
  "p95_duration_ms": 450.2,
  "top_services": [
    {
      "service_name": "UserService",
      "total_requests": 845,
      "success_rate": 98.2
    },
    {
      "service_name": "ProductService",
      "total_requests": 523,
      "success_rate": 95.4
    }
  ],
  "top_methods": [
    {
      "method_name": "GetUser",
      "total_requests": 456,
      "avg_duration_ms": 45.2
    }
  ],
  "recent_errors": [
    {
      "request_id": "a3b4c5d6-e7f8-9012-3456-789abcdef012",
      "service_name": "UserService",
      "method_name": "GetUser",
      "error_message": "User not found",
      "created_at": "2025-11-01T14:30:00Z"
    }
  ]
}
```

### 2. Requests Endpoint

**GET** `/cfg/grpc/monitor/requests/`

Query parameters:
- `?hours=24` - Recent hours (default: 24)
- `?status=success` - Filter by status
- `?service=UserService` - Filter by service
- `?method=GetUser` - Filter by method
- `?page=1&page_size=20` - Pagination

Returns paginated request logs:

```json
{
  "count": 1543,
  "next": "/cfg/grpc/monitor/requests/?page=2",
  "previous": null,
  "results": [
    {
      "request_id": "a3b4c5d6-e7f8-9012-3456-789abcdef012",
      "service_name": "UserService",
      "method_name": "GetUser",
      "full_method": "/api.users.UserService/GetUser",
      "status": "success",
      "grpc_status_code": "OK",
      "duration_ms": 125,
      "request_size": 1024,
      "response_size": 2048,
      "user": {
        "id": 1,
        "username": "admin"
      },
      "client_ip": "192.168.1.100",
      "created_at": "2025-11-01T14:30:00Z"
    }
  ]
}
```

### 3. Services Endpoint

**GET** `/cfg/grpc/monitor/services/`

Query parameters:
- `?hours=24` - Recent hours

Returns per-service statistics:

```json
{
  "services": [
    {
      "service_name": "UserService",
      "total_requests": 845,
      "successful_requests": 830,
      "error_requests": 15,
      "success_rate": 98.2,
      "avg_duration_ms": 87.3,
      "p95_duration_ms": 250.0,
      "methods": [
        {
          "method_name": "GetUser",
          "total_requests": 456,
          "avg_duration_ms": 45.2
        },
        {
          "method_name": "UpdateProfile",
          "total_requests": 389,
          "avg_duration_ms": 125.8
        }
      ]
    }
  ]
}
```

### 4. Timeline Endpoint

**GET** `/cfg/grpc/monitor/timeline/`

Query parameters:
- `?hours=24` - Recent hours

Returns hourly breakdown:

```json
{
  "timeline": [
    {
      "hour": "2025-11-01T14:00:00Z",
      "total_requests": 125,
      "successful_requests": 120,
      "error_requests": 5,
      "avg_duration_ms": 95.3
    },
    {
      "hour": "2025-11-01T15:00:00Z",
      "total_requests": 143,
      "successful_requests": 138,
      "error_requests": 5,
      "avg_duration_ms": 102.1
    }
  ]
}
```

### 5. Health Endpoint

**GET** `/cfg/grpc/monitor/health/`

Returns health status:

```json
{
  "status": "healthy",
  "grpc_server": {
    "running": true,
    "host": "[::]",
    "port": 50051
  },
  "last_request": "2025-11-01T15:30:00Z",
  "requests_last_hour": 125,
  "error_rate_last_hour": 3.2
}
```

## 📊 Using the REST API

### Python Example

```python
import requests

# Get overview
response = requests.get("http://localhost:8000/cfg/grpc/monitor/overview/")
data = response.json()

print(f"Total requests: {data['total_requests']}")
print(f"Success rate: {data['success_rate']}%")
print(f"Avg duration: {data['avg_duration_ms']}ms")

# Get recent errors
response = requests.get(
    "http://localhost:8000/cfg/grpc/monitor/requests/",
    params={"status": "error", "hours": 1}
)
errors = response.json()

for error in errors['results']:
    print(f"Error in {error['method_name']}: {error['error_message']}")
```

### JavaScript Example

```javascript
// Get services statistics
fetch('/cfg/grpc/monitor/services/?hours=24')
  .then(res => res.json())
  .then(data => {
    data.services.forEach(service => {
      console.log(`${service.service_name}: ${service.success_rate}% success`);
    });
  });

// Get timeline data
fetch('/cfg/grpc/monitor/timeline/?hours=24')
  .then(res => res.json())
  .then(data => {
    // Render chart with timeline data
    renderChart(data.timeline);
  });
```

### cURL Example

```bash
# Get overview
curl http://localhost:8000/cfg/grpc/monitor/overview/

# Get recent errors
curl "http://localhost:8000/cfg/grpc/monitor/requests/?status=error&hours=1"

# Get service statistics
curl http://localhost:8000/cfg/grpc/monitor/services/

# With authentication (if required)
curl -H "Authorization: Bearer <token>" \
  http://localhost:8000/cfg/grpc/monitor/overview/
```

## 🔍 Console Logging

In development mode, requests are also logged to console:

```
[gRPC] ➡️  UserService.GetUser | peer=ipv4:127.0.0.1:54321
[gRPC] ✅ UserService.GetUser | status=OK | time=125.50ms | peer=ipv4:127.0.0.1:54321

[gRPC] ➡️  ProductService.GetProduct | peer=ipv4:127.0.0.1:54322
[gRPC] ❌ ProductService.GetProduct | status=NOT_FOUND | time=50.00ms | error=Product not found | peer=ipv4:127.0.0.1:54322
```

**Log format:**
- ➡️ - Request received
- ✅ - Success response
- ❌ - Error response
- 🚫 - Cancelled
- ⏱️ - Timeout

## 🎯 Performance Monitoring

### Key Metrics to Track

1. **Request Rate** - Requests per second/minute/hour
2. **Success Rate** - Percentage of successful requests
3. **Error Rate** - Percentage of failed requests
4. **Average Duration** - Mean request duration
5. **P95 Duration** - 95th percentile latency
6. **Service Distribution** - Requests per service
7. **Method Distribution** - Requests per method

### Django ORM Queries

```python
from django.db.models import Count, Avg, Max, Min
from django.utils import timezone
from datetime import timedelta

# Requests in last hour
last_hour = timezone.now() - timedelta(hours=1)
recent_count = GRPCRequestLog.objects.filter(
    created_at__gte=last_hour
).count()

# Average duration by service
avg_by_service = GRPCRequestLog.objects.filter(
    created_at__gte=last_hour,
    status='success'
).values('service_name').annotate(
    avg_duration=Avg('duration_ms'),
    total_requests=Count('id')
).order_by('-total_requests')

# Error rate by method
error_rate = GRPCRequestLog.objects.filter(
    created_at__gte=last_hour
).values('method_name').annotate(
    total=Count('id'),
    errors=Count('id', filter=Q(status='error'))
).annotate(
    error_rate=(F('errors') * 100.0 / F('total'))
)
```

## 🔔 Alerts & Notifications

### Django Signals

Monitor requests in real-time with Django signals:

```python
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_cfg.apps.grpc.models import GRPCRequestLog

@receiver(post_save, sender=GRPCRequestLog)
def alert_on_error(sender, instance, created, **kwargs):
    """Send alert when error occurs."""
    if instance.status == 'error':
        # Send notification
        send_slack_alert(
            f"gRPC Error: {instance.service_name}.{instance.method_name}\n"
            f"Error: {instance.error_message}\n"
            f"User: {instance.user}\n"
            f"Time: {instance.created_at}"
        )
```

### Custom Monitoring

```python
# Monitor slow requests
slow_threshold_ms = 1000

slow_requests = GRPCRequestLog.objects.filter(
    duration_ms__gt=slow_threshold_ms,
    created_at__gte=timezone.now() - timedelta(hours=1)
)

if slow_requests.count() > 10:
    send_alert("Too many slow gRPC requests!")
```

## 📚 Related Documentation

- **[Architecture](./architecture.md)** - Logging architecture details
- **[Setup Guide](./setup.md)** - Configuration options
- **[Backend Guide](./backend-guide.md)** - Service development
- **[Troubleshooting](./troubleshooting.md)** - Debug logging issues

---

**Next:** Learn about [client usage](./client-usage.md) or explore [examples](./examples.md).
