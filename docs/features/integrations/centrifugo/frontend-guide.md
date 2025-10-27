# Frontend Developer Guide

Learn how to use generated Centrifugo clients in your frontend applications.

## Installation

### Python Client

```bash
cd opensdk/python
pip install -r requirements.txt
```

### TypeScript/JavaScript Client

```bash
cd opensdk/typescript
npm install
```

### Go Client

```bash
cd opensdk/go
go mod tidy
```

## Usage Examples

### Python Client

```python
import asyncio
from opensdk.python import CentrifugoRPCClient, APIClient, TaskStatsParams

async def main():
    # Create RPC client
    rpc = CentrifugoRPCClient(
        url="ws://localhost:8000/connection/websocket",
        token="your-jwt-token",
        user_id="user-123"
    )

    # Connect
    await rpc.connect()

    # Create API client
    api = APIClient(rpc)

    # Call RPC methods
    result = await api.tasks_get_stats(TaskStatsParams(
        user_id="user-123",
        include_completed=True
    ))

    print(f"Total: {result.total}, Completed: {result.completed}")

    # Disconnect
    await rpc.disconnect()

asyncio.run(main())
```

### TypeScript/React Client

```typescript
import { CentrifugoRPCClient, APIClient } from './opensdk/typescript';
import { useEffect, useState } from 'react';

function TaskStats() {
  const [stats, setStats] = useState(null);

  useEffect(() => {
    const rpc = new CentrifugoRPCClient(
      'ws://localhost:8000/connection/websocket',
      'your-jwt-token',
      'user-123'
    );

    rpc.connect().then(() => {
      const api = new APIClient(rpc);

      api.tasksGetStats({ user_id: 'user-123', include_completed: true })
        .then(result => setStats(result));
    });

    return () => rpc.disconnect();
  }, []);

  if (!stats) return <div>Loading...</div>;

  return (
    <div>
      <p>Total: {stats.total}</p>
      <p>Completed: {stats.completed}</p>
    </div>
  );
}
```

### Go Client

```go
package main

import (
    "context"
    "fmt"
    "log"

    client "path/to/opensdk/go"
)

func main() {
    ctx := context.Background()

    // Create API client
    api := client.NewAPIClient(
        "ws://localhost:8000/connection/websocket",
        "your-jwt-token",
        "user-123",
    )

    // Connect
    if err := api.Connect(ctx); err != nil {
        log.Fatal(err)
    }
    defer api.Disconnect()

    // Call RPC method
    result, err := api.TasksGetStats(ctx, client.TaskStatsParams{
        UserId:           "user-123",
        IncludeCompleted: true,
    })
    if err != nil {
        log.Fatal(err)
    }

    fmt.Printf("Total: %d, Completed: %d\n", result.Total, result.Completed)
}
```

## Authentication

### Generating JWT Tokens

Django-CFG provides JWT token generation:

```python
# Django view
from django_cfg.apps.centrifugo.auth import generate_centrifugo_token

def get_websocket_token(request):
    token = generate_centrifugo_token(
        user_id=str(request.user.id),
        expiration_hours=24
    )
    return JsonResponse({"token": token})
```

### Frontend Token Usage

```typescript
// Fetch token from backend
const response = await fetch('/api/websocket/token');
const { token } = await response.json();

// Use in RPC client
const rpc = new CentrifugoRPCClient(
  'ws://localhost:8000/connection/websocket',
  token,  // ← JWT token from backend
  'user-123'
);
```

## Error Handling

### TypeScript

```typescript
try {
  const result = await api.tasksGetStats(params);
  console.log('Success:', result);
} catch (error) {
  if (error.code) {
    console.error(`RPC Error ${error.code}: ${error.message}`);
  } else {
    console.error('Connection error:', error);
  }
}
```

### Python

```python
try:
    result = await api.tasks_get_stats(params)
except ValueError as e:
    print(f"Validation error: {e}")
except ConnectionError as e:
    print(f"Connection error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

### Go

```go
result, err := api.TasksGetStats(ctx, params)
if err != nil {
    if rpcErr, ok := err.(*client.RPCError); ok {
        log.Printf("RPC error %d: %s", rpcErr.Code, rpcErr.Message)
    } else {
        log.Printf("Connection error: %v", err)
    }
    return
}
```

## React Integration

### Custom Hook

```typescript
// hooks/useCentrifugo.ts
import { useEffect, useState, useRef } from 'react';
import { CentrifugoRPCClient, APIClient } from '../opensdk/typescript';

export function useCentrifugo(url: string, token: string, userId: string) {
  const [api, setApi] = useState<APIClient | null>(null);
  const [connected, setConnected] = useState(false);
  const rpcRef = useRef<CentrifugoRPCClient | null>(null);

  useEffect(() => {
    const rpc = new CentrifugoRPCClient(url, token, userId);

    rpc.connect().then(() => {
      const apiClient = new APIClient(rpc);
      setApi(apiClient);
      setConnected(true);
      rpcRef.current = rpc;
    });

    return () => {
      rpc.disconnect();
    };
  }, [url, token, userId]);

  return { api, connected };
}
```

### Usage in Component

```typescript
function TaskDashboard() {
  const { api, connected } = useCentrifugo(
    'ws://localhost:8000/connection/websocket',
    authToken,
    userId
  );

  const [stats, setStats] = useState(null);

  useEffect(() => {
    if (!api || !connected) return;

    api.tasksGetStats({ user_id: userId })
      .then(setStats)
      .catch(console.error);
  }, [api, connected, userId]);

  // ... render stats
}
```

## Next Steps

- **[Architecture](./architecture.md)** - Understand how it works
- **[API Reference](./api-reference.md)** - Complete API docs

---

:::tip[Frontend Best Practices]
- ✅ Always handle connection errors
- ✅ Disconnect clients on component unmount
- ✅ Use context/hooks for shared connections
- ✅ Implement reconnection logic
- ✅ Validate tokens before connecting
:::
