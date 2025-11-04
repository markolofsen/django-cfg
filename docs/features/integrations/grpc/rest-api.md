---
title: REST API
description: REST API endpoints for gRPC monitoring and management
sidebar_label: REST API
sidebar_position: 8
---

# gRPC REST API

Django-CFG provides REST API endpoints for monitoring gRPC services, managing API keys, and downloading proto files.

## 📄 Proto Files Endpoints

### List Proto Files

```http
GET /cfg/grpc/proto-files/
```

**Response:**
```json
{
  "files": [
    {
      "app_label": "crypto",
      "filename": "crypto.proto",
      "size_bytes": 1917,
      "package": "api.crypto",
      "messages_count": 3,
      "services_count": 1,
      "created_at": 1762235965.5593333,
      "modified_at": 1762235965.5593333
    }
  ],
  "total_files": 1,
  "proto_dir": "/path/to/media/protos"
}
```

### Download Proto File

```http
GET /cfg/grpc/proto-files/{app_label}/
```

**Parameters:**
- `app_label` (path) - App label (e.g., 'crypto')

**Response:** Proto file content (text/plain)

**Example:**
```bash
curl http://localhost:8000/cfg/grpc/proto-files/crypto/ \
  -H "Authorization: Bearer <token>" \
  -o crypto.proto
```

### Download All Proto Files

```http
GET /cfg/grpc/proto-files/download-all/
```

**Response:** Zip archive with all proto files

**Example:**
```bash
curl http://localhost:8000/cfg/grpc/proto-files/download-all/ \
  -H "Authorization: Bearer <token>" \
  -o protos.zip
```

### Generate Proto Files

```http
POST /cfg/grpc/proto-files/generate/
```

**Request Body:**
```json
{
  "apps": ["crypto", "accounts"],  // Optional, uses enabled_apps if not specified
  "force": false  // Optional, force regeneration
}
```

**Response:**
```json
{
  "status": "success",
  "generated": ["crypto"],
  "generated_count": 1,
  "errors": [],
  "proto_dir": "/path/to/media/protos"
}
```

:::tip Self-Service Proto Files
Proto files endpoints enable self-service for client developers. Frontend, mobile, and third-party teams can download proto files directly without asking backend team.

Perfect for:
- CI/CD pipelines (automated client generation)
- Developer onboarding
- Third-party integrations
- Documentation as code
:::

## 🔑 API Keys Endpoints

### List API Keys

```http
GET /api/grpc/api-keys/
```

**Query Parameters:**
- `is_active` (bool) - Filter by active status
- `key_type` (str) - Filter by key type (service, cli, webhook, internal, development)
- `user_id` (int) - Filter by user ID

**Response:**
```json
{
  "results": [
    {
      "id": 1,
      "name": "Analytics Service",
      "key_type": "service",
      "masked_key": "52df...1660",
      "is_active": true,
      "is_valid": true,
      "user_id": 5,
      "username": "service_user",
      "user_email": "service@example.com",
      "request_count": 1543,
      "last_used_at": "2025-11-04T05:58:43Z",
      "expires_at": null,
      "created_at": "2025-11-01T10:00:00Z",
      "created_by": "admin"
    }
  ],
  "count": 1
}
```

### Get API Key Details

```http
GET /api/grpc/api-keys/{id}/
```

**Response:** Same as single item from list above.

### API Keys Statistics

```http
GET /api/grpc/api-keys/stats/
```

**Response:**
```json
{
  "total_keys": 15,
  "active_keys": 12,
  "expired_keys": 2,
  "total_requests": 45231,
  "keys_by_type": {
    "service": 8,
    "cli": 3,
    "development": 2,
    "internal": 2
  }
}
```

:::info Read-Only Endpoints
API Keys endpoints are **read-only**. To create, update, or delete API keys, use the Django Admin interface at `/admin/` → **gRPC API Keys**.
:::

## 📊 Monitoring Endpoints

### Recent Requests

```http
GET /api/grpc/monitor/requests/
```

**Query Parameters:**
- `service` (str) - Filter by service name
- `method` (str) - Filter by method name
- `status` (str) - Filter by status (success, error, timeout, pending, cancelled)

**Response:**
```json
{
  "results": [
    {
      "id": 123,
      "request_id": "abc-123-def",
      "service_name": "api.users.UserService",
      "method_name": "GetUser",
      "status": "success",
      "duration_ms": 125,
      "grpc_status_code": "OK",
      "error_message": "",
      "created_at": "2025-11-04T05:58:43Z",
      "client_ip": "192.168.1.100",
      "user_id": 5,
      "username": "service_user",
      "is_authenticated": true,
      "api_key_id": 1,
      "api_key_name": "Analytics Service"
    }
  ],
  "count": 100
}
```

:::tip API Key Tracking
All request logs now include `user_id`, `username`, `api_key_id`, and `api_key_name` fields for comprehensive audit trails.
:::

### Health Status

```http
GET /api/grpc/monitor/health/
```

**Response:**
```json
{
  "status": "healthy",
  "server_running": true,
  "uptime_seconds": 86400,
  "registered_services": 5
}
```

### Overview Statistics

```http
GET /api/grpc/monitor/overview/?hours=24
```

**Query Parameters:**
- `hours` (int, default: 24) - Time window for statistics

**Response:**
```json
{
  "total_requests": 15234,
  "successful_requests": 14892,
  "failed_requests": 342,
  "success_rate": 97.8,
  "avg_duration_ms": 125.3,
  "total_services": 5,
  "active_api_keys": 12
}
```

### Service Statistics

```http
GET /api/grpc/monitor/services/?hours=24
```

**Query Parameters:**
- `hours` (int, default: 24) - Time window for statistics

**Response:**
```json
{
  "services": [
    {
      "service_name": "api.users.UserService",
      "total_requests": 8543,
      "successful_requests": 8421,
      "failed_requests": 122,
      "success_rate": 98.6,
      "avg_duration_ms": 98.4,
      "methods_count": 5
    }
  ]
}
```

### Method Statistics

```http
GET /api/grpc/monitor/methods/?hours=24&service=api.users.UserService
```

**Query Parameters:**
- `hours` (int, default: 24) - Time window for statistics
- `service` (str, optional) - Filter by service name

**Response:**
```json
{
  "methods": [
    {
      "service_name": "api.users.UserService",
      "method_name": "GetUser",
      "total_requests": 5432,
      "successful_requests": 5401,
      "failed_requests": 31,
      "success_rate": 99.4,
      "avg_duration_ms": 87.2,
      "min_duration_ms": 45,
      "max_duration_ms": 321
    }
  ]
}
```

## 🔐 Authentication

All REST endpoints require admin authentication. You can use:

### Session Auth (Recommended)

```python
import requests

session = requests.Session()
session.auth = ('admin', 'password')

# Login first
session.post('http://localhost:8000/api/auth/login/')

# Use authenticated session
response = session.get('http://localhost:8000/api/grpc/api-keys/')
```

### Basic Auth

```bash
curl http://localhost:8000/api/grpc/api-keys/ \
  -u admin:password
```

## 📖 Integration Examples

### Downloading Proto Files

```bash
# List available proto files
curl http://localhost:8000/cfg/grpc/proto-files/ \
  -H "Authorization: Bearer <token>"

# Download specific proto file
curl http://localhost:8000/cfg/grpc/proto-files/crypto/ \
  -H "Authorization: Bearer <token>" \
  -o crypto.proto

# Download all proto files as zip
curl http://localhost:8000/cfg/grpc/proto-files/download-all/ \
  -H "Authorization: Bearer <token>" \
  -o protos.zip
```

### Python Example

```python
import requests

# Download proto files
response = requests.get(
    'http://localhost:8000/cfg/grpc/proto-files/crypto/',
    headers={'Authorization': f'Bearer {token}'}
)

# Save to file
with open('crypto.proto', 'w') as f:
    f.write(response.text)
```

### Monitoring with Python

```python
import requests

# Get API keys
response = requests.get(
    'http://localhost:8000/api/grpc/api-keys/',
    headers={'Authorization': f'Bearer {token}'},
    params={'is_active': True}
)

for key in response.json()['results']:
    print(f"{key['name']}: {key['request_count']} requests")

# Get recent requests
response = requests.get(
    'http://localhost:8000/api/grpc/monitor/requests/',
    headers={'Authorization': f'Bearer {token}'}
)

for req in response.json()['results']:
    print(f"{req['service_name']}.{req['method_name']} - User: {req['username']}")
```

### JavaScript Example

```javascript
// Get API keys
const response = await fetch('http://localhost:8000/api/grpc/api-keys/', {
  headers: { 'Authorization': `Bearer ${token}` }
});

const data = await response.json();
data.results.forEach(key => {
  console.log(`${key.name}: ${key.request_count} requests`);
});
```

### cURL Examples

```bash
# Get all active API keys
curl "http://localhost:8000/api/grpc/api-keys/?is_active=true" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get API key statistics
curl "http://localhost:8000/api/grpc/api-keys/stats/" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get recent requests (last hour)
curl "http://localhost:8000/api/grpc/monitor/requests/" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get service statistics (last 24 hours)
curl "http://localhost:8000/api/grpc/monitor/services/?hours=24" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get method statistics for specific service
curl "http://localhost:8000/api/grpc/monitor/methods/?service=api.users.UserService" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Filter requests by status
curl "http://localhost:8000/api/grpc/monitor/requests/?status=error" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 🎯 Use Cases

### Monitoring Dashboard
Build custom dashboards by fetching statistics, recent requests, and service health data via REST API.

### Alert System
Monitor error rates and send alerts when thresholds are exceeded. Filter requests by status and analyze error patterns.

### Usage Analytics
Track API key usage patterns, identify most active services, and analyze request distribution across different time windows.

### Client Code Generation
Download proto files automatically in CI/CD pipelines to generate type-safe clients for Python, TypeScript, Go, and other languages.

### Developer Onboarding
New team members can self-serve proto files without backend team involvement, accelerating integration development.

---

**Next Steps:**
- **[Authentication](./authentication.md)** - Learn about API key management
- **[Configuration](./configuration.md)** - Configure REST API endpoints
- **[Getting Started](./getting-started.md)** - Build your first service
