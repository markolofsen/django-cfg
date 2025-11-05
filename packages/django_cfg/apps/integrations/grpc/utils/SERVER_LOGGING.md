# Server Lifecycle Logging Utilities

Reusable functions for logging server startup and shutdown with timestamps and uptime tracking.

**Uses Rich** for beautiful output with panels, tables, and colors! 🎨

## 📦 Functions

### `log_server_start()`

Logs server startup with timestamp and configuration.

```python
from django_cfg.apps.integrations.grpc.utils import log_server_start

start_time = log_server_start(
    logger,
    server_type="gRPC Server",       # Server type
    mode="Development",               # Production/Development
    hotreload_enabled=True,           # Is hotreload enabled?
    host="0.0.0.0",                   # Additional parameters
    port=50051
)
```

**Output (Rich Panel):**
```
╭────────────── 🚀 gRPC Server Starting ───────────────╮
│                                                      │
│  ⏰ Started at    2025-11-05 14:30:15               │
│  Mode            Development                        │
│  Hotreload       Enabled ⚡                          │
│  Host            0.0.0.0                            │
│  Port            50051                              │
│                                                      │
╰──────────────────────────────────────────────────────╯
⚠️  Hotreload active - connections may be dropped on code changes
```
(with green border and colors!)

**Returns:** `datetime` object of start time (for use in `log_server_shutdown`)

---

### `log_server_shutdown()`

Logs server shutdown with uptime calculation.

```python
from django_cfg.apps.integrations.grpc.utils import log_server_shutdown

log_server_shutdown(
    logger,
    start_time,                       # datetime from log_server_start()
    server_type="gRPC Server",
    reason="Hotreload triggered",     # Shutdown reason
    active_connections=5              # Additional parameters
)
```

**Output (Rich Panel):**
```
╭───────────── 🧹 Shutting down gRPC Server ──────────────╮
│                                                          │
│  📋 Reason            Hotreload triggered               │
│  ⏱️  Uptime            0h 2m 35s                         │
│  🕐 Stopped at        2025-11-05 14:32:50               │
│  Active Connections  5                                  │
│                                                          │
╰──────────────────────────────────────────────────────────╯
✅ Server shutdown complete
```
(with red border and colors!)

---

## 🎯 Complete Usage Example

```python
from django_cfg.apps.integrations.grpc.utils import (
    setup_streaming_logger,
    log_server_start,
    log_server_shutdown,
)

# Create logger
logger = setup_streaming_logger('my_server')

# Log server start
start_time = log_server_start(
    logger,
    server_type="WebSocket Server",
    mode="Production",
    hotreload_enabled=False,
    host="0.0.0.0",
    port=8000
)

try:
    # Server work...
    await server.serve_forever()
    shutdown_reason = "Normal termination"
except KeyboardInterrupt:
    shutdown_reason = "Keyboard interrupt"
finally:
    # Log server shutdown
    log_server_shutdown(
        logger,
        start_time,
        server_type="WebSocket Server",
        reason=shutdown_reason,
        total_connections=1250
    )
```

---

## 📊 Used in:

- ✅ `rungrpc` - gRPC server command
- ✅ Can be used for any servers (WebSocket, HTTP, etc.)

---

## 🔧 Parameters

### `log_server_start()`

| Parameter | Type | Required | Description |
|----------|-----|----------|-------------|
| `logger` | `logging.Logger` | ✅ Yes | Logger instance |
| `server_type` | `str` | ❌ No | Server type (default: "Server") |
| `mode` | `str` | ❌ No | Running mode (default: "Development") |
| `hotreload_enabled` | `bool` | ❌ No | Is hotreload enabled (default: False) |
| `use_rich` | `bool` | ❌ No | Use Rich for output (default: True) |
| `**extra_info` | `dict` | ❌ No | Additional key-value pairs to log |

### `log_server_shutdown()`

| Parameter | Type | Required | Description |
|----------|-----|----------|-------------|
| `logger` | `logging.Logger` | ✅ Yes | Logger instance |
| `start_time` | `datetime` | ✅ Yes | Start time from `log_server_start()` |
| `server_type` | `str` | ❌ No | Server type (default: "Server") |
| `reason` | `str` | ❌ No | Shutdown reason |
| `use_rich` | `bool` | ❌ No | Use Rich for output (default: True) |
| `**extra_info` | `dict` | ❌ No | Additional key-value pairs to log |

---

## 💡 Benefits

1. ✅ **DRY** - single code for all servers
2. ✅ **Consistency** - uniform log format
3. ✅ **Rich UI** - beautiful panels, tables, colors 🎨
4. ✅ **Uptime tracking** - automatic time calculation
5. ✅ **Flexible** - can add arbitrary parameters via `**extra_info`
6. ✅ **Hotreload aware** - special warning for hotreload mode
7. ✅ **Fallback** - works without Rich (if `use_rich=False`)

---

**Author:** django-cfg team
**Date:** 2025-11-05
