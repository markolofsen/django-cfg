# Terminal Web API Documentation

## Overview

The Terminal Web API provides RESTful endpoints for managing terminal sessions and command history. It complements the WebSocket-based real-time communication via Centrifugo.

## API Endpoints

### Base URL

```
/api/terminal/
```

### Session Management

#### List Sessions

```http
GET /api/terminal/sessions/
```

Returns list of user's terminal sessions.

**Response:**
```json
[
    {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "name": "dev-session",
        "status": "connected",
        "display_name": "dev-session",
        "is_alive": true,
        "electron_hostname": "macbook-pro.local",
        "working_directory": "/Users/developer/project",
        "shell": "/bin/zsh",
        "connected_at": "2024-01-15T10:30:00Z",
        "last_heartbeat_at": "2024-01-15T10:35:00Z",
        "created_at": "2024-01-15T10:30:00Z"
    }
]
```

#### Get Active Sessions Only

```http
GET /api/terminal/sessions/active/
```

Returns only connected sessions with recent heartbeat.

#### Create Session

```http
POST /api/terminal/sessions/
Content-Type: application/json

{
    "name": "dev-session",
    "shell": "/bin/zsh",
    "working_directory": "~",
    "environment": {
        "TERM": "xterm-256color"
    }
}
```

**Response:**
```json
{
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "dev-session",
    "status": "pending",
    "shell": "/bin/zsh",
    "working_directory": "~",
    "environment": {"TERM": "xterm-256color"},
    "user": 1,
    "created_at": "2024-01-15T10:30:00Z"
}
```

#### Get Session Details

```http
GET /api/terminal/sessions/{id}/
```

Returns full session details including recent commands.

#### Close Session

```http
DELETE /api/terminal/sessions/{id}/
```

Closes the terminal session and updates status to `disconnected`.

### Terminal Operations

#### Send Input

```http
POST /api/terminal/sessions/{id}/input/
Content-Type: application/json

{
    "data": "ls -la\n"
}
```

Or with base64 encoding:

```json
{
    "data_base64": "bHMgLWxhCg=="
}
```

**Response:**
```json
{
    "status": "sent",
    "bytes": 7
}
```

#### Resize Terminal

```http
POST /api/terminal/sessions/{id}/resize/
Content-Type: application/json

{
    "cols": 120,
    "rows": 40
}
```

**Response:**
```json
{
    "status": "resized",
    "cols": 120,
    "rows": 40
}
```

#### Send Signal

```http
POST /api/terminal/sessions/{id}/signal/
Content-Type: application/json

{
    "signal": 2
}
```

Available signals:
- `2` - SIGINT (Ctrl+C)
- `9` - SIGKILL
- `15` - SIGTERM

**Response:**
```json
{
    "status": "sent",
    "signal": 2,
    "signal_name": "SIGINT"
}
```

#### Get Session Command History

```http
GET /api/terminal/sessions/{id}/history/
```

Returns last 100 commands for this session.

### Command History

#### List All Commands

```http
GET /api/terminal/commands/
```

Query parameters:
- `session` - Filter by session UUID
- `status` - Filter by status (SUCCESS, FAILED, etc.)
- `search` - Search in command text

**Response:**
```json
{
    "count": 150,
    "next": "/api/terminal/commands/?page=2",
    "previous": null,
    "results": [
        {
            "id": "660e8400-e29b-41d4-a716-446655440001",
            "session_id": "550e8400-e29b-41d4-a716-446655440000",
            "command": "git status",
            "status": "SUCCESS",
            "exit_code": 0,
            "output_preview": "On branch main...",
            "duration_ms": 125,
            "created_at": "2024-01-15T10:35:00Z"
        }
    ]
}
```

#### Get Command Details

```http
GET /api/terminal/commands/{id}/
```

Returns full command details including stdout/stderr.

## Error Responses

### Session Not Active

```json
{
    "error": "session_not_active",
    "message": "Session is not connected"
}
```
Status: `400 Bad Request`

### Send Failed

```json
{
    "error": "send_failed",
    "message": "Failed to send input"
}
```
Status: `503 Service Unavailable`

### Session Not Found

```json
{
    "detail": "Not found."
}
```
Status: `404 Not Found`

## Authentication

All endpoints require authentication:
- Session-based authentication
- JWT token authentication

```http
Authorization: Bearer <jwt_token>
```

## WebSocket Integration

For real-time output, subscribe to Centrifugo channel:

```javascript
const channel = `terminal#session#${sessionId}`;
centrifuge.subscribe(channel, (message) => {
    switch (message.data.type) {
        case 'output':
            // Decode base64 and write to terminal
            const data = atob(message.data.data);
            terminal.write(data);
            break;
        case 'status':
            console.log('Status:', message.data.status);
            break;
        case 'error':
            console.error('Error:', message.data.message);
            break;
        case 'command_complete':
            console.log('Exit code:', message.data.exit_code);
            break;
    }
});
```

## WebSocket RPC (Alternative to REST)

For lower latency operations, use Centrifugo RPC:

```javascript
// Send input
await centrifuge.rpc('terminal.input', {
    session_id: sessionId,
    data: btoa(input)  // base64 encoded
});

// Resize
await centrifuge.rpc('terminal.resize', {
    session_id: sessionId,
    cols: 120,
    rows: 40
});

// Send signal
await centrifuge.rpc('terminal.signal', {
    session_id: sessionId,
    signal: 2  // SIGINT
});

// Close session
await centrifuge.rpc('terminal.close', {
    session_id: sessionId,
    reason: 'User closed terminal'
});
```

## Recommended Usage Pattern

| Operation | Use | Reason |
|-----------|-----|--------|
| Create session | REST API | One-time operation |
| List sessions | REST API | Cacheable, paginated |
| Send input | **WebSocket RPC** | Low latency critical |
| Resize | **WebSocket RPC** | Low latency |
| Send signal | Either | Both work well |
| Receive output | **WebSocket subscription** | Real-time only |
| Command history | REST API | Pagination support |

## OpenAPI Schema

API documentation available at:
- Swagger UI: `/api/docs/`
- ReDoc: `/api/redoc/`
- OpenAPI JSON: `/api/schema/`

## Rate Limiting

- Input operations: 100 requests/second per session
- Session creation: 10 requests/minute per user
- History queries: 60 requests/minute per user

## Code Examples

### Python (requests)

```python
import requests

# Create session
response = requests.post(
    'http://localhost:8000/api/terminal/sessions/',
    json={'name': 'my-session', 'shell': '/bin/bash'},
    headers={'Authorization': 'Bearer <token>'}
)
session = response.json()

# Send command
requests.post(
    f'http://localhost:8000/api/terminal/sessions/{session["id"]}/input/',
    json={'data': 'echo "Hello World"\n'},
    headers={'Authorization': 'Bearer <token>'}
)
```

### TypeScript (fetch)

```typescript
// Create session
const session = await fetch('/api/terminal/sessions/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({
        name: 'my-session',
        shell: '/bin/zsh'
    })
}).then(r => r.json());

// Subscribe to output
centrifuge.subscribe(`terminal#session#${session.id}`, (msg) => {
    if (msg.data.type === 'output') {
        terminal.write(atob(msg.data.data));
    }
});

// Send input via WebSocket RPC (recommended)
await centrifuge.rpc('terminal.input', {
    session_id: session.id,
    data: btoa('ls -la\n')
});
```

### cURL

```bash
# Create session
curl -X POST http://localhost:8000/api/terminal/sessions/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{"name": "test-session", "shell": "/bin/zsh"}'

# Send input
curl -X POST http://localhost:8000/api/terminal/sessions/<session_id>/input/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{"data": "pwd\n"}'

# Get history
curl http://localhost:8000/api/terminal/sessions/<session_id>/history/ \
  -H "Authorization: Bearer <token>"
```
