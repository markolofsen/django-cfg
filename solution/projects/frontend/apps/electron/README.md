# DjangoCFG Desktop

Cross-platform desktop application for DjangoCFG built with Electron, React, and Vite.

## Features

- **Terminal** - Remote terminal sessions via gRPC with xterm.js
- **Settings** - Application configuration and preferences
- **Theme Support** - Light/dark/system theme modes

## Tech Stack

- **Electron 39** - Desktop application framework
- **React 19** - UI library
- **Vite** - Build tool and dev server
- **Tailwind CSS v4** - Styling
- **gRPC** - Terminal communication protocol
- **xterm.js** - Terminal emulator
- **Electron Forge** - Build and packaging

## Development

```bash
# Install dependencies
pnpm install

# Start development
pnpm dev

# Type check
pnpm check
```

## Build

```bash
# Package for current platform
pnpm package

# Create distributable
pnpm make
```

## Project Structure

```
src/
├── main.ts          # Electron main process
├── preload.ts       # Preload script (IPC bridge)
├── renderer.tsx     # React entry point
├── App.tsx          # Main React component
├── env.ts           # Environment configuration
├── features/
│   └── terminal/    # Terminal feature (gRPC + xterm)
├── pages/           # Route pages
├── grpc/            # gRPC client setup
└── utils/           # Utilities
```

## Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
GRPC_HOST=localhost
GRPC_PORT=50051
GRPC_USE_TLS=false
```

## Packages

- `@djangocfg/ui-core` - UI components
- `@djangocfg/electron-ui` - Electron-specific UI (ThemeProvider)
- `@djangocfg/grpc-terminal` - Terminal gRPC client
