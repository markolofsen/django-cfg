# RPC Logger Module

Universal logging solution for `django-ipc` server and clients.

## Features

✅ **Structured JSON Logging** - Machine-readable logs
✅ **Log Rotation** - Size and time-based rotation
✅ **Separate Log Files** - app, errors, rpc, performance
✅ **Correlation ID Tracking** - Track requests end-to-end
✅ **Auto RPC Logging** - Middleware for automatic logging
✅ **Performance Metrics** - Track RPC timing
✅ **Human-readable Console** - Color-coded terminal output

---

## Quick Start

### 1. Basic Setup

```python
from django_ipc.logger import RPCLogger, LoggerConfig

# Configure logger
config = LoggerConfig(
    log_dir="./logs",
    level="INFO",
    log_rpc_calls=True,
    log_errors=True,
)

# Create logger
logger = RPCLogger(config, name="my_rpc_server")

# Simple logging
logger.info("Server started")
logger.error("Connection failed", exc_info=True)
```

### 2. With MessageRouter

```python
from django_ipc.server import MessageRouter
from django_ipc.logger import RPCLogger, LoggerConfig

# Setup logger
logger = RPCLogger(LoggerConfig(log_dir="./logs"))

# Pass logger to router (auto-logging enabled!)
router = MessageRouter(
    connection_manager=connection_manager,
    logger=logger,  # ✅ All RPC calls logged automatically
)

# Register handlers as usual
@router.register("create_user")
async def create_user(conn, params):
    # Automatically logged: request, response, timing, errors
    return UserResult(...)
```

### 3. Manual RPC Logging

```python
# Log RPC request
logger.log_rpc_request(
    method="create_user",
    params={"username": "john"},
    correlation_id="abc-123",
    user_id="user_456",
)

# Log RPC response
logger.log_rpc_response(
    method="create_user",
    result={"user_id": "1"},
    correlation_id="abc-123",
    duration_ms=45.2,
    success=True,
)
```

---

## Configuration

```python
from django_ipc.logger import LoggerConfig, LogRotationConfig

config = LoggerConfig(
    # Directory
    log_dir="./logs",  # Where to save logs

    # Levels
    level="INFO",  # DEBUG, INFO, WARNING, ERROR, CRITICAL

    # What to log
    log_rpc_calls=True,       # All RPC calls
    log_errors=True,          # Separate error log
    log_performance=True,     # Performance metrics
    log_connections=True,     # WebSocket connections

    # Format
    use_json=True,            # JSON format for files
    include_timestamp=True,   # Include timestamps
    include_correlation_id=True,  # Track requests
    include_caller_info=False,    # File/line (slow)

    # Rotation
    rotation=LogRotationConfig(
        max_bytes=10 * 1024 * 1024,  # 10 MB
        backup_count=5,               # Keep 5 backups
    ),

    # Console
    console_output=True,      # Also log to console
    console_level="INFO",     # Console log level
)
```

---

## Log Files

After initialization, you'll have:

```
logs/
├── app.log         # All logs (JSON)
├── error.log       # Errors only (JSON)
├── rpc.log         # RPC calls only (JSON)
└── performance.log # Performance metrics (JSON)
```

### Example Log Entry (JSON)

```json
{
  "timestamp": "2025-10-04T12:34:56.789Z",
  "level": "INFO",
  "logger": "message_router",
  "message": "RPC Response: create_user (success)",
  "rpc_type": "response",
  "method": "create_user",
  "result": {"user_id": "123", "username": "john"},
  "correlation_id": "abc-123",
  "duration_ms": 45.2,
  "success": true
}
```

---

## Advanced Usage

### Performance Logging

```python
logger.log_performance(
    operation="database_query",
    duration_ms=125.5,
    query_type="SELECT",
    rows_returned=100,
)
```

### Connection Logging

```python
logger.log_connection(
    event="connect",
    connection_id=uuid4(),
    user_id="user_123",
    remote_addr="192.168.1.1",
)
```

### With Middleware Decorator

```python
from django_ipc.logger import auto_log_rpc

@auto_log_rpc(logger)
@router.register("create_user")
async def create_user(conn, params):
    # Automatically logged with timing!
    return UserResult(...)
```

---

## Client-Side Logging

Logger can be generated for TypeScript and Python clients:

### Python Client

```python
# Generated client includes RPCLogger
from clients.python import RPCClient, LoggerConfig

# Configure client logger
client = RPCClient.from_env()
client.setup_logger(LoggerConfig(
    log_dir="./client_logs",
    log_rpc_calls=True,
))

# All RPC calls logged automatically
await client.create_user(...)
```

### TypeScript Client

```typescript
// Generated client includes logger
import { RPCClient, LoggerConfig } from './clients/typescript';

const client = RPCClient.fromEnv();

// Configure client logger
client.setupLogger({
  logDir: './client_logs',
  logRPCCalls: true,
});

// All RPC calls logged automatically
await client.createUser(...);
```

---

## Log Rotation

Logs automatically rotate based on:

1. **Size** - When file exceeds `max_bytes` (default: 10 MB)
2. **Time** - Daily, weekly, etc. (optional)

Example rotation:
```
logs/
├── app.log          # Current log
├── app.log.1        # Yesterday
├── app.log.2        # 2 days ago
├── app.log.3        # 3 days ago
├── app.log.4        # 4 days ago
└── app.log.5        # 5 days ago (oldest)
```

Old logs automatically deleted (keeps `backup_count`).

---

## Performance

- **Structured JSON** - Fast parsing, easy analysis
- **Async-safe** - Thread-safe file operations
- **Minimal overhead** - < 1ms per log entry
- **Rotation** - Prevents disk space issues

---

## Integration

### With WebSocket Server

```python
from django_ipc.server import WebSocketServer
from django_ipc.logger import RPCLogger, LoggerConfig

logger = RPCLogger(LoggerConfig(log_dir="./logs"))

# Router with logger
router = MessageRouter(connection_manager, logger=logger)

# Server
server = WebSocketServer(
    host="0.0.0.0",
    port=8001,
    router=router,
)
```

### With RPC Bridge

```python
from django_ipc.bridge import RPCBridge
from django_ipc.logger import RPCLogger

logger = RPCLogger(LoggerConfig(log_dir="./logs"))

bridge = RPCBridge(
    redis_url="redis://localhost:6379/2",
    logger=logger,  # ✅ Bridge will log all RPC calls
)
```

---

## Examples

See [examples/logging_example.py](../../../examples/logging_example.py) for complete example.

---

## Architecture

```
RPCLogger
├── config.py         # LoggerConfig, LogRotationConfig
├── formatters.py     # JSONFormatter, HumanReadableFormatter
├── logger.py         # RPCLogger, filters
└── middleware.py     # LoggingMiddleware, auto_log_rpc
```

---

## API Reference

### LoggerConfig

```python
LoggerConfig(
    log_dir: str = "./logs",
    level: LogLevel = "INFO",
    log_rpc_calls: bool = True,
    log_errors: bool = True,
    log_performance: bool = True,
    log_connections: bool = True,
    use_json: bool = True,
    console_output: bool = True,
    rotation: LogRotationConfig = LogRotationConfig(),
)
```

### RPCLogger

```python
logger = RPCLogger(config, name="my_logger")

# Basic logging
logger.debug(msg, **kwargs)
logger.info(msg, **kwargs)
logger.warning(msg, **kwargs)
logger.error(msg, **kwargs)
logger.critical(msg, **kwargs)

# RPC logging
logger.log_rpc_request(method, params, correlation_id, ...)
logger.log_rpc_response(method, result, correlation_id, duration_ms, ...)

# Performance
logger.log_performance(operation, duration_ms, **kwargs)

# Connection events
logger.log_connection(event, connection_id, user_id, **kwargs)
```

---

## Best Practices

1. **Use correlation IDs** - Track requests end-to-end
2. **Separate logs** - Enable all log types for easier debugging
3. **Set rotation** - Prevent disk space issues
4. **JSON format** - Easy parsing with tools like `jq`
5. **Console level** - Use INFO or WARNING for console
6. **Performance** - Monitor RPC timing to find bottlenecks

---

## Troubleshooting

**Q: Logs not appearing?**
A: Check `log_dir` permissions and `level` setting.

**Q: Too many log files?**
A: Reduce `backup_count` in rotation config.

**Q: Logs too verbose?**
A: Increase `level` to WARNING or ERROR.

**Q: Need caller info (file/line)?**
A: Set `include_caller_info=True` (has performance overhead).

---

**Built for django-ipc** 📚
