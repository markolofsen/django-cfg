---
title: Best Practices & Troubleshooting
description: Django-CFG troubleshooting feature guide. Production-ready best practices & troubleshooting with built-in validation, type safety, and seamless Django integrati
sidebar_label: Troubleshooting
sidebar_position: 6
keywords:
  - django-cfg troubleshooting
  - django troubleshooting
  - troubleshooting django-cfg
---

# Best Practices & Troubleshooting

Best practices for using ngrok with Django-CFG and solutions to common issues.

## Best Practices

### 1. Development Only

Ngrok should **only** be used in development, never in production.

```python
# ✅ CORRECT - ngrok only in development
from django_cfg import DjangoConfig, NgrokConfig

class MyConfig(DjangoConfig):
    ngrok: NgrokConfig = NgrokConfig(
        enabled=True  # Automatically disabled if DEBUG=False
    )

# ❌ WRONG - enable ngrok in production
# Ngrok is NOT for production! Only for local development.
```

**Even better - explicit environment check:**

```python
from .environment import env

class MyConfig(DjangoConfig):
    # Ngrok only in development
    ngrok: NgrokConfig = NgrokConfig(
        enabled=(env.environment == "development")
    )
```

---

### 2. Use Helper Functions

Always use Django-CFG helper functions instead of manual URL construction.

```python
# ✅ CORRECT - automatic fallback
from django_cfg.modules.django_ngrok import get_webhook_url

webhook_url = get_webhook_url("/webhooks/")
# If ngrok active: "https://abc123.ngrok.io/webhooks/"
# If not: "http://localhost:8000/webhooks/" (or api_url from config)

# ❌ WRONG - hardcode URL
webhook_url = "http://localhost:8000/webhooks/"  # Won't work with ngrok!

# ❌ WRONG - manual construction
import os
ngrok_url = os.environ.get('NGROK_URL')
webhook_url = f"{ngrok_url}/webhooks/" if ngrok_url else "http://localhost:8000/webhooks/"
```

---

### 3. Check Tunnel Status Before Critical Operations

```python
# ✅ CORRECT - check before using
from django_cfg.modules.django_ngrok import is_tunnel_active, get_webhook_url

if is_tunnel_active():
    print("✅ Using ngrok tunnel for webhooks")
else:
    print("⚠️ Ngrok not active, using fallback URL")

webhook_url = get_webhook_url("/webhooks/")

# ❌ WRONG - assume tunnel is always active
webhook_url = get_webhook_url("/webhooks/")  # May return fallback URL!
```

---

### 4. Log Webhook Events

Always log webhook events for debugging.

```python
# ✅ CORRECT - log webhooks for debugging
import logging

logger = logging.getLogger(__name__)

def webhook_handler(request):
    logger.info(f"Webhook received from {request.META.get('HTTP_HOST')}")
    logger.debug(f"Headers: {dict(request.headers)}")
    logger.debug(f"Payload: {request.body.decode()}")

    # Process webhook
    # ...

    return JsonResponse({"status": "ok"})
```

---

### 5. Environment-Specific Configuration

Use different configurations for different environments.

```python
# ✅ CORRECT - different settings for dev/prod
from .environment import env

class MyConfig(DjangoConfig):
    # Ngrok only in development
    ngrok: NgrokConfig = NgrokConfig(
        enabled=(env.environment == "development"),
        webhook_path="/api/webhooks/"
    )

    # Production uses real domain
    api_url: str = (
        "https://api.myapp.com"
        if env.environment == "production"
        else "http://localhost:8000"
    )
```

---

### 6. Use Type Hints

Always use type hints for better IDE support.

```python
# ✅ CORRECT - type hints
from typing import Optional
from django_cfg.modules.django_ngrok import get_tunnel_url

def get_public_url() -> Optional[str]:
    """Get public URL for webhooks."""
    return get_tunnel_url()

# ✅ CORRECT - type hints for service
class WebhookService:
    def __init__(self):
        self.base_url: str = get_tunnel_url() or "http://localhost:8000"

    def get_webhook_url(self, path: str) -> str:
        return f"{self.base_url}{path}"
```

---

## Common Issues

### Issue 1: Tunnel Not Starting

**Symptom:**
```bash
$ python manage.py runserver_ngrok
❌ Error: No module named 'ngrok'
```

**Solution:**

```bash
# Check that ngrok is available
python -c "import ngrok; print('OK')"

# If error "No module named 'ngrok'":
pip install ngrok

# For Python < 3.12 may need:
pip install pyngrok
```

**Verify installation:**

```python
# Check ngrok is installed
import ngrok
print(f"Ngrok version: {ngrok.__version__}")
```

---

### Issue 2: Webhooks Not Received

**Symptom:**
```
External service sends webhook but Django doesn't receive it
```

**Solution 1: Check tunnel is active**

```python
from django_cfg.modules.django_ngrok import is_tunnel_active, get_tunnel_url

print(f"Tunnel active: {is_tunnel_active()}")
print(f"Tunnel URL: {get_tunnel_url()}")

# If not active:
# - Restart with: python manage.py runserver_ngrok
# - Verify ngrok: NgrokConfig(enabled=True)
```

**Solution 2: Check ALLOWED_HOSTS**

```python
from django.conf import settings

print(f"ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")

# Should include ngrok host like:
# ['localhost', '127.0.0.1', 'abc123.ngrok.io']

# If not:
# - Restart server with runserver_ngrok
# - Check NgrokConfig(enabled=True)
```

**Solution 3: Verify webhook URL**

```python
from django_cfg.modules.django_ngrok import get_webhook_url

webhook_url = get_webhook_url('/api/webhooks/')
print(f"Webhook URL: {webhook_url}")

# Should be like: https://abc123.ngrok.io/api/webhooks/
# NOT: http://localhost:8000/api/webhooks/
```

**Solution 4: Check URL routing**

```python
# urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Ensure webhook path exists
    path('api/webhooks/stripe/', views.stripe_webhook, name='stripe_webhook'),
]

# Test URL manually:
# curl https://abc123.ngrok.io/api/webhooks/stripe/
```

---

### Issue 3: Auth Token Issues

**Symptom:**
```
Error: Invalid ngrok auth token
```

**Solution:**

```bash
# If need advanced features (custom domain, etc):
export NGROK_AUTHTOKEN="your-ngrok-token"

# Get token from: https://dashboard.ngrok.com/get-started/your-authtoken
```

**Or configure in code:**

```python
from django_cfg import NgrokConfig, NgrokAuthConfig

ngrok: NgrokConfig = NgrokConfig(
    enabled=True,
    auth=NgrokAuthConfig(
        authtoken_from_env=True  # Load from NGROK_AUTHTOKEN
    )
)
```

---

### Issue 4: CSRF Token Errors

**Symptom:**
```
403 Forbidden - CSRF verification failed
```

**Solution:**

```python
# Disable CSRF for webhook endpoints
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def stripe_webhook(request):
    # Process webhook
    return JsonResponse({"status": "ok"})
```

**Or add ngrok host to trusted origins:**

```python
# settings.py (generated by Django-CFG)
CSRF_TRUSTED_ORIGINS = [
    "https://*.ngrok.io",
    "https://*.ngrok-free.app",
]
```

---

### Issue 5: Tunnel URL Changes

**Symptom:**
```
Ngrok URL changes on each restart (free plan)
```

**Solutions:**

**Option 1: Use helper functions (recommended)**

```python
# ✅ Always use helper functions
from django_cfg.modules.django_ngrok import get_webhook_url

# URL automatically updated on each restart
webhook_url = get_webhook_url("/webhooks/")
```

**Option 2: Custom domain (paid plan)**

```python
from django_cfg import NgrokConfig, NgrokTunnelConfig, NgrokAuthConfig

ngrok: NgrokConfig = NgrokConfig(
    enabled=True,
    auth=NgrokAuthConfig(
        authtoken_from_env=True  # Requires token
    ),
    tunnel=NgrokTunnelConfig(
        domain="myapp.ngrok.io"  # Fixed domain (paid plan)
    )
)
```

---

### Issue 6: Slow Webhook Response

**Symptom:**
```
Webhooks timeout or are very slow
```

**Solutions:**

**Solution 1: Enable compression**

```python
from django_cfg import NgrokConfig, NgrokTunnelConfig

ngrok: NgrokConfig = NgrokConfig(
    enabled=True,
    tunnel=NgrokTunnelConfig(
        compression=True  # Enable gzip compression
    )
)
```

**Solution 2: Use async webhook processing**

```python
# Process webhooks asynchronously
import dramatiq
from django.http import JsonResponse

@csrf_exempt
def stripe_webhook(request):
    # Immediately return success
    # Process webhook in background

    payload = request.body
    process_stripe_webhook.send(payload.decode())

    return JsonResponse({"status": "received"})

@dramatiq.actor
def process_stripe_webhook(payload: str):
    # Process webhook in background
    # ...
    pass
```

---

### Issue 7: Environment Variables Not Set

**Symptom:**
```python
print(os.environ.get('NGROK_URL'))  # None
```

**Solution:**

```bash
# Make sure you use runserver_ngrok
python manage.py runserver_ngrok  # NOT runserver!

# Verify variables are set:
echo $NGROK_URL
echo $NGROK_HOST
echo $NGROK_SCHEME
```

**In Python:**

```python
import os

# Check environment variables
ngrok_url = os.environ.get('NGROK_URL')
if not ngrok_url:
    print("⚠️ NGROK_URL not set!")
    print("Did you use 'runserver_ngrok' instead of 'runserver'?")
```

---

### Issue 8: Multiple Tunnels

**Symptom:**
```
Multiple ngrok tunnels running at same time
```

**Solution:**

```bash
# Stop all ngrok processes
pkill -f ngrok

# Restart server
python manage.py runserver_ngrok
```

**Or programmatically:**

```python
from django_cfg.modules.django_ngrok import get_ngrok_service

# Stop existing tunnel
service = get_ngrok_service()
service.stop_tunnel()

# Start new tunnel
service.start_tunnel(port=8000)
```

---

## Debugging Tips

### 1. Check Ngrok Web Interface

Ngrok provides a web interface for debugging:

```bash
# Start server
python manage.py runserver_ngrok

# Open ngrok web interface
# http://127.0.0.1:4040

# Shows:
# - All HTTP requests
# - Request/response details
# - Timing information
```

### 2. Enable Verbose Logging

```python
# config.py
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Or in Django settings:
LOGGING = {
    'version': 1,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django_cfg.modules.django_ngrok': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

### 3. Test Webhook Manually

```bash
# Test webhook with curl
curl -X POST https://abc123.ngrok.io/api/webhooks/test/ \
  -H "Content-Type: application/json" \
  -d '{"event": "test", "data": {"amount": 1000}}'

# Should return webhook response
```

### 4. Monitor Django Logs

```python
# In webhook handler
import logging

logger = logging.getLogger(__name__)

def webhook_handler(request):
    logger.info(f"📥 Webhook received")
    logger.debug(f"Headers: {dict(request.headers)}")
    logger.debug(f"Body: {request.body.decode()}")

    # Process webhook
    result = process_webhook(request)

    logger.info(f"✅ Webhook processed: {result}")
    return JsonResponse({"status": "ok"})
```

---

## Performance Optimization

### 1. Background Processing

Process webhooks asynchronously:

```python
import dramatiq
from django.http import JsonResponse

@csrf_exempt
def webhook_handler(request):
    # Immediately acknowledge receipt
    payload = request.body.decode()
    process_webhook_task.send(payload)

    return JsonResponse({"status": "received"})

@dramatiq.actor
def process_webhook_task(payload: str):
    # Process in background
    # ...
    pass
```

### 2. Enable Compression

```python
ngrok: NgrokConfig = NgrokConfig(
    enabled=True,
    tunnel=NgrokTunnelConfig(
        compression=True  # Faster for large payloads
    )
)
```

### 3. Use Webhook Queues

```python
# Queue webhooks for processing
from django.core.cache import cache

@csrf_exempt
def webhook_handler(request):
    # Add to queue
    webhook_id = str(uuid.uuid4())
    cache.set(f"webhook:{webhook_id}", request.body, timeout=3600)

    # Process asynchronously
    process_webhook_queue.send(webhook_id)

    return JsonResponse({"status": "queued"})
```

---

## Security Considerations

### 1. Verify Webhook Signatures

Always verify webhook signatures from external services:

```python
# Stripe signature verification
import stripe

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except stripe.error.SignatureVerificationError:
        return JsonResponse({"error": "Invalid signature"}, status=400)

    # Process verified event
    # ...
```

### 2. Use HTTPS Only

```python
ngrok: NgrokConfig = NgrokConfig(
    enabled=True,
    tunnel=NgrokTunnelConfig(
        bind_tls=True  # Force HTTPS
    )
)
```

### 3. Password Protect Tunnel (Testing)

```python
ngrok: NgrokConfig = NgrokConfig(
    enabled=True,
    tunnel=NgrokTunnelConfig(
        basic_auth=["admin:supersecret"]  # Require authentication
    )
)
```

---

## Summary

**Key Takeaways:**

✅ Use `runserver_ngrok` instead of `runserver`
✅ Always use helper functions (`get_webhook_url()`, etc.)
✅ Check tunnel status before critical operations
✅ Log all webhook events for debugging
✅ Verify webhook signatures from external services
✅ Process webhooks asynchronously for better performance
✅ Use ngrok web interface (localhost:4040) for debugging
✅ Development only - never use in production

---

## Next Steps

- **[Overview](./overview)** - Back to ngrok overview
- **[Configuration](./configuration)** - Advanced configuration options
- **[Webhook Examples](./webhook-examples)** - More integration examples

## See Also

- [Dramatiq Integration](/features/integrations/dramatiq/overview) - Background task processing
- [Configuration Guide](/fundamentals/configuration) - DjangoConfig reference
- [Deployment Guide](/guides/docker/production) - Production deployment
