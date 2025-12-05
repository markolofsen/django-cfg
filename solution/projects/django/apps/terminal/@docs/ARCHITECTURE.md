# Terminal App Architecture

## Overview

The Terminal app provides a full-duplex terminal experience from browser to local machine via Electron, with proper session management, heartbeat monitoring, and real-time updates.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              BROWSER                                     │
│  ┌─────────────┐    ┌──────────────────┐    ┌─────────────────────────┐ │
│  │  xterm.js   │◄───│  Centrifugo WS   │◄───│    REST API Client      │ │
│  │  Terminal   │    │  (real-time)     │    │    (session mgmt)       │ │
│  └──────┬──────┘    └────────┬─────────┘    └───────────┬─────────────┘ │
│         │                    │                          │               │
└─────────┼────────────────────┼──────────────────────────┼───────────────┘
          │ output             │ input/resize/signal      │ CRUD
          │                    ▼                          ▼
┌─────────┼────────────────────────────────────────────────────────────────┐
│         │                    DJANGO                                      │
│         │   ┌────────────────────────────────────────────────────────┐  │
│         │   │                Centrifugo Integration                   │  │
│         │   │  ┌─────────────────────┐   ┌─────────────────────────┐ │  │
│         │   │  │  centrifugo_        │   │     consumers.py         │ │  │
│         │   │  │  handlers.py        │   │  (Publisher/Output)      │ │  │
│         │   │  │  (RPC Handlers)     │   │                          │ │  │
│         │   │  │  @websocket_rpc     │   │  publish_output()        │ │  │
│         │   │  │  terminal.input     │   │  publish_status()        │ │  │
│         │   │  │  terminal.resize    │◄──│  publish_error()         │ │  │
│         │   │  │  terminal.signal    │   │  publish_command_complete│ │  │
│         │   │  └──────────┬──────────┘   └─────────────▲────────────┘ │  │
│         │   └─────────────┼────────────────────────────┼──────────────┘  │
│         │                 │                            │                 │
│         │   ┌─────────────▼────────────────────────────┼──────────────┐  │
│         │   │              gRPC Service                │              │  │
│         │   │  ┌─────────────────────────────────────────────────┐   │  │
│         │   │  │  TerminalStreamingServiceServicer              │   │  │
│         │   │  │                                                 │   │  │
│         │   │  │  ConnectTerminal() - bidirectional stream      │   │  │
│         │   │  │  CreateSession() / CloseSession()              │   │  │
│         │   │  │  SendInput() / SendResize() / SendSignal()     │   │  │
│         │   │  └─────────────────────────────────────────────────┘   │  │
│         │   └────────────────────────┬───────────────────────────────┘  │
│         │                            │                                   │
│         │   ┌────────────────────────▼───────────────────────────────┐  │
│         │   │                    REST API                            │  │
│         │   │  ┌─────────────────────────────────────────────────┐   │  │
│         │   │  │  TerminalSessionViewSet                         │   │  │
│         │   │  │  - list/create/retrieve/destroy sessions        │   │  │
│         │   │  │  - @action input/resize/signal/history          │   │  │
│         │   │  └─────────────────────────────────────────────────┘   │  │
│         │   │  ┌─────────────────────────────────────────────────┐   │  │
│         │   │  │  TerminalCommandViewSet (ReadOnly)              │   │  │
│         │   │  │  - Command history browsing                     │   │  │
│         │   │  └─────────────────────────────────────────────────┘   │  │
│         │   └────────────────────────────────────────────────────────┘  │
│         │                                                                │
│         │   ┌────────────────────────────────────────────────────────┐  │
│         │   │                    Models                              │  │
│         │   │  TerminalSession | CommandHistory                      │  │
│         │   └────────────────────────────────────────────────────────┘  │
└─────────┼────────────────────────────────────────────────────────────────┘
          │
          │ gRPC bidirectional stream
          ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                              ELECTRON                                     │
│  ┌─────────────────────┐   ┌─────────────────────┐   ┌────────────────┐ │
│  │  gRPC Client        │◄──│  TerminalService    │──►│  PTYManager    │ │
│  │  (TerminalStreaming │   │  (Orchestrator)     │   │  (node-pty)    │ │
│  │  Client)            │   └─────────────────────┘   └───────┬────────┘ │
│  └─────────────────────┘                                     │          │
└──────────────────────────────────────────────────────────────┼──────────┘
                                                               │
                                                               ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                              OS SHELL                                     │
│                           /bin/zsh or /bin/bash                          │
└──────────────────────────────────────────────────────────────────────────┘
```

## Components

### 1. Browser Layer

| Component | Purpose |
|-----------|---------|
| xterm.js | Terminal emulator in browser |
| Centrifugo WS | Real-time WebSocket for output streaming |
| REST API Client | Session management (CRUD operations) |

### 2. Django Layer

#### Centrifugo Integration

| File | Role | Direction |
|------|------|-----------|
| `centrifugo_handlers.py` | RPC Handlers | Browser → Django (input) |
| `consumers.py` | Publisher | Django → Browser (output) |

#### REST API

| ViewSet | Purpose |
|---------|---------|
| `TerminalSessionViewSet` | Session CRUD + actions (input, resize, signal) |
| `TerminalCommandViewSet` | Command history (read-only) |

#### gRPC Service

| Method | Type | Purpose |
|--------|------|---------|
| `ConnectTerminal` | Bidirectional Stream | Main communication channel |
| `CreateSession` | Unary | Create new session |
| `CloseSession` | Unary | Close session |
| `SendInput` | Unary | Send input bytes |
| `SendResize` | Unary | Resize terminal |
| `SendSignal` | Unary | Send signal (SIGINT, etc) |

### 3. Electron Layer

| Component | Purpose |
|-----------|---------|
| TerminalStreamingClient | gRPC client with auto-reconnect |
| TerminalService | Orchestrates gRPC + PTY |
| PTYManager | node-pty wrapper |

### 4. Models

```python
TerminalSession:
    - id: UUID (PK)
    - user: ForeignKey (optional)
    - name, status, shell, working_directory
    - electron_hostname, electron_version
    - commands_count, bytes_sent, bytes_received
    - connected_at, last_heartbeat_at, disconnected_at

CommandHistory:
    - id: UUID (PK)
    - session: ForeignKey
    - command, status, exit_code
    - stdout, stderr
    - started_at, finished_at
```

## Data Flow

### Input Flow (Browser → Shell)

```
1. User types in xterm.js
2. Browser sends via:
   - WebSocket RPC: terminal.input (low latency) ← RECOMMENDED
   - REST API: POST /sessions/{id}/input/ (higher latency)
3. Django forwards to gRPC service
4. gRPC sends TerminalInput message to Electron
5. Electron writes to PTY stdin
6. Shell executes command
```

### Output Flow (Shell → Browser)

```
1. Shell produces output
2. PTY captures output
3. Electron sends via gRPC stream (ElectronMessage.output)
4. Django gRPC handler receives output
5. Django publishes to Centrifugo channel
6. Browser receives via WebSocket subscription
7. xterm.js renders output
```

## Channel Naming Convention

```
terminal#session#{session_id}
```

Events published:
- `type: "output"` - Terminal output (base64 encoded)
- `type: "status"` - Session status change
- `type: "error"` - Error occurred
- `type: "command_complete"` - Command finished

## Configuration

### Django (config.py)

```python
# gRPC enabled for terminal
grpc: GRPCConfig = GRPCConfig(
    enabled=True,
    host="0.0.0.0",
    port=50051,
    enabled_apps=["terminal"],
    handlers_hook=[
        "apps.terminal.grpc.services.handlers.grpc_handlers",
    ]
)

# Centrifugo for real-time
centrifugo: DjangoCfgCentrifugoConfig = DjangoCfgCentrifugoConfig(
    enabled=True,
    # ... configuration
)
```

### Electron (config)

```typescript
ClientConfig {
    sessionId: string  // UUID from Django
    grpc: {
        host: 'localhost',
        port: 50051,
        reconnectInterval: 5,
        heartbeatInterval: 30
    }
    terminal: {
        shell: '/bin/zsh',
        cols: 80, rows: 24
    }
}
```

## Security Considerations

1. **User Scoping**: All REST/WebSocket operations filter by `user_id`
2. **Session Ownership**: Sessions linked to authenticated users
3. **gRPC**: Currently no auth (localhost only, relies on session UUID)
4. **Centrifugo**: User authentication via Django session/JWT

## File Structure

```
apps/terminal/
├── models/
│   ├── session.py          # TerminalSession model
│   └── command.py          # CommandHistory model
├── views/
│   ├── api/
│   │   ├── session_viewsets.py    # REST API
│   │   └── command_viewsets.py
│   └── serializers/
│       ├── session_serializers.py
│       └── command_serializers.py
├── grpc/
│   └── services/
│       ├── proto/          # Protobuf definitions
│       └── handlers/       # gRPC service implementation
├── centrifugo_handlers.py  # WebSocket RPC handlers
├── consumers.py            # Centrifugo publisher
├── urls.py                 # REST API URLs
└── admin.py
```
