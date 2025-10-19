---
title: Testing & Monitoring Commands
description: Django-CFG testing and monitoring commands. Health checks, endpoint validation, and service testing.
sidebar_label: Testing & Monitoring
sidebar_position: 4
keywords:
  - django-cfg testing
  - endpoint health check
  - api monitoring
  - service testing
---

# Testing & Monitoring Commands

Comprehensive commands for testing services, monitoring endpoints, and validating integrations.

## Endpoint Health Monitoring

### `check_endpoints`

**Production-ready endpoint health checker** with automatic parameter resolution, JWT authentication, and multi-database awareness.

```bash
python manage.py check_endpoints [OPTIONS]
```

**Options:**
- `--include-unnamed` - Include unnamed URL patterns
- `--timeout INTEGER` - Request timeout in seconds (default: 5)
- `--json` - Output as JSON for automation
- `--url TEXT` - Check specific endpoint by URL name
- `--no-auth` - Disable automatic JWT authentication retry

**Examples:**

```bash
# Check all endpoints (auto-resolves parametrized URLs)
python manage.py check_endpoints

# JSON output for CI/CD
python manage.py check_endpoints --json

# Custom timeout
python manage.py check_endpoints --timeout 10

# Disable auto-auth
python manage.py check_endpoints --no-auth

# Check specific endpoint
python manage.py check_endpoints --url api_users_list
```

**Features:**

- ✅ **Automatic URL parameter resolution** - resolves `<int:pk>`, `<uuid:id>`, `(?P<slug>[^/]+)` with test values
- ✅ **JWT auto-authentication** - creates test user and retries 401/403 endpoints automatically
- ✅ **Rate limiting bypass** - internal checks don't count towards rate limits
- ✅ **Multi-database aware** - treats cross-database errors as warnings (expected for SQLite multi-db)
- ✅ **Context-aware warnings** - 404 for detail views = warning (no data), not error
- ✅ Response time tracking in milliseconds
- ✅ Status code visibility
- ✅ Error type classification (database, general)
- ✅ Color-coded console output

**Console Output:**

```
✅ Overall Status: HEALTHY

📊 Summary:
  Total endpoints: 244
  ✅ Healthy: 154
  ⚠️  Warnings: 90
  ❌ Unhealthy: 0
  ❌ Errors: 0
  ⏭️  Skipped: 0

🔗 Endpoints:
  ✅ product-detail
     Pattern: /api/shop/products/(?P<slug>[/.]+)/
     Resolved: /api/shop/products/test-slug/
     Status: healthy (200)
     Response time: 12.35ms
     🔐 Required JWT authentication

  ❌ ticket-list
     URL: /api/support/tickets/
     Status: warning (404)
     Response time: 0.24ms
     ⚠️  Not Found - endpoint works but no data exists
```

**JSON Response:**

```json
{
  "status": "healthy|degraded|unhealthy",
  "timestamp": "2025-10-06T05:18:09.956705+00:00",
  "total_endpoints": 244,
  "healthy": 154,
  "unhealthy": 0,
  "warnings": 90,
  "errors": 0,
  "skipped": 0,
  "endpoints": [
    {
      "url": "/api/products/test-slug/",
      "url_pattern": "/api/products/(?P<slug>[^/]+)/",
      "url_name": "product-detail",
      "status": "healthy",
      "status_code": 200,
      "response_time_ms": 12.35,
      "has_parameters": true,
      "required_auth": true,
      "error": null,
      "error_type": null,
      "reason": null
    }
  ]
}
```

**REST API Endpoints:**

The checker is also available as REST API for monitoring systems:

```bash
# JSON API
curl http://localhost:8000/cfg/endpoints/

# DRF Browsable API
curl http://localhost:8000/cfg/endpoints/drf/

# With query parameters
curl "http://localhost:8000/cfg/endpoints/?timeout=10&auto_auth=true"
```

**Query Parameters:**
- `include_unnamed` (default: false) - Include endpoints without URL names
- `timeout` (default: 5) - Request timeout in seconds
- `auto_auth` (default: true) - Auto-retry with JWT on 401/403

**Use Cases:**

**1. CI/CD Integration:**
```bash
# GitHub Actions / GitLab CI
python manage.py check_endpoints --json | jq '.errors'
# Exit if errors > 0
test $(python manage.py check_endpoints --json | jq '.errors') -eq 0
```

**2. Monitoring & Alerting:**
```python
import requests

def check_api_health():
    resp = requests.get('http://localhost/cfg/endpoints/')
    data = resp.json()

    if data['errors'] > 0 or data['unhealthy'] > 0:
        alert_team(f"API unhealthy: {data['errors']} errors, {data['unhealthy']} unhealthy")

    return data
```

**3. Load Balancer Health Check:**
```nginx
# Nginx upstream health check
upstream django_api {
    server backend1:8000;
    check interval=30s fall=3 rise=2 timeout=5s type=http;
    check_http_send "GET /cfg/endpoints/ HTTP/1.0\r\n\r\n";
    check_http_expect_alive http_2xx;
}
```

**4. Performance Tracking:**
```bash
# Find slow endpoints
python manage.py check_endpoints --json | \
  jq '.endpoints[] | select(.response_time_ms > 1000) | {url, response_time_ms}'

# Track over time
while true; do
  python manage.py check_endpoints --json >> health-$(date +%Y%m%d).jsonl
  sleep 300
done
```

**5. Prometheus Metrics:**
```python
# Export to Prometheus format
from prometheus_client import Gauge, generate_latest

healthy_gauge = Gauge('api_endpoints_healthy', 'Number of healthy endpoints')
unhealthy_gauge = Gauge('api_endpoints_unhealthy', 'Number of unhealthy endpoints')

def update_metrics():
    data = requests.get('http://localhost/cfg/endpoints/').json()
    healthy_gauge.set(data['healthy'])
    unhealthy_gauge.set(data['unhealthy'])
```

## Email Testing

### `test_email`

Test email configuration and delivery.

```bash
cli test-email --to admin@example.com [OPTIONS]
```

**Options:**
- `--to TEXT` - Recipient email (required)
- `--subject TEXT` - Email subject (default: "Django-CFG Test Email")
- `--backend TEXT` - Specific backend to test

**Examples:**

```bash
# Basic test
cli test-email --to admin@example.com

# Custom subject
cli test-email --to test@test.com --subject "Configuration Test"

# Test specific backend
cli test-email --to admin@test.com --backend sendgrid
```

## Telegram Testing

### `test_telegram`

Test Telegram bot configuration.

```bash
cli test-telegram --message "Hello!" [OPTIONS]
```

**Options:**
- `--message TEXT` - Test message to send (required)
- `--chat-id TEXT` - Target chat ID (optional)

**Examples:**

```bash
# Send test message
cli test-telegram --message "Hello from Django-CFG!"

# Send to specific chat
cli test-telegram --message "Deploy successful" --chat-id "-1001234567890"
```

## SMS & WhatsApp Testing

### `test_twilio`

Test Twilio SMS and WhatsApp messaging.

```bash
python manage.py test_twilio --to "+1234567890" [OPTIONS]
```

**Options:**
- `--to TEXT` - Phone number (required, E.164 format)
- `--message TEXT` - Message to send
- `--whatsapp` - Send WhatsApp instead of SMS
- `--content-sid TEXT` - WhatsApp template SID

**Examples:**

```bash
# Test SMS
python manage.py test_twilio --to "+1234567890" --message "Test SMS"

# Test WhatsApp
python manage.py test_twilio --to "+1234567890" --message "Test" --whatsapp

# WhatsApp template
python manage.py test_twilio --to "+1234567890" --whatsapp --content-sid "HXxxxxx"
```

## Payment Provider Testing

### `test_providers`

Test payment provider integrations.

```bash
python manage.py test_providers [OPTIONS]
```

**Options:**
- `--provider TEXT` - Specific provider to test

**Examples:**

```bash
# Test all providers
python manage.py test_providers

# Test specific provider
python manage.py test_providers --provider nowpayments
```

## Newsletter Testing

### `test_newsletter`

Test newsletter sending functionality.

```bash
python manage.py test_newsletter --email test@example.com [OPTIONS]
```

**Options:**
- `--email TEXT` - Recipient email (required)
- `--template TEXT` - Template name to test

**Examples:**

```bash
# Send test newsletter
python manage.py test_newsletter --email test@example.com

# Test specific template
python manage.py test_newsletter --template welcome --email test@example.com
```

## OTP Authentication Testing

### `test_otp`

Test OTP authentication system.

```bash
python manage.py test_otp [OPTIONS]
```

**Options:**
- `--email TEXT` - Email for OTP test
- `--phone TEXT` - Phone number for SMS OTP test

**Examples:**

```bash
# Test email OTP
python manage.py test_otp --email user@example.com

# Test SMS OTP
python manage.py test_otp --phone "+1234567890"
```

## Best Practices

### 1. Continuous Health Monitoring

```bash
# Add to cron - check every 5 minutes
*/5 * * * * cd /path/to/project && \
  python manage.py check_endpoints --json > /var/log/health-check.json
```

### 2. Pre-Deployment Validation

```bash
#!/bin/bash
# deploy-check.sh

echo "🔍 Checking endpoint health..."
python manage.py check_endpoints || exit 1

echo "📧 Testing email..."
cli test-email --to admin@example.com || exit 1

echo "✅ All checks passed"
```

### 3. Load Testing Integration

```bash
# Before load test - ensure all endpoints healthy
python manage.py check_endpoints
if [ $? -ne 0 ]; then
  echo "❌ Fix unhealthy endpoints before load testing"
  exit 1
fi

# Run load test
locust -f locustfile.py
```

### 4. Monitoring Dashboard

Create a simple monitoring dashboard:

```python
# monitor.py
import requests
import time

while True:
    data = requests.get('http://localhost/cfg/endpoints/').json()

    print(f"Status: {data['status']}")
    print(f"Healthy: {data['healthy']}/{data['total_endpoints']}")
    print(f"Warnings: {data['warnings']}")
    print(f"Errors: {data['errors']}")

    time.sleep(30)
```

## Related Commands

- [**Development**](./development.md) - Development server commands
- [**Core Commands**](./core-commands.md) - Configuration validation
- [**Payments**](./payments.md) - Payment provider management

---

**Keep your API healthy!** 🚀
