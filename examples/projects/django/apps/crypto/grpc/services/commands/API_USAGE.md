# Crypto Client Commands - REST API Usage

**Control crypto clients via REST API → gRPC commands**

Created: 2025-11-14
Status: %%PRODUCTION%%

## 📋 Overview

The Crypto Client Commands API allows you to control connected crypto clients via REST API. The API internally uses gRPC bidirectional streaming to send commands to clients in real-time.

**Architecture:**
```
REST API → ClientCommandViewSet → StreamingCommandClient → gRPC → Crypto Client
```

## 🚀 API Endpoints

Base URL: `/api/crypto/commands/`

### List All Active Clients
```http
GET /api/crypto/commands/
```

**Response:**
```json
[
  {
    "client_id": "uuid-here",
    "client_name": "crypto-bot-001",
    "connected": true,
    "wallets_synced": 15
  }
]
```

### Get Client Details
```http
GET /api/crypto/commands/{client_id}/
```

**Response:**
```json
{
  "client_id": "uuid-here",
  "client_name": "crypto-bot-001",
  "connected": true,
  "last_heartbeat": "2025-11-14T10:30:00Z",
  "metadata": {
    "version": "1.0.0",
    "exchange": "binance"
  },
  "wallets_synced": 15,
  "sync_requests": 42,
  "last_sync": "2025-11-14T10:28:00Z"
}
```

### Pause Client
```http
POST /api/crypto/commands/{client_id}/pause/
```

Temporarily pauses the crypto client (stops wallet sync).

**Response:**
```json
{
  "client_id": "uuid-here",
  "client_name": "crypto-bot-001",
  "connected": true,
  "command_result": {
    "success": true,
    "message": "Client paused successfully",
    "current_status": "PAUSED"
  }
}
```

### Resume Client
```http
POST /api/crypto/commands/{client_id}/resume/
```

Resumes a paused crypto client.

**Response:**
```json
{
  "client_id": "uuid-here",
  "command_result": {
    "success": true,
    "message": "Client resumed successfully",
    "current_status": "ACTIVE"
  }
}
```

### Ping Client
```http
POST /api/crypto/commands/{client_id}/ping/
```

Health check - verifies client is responsive.

**Response:**
```json
{
  "client_id": "uuid-here",
  "ping": "pong",
  "command_result": {
    "success": true,
    "message": "Pong received",
    "current_status": "ACTIVE"
  }
}
```

### Sync Wallets
```http
POST /api/crypto/commands/{client_id}/sync_wallets/?symbols=BTC,ETH,USDT
```

Request wallet balance sync for specific coins (or all if no symbols provided).

**Query Parameters:**
- `symbols` (optional): Comma-separated coin symbols (e.g., `BTC,ETH,USDT`)

**Response:**
```json
{
  "client_id": "uuid-here",
  "symbols": ["BTC", "ETH", "USDT"],
  "command_result": {
    "success": true,
    "message": "Wallet sync started for 3 coins",
    "current_status": "SYNCING"
  }
}
```

### Request Status
```http
POST /api/crypto/commands/{client_id}/request_status/?include_stats=true
```

Request current status and statistics from client.

**Query Parameters:**
- `include_stats` (optional): Include detailed statistics (default: false)

**Response:**
```json
{
  "client_id": "uuid-here",
  "command_result": {
    "success": true,
    "message": "Status: ACTIVE, Wallets: 15, Last sync: 2m ago",
    "current_status": "ACTIVE"
  }
}
```

## 🔄 Bulk Actions

### Pause All Clients
```http
POST /api/crypto/commands/pause_all/
```

Pause all active crypto clients.

**Response:**
```json
{
  "total": 3,
  "results": [
    {
      "client_id": "uuid-1",
      "success": true,
      "result": {"success": true, "message": "Paused"}
    },
    {
      "client_id": "uuid-2",
      "success": true,
      "result": {"success": true, "message": "Paused"}
    }
  ]
}
```

### Resume All Clients
```http
POST /api/crypto/commands/resume_all/
```

Resume all active crypto clients.

### Sync All Clients
```http
POST /api/crypto/commands/sync_all/?symbols=BTC,ETH
```

Trigger wallet sync on all active crypto clients.

**Query Parameters:**
- `symbols` (optional): Comma-separated coin symbols to sync

## 🔐 Authentication

The API requires authentication. Use one of:
- Django session authentication
- JWT token authentication

**Example with curl:**
```bash
# With session cookie
curl -X POST \
  -H "Cookie: sessionid=your-session-id" \
  http://localhost:8000/api/crypto/commands/{client_id}/pause/

# With JWT token (if configured)
curl -X POST \
  -H "Authorization: Bearer your-jwt-token" \
  http://localhost:8000/api/crypto/commands/{client_id}/pause/
```

## 🐍 Python Client Example

```python
import requests

# Base URL
base_url = "http://localhost:8000/api/crypto/commands"

# Create session with authentication
session = requests.Session()
session.cookies.set('sessionid', 'your-session-id')

# List all clients
response = session.get(f"{base_url}/")
clients = response.json()
print(f"Active clients: {len(clients)}")

# Get specific client
client_id = clients[0]['client_id']
response = session.get(f"{base_url}/{client_id}/")
client = response.json()
print(f"Client: {client['client_name']}, Status: {client['connected']}")

# Pause client
response = session.post(f"{base_url}/{client_id}/pause/")
result = response.json()
print(f"Pause result: {result['command_result']['message']}")

# Sync specific wallets
response = session.post(
    f"{base_url}/{client_id}/sync_wallets/",
    params={'symbols': 'BTC,ETH,USDT'}
)
result = response.json()
print(f"Sync result: {result['command_result']['message']}")

# Request status with stats
response = session.post(
    f"{base_url}/{client_id}/request_status/",
    params={'include_stats': 'true'}
)
result = response.json()
print(f"Status: {result['command_result']['message']}")

# Resume client
response = session.post(f"{base_url}/{client_id}/resume/")
result = response.json()
print(f"Resume result: {result['command_result']['message']}")
```

## 📊 Error Responses

### 503 Service Unavailable
```json
{
  "error": "client_not_connected",
  "message": "Client uuid-here is not connected",
  "detail": "Client is not connected to gRPC server"
}
```

### 504 Gateway Timeout
```json
{
  "error": "command_timeout",
  "message": "Command command-id timeout after 5.0s",
  "detail": "Client did not respond within timeout period"
}
```

### 500 Internal Server Error
```json
{
  "error": "command_error",
  "message": "Failed to send command",
  "detail": "Failed to execute command on client"
}
```

## 🎯 Command Flow

```
1. REST API Request
   ↓
2. ClientCommandViewSet validates request
   ↓
3. StreamingCommandClient creates DjangoCommand protobuf
   ↓
4. Command sent via gRPC bidirectional stream
   ↓
5. Crypto client receives command
   ↓
6. Client executes command (pause, sync wallets, etc.)
   ↓
7. Client sends CommandAck back via stream
   ↓
8. BidirectionalStreamingService resolves Future
   ↓
9. API returns CommandAck as JSON response
```

## 🧪 Testing

### Manual Testing with curl

```bash
# 1. Start Django and gRPC server
poetry run python manage.py runserver &
poetry run python manage.py rungrpc &

# 2. List clients
curl http://localhost:8000/api/crypto/commands/

# 3. Pause a client
curl -X POST http://localhost:8000/api/crypto/commands/{client_id}/pause/

# 4. Sync wallets
curl -X POST "http://localhost:8000/api/crypto/commands/{client_id}/sync_wallets/?symbols=BTC,ETH"

# 5. Request status
curl -X POST "http://localhost:8000/api/crypto/commands/{client_id}/request_status/?include_stats=true"

# 6. Resume client
curl -X POST http://localhost:8000/api/crypto/commands/{client_id}/resume/
```

### Integration Testing

```python
import pytest
from rest_framework.test import APIClient

@pytest.mark.django_db
def test_pause_crypto_client():
    client = APIClient()
    # Authenticate
    client.force_authenticate(user=test_user)

    # Pause client
    response = client.post(
        f'/api/crypto/commands/{client_id}/pause/'
    )

    assert response.status_code == 200
    assert response.json()['command_result']['success'] is True
```

## 📁 File Structure

```
apps/crypto/
├── grpc/
│   └── services/
│       └── commands/
│           ├── __init__.py              # StreamingCommandClient
│           ├── base_client.py           # CryptoStreamingCommandClient
│           ├── pause.py                 # pause_client()
│           ├── resume.py                # resume_client()
│           ├── ping.py                  # ping_client()
│           ├── sync_wallets.py          # sync_wallets()
│           ├── request_status.py        # request_status()
│           ├── README.md                # Command implementation guide
│           └── API_USAGE.md             # This file
├── views/
│   ├── api/
│   │   ├── __init__.py
│   │   └── client_command_viewsets.py   # ClientCommandViewSet
│   └── serializers/
│       ├── __init__.py
│       └── client_command_serializers.py # ClientCommandSerializer
└── urls.py                              # URL routing

```

## 💡 Best Practices

### 1. Always Check Client Connection

Before sending commands, verify the client is connected:

```python
response = session.get(f"{base_url}/{client_id}/")
if response.status_code == 404:
    print("Client not connected")
elif response.json()['connected']:
    print("Client is connected and ready")
```

### 2. Handle Timeouts Gracefully

Commands may timeout if clients are slow or busy:

```python
try:
    response = session.post(
        f"{base_url}/{client_id}/sync_wallets/",
        timeout=35.0  # Longer timeout for wallet sync
    )
    response.raise_for_status()
except requests.Timeout:
    print("Command timed out - client may be busy")
except requests.HTTPError as e:
    if e.response.status_code == 504:
        print("Gateway timeout - client did not respond")
```

### 3. Use Bulk Actions for Multiple Clients

Instead of looping over clients, use bulk actions:

```python
# ❌ BAD - individual requests
for client in clients:
    session.post(f"{base_url}/{client['client_id']}/pause/")

# ✅ GOOD - bulk action
session.post(f"{base_url}/pause_all/")
```

### 4. Check Command Results

Always verify command execution:

```python
response = session.post(f"{base_url}/{client_id}/pause/")
result = response.json()

if result.get('command_result', {}).get('success'):
    print("✅ Command succeeded")
else:
    print(f"❌ Command failed: {result.get('command_result', {}).get('message')}")
```

## 🔗 Related Documentation

- [ARCHITECTURE_GUIDE.md](../../ARCHITECTURE_GUIDE.md) - Overall crypto gRPC architecture
- [BIDIRECTIONAL_STREAMING.md](../../BIDIRECTIONAL_STREAMING.md) - Streaming implementation guide
- [README.md](./README.md) - Command implementation details

---

**Questions?** Check the main crypto gRPC documentation or signals app implementation for reference patterns.
