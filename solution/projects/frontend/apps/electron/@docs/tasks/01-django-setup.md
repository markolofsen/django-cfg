# Task 01: Django gRPC Server Setup

## Overview

Django gRPC server provides terminal streaming service for Electron client communication.

## Architecture

```mermaid
graph LR
    E[Electron App] -->|gRPC| D[Django gRPC Server]
    D -->|WebSocket| B[Browser UI]
    E -->|PTY| S[Shell/zsh]
```

## Configuration

### gRPC Port

Default: `50051` (configurable via environment)

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GRPC_HOST` | `localhost` | gRPC server host |
| `GRPC_PORT` | `50051` | gRPC server port |
| `GRPC_USE_TLS` | `false` | Enable TLS |

## Proto Files

Location: `packages/grpc-terminal/src/grpc/proto/`

- `common.proto` - Shared types (SessionStatus, TerminalSize)
- `terminal_streaming_service.proto` - Main bidirectional streaming service

### Key Message Types

```mermaid
classDiagram
    class ElectronMessage {
        session_id: string
        register: RegisterRequest
        heartbeat: HeartbeatUpdate
        output: TerminalOutput
        status: StatusUpdate
        error: ErrorReport
        ack: CommandAck
    }

    class DjangoMessage {
        command_id: string
        input: TerminalInput
        resize: ResizeCommand
        start_session: StartSessionCommand
        close_session: CloseSessionCommand
        signal: SignalCommand
        ping: PingCommand
    }
```

## Code Generation

```bash
cd packages/grpc-terminal
pnpm run proto:generate
```

Output: `src/grpc/generated/`

## Verification

- [ ] gRPC server starts on configured port
- [ ] Health check responds
- [ ] Proto files generated successfully
