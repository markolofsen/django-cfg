# Centrifugo WebSocket RPC

> **Production-Ready Real-Time Messaging with Type-Safe Auto-Generated Clients**

Centrifugo integration provides a complete real-time WebSocket RPC solution with automatic type-safe client generation for Python, TypeScript, and Go.

## 🎯 What is Centrifugo?

[Centrifugo](https://centrifugal.dev/) is a scalable real-time messaging server that can handle **millions of concurrent connections**. Django-CFG provides seamless integration with:

- ✅ **Type-safe RPC handlers** using Pydantic models
- ✅ **Auto-generated clients** for Python, TypeScript, and Go
- ✅ **Correlation ID pattern** for request-response over pub/sub
- ✅ **Production-ready** with 99.9% less HTTP requests
- ✅ **Thin wrapper architecture** for minimal overhead

## 🚀 Quick Start

### 1. Enable Centrifugo in Configuration

```python
# config.py
from django_cfg import DjangoConfig, DjangoCfgCentrifugoConfig

class MyConfig(DjangoConfig):
    centrifugo: DjangoCfgCentrifugoConfig = DjangoCfgCentrifugoConfig(
        enabled=True,
        wrapper_url="http://localhost:8001",
        wrapper_api_key="your-api-key",
        centrifugo_url="ws://localhost:8000/connection/websocket",
        centrifugo_api_url="http://localhost:8000/api",
        centrifugo_api_key="your-centrifugo-api-key",
        centrifugo_token_hmac_secret="your-hmac-secret",
    )
```

### 2. Create RPC Handler

```python
# core/centrifugo_handlers.py
from pydantic import BaseModel, Field
from django_cfg.apps.centrifugo.decorators import websocket_rpc

class TaskStatsParams(BaseModel):
    user_id: str = Field(..., description="User ID")

class TaskStatsResult(BaseModel):
    total: int = Field(..., description="Total tasks")
    completed: int = Field(..., description="Completed tasks")

@websocket_rpc("tasks.get_stats")
async def get_task_stats(conn, params: TaskStatsParams) -> TaskStatsResult:
    """Get task statistics for a user."""
    # Your business logic here
    return TaskStatsResult(total=100, completed=75)
```

### 3. Register Handlers

```python
# core/apps.py
from django.apps import AppConfig

class CoreConfig(AppConfig):
    name = "core"

    def ready(self):
        # Import handlers to register them
        from . import centrifugo_handlers
```

### 4. Generate Clients

```bash
# Generate all clients (Python, TypeScript, Go)
python manage.py generate_centrifugo_clients --output ./opensdk --all

# Or use the integrated workflow
make api
```

### 5. Use Generated Clients

**Python:**
```python
from opensdk.python import CentrifugoRPCClient, APIClient

rpc = CentrifugoRPCClient('ws://...', 'token', 'user-123')
await rpc.connect()

api = APIClient(rpc)
result = await api.tasks_get_stats(TaskStatsParams(user_id='123'))
print(f"Tasks: {result.total}, Completed: {result.completed}")
```

**TypeScript:**
```typescript
import { CentrifugoRPCClient, APIClient } from './opensdk/typescript';

const rpc = new CentrifugoRPCClient('ws://...', 'token', 'user-123');
await rpc.connect();

const api = new APIClient(rpc);
const result = await api.tasksGetStats({ user_id: '123' });
console.log(`Tasks: ${result.total}, Completed: ${result.completed}`);
```

**Go:**
```go
import client "path/to/opensdk/go"

api := client.NewAPIClient("ws://...", "token", "user-123")
api.Connect(ctx)

result, err := api.TasksGetStats(ctx, client.TaskStatsParams{UserId: "123"})
fmt.Printf("Tasks: %d, Completed: %d\n", result.Total, result.Completed)
```

## 📊 Key Features

### Type Safety

- **Single Source of Truth**: Pydantic models define types for all languages
- **Compile-time Checking**: TypeScript and Go clients are fully typed
- **Runtime Validation**: Python clients validate with Pydantic

### Auto-Generated Clients

- **Python**: Async/await with Pydantic models
- **TypeScript**: Promise-based with interfaces
- **Go**: Context-aware with structs (**NO GitHub dependencies!**)

### Thin Wrapper Architecture

Two-layer design for minimal overhead:

1. **Base RPC Client**: Handles WebSocket, correlation IDs, pub/sub
2. **Typed API Client**: One type-safe method per RPC endpoint

### Production Ready

- ✅ **Scalable**: Handles millions of concurrent connections via Centrifugo
- ✅ **Reliable**: Correlation ID pattern ensures request-response matching
- ✅ **Observable**: Built-in logging and monitoring
- ✅ **Tested**: Comprehensive test coverage

## 📖 Documentation Sections

- **[Setup Guide](./setup.md)** - Installation and configuration
- **[Backend Guide](./backend-guide.md)** - Creating RPC handlers
- **[Client Generation](./client-generation.md)** - Generating type-safe clients
- **[Frontend Guide](./frontend-guide.md)** - Using clients in your frontend
- **[Architecture](./architecture.md)** - How it all works
- **[API Reference](./api-reference.md)** - Complete API documentation

## 🎓 Learn More

- [Centrifugo Official Docs](https://centrifugal.dev/)
- [Django-CFG Documentation](https://djangocfg.com/)

---

**Next Steps:**
- 📖 Read the [Setup Guide](./setup.md) for detailed installation
- 🔨 Follow the [Backend Guide](./backend-guide.md) to create your first handler
- 🚀 Check out [Client Generation](./client-generation.md) to generate clients
