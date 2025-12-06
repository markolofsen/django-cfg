# @djangocfg/terminal

Web-based terminal application built with Next.js and xterm.js.

## Overview

This app provides a browser-based terminal interface that connects to Django backend terminal sessions via WebSocket (Centrifugo). It's designed to be embedded in the Electron app or accessed standalone.

## Stack

- **Next.js 15** - React framework
- **xterm.js** - Terminal emulator
- **Centrifugo** - Real-time WebSocket messaging
- **Tailwind CSS v4** - Styling

## Scripts

```bash
pnpm dev      # Start dev server on port 3002
pnpm build    # Production build
pnpm start    # Start production server on port 3002
pnpm check    # TypeScript type checking
pnpm ai-docs  # Search DjangoCFG documentation
```

## AI Documentation CLI

```bash
# Search docs
pnpm ai-docs search "terminal session"

# Get MCP config
pnpm ai-docs mcp
```

## Structure

```
app/
├── page.tsx              # Main entry - sessions list or terminal view
├── [sessionId]/          # Session-specific routes
├── _components/          # UI components (InteractiveTerminal, etc.)
├── _views/               # Page views
└── _lib/
    ├── api/              # Generated API client for Django backend
    └── contexts/         # React contexts (TerminalContext)
```

## Features

- Interactive terminal sessions
- Session management (create, list, close)
- Command history
- Resize support
- Real-time output via WebSocket

## Related

- `@djangocfg/grpc-terminal` - gRPC terminal package for Electron
- `@djangocfg/centrifugo` - Centrifugo client wrapper
