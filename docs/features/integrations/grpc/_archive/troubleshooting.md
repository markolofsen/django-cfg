---
title: Troubleshooting
description: Common gRPC issues and solutions
sidebar_label: Troubleshooting
sidebar_position: 9
keywords:
  - grpc troubleshooting
  - grpc errors
  - grpc debugging
  - grpc issues
---

# gRPC Troubleshooting Guide

Common issues and solutions for Django-CFG gRPC integration.

## 🔍 Common Issues

### 1. "Module 'grpc' has no attribute..."

**Problem:**
```
AttributeError: module 'grpc' has no attribute 'server'
```

**Cause:** Missing or incorrectly installed gRPC dependencies.

**Solution:**
```bash
# Uninstall all grpc packages
pip uninstall grpcio grpcio-tools grpcio-reflection grpcio-health-checking -y

# Reinstall fresh
pip install grpcio grpcio-tools grpcio-reflection grpcio-health-checking protobuf

# Or use django-cfg extras
pip install django-cfg[grpc]
```

**Verify:**
```python
python -c "import grpc; print(grpc.__version__)"
# Should print: 1.60.0 (or similar)
```

---

### 2. Server Not Starting

**Problem:**
```bash
python manage.py rungrpc
# Nothing happens or immediate exit
```

**Debug steps:**

**Step 1:** Check if port is already in use
```bash
# On macOS/Linux
lsof -i :50051

# On Windows
netstat -ano | findstr :50051
```

**Step 2:** Try different port
```bash
python manage.py rungrpc --port 50052
```

**Step 3:** Check for errors
```bash
python manage.py rungrpc --verbosity 3
```

**Step 4:** Verify migrations
```bash
python manage.py migrate
```

---

### 3. Service Not Found

**Problem:**
```bash
grpcurl -plaintext localhost:50051 list
# Returns empty or service not found
```

**Causes & Solutions:**

**Cause 1:** Service not auto-discovered

Check if your service file is in the right location:
```
apps/users/
├── grpc_services.py     # ✅ Will be discovered
├── services/grpc.py     # ✅ Will be discovered
├── api/grpc.py          # ✅ Will be discovered
├── grpc/services.py     # ❌ Won't be discovered
```

**Cause 2:** App not in `enabled_apps`

```python
# api/config.py
grpc: GRPCConfig = GRPCConfig(
    auto_register_apps=True,
    enabled_apps=[
        "apps.users",  # ✅ Include your app
    ],
)
```

**Cause 3:** Reflection disabled

```python
# api/config.py
grpc: GRPCConfig = GRPCConfig(
    server=GRPCServerConfig(
        enable_reflection=True,  # ✅ Enable for grpcurl
    ),
)
```

**Verify discovery:**
```bash
python manage.py rungrpc
# Should show: "✅ Registered 3 services"
```

---

### 4. Authentication Errors

**Problem:**
```
grpc._channel._InactiveRpcError: <_InactiveRpcError of RPC that terminated with:
    status = StatusCode.UNAUTHENTICATED
    details = "Authentication required"
>
```

**Solutions:**

**Solution 1:** Include JWT token
```bash
grpcurl -plaintext \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..." \
  localhost:50051 api.users.UserService/GetProfile
```

**Solution 2:** Add method to public list
```python
# api/config.py
grpc: GRPCConfig = GRPCConfig(
    auth=GRPCAuthConfig(
        enabled=True,
        require_auth=False,  # Don't require for all methods
        public_methods=[
            "/api.users.UserService/GetUser",  # Public method
        ],
    ),
)
```

**Solution 3:** Disable auth in development
```python
# api/config.py
grpc: GRPCConfig = GRPCConfig(
    auth=GRPCAuthConfig(
        enabled=False,  # Disable auth for testing
    ),
)
```

---

### 5. Import Errors

**Problem:**
```python
ImportError: cannot import name 'BaseService' from 'django_cfg.apps.grpc.services'
```

**Solution:** Use correct import path
```python
# ❌ Wrong
from django_cfg.apps.grpc.services import BaseService

# ✅ Correct
from django_cfg.apps.integrations.grpc.services import BaseService
```

---

### 6. Database Connection Issues

**Problem:**
```
django.db.utils.OperationalError: database is locked
```

**Cause:** SQLite doesn't support concurrent writes well.

**Solutions:**

**Solution 1:** Use PostgreSQL in production
```python
# settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'mydb',
        # ...
    }
}
```

**Solution 2:** Disable request logging (temporary)
```python
# Remove RequestLoggerInterceptor for testing
# This is not recommended for production
```

**Solution 3:** Increase SQLite timeout
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'OPTIONS': {
            'timeout': 20,  # Increase timeout
        },
    }
}
```

---

### 7. Proto Import Errors

**Problem:**
```
ModuleNotFoundError: No module named 'user_pb2'
```

**Solutions:**

**Solution 1:** Generate proto files
```bash
# If using auto-generation
python manage.py generateproto

# Or manually with protoc
python -m grpc_tools.protoc \
  -I. \
  --python_out=. \
  --grpc_python_out=. \
  user.proto
```

**Solution 2:** Add to Python path
```python
# apps/users/grpc_services.py
import sys
from pathlib import Path

# Add proto directory to path
proto_dir = Path(__file__).parent / "protos"
sys.path.insert(0, str(proto_dir))

from user_pb2 import User
from user_pb2_grpc import UserServiceServicer
```

---

### 8. Reflection Not Working

**Problem:**
```bash
grpcurl -plaintext localhost:50051 list
# Error: server does not support the reflection API
```

**Solutions:**

**Solution 1:** Enable reflection
```python
# api/config.py
grpc: GRPCConfig = GRPCConfig(
    server=GRPCServerConfig(
        enable_reflection=True,  # ✅ Enable
    ),
)
```

**Solution 2:** Check if reflection service is registered
```bash
python manage.py rungrpc
# Should show: "🔍 Reflection enabled"
```

**Solution 3:** Verify reflection package installed
```bash
pip install grpcio-reflection
```

---

### 9. Slow Performance

**Problem:** Requests taking too long (> 1 second).

**Debug steps:**

**Step 1:** Check database queries
```python
# Enable Django query logging
LOGGING = {
    'loggers': {
        'django.db.backends': {
            'level': 'DEBUG',
        },
    },
}
```

**Step 2:** Use select_related / prefetch_related
```python
# ❌ Bad: N+1 queries
user = User.objects.get(id=1)
profile = user.profile  # Extra query!

# ✅ Good: Single query
user = User.objects.select_related('profile').get(id=1)
```

**Step 3:** Increase thread pool size
```python
# api/config.py
grpc: GRPCConfig = GRPCConfig(
    server=GRPCServerConfig(
        max_workers=20,  # Increase from 10
    ),
)
```

**Step 4:** Disable request logging (if needed)
```python
# Disable database logging for performance testing
# Not recommended for production
```

---

### 10. Memory Leaks

**Problem:** Memory usage increasing over time.

**Solutions:**

**Solution 1:** Close database connections properly
```python
# Django handles this automatically, but verify:
CONN_MAX_AGE = 600  # Close connections after 10 minutes
```

**Solution 2:** Limit queryset size
```python
# ❌ Bad: Load all users
users = User.objects.all()

# ✅ Good: Limit results
users = User.objects.all()[:100]
```

**Solution 3:** Use streaming for large responses
```python
def ListUsers(self, request, context):
    # Stream users instead of loading all at once
    for user in User.objects.iterator(chunk_size=100):
        yield user_pb2.User(...)
```

---

## 🔧 Debugging Tools

### 1. Enable Debug Logging

```python
# settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django_cfg.apps.integrations.grpc': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
        'grpc': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

### 2. grpcurl Commands

```bash
# List all services
grpcurl -plaintext localhost:50051 list

# Describe service
grpcurl -plaintext localhost:50051 describe api.users.UserService

# Call method with data
grpcurl -plaintext \
  -d '{"user_id": 1}' \
  localhost:50051 api.users.UserService/GetUser

# With authentication
grpcurl -plaintext \
  -H "Authorization: Bearer <token>" \
  -d '{"user_id": 1}' \
  localhost:50051 api.users.UserService/GetUser

# Pretty print response
grpcurl -plaintext \
  -format text \
  -d '{"user_id": 1}' \
  localhost:50051 api.users.UserService/GetUser
```

### 3. Python Debug Client

```python
import grpc
from google.protobuf.json_format import MessageToDict

# Create channel
channel = grpc.insecure_channel('localhost:50051')

# Import stubs
from apps.users import user_pb2, user_pb2_grpc

# Create stub
stub = user_pb2_grpc.UserServiceStub(channel)

# Call method
try:
    request = user_pb2.GetUserRequest(user_id=1)
    response = stub.GetUser(request)
    print(MessageToDict(response))
except grpc.RpcError as e:
    print(f"Error: {e.code()}")
    print(f"Details: {e.details()}")
```

### 4. Django Shell Testing

```bash
python manage.py shell
```

```python
from django_cfg.apps.integrations.grpc.services.grpc_client import DynamicGRPCClient

# Test service
client = DynamicGRPCClient(host="localhost", port=50051)

# List services
services = client.list_services()
print(services)

# Invoke method
response = client.invoke_method(
    service="api.users.UserService",
    method="GetUser",
    request_data={"user_id": 1}
)
print(response)
```

---

## 📊 Monitoring Issues

### Check Request Logs

```python
from django_cfg.apps.integrations.grpc.models import GRPCRequestLog

# Recent errors
errors = GRPCRequestLog.objects.filter(
    status='error'
).order_by('-created_at')[:10]

for log in errors:
    print(f"{log.service_name}.{log.method_name}")
    print(f"  Error: {log.error_message}")
    print(f"  Status: {log.grpc_status_code}")
    print(f"  User: {log.user}")
    print()

# Slow requests
slow = GRPCRequestLog.objects.filter(
    duration_ms__gt=1000  # > 1 second
).order_by('-duration_ms')[:10]

for log in slow:
    print(f"{log.service_name}.{log.method_name}: {log.duration_ms}ms")
```

### Admin Interface

View logs in Django admin:
```
http://localhost:8000/admin/integrations/grpc/grpcrequestlog/
```

Features:
- Filter by status, service, method, user
- Search by request ID, client IP
- Export to CSV
- Color-coded badges

---

## 🚨 Emergency Procedures

### Server Won't Stop

```bash
# Find process
ps aux | grep rungrpc

# Kill process
kill -9 <PID>

# Or find by port
lsof -ti :50051 | xargs kill -9
```

### Clear Request Logs

```bash
python manage.py shell
```

```python
from django_cfg.apps.integrations.grpc.models import GRPCRequestLog

# Delete old logs (older than 7 days)
from datetime import timedelta
from django.utils import timezone

cutoff = timezone.now() - timedelta(days=7)
GRPCRequestLog.objects.filter(created_at__lt=cutoff).delete()

# Or delete all logs
GRPCRequestLog.objects.all().delete()
```

### Reset Migrations

```bash
# Delete migration files (except __init__.py)
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc" -delete

# Recreate migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate
```

---

## 📚 Related Documentation

- **[Setup Guide](./setup.md)** - Installation and configuration
- **[Backend Guide](./backend-guide.md)** - Creating services
- **[Monitoring](./monitoring.md)** - Request logging
- **[Interceptors](./interceptors.md)** - Middleware system

---

## 💡 Still Having Issues?

1. **Check Django-CFG logs:** Look for error messages in console
2. **Enable DEBUG mode:** Set `DEBUG=True` for detailed errors
3. **Check dependencies:** Verify all gRPC packages installed
4. **Review configuration:** Double-check `api/config.py` settings
5. **Test with grpcurl:** Verify server is responding

**Need help?** Check the [Django-CFG GitHub Issues](https://github.com/anthropics/django-cfg/issues) or create a new issue with:
- Django version
- Python version
- gRPC version
- Full error traceback
- Configuration (without sensitive data)
