# WebSocket Consumers

Background consumers that process events from Redis Streams.

---

## Overview

This package contains two Redis Streams consumers that run as background tasks:

1. **File Watcher Consumer** - Broadcasts file change events to WebSocket clients
2. **AI Command Consumer** - Routes AI commands to CLI manager services (**Router Replacement**)

---

## File Watcher Consumer

**Purpose:** Consumes file change events from the File Watcher Service and broadcasts them to workspace-specific WebSocket rooms.

**Architecture:**
```
File Watcher (Node.js)
  ↓ Redis XADD
Redis Streams (stream:file-events)
  ↓ XREADGROUP
File Watcher Consumer (Python)
  ↓ broadcast_to_room()
WebSocket Clients (workspace:{id} room)
  ↓
Frontend UI updates
```

---

## AI Command Consumer

**Purpose:** Consumes AI commands from Django and routes them to service-specific CLI manager streams. **Replaces the need for a standalone Router service.**

**Architecture:**
```
Django (ai_agents app)
  ↓ Redis XADD
Redis Streams (stream:ai-commands)
  ↓ XREADGROUP
AI Command Consumer (Python) ← ROUTER REPLACEMENT!
  ↓ Redis XADD (route to service stream)
Redis Streams (stream:{service}-commands)
  ↓ XREADGROUP
CLI Manager Services (claude, cursor, mcp)
  ↓
Execute CLI commands & return results
```

**Why not a separate Router?**
- django-ipc already has Redis Streams infrastructure (FileWatcherConsumer)
- AICommandConsumer uses the exact same pattern (~100 LOC)
- Reduces deployment from 12 to 11 containers
- Simpler monitoring (one less log source)
- Shared Redis connection pool
- Same error handling, retry logic, graceful shutdown

**Routing Logic:**
```python
# Input: stream:ai-commands
{
  "service": "claude",  # or "cursor" or "mcp"
  "session_id": "session-123",
  "workspace_path": "/workspaces/my-project",
  "message": "Help me debug this code",
  "context": {"file": "main.py", "line": 42},
  "timestamp": "2025-10-06T01:00:00Z"
}

# Output: stream:claude-commands (routed based on service field)
# Same payload, routed to service-specific stream
```

**Supported Services:**
- `claude` → `stream:claude-commands` → cli-manager-claude
- `cursor` → `stream:cursor-commands` → cli-manager-cursor
- `mcp` → `stream:mcp-commands` → mcp-server

**Dead Letter Queue:**
- Invalid commands (validation errors) → `stream:ai-commands-dlq`
- Processing errors (temporary failures) → retry (no ACK)

---

## Features

Both consumers share the same Redis Streams infrastructure:

### ✅ Redis Streams Consumer
- **XREADGROUP**: Reliable consumption with consumer groups
- **File Watcher Consumer Group**: `websocket-consumers`
- **AI Command Consumer Group**: `websocket-router`
- **Consumer Name**: `websocket-1` (can scale to multiple consumers)
- **Batch Reading**: 10 events per iteration
- **Block Time**: File Watcher: 5s, AI Command: 1s

### ✅ Gzip Decompression
- Automatically detects compressed batches
- Base64 decode → Gzip decompress
- Falls back to uncompressed JSON

### ✅ Event Broadcasting
- Workspace-based routing: `workspace:{id}` rooms
- Preserves complete event structure (nested)
- Real-time delivery to connected clients

### ✅ Error Handling
- Validation errors → ACK + log (avoid reprocessing)
- Processing errors → No ACK (will retry)
- Graceful shutdown on SIGINT/SIGTERM

---

## Event Flow

### 1. File Change Detected
```typescript
// File Watcher Service (TypeScript)
const event: FileEvent = {
  event_id: "evt-123",
  timestamp: "2025-10-06T01:00:00Z",
  workspace: { id: "ws-abc", name: "My Project" },
  file: {
    path: "src/main.py",
    event_type: "modify",
  },
  change: {
    type: "diff",
    diff: "@@ -10,3 +10,4 @@\n+ print('hello')",
  },
  git: {
    branch: "main",
    commit: "abc123",
  },
};
```

### 2. Batched & Published to Redis
```typescript
// Batch Manager
const batch: BatchEvent = {
  batch_id: "batch-456",
  timestamp: "2025-10-06T01:00:01Z",
  batch_count: 1,
  events: [event],
};

// Redis Streams
await redis.xadd("stream:file-events", "*", {
  data: JSON.stringify(batch),  // or gzip + base64
  compressed: "false",  // or "true"
  batch_id: batch.batch_id,
  batch_count: "1",
});
```

### 3. Consumer Reads from Stream
```python
# File Watcher Consumer (Python)
messages = await redis.xreadgroup(
    groupname="websocket-consumers",
    consumername="websocket-1",
    streams={"stream:file-events": ">"},
    count=10,
    block=5000,
)

for message_id, data in messages:
    batch = BatchEvent.model_validate_json(data["data"])
    for event in batch.events:
        await broadcast_event(event)
    await redis.xack("stream:file-events", "websocket-consumers", message_id)
```

### 4. Broadcast to WebSocket Room
```python
# Broadcast to workspace:{id} room
await connection_manager.broadcast_to_room(
    room="workspace:ws-abc",
    message={
        "type": "file.changed",
        "data": {
            "event_id": "evt-123",
            "workspace": {"id": "ws-abc", "name": "My Project"},
            "file": {"path": "src/main.py", "event_type": "modify"},
            "change": {"type": "diff", "diff": "@@ -10,3 +10,4 @@\n+ print('hello')"},
            "git": {"branch": "main", "commit": "abc123"},
        },
    },
)
```

### 5. Frontend Receives Update
```javascript
// WebSocket Client (Frontend)
socket.on("file.changed", (data) => {
  console.log(`File ${data.file.path} changed in workspace ${data.workspace.id}`);
  // Update file explorer, show diff, etc.
});
```

---

## Configuration

### Environment Variables

**Redis Connection:**
```bash
REDIS_URL=redis://localhost:6379/2  # Shared Redis for both consumers
```

### Consumer Settings (in main.py)

**File Watcher Consumer:**
```python
stream_name="stream:file-events"       # Redis Stream name
consumer_group="websocket-consumers"   # Consumer group
consumer_name="websocket-1"            # This consumer's name
batch_size=10                          # Max events per read
block_ms=5000                          # Block time (5s)
```

**AI Command Consumer:**
```python
stream_name="stream:ai-commands"       # Redis Stream name
consumer_group="websocket-router"      # Consumer group (Router replacement)
consumer_name="websocket-1"            # This consumer's name
batch_size=10                          # Max commands per read
block_ms=1000                          # Block time (1s, faster routing)
```

---

## Monitoring

### Consumer Logs

**File Watcher Consumer:**
```
🚀 Starting File Watcher Consumer
📡 Stream: stream:file-events
👥 Consumer Group: websocket-consumers
🏷️  Consumer Name: websocket-1

📨 Received batch: batch-456 | Events: 1 | Compressed: false
📡 Broadcast file event: modify | src/main.py → 3 clients
✅ ACK: 1728177601000-0
```

**AI Command Consumer:**
```
🚀 Starting AI Command Consumer (Router Replacement)
📡 Stream: stream:ai-commands
👥 Consumer Group: websocket-router
🏷️  Consumer Name: websocket-1

✅ Routed claude command 17281776... → stream:claude-commands
✅ ACK: 1728177601000-0
```

### Health Check

**File Watcher Consumer:**
```python
# Check consumer group status
await redis.xinfo_groups("stream:file-events")
# Returns: [{'name': 'websocket-consumers', 'consumers': 1, 'pending': 0, ...}]

# Check pending messages
await redis.xpending("stream:file-events", "websocket-consumers")
```

**AI Command Consumer:**
```python
# Check consumer group status
await redis.xinfo_groups("stream:ai-commands")
# Returns: [{'name': 'websocket-router', 'consumers': 1, 'pending': 0, ...}]

# Check pending commands
await redis.xpending("stream:ai-commands", "websocket-router")

# Check DLQ for invalid commands
await redis.xlen("stream:ai-commands-dlq")
```

---

## Scaling

Both consumers support horizontal scaling using Redis Streams Consumer Groups:

**Horizontal Scaling:**
- Run multiple WebSocket servers with unique `consumer_name`:
  ```python
  consumer_name="websocket-1"  # Server 1
  consumer_name="websocket-2"  # Server 2
  consumer_name="websocket-3"  # Server 3
  ```
- Redis Streams automatically distributes messages across consumers
- Each consumer processes different events/commands (load balancing)
- File events AND AI commands are load balanced independently

**Vertical Scaling:**
- Increase `batch_size` for higher throughput
- Decrease `block_ms` for lower latency
- AI Command Consumer uses 1s block (faster routing) vs File Watcher 5s

---

## Error Handling

### Validation Errors
```python
try:
    batch = BatchEvent.model_validate_json(batch_json)
except ValidationError as e:
    logger.error(f"Validation error: {e}")
    await redis.xack(...)  # ACK to avoid infinite retry
```

**Why ACK?** Invalid data won't become valid on retry.

### Processing Errors
```python
try:
    await broadcast_event(event)
except Exception as e:
    logger.error(f"Processing error: {e}")
    # DON'T ACK - will be retried
```

**Why no ACK?** Temporary failures (e.g., connection issues) may resolve on retry.

---

## Testing

### Manual Test: Publish Event
```python
import asyncio
from redis.asyncio import Redis
import json

async def test_publish():
    redis = Redis.from_url("redis://localhost:6379/2")

    batch = {
        "batch_id": "test-batch",
        "timestamp": "2025-10-06T01:00:00Z",
        "batch_count": 1,
        "events": [{
            "event_id": "test-event",
            "timestamp": "2025-10-06T01:00:00Z",
            "workspace": {"id": "test-workspace"},
            "file": {"path": "test.py", "event_type": "create"},
            "change": {"type": "full_content", "content": "print('test')"},
        }],
    }

    await redis.xadd(
        "stream:file-events", "*",
        {"data": json.dumps(batch), "compressed": "false", "batch_id": "test-batch"},
    )
    print("✅ Event published")

asyncio.run(test_publish())
```

### Expected Output
```
📨 Received batch: test-batch | Events: 1 | Compressed: false
📡 Broadcast to workspace:test-workspace: create | test.py
✅ ACK: 1728177601000-0
```

---

## Related Documentation

### File Watcher Consumer
- **File Watcher Service:** `@refactoring/filewatcher/`
- **WebSocket RPC:** `@docs/DJANGO_INTEGRATION.md`

### AI Command Consumer
- **Router Alternative Analysis:** `@refactoring/router/ROUTER_ALTERNATIVE_DJANGO_IPC.md`
- **Router Documentation:** `@refactoring/router/ROUTER_NAVIGATION.md`
- **CLI Manager Services:** `@refactoring/router/ROUTER_ARCHITECTURE.md`

### General
- **Redis Streams:** https://redis.io/docs/data-types/streams/
- **Consumer Groups:** https://redis.io/docs/data-types/streams/#consumer-groups

---

## Testing

**Manual test for AI Command Consumer:**
```bash
cd /path/to/websocket
python test_ai_consumer.py
```

See `test_ai_consumer.py` for automated testing of AI command routing.

---

**Last Updated:** October 6, 2025
