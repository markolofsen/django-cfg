# gRPC Terminal - Manual Testing Guide

**Date:** 2025-12-04

---

## Quick Start

### 1. Start gRPC Server (Django)

```bash
cd /Users/markinmatrix/Documents/htdocs/@CARAPIS/encar_parser_new/@projects/djangocfg/solution/projects/django

# Start via poetry
poetry run python manage.py rungrpc

# Or with hotreload disabled (more stable for streaming)
poetry run python manage.py rungrpc --noreload
```

**Expected output:**
```
[INFO] Starting gRPC server on [::]:50051
[INFO] Interceptors: ApiKeyAuthInterceptor, ObservabilityInterceptor
[INFO] Services: TerminalStreamingService
```

### 2. Start Electron Application

```bash
cd /Users/markinmatrix/Documents/htdocs/@CARAPIS/encar_parser_new/@projects/djangocfg/solution/projects/frontend/apps/electron

# Install dependencies (if not installed)
pnpm install

# Start in dev mode
pnpm dev
```

**Expected output:**
```
✔ Electron Forge started
✔ Launching Application
```

---

## Architecture

### Data Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              ELECTRON                                    │
│                                                                          │
│  ┌──────────────┐    IPC     ┌──────────────┐    gRPC    ┌───────────┐ │
│  │   Renderer   │◄──────────►│     Main     │◄──────────►│   Django  │ │
│  │  (React UI)  │            │  (grpc-term) │            │  Server   │ │
│  │              │            │              │            │           │ │
│  │  TerminalUI  │            │  PTYManager  │            │  Commands │ │
│  │    xterm.js  │            │  GRPCClient  │            │  Sessions │ │
│  └──────────────┘            └──────────────┘            └───────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
```

### Bidirectional Streaming

```
Electron (ElectronMessage)          Django (DjangoMessage)
─────────────────────────           ─────────────────────
     register         ──────────►
                      ◄──────────   startSession
     output           ──────────►
                      ◄──────────   input
     output           ──────────►
     status           ──────────►
     heartbeat        ──────────►
                      ◄──────────   ping
     heartbeat        ──────────►
                      ◄──────────   resize
     ack              ──────────►
```

---

## What to Check

### 1. Session Registration

In Django logs:
```
[gRPC] <-- TerminalStreamingService.ConnectTerminal #1 type=register
[Terminal] New session registered: session_id=abc-123, hostname=Marks-Laptop
```

In Electron logs:
```
[TerminalClient] Registration sent
[TerminalClient] Connected
```

### 2. PTY Start and Output

After receiving `startSession` from Django:
```
[TerminalService] PTY started: /bin/zsh @ /Users/user
[TerminalClient] Sent output: 1024 bytes
```

### 3. Heartbeat (keepalive)

Every 30 seconds:
```
[TerminalClient] Heartbeat sent
[gRPC] <-- TerminalStreamingService.ConnectTerminal #N type=heartbeat
```

**Before fix:** Stopped after ~15 messages
**After fix:** Continues indefinitely

### 4. Command Input

When user types in terminal via web:
```
Django:
[Terminal] Input command received: 'ls -la\n'
[gRPC] --> input to session abc-123

Electron:
[TerminalService] Input received from Django
[PTYManager] Writing to PTY: 'ls -la\n'
```

---

## Project Structure

```
djangocfg/solution/projects/
├── django/                                    # gRPC Server
│   └── apps/terminal/
│       ├── grpc/
│       │   ├── services/
│       │   │   ├── proto/                    # .proto files
│       │   │   │   ├── common.proto
│       │   │   │   ├── terminal_streaming_service.proto
│       │   │   │   └── generate_proto.sh     # Generator script
│       │   │   ├── generated/                # Python protobuf
│       │   │   └── handlers/                 # gRPC handlers
│       │   └── commands/                     # Terminal commands
│       ├── models/                           # TerminalSession, CommandHistory
│       ├── centrifugo_handlers.py            # Centrifugo (web → django)
│       └── consumers.py                      # WebSocket consumers
│
└── frontend/
    ├── packages/
    │   └── grpc-terminal/                    # gRPC Client Library
    │       ├── src/
    │       │   ├── grpc/
    │       │   │   ├── proto/                # .proto files (copy)
    │       │   │   ├── generated/            # TypeScript protobuf
    │       │   │   └── client.ts             # TerminalStreamingClient
    │       │   ├── pty/
    │       │   │   └── manager.ts            # PTYManager (node-pty)
    │       │   ├── core/
    │       │   │   └── service.ts            # TerminalService
    │       │   └── models/
    │       │       └── config.ts             # Configuration
    │       └── package.json
    │
    └── apps/
        └── electron/                         # Electron App
            └── src/
                └── features/
                    └── terminal/             # Terminal Feature
                        ├── components/       # React UI
                        ├── hooks/            # useTerminal
                        ├── ipc/              # Main/Renderer bridge
                        └── types/            # TypeScript types
```

---

## Proto File Generation

### Source Location

Proto files are stored in Django and serve as the **single source of truth**:

```
django/apps/terminal/grpc/services/proto/
├── common.proto                    # Shared types (TerminalSize, SessionStatus, etc.)
├── terminal_streaming_service.proto # Main streaming service definition
└── generate_proto.sh               # Generator script
```

### Running the Generator

```bash
cd /Users/markinmatrix/Documents/htdocs/@CARAPIS/encar_parser_new/@projects/djangocfg/solution/projects/django/apps/terminal/grpc/services/proto

./generate_proto.sh
```

### What the Generator Does

1. **Python generation** (for Django gRPC server):
   - Uses `grpc_tools.protoc` to generate `*_pb2.py` and `*_pb2_grpc.py`
   - Fixes relative imports (`import common_pb2` → `from . import common_pb2`)
   - Output: `../generated/`

2. **TypeScript generation** (for Electron/grpc-terminal):
   - Copies proto files to the grpc-terminal package
   - Uses `@protobuf-ts/plugin` via npx to generate TypeScript
   - Output: `frontend/packages/grpc-terminal/src/grpc/generated/`

### Import Fix Details

The generator automatically fixes Python imports for cross-proto references:

```python
# Before (broken - absolute import)
import common_pb2 as common__pb2

# After (fixed - relative import)
from . import common_pb2 as common__pb2
```

This fix is applied to both `*_pb2.py` and `*_grpc.py` files.

### Verify Generation

```bash
# Python files
ls -la ../generated/*.py
# Expected: common_pb2.py, common_pb2_grpc.py, terminal_streaming_service_pb2.py, etc.

# TypeScript files
ls -la ../../../../../../frontend/packages/grpc-terminal/src/grpc/generated/*.ts
# Expected: common.ts, terminal_streaming_service.ts, terminal_streaming_service.client.ts

# Test Python import
cd /path/to/django
poetry run python -c "from apps.terminal.grpc.services.generated import terminal_streaming_service_pb2; print('OK')"
```

### When to Regenerate

Run the generator after:
- Modifying `.proto` files
- Adding new message types or services
- Changing field numbers or types
- After `git pull` if proto files were updated

---

## Common Errors

### 1. `StatusCode.CANCELLED` on client

**Cause:** Server closed the stream
**Check:**
- Django logs for errors
- Heartbeat interval (should be < 60 sec)

### 2. PTY fails to start

**Error:** `PTY_START_FAILED`
**Cause:** node-pty not installed or shell not found
**Solution:**
```bash
cd apps/electron
pnpm rebuild node-pty
```

### 3. Electron cannot connect to gRPC

**Error:** `UNAVAILABLE: Connection refused`
**Check:**
- Django gRPC server is running on port 50051
- Firewall is not blocking the port
- Config: `grpc.host` and `grpc.port`

### 4. Proto types mismatch

**Error:** TypeScript errors about type mismatches
**Solution:** Regenerate proto files:
```bash
cd django/apps/terminal/grpc/services/proto
./generate_proto.sh

cd frontend/packages/grpc-terminal
pnpm build
```

### 5. xterm not displaying output

**Cause:** CSS not loaded
**Solution:** Add import:
```tsx
import '@xterm/xterm/css/xterm.css';
```

---

## Configuration

### Django settings

```python
GRPC_AUTH = {
    "enabled": True,
    "require_auth": False,  # False for development
}

GRPC_SERVER = {
    "host": "[::]:50051",
    "max_workers": 10,
}
```

### Electron config

```typescript
// In main.ts
setupTerminalIPC(mainWindow, {
  host: 'localhost',
  port: 50051,
});

// Or from env
const grpcConfig = {
  host: process.env.GRPC_HOST || 'localhost',
  port: parseInt(process.env.GRPC_PORT || '50051'),
};
```

### grpc-terminal defaults

```typescript
// DEFAULT_GRPC_CONFIG
{
  host: 'localhost',
  port: 50051,
  useTls: false,
  timeoutSeconds: 30,
  reconnectInterval: 5,
  heartbeatInterval: 30,
}

// DEFAULT_TERMINAL_CONFIG
{
  shell: '/bin/zsh',  // or 'powershell.exe' on Windows
  workingDirectory: process.env.HOME,
  cols: 80,
  rows: 24,
}
```

---

## Testing Checklist

### Basic Connection
- [ ] Django gRPC server starts without errors
- [ ] Electron application launches
- [ ] Terminal component is displayed
- [ ] Client connects to server (logs: `Connected`)

### Bidirectional Streaming
- [ ] Session registration succeeds
- [ ] Heartbeat works (counter grows above 15)
- [ ] No `StatusCode.CANCELLED` errors
- [ ] Reconnection works after disconnect

### PTY Functionality
- [ ] PTY starts on `startSession` command
- [ ] Command output is displayed in xterm
- [ ] Keyboard input is passed to PTY
- [ ] Terminal resize works
- [ ] Session close properly terminates PTY

### UI
- [ ] Toolbar shows correct status
- [ ] Start/Stop button works
- [ ] Clear clears the terminal
- [ ] Errors are displayed with Retry option

---

## Useful Commands

### Check Ports

```bash
# Check that gRPC is listening
lsof -i :50051

# Check that Electron is listening (Vite dev server)
lsof -i :5173
```

### Clean and Rebuild

```bash
# grpc-terminal
cd frontend/packages/grpc-terminal
pnpm clean && pnpm build

# Electron
cd frontend/apps/electron
pnpm check
```

### Logs

```bash
# Django
tail -f django/logs/grpc.log

# Electron (in DevTools console)
# View → Toggle Developer Tools → Console
```
