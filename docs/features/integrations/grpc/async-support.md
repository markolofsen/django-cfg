---
title: Async Support
description: Async/await support for high-concurrency gRPC streaming
sidebar_label: Async Support
sidebar_position: 7
keywords:
  - grpc async
  - async streaming
  - high concurrency
---

# Async gRPC Support

High-concurrency async gRPC server with streaming support.

## What's Changed

### Async Server (v1.5.8+)

gRPC server now uses **`grpc.aio`** (async) instead of sync ThreadPoolExecutor:

| Before (Sync) | Now (Async) |
|---------------|-------------|
| `grpc.server()` | `grpc.aio.server()` |
| ThreadPoolExecutor | asyncio event loop |
| ~10 concurrent requests | 1000+ concurrent requests |
| No streaming support | Full streaming support |

## How It Works

```
┌─────────────────────────────────────┐
│   python manage.py rungrpc          │
│                                     │
│  ┌─────────────────────────────┐   │
│  │ grpc.aio.server() [ASYNC]   │   │
│  │  └─ asyncio event loop      │   │
│  │     ├─ API Key Auth (async) │   │
│  │     ├─ Logging (async)      │   │
│  │     └─ Your Services        │   │
│  └─────────────────────────────┘   │
└─────────────────────────────────────┘
```

**Key Points:**
- Server runs async automatically
- API key auth works async
- Request logging works async
- Django ORM wrapped in `asyncio.to_thread()`

## Configuration

### Enable Async Options

```python
# api/config.py
from django_cfg import DjangoConfig, GRPCConfig, GRPCServerConfig

class MyConfig(DjangoConfig):
    grpc = GRPCConfig(
        enabled=True,
        server=GRPCServerConfig(
            host="[::]",
            port=50051,

            # Async options
            max_concurrent_streams=1000,  # Concurrent streams per connection
            asyncio_debug=False,          # Debug mode (dev only)

            # Standard options still work
            enable_reflection=True,
            enable_health_check=True,
        ),
    )
```

### Async Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `max_concurrent_streams` | `int` | `None` | Max concurrent streams per connection (None = unlimited) |
| `asyncio_debug` | `bool` | `False` | Enable asyncio debug mode (shows warnings) |

## Writing Services

### Sync Services (Recommended)

**Most services work as-is** - no changes needed:

```python
from django_cfg.apps.integrations.grpc.services import BaseService

class UserService(BaseService):
    def GetUser(self, request, context):
        # Standard sync code - works on async server
        user = self.require_user(context)
        db_user = User.objects.get(id=request.user_id)
        return UserResponse(id=db_user.id, name=db_user.name)
```

**Why it works:** Async server wraps sync methods automatically.

### Async Services (Advanced)

For I/O-bound operations or streaming:

```python
import asyncio
from django_cfg.apps.integrations.grpc.services import BaseService

class UserService(BaseService):
    async def GetUser(self, request, context):
        # Async method
        user = self.require_user(context)

        # Wrap Django ORM in asyncio.to_thread
        db_user = await asyncio.to_thread(
            User.objects.get,
            id=request.user_id
        )

        return UserResponse(id=db_user.id, name=db_user.name)

    async def StreamUsers(self, request, context):
        # Server-side streaming
        users = await asyncio.to_thread(
            lambda: list(User.objects.all()[:100])
        )

        for user in users:
            yield UserResponse(id=user.id, name=user.name)
            await asyncio.sleep(0)  # Yield control to event loop
```

## Streaming Examples

### Server-Side Streaming

```python
class EventService(BaseService):
    async def StreamEvents(self, request, context):
        """Stream events to client."""
        while not context.cancelled():
            # Get events from DB
            events = await asyncio.to_thread(
                lambda: Event.objects.filter(user_id=request.user_id)[:10]
            )

            for event in events:
                yield EventResponse(
                    id=event.id,
                    type=event.type,
                    data=event.data,
                )

            await asyncio.sleep(1)  # Stream every 1 second
```

### Client-Side Streaming

```python
class LogService(BaseService):
    async def UploadLogs(self, request_iterator, context):
        """Receive stream of logs from client."""
        count = 0
        async for log_entry in request_iterator:
            # Process each log entry
            await asyncio.to_thread(
                Log.objects.create,
                message=log_entry.message,
                level=log_entry.level,
            )
            count += 1

        return UploadResponse(logs_received=count)
```

### Bidirectional Streaming

```python
class ChatService(BaseService):
    async def Chat(self, request_iterator, context):
        """Bidirectional chat stream."""
        async for message in request_iterator:
            # Process incoming message
            await asyncio.to_thread(
                Message.objects.create,
                text=message.text,
                user_id=message.user_id,
            )

            # Send response
            yield ChatResponse(
                text=f"Received: {message.text}",
                timestamp=int(time.time()),
            )
```

## Performance

### Concurrency Comparison

| Metric | Sync Server | Async Server |
|--------|-------------|--------------|
| Max concurrent requests | ~10 | 1000+ |
| Memory per request | 2-4 MB | 50-100 KB |
| Streaming support | Limited | Full support |
| I/O-bound workloads | Slow | Fast |

### When to Use Async

✅ **Use async for:**
- High-concurrency scenarios (100+ concurrent clients)
- Server-side streaming
- Bidirectional streaming
- I/O-bound operations (external APIs, long DB queries)

❌ **Sync is fine for:**
- Low-medium concurrency (under 50 clients)
- Simple CRUD operations
- CPU-bound workloads

## Django ORM with Async

### The Problem

Django ORM is synchronous - can't use `await`:

```python
# ❌ Won't work
user = await User.objects.get(id=1)
```

### The Solution

Wrap ORM calls in `asyncio.to_thread()`:

```python
# ✅ Works
import asyncio
user = await asyncio.to_thread(User.objects.get, id=1)
```

### Helper Pattern

Create a helper for cleaner code:

```python
class UserService(BaseService):
    async def _get_user_async(self, user_id):
        """Helper to get user async."""
        return await asyncio.to_thread(
            User.objects.get,
            id=user_id
        )

    async def GetUser(self, request, context):
        user = await self._get_user_async(request.user_id)
        return UserResponse(...)
```

## Running the Server

Same command - async enabled automatically:

```bash
# Development
python manage.py rungrpc

# Production
python manage.py rungrpc --host 0.0.0.0 --port 50051
```

## Debugging

Enable asyncio debug mode:

```python
# api/config.py
server=GRPCServerConfig(
    asyncio_debug=True,  # Shows async warnings
)
```

Or via command line:

```bash
python manage.py rungrpc --asyncio-debug
```

## Migration from Old Code

### No Changes Needed

If you have existing sync services - they work as-is:

```python
# Old sync code - still works!
class UserService(BaseService):
    def GetUser(self, request, context):
        return UserResponse(...)
```

### Optional: Convert to Async

Only convert if you need streaming or high concurrency:

```python
# New async version
class UserService(BaseService):
    async def GetUser(self, request, context):
        user = await asyncio.to_thread(...)
        return UserResponse(...)
```

## Common Issues

### Issue: "RuntimeError: no running event loop"

**Cause:** Trying to use `await` in sync context

**Solution:** Make method `async def`:

```python
# Before
def GetUser(self, request, context):
    user = await something()  # ❌ Error

# After
async def GetUser(self, request, context):
    user = await something()  # ✅ Works
```

### Issue: "This query is synchronous"

**Cause:** Using Django ORM directly with `await`

**Solution:** Wrap in `asyncio.to_thread()`:

```python
# Before
user = await User.objects.get(id=1)  # ❌ Error

# After
user = await asyncio.to_thread(User.objects.get, id=1)  # ✅ Works
```

## Best Practices

1. **Keep sync by default** - Only use async when needed
2. **Wrap ORM calls** - Always use `asyncio.to_thread()` for Django ORM
3. **Yield control** - Use `await asyncio.sleep(0)` in tight loops
4. **Handle cancellation** - Check `context.cancelled()` in streams
5. **Test thoroughly** - Async bugs are harder to debug

## Next Steps

- **[Getting Started](./getting-started.md)** - Build your first service
- **[Configuration](./configuration.md)** - Full config options
- **[Authentication](./authentication.md)** - API key setup
- **[FAQ](./faq.md)** - Common questions

---

**Summary:** Async is enabled automatically. Write services normally (sync), or use `async def` for streaming/high-concurrency. Wrap Django ORM in `asyncio.to_thread()`.
