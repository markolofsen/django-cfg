# Unrealon WebSocket Server

Real-time WebSocket RPC server for Unrealon Cloud IDE.

## Features

- **WebSocket RPC** - Type-safe RPC over WebSocket with auto-generated clients
- **Real-time Events** - Workspace file changes, AI session messages, notifications
- **Redis Streams** - Reliable message delivery with consumer groups
- **JWT Authentication** - Secure WebSocket connections
- **Presence Tracking** - Track online users with Redis
- **Room-based Broadcasting** - Send events to specific workspace/session rooms

## Quick Start

### 1. Install Dependencies

```bash
make install-ipc
```

### 2. Configure Environment

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

### 3. Start Server

```bash
make dev
```

Server will start on:
- **WebSocket**: `ws://localhost:8765/ws`
- **Health Check**: `http://localhost:8766/health`

## RPC Methods

### Workspace Events

- `workspace.file_changed` - File create/modify/delete/rename
- `workspace.snapshot_created` - Snapshot notifications
- `workspace.state_changed` - Workspace state updates

### AI Session Events

- `session.message` - AI message streaming
- `session.task_status` - Task status updates
- `session.context_updated` - Context change notifications

### Notifications

- `notification.send` - Send notification to specific user
- `notification.broadcast` - Broadcast to all users

## Development

```bash
# Run development server
make dev

# Check health
make health

# View logs
make logs

# Run tests
make test
```

## Production

```bash
# Run production server
make run-prod

# Build Docker image
make docker-build

# Run Docker container
make docker-run
```

## Architecture

```
Django App → Redis Streams → WebSocket Server → Browser Client
                  ↓
            RPC Bridge (Consumer Groups)
                  ↓
            Message Router → Handlers
                  ↓
            Connection Manager → WebSocket Rooms
```

## Client Generation

TypeScript and Python clients are auto-generated from RPC handlers:

```bash
make generate-client
```

Clients will be generated in `clients/` directory.
