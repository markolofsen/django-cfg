# Django RPC Module - WebSocket Integration for Django-CFG

## Overview

This module provides type-safe, synchronous RPC communication between Django applications and external WebSocket servers using Redis as the IPC backbone.

**Key Features:**
- ✅ 100% synchronous (no async/await in Django)
- ✅ Type-safe with Pydantic 2 models
- ✅ Automatic connection pooling
- ✅ Reliable delivery via Redis Streams
- ✅ Fast responses via Redis Lists + BLPOP
- ✅ Complete isolation from async complexity

---

## Module Structure

```
django_cfg/
├── models/websocket/          # Pydantic 2 models
│   ├── __init__.py
│   ├── base.py               # Base RPC message models
│   ├── rpc.py                # Generic RPC request/response
│   ├── notifications.py      # Notification models
│   ├── broadcast.py          # Broadcast models
│   ├── errors.py             # Error models
│   └── connections.py        # Connection state models
│
├── modules/django_rpc/        # RPC client module
│   ├── __init__.py
│   ├── client.py             # WebSocketRPCClient
│   ├── config.py             # WebSocketRPCConfig
│   ├── exceptions.py         # Custom exceptions
│   └── README.md             # This file
│
└── tests/websocket/           # Unit tests
    ├── __init__.py
    ├── test_models.py        # Model tests
    └── test_client.py        # Client tests
```

---

## Quick Start

### 1. Configure in Django Settings

```python
# settings.py
from django_cfg import DjangoConfig
from django_cfg.modules.django_rpc import WebSocketRPCConfig

config = DjangoConfig(
    websocket_rpc=WebSocketRPCConfig(
        enabled=True,
        redis_url="redis://localhost:6379/2",  # Dedicated Redis DB
        rpc_timeout=30,
    )
)

# Generated settings
WEBSOCKET_RPC = config.websocket_rpc.to_django_settings()["WEBSOCKET_RPC"]
```

### 2. Use RPC Client

```python
# views.py
from django_cfg.modules.django_rpc import get_rpc_client
from django_cfg.models.websocket import (
    NotificationRequest,
    NotificationResponse,
    NotificationPriority,
)

rpc = get_rpc_client()

def notify_user(request, user_id):
    """Send notification to user via WebSocket."""

    result: NotificationResponse = rpc.call(
        method="send_notification",
        params=NotificationRequest(
            user_id=user_id,
            notification_type="order_update",
            title="Order Confirmed",
            message="Your order #12345 has been confirmed",
            priority=NotificationPriority.HIGH,
        ),
        result_model=NotificationResponse,
        timeout=10,
    )

    return JsonResponse({
        "delivered": result.delivered,
        "user_connected": result.user_connected,
    })
```

---

## API Reference

### WebSocketRPCClient

Main RPC client for synchronous communication.

#### Methods

##### `call(method, params, result_model, timeout=None)`

Make synchronous RPC call to WebSocket server.

**Args:**
- `method` (str): RPC method name
- `params` (BaseModel): Pydantic model with parameters
- `result_model` (Type[BaseModel]): Expected result model class
- `timeout` (int, optional): Timeout override in seconds

**Returns:**
- Pydantic result model instance

**Raises:**
- `RPCTimeoutError`: If timeout exceeded
- `RPCRemoteError`: If remote execution failed
- `ValidationError`: If response doesn't match result_model

**Example:**
```python
result = rpc.call(
    method="echo",
    params=EchoParams(message="Hello"),
    result_model=EchoResult,
    timeout=10
)
```

##### `fire_and_forget(method, params)`

Send RPC request without waiting for response.

**Args:**
- `method` (str): RPC method name
- `params` (BaseModel): Pydantic model with parameters

**Returns:**
- str: Message ID from Redis Stream

**Example:**
```python
message_id = rpc.fire_and_forget(
    method="log_event",
    params=EventLog(event="user_login", user_id="123")
)
```

##### `broadcast(channel, message)`

Broadcast message via Redis Pub/Sub.

**Args:**
- `channel` (str): Redis channel name
- `message` (BaseModel): Pydantic model to broadcast

**Returns:**
- int: Number of subscribers that received message

**Example:**
```python
subscribers = rpc.broadcast(
    channel="notifications:broadcast",
    message=BroadcastRequest(
        target="all",
        event_type="system_update",
        payload={"version": "2.0"}
    )
)
```

##### `health_check(timeout=5)`

Check if RPC system is healthy.

**Args:**
- `timeout` (int): Health check timeout in seconds

**Returns:**
- bool: True if healthy, False otherwise

**Example:**
```python
if rpc.health_check():
    print("RPC system healthy")
```

---

## Pydantic Models

All communication uses type-safe Pydantic 2 models:

### Base Models

- `BaseRPCMessage` - Base for all messages
- `BaseRPCRequest` - Base for RPC requests
- `BaseRPCResponse` - Base for RPC responses

### RPC Models

- `RPCRequest[TParams]` - Generic typed request
- `RPCResponse[TResult]` - Generic typed response

### Notification Models

- `NotificationRequest` - Send notification to user
- `NotificationResponse` - Notification delivery result
- `BatchNotificationRequest` - Send to multiple users
- `BatchNotificationResponse` - Batch delivery results

### Broadcast Models

- `BroadcastRequest` - Broadcast to multiple users
- `BroadcastResponse` - Broadcast delivery results

### Error Models

- `RPCError` - Structured error information
- `RPCValidationError` - Validation error details
- `TimeoutError` - Timeout error
- `UserNotConnectedError` - User offline error
- `RateLimitError` - Rate limit exceeded

### Connection Models

- `ConnectionInfo` - WebSocket connection details
- `ConnectionStateUpdate` - Update connection state

---

## Configuration Options

### WebSocketRPCConfig

```python
WebSocketRPCConfig(
    # Module settings
    enabled: bool = False,
    module_name: str = "websocket_rpc",

    # Redis settings
    redis_url: str = "redis://localhost:6379/2",
    redis_max_connections: int = 50,

    # RPC settings
    rpc_timeout: int = 30,
    request_stream: str = "stream:requests",
    consumer_group: str = "rpc_group",
    stream_maxlen: int = 10000,

    # Response settings
    response_key_prefix: str = "list:response:",
    response_key_ttl: int = 60,

    # Bridge listener settings
    enable_bridge: bool = False,
    bridge_consumer_name: str = "django_bridge",
    bridge_stream: str = "stream:django:requests",

    # WebSocket server settings
    websocket_url: str = "ws://localhost:8765",

    # Logging settings
    log_rpc_calls: bool = False,
    log_level: str = "INFO",
)
```

---

## Integration with Dramatiq

The RPC client works seamlessly with Dramatiq for background tasks:

```python
# tasks.py
import dramatiq
from django_cfg.modules.django_rpc import get_rpc_client
from django_cfg.models.websocket import NotificationRequest, NotificationResponse

rpc = get_rpc_client()

@dramatiq.actor(queue_name="notifications", max_retries=3)
def send_async_notification(user_id: str, message: str):
    """Send notification asynchronously via Dramatiq."""

    result: NotificationResponse = rpc.call(
        method="send_notification",
        params=NotificationRequest(
            user_id=user_id,
            notification_type="async_event",
            title="Event Notification",
            message=message,
        ),
        result_model=NotificationResponse,
    )

    return result.model_dump()
```

---

## Error Handling

### Timeout Errors

```python
from django_cfg.modules.django_rpc import RPCTimeoutError

try:
    result = rpc.call(method="slow", params=..., timeout=5)
except RPCTimeoutError as e:
    logger.warning(f"RPC timeout: {e.method} after {e.timeout_seconds}s")
    # Handle timeout (retry, fallback, etc.)
```

### Remote Errors

```python
from django_cfg.modules.django_rpc import RPCRemoteError
from django_cfg.models.websocket import RPCErrorCode

try:
    result = rpc.call(method="...", params=...)
except RPCRemoteError as e:
    if e.error.code == RPCErrorCode.USER_NOT_CONNECTED:
        # Queue for offline delivery
        queue_for_later(params)
    elif e.is_retryable:
        # Retry after delay
        time.sleep(e.retry_after or 5)
        result = rpc.call(...)  # Retry
    else:
        # Non-retryable error
        raise
```

---

## Testing

Run unit tests:

```bash
# Test models
pytest django_cfg/tests/websocket/test_models.py -v

# Test RPC client
pytest django_cfg/tests/websocket/test_client.py -v

# Test all
pytest django_cfg/tests/websocket/ -v
```

---

## File Size Compliance

All files follow django-cfg standards:

| File | Lines | Status |
|------|-------|--------|
| `base.py` | ~150 | ✅ |
| `rpc.py` | ~200 | ✅ |
| `notifications.py` | ~350 | ✅ |
| `broadcast.py` | ~250 | ✅ |
| `errors.py` | ~250 | ✅ |
| `connections.py` | ~200 | ✅ |
| `config.py` | ~250 | ✅ |
| `client.py` | ~650 | ✅ |
| `exceptions.py` | ~150 | ✅ |

**Total: 9 files, ~2450 lines (avg ~272 lines/file)**

---

## See Also

- [Architecture Documentation](/@docs/websocket/architecture/overview.md)
- [RPC Flow Diagrams](/@docs/websocket/diagrams/rpc-flow.md)
- [Implementation Guide](/@docs/websocket/IMPLEMENTATION_GUIDE.md)

---

**Status:** ✅ Production Ready
**Django-CFG Version:** 2.0+
**Python Version:** 3.10+
