# Architecture

Understanding the Centrifugo WebSocket RPC architecture and how all components work together.

## Overview

```
┌──────────────┐         WebSocket          ┌──────────────┐
│              │◄──────────────────────────►│              │
│   Frontend   │    Correlation ID Pattern  │  Centrifugo  │
│    Client    │                            │    Server    │
│              │                            │              │
└──────────────┘                            └──────┬───────┘
                                                   │
                                            pub/sub channels
                                                   │
                                            ┌──────▼───────┐
                                            │              │
                                            │    Django    │
                                            │   Handlers   │
                                            │              │
                                            └──────────────┘
```

## Core Components

### 1. Pydantic Models (Single Source of Truth)

All types are defined once using Pydantic:

```python
class TaskStatsParams(BaseModel):
    user_id: str = Field(..., description="User ID")

class TaskStatsResult(BaseModel):
    total: int = Field(..., description="Total tasks")
```

These models drive:
- ✅ Runtime validation (Python)
- ✅ Code generation (TypeScript, Go)
- ✅ API documentation
- ✅ Type safety across all languages

### 2. @websocket_rpc Decorator

Registers handlers with the router:

```python
@websocket_rpc("tasks.get_stats")
async def get_task_stats(conn, params: TaskStatsParams) -> TaskStatsResult:
    return TaskStatsResult(total=100)
```

**What it does:**
1. Extracts type hints (Pydantic models)
2. Registers with MessageRouter (runtime)
3. Registers with RPCRegistry (codegen)
4. Validates async handler
5. Stores docstring and metadata

### 3. MessageRouter (Runtime)

Routes incoming RPC calls to handlers:

```python
router = MessageRouter()

# Decorator registers handler
router.register_handler("tasks.get_stats", handler_func)

# Runtime call
result = await router.handle_message("tasks.get_stats", params)
```

### 4. Code Generators

Generate clients from registered handlers:

**Discovery:**
```python
methods = discover_rpc_methods_from_router(router)
# Returns list of RPCMethodInfo with:
# - method name
# - params model
# - result model
# - docstring
```

**Generation:**
```python
# Python
generator = PythonThinGenerator(methods)
generator.generate(output_dir)

# TypeScript
generator = TypeScriptThinGenerator(methods)
generator.generate(output_dir)

# Go
generator = GoThinGenerator(methods)
generator.generate(output_dir)
```

## Thin Wrapper Pattern

### Two-Layer Architecture

**Layer 1: Base RPC Client**
- Handles WebSocket connection
- Implements correlation ID pattern
- Manages pub/sub subscriptions
- Matches responses

```python
# Base layer (generic RPC)
class CentrifugoRPCClient:
    async def call(self, method: str, params: dict) -> dict:
        correlation_id = generate_uuid()
        await self.publish("rpc.requests", {
            "method": method,
            "params": params,
            "correlation_id": correlation_id,
            "reply_to": f"user#{self.user_id}"
        })
        return await self.wait_for_response(correlation_id)
```

**Layer 2: Typed API Client**
- Type-safe methods
- One method per RPC endpoint
- Thin wrapper (no business logic)

```python
# Typed layer (specific methods)
class APIClient:
    async def tasks_get_stats(
        self,
        params: TaskStatsParams
    ) -> TaskStatsResult:
        result = await self.rpc.call(
            "tasks.get_stats",
            params.model_dump()
        )
        return TaskStatsResult(**result)
```

### Benefits

- ✅ **Small code size** - Thin wrappers, not fat SDKs
- ✅ **Maintainability** - Separation of concerns
- ✅ **Flexibility** - Easy to extend base client
- ✅ **Type safety** - Full typing at API layer

## Correlation ID Pattern

Request-response over pub/sub:

```
1. Client generates correlation_id = "uuid-123"
   ↓
2. Client publishes to "rpc.requests":
   {
     method: "tasks.get_stats",
     params: {...},
     correlation_id: "uuid-123",
     reply_to: "user#456"
   }
   ↓
3. Server receives message on "rpc.requests"
   ↓
4. Server calls handler: get_task_stats(params)
   ↓
5. Server publishes to "user#456":
   {
     correlation_id: "uuid-123",
     result: {...}
   }
   ↓
6. Client receives on "user#456"
   ↓
7. Client matches by correlation_id
   ↓
8. Client returns result to caller
```

### Implementation

**Client Side:**
```typescript
private pendingCalls = new Map<string, (result: any) => void>();

async call(method: string, params: any): Promise<any> {
  const correlationId = generateUUID();

  // Create promise
  const promise = new Promise((resolve) => {
    this.pendingCalls.set(correlationId, resolve);
  });

  // Publish request
  await this.client.publish('rpc.requests', {
    method,
    params,
    correlation_id: correlationId,
    reply_to: `user#${this.userId}`
  });

  return promise;
}

private handleResponse(message: any) {
  const correlationId = message.correlation_id;
  const callback = this.pendingCalls.get(correlationId);

  if (callback) {
    callback(message.result);
    this.pendingCalls.delete(correlationId);
  }
}
```

**Server Side:**
```python
async def handle_rpc_request(message):
    method = message["method"]
    params = message["params"]
    correlation_id = message["correlation_id"]
    reply_to = message["reply_to"]

    # Call handler
    result = await router.handle_message(method, params)

    # Publish response
    await centrifugo.publish(reply_to, {
        "correlation_id": correlation_id,
        "result": result
    })
```

## Type Conversion System

### Pydantic → TypeScript

```python
# Type converter
def pydantic_to_typescript(field_type):
    if field_type == str:
        return "string"
    if field_type == int or field_type == float:
        return "number"
    if field_type == bool:
        return "boolean"
    if is_list(field_type):
        inner = get_args(field_type)[0]
        return f"{pydantic_to_typescript(inner)}[]"
    if is_optional(field_type):
        inner = get_args(field_type)[0]
        return f"{pydantic_to_typescript(inner)} | null"
    if is_basemodel(field_type):
        return field_type.__name__  # Interface name
```

### Pydantic → Go

```python
def pydantic_to_go(field_type):
    if field_type == str:
        return "string"
    if field_type == int:
        return "int64"
    if field_type == float:
        return "float64"
    if field_type == bool:
        return "bool"
    if is_list(field_type):
        inner = get_args(field_type)[0]
        return f"[]{pydantic_to_go(inner)}"
    if is_optional(field_type):
        inner = get_args(field_type)[0]
        return f"*{pydantic_to_go(inner)}"  # Pointer
    if is_basemodel(field_type):
        return field_type.__name__  # Struct name
```

## Scalability

### Horizontal Scaling

Centrifugo supports millions of concurrent connections:

```
┌─────────┐     ┌─────────┐     ┌─────────┐
│ Client  │     │ Client  │     │ Client  │
│ 1-100k  │     │ 100k+   │     │ 200k+   │
└────┬────┘     └────┬────┘     └────┬────┘
     │               │               │
     ▼               ▼               ▼
┌─────────────────────────────────────────┐
│         Load Balancer (nginx)           │
└─────────┬───────────────────┬───────────┘
          │                   │
     ┌────▼─────┐       ┌────▼─────┐
     │ Centri 1 │       │ Centri 2 │
     └────┬─────┘       └────┬─────┘
          │                   │
          └─────────┬─────────┘
                    │
              ┌─────▼──────┐
              │   Django   │
              │  Handlers  │
              └────────────┘
```

### Redis Broker

Centrifugo uses Redis for pub/sub across instances:

```yaml
# centrifugo.json
{
  "engine": "redis",
  "redis_address": "redis://localhost:6379"
}
```

## Next Steps

- **[API Reference](./api-reference.md)** - Complete API documentation
- **[Setup Guide](./setup.md)** - Configuration details
