# Unrealon Admin

Admin panel for Unrealon Router & Swarm built with Next.js 15 and React 19.

## Features

- 🎨 Modern UI with shadcn/ui components
- 🔄 Real-time updates via WebSocket
- 📊 Dashboard with metrics and stats
- 💼 Session management
- ⚡ Job management for AI code generation
- 🌓 Dark mode support
- 📱 Responsive design

## Architecture

Built following the **view-based architecture** pattern:

```
src/
├── api/              # API clients (router.ts, swarm.ts)
├── components/       # Shared components
├── contexts/         # React contexts (Router, Swarm, Theme, WebSocket)
├── core/            # Configuration (routes.ts, settings.ts)
├── hooks/           # Global hooks
├── layouts/         # Layout wrappers (DashboardLayout)
├── lib/             # Utilities
├── pages/           # Next.js pages (thin wrappers)
├── types/           # Type definitions
└── views/           # Feature views
    ├── overview/    # Dashboard overview
    ├── sessions/    # Sessions management
    └── jobs/        # Jobs management
```

Each view follows this structure:
```
views/[feature]/
├── components/      # View-specific UI components
├── hooks/          # Data fetching and business logic
├── types/          # View-specific types
└── index.tsx       # Main view component
```

## Environment Variables

Create a `.env.local` file in the app directory:

```bash
# API Configuration
NEXT_PUBLIC_ROUTER_API_URL=http://localhost:8083
NEXT_PUBLIC_ROUTER_WS_URL=ws://localhost:8083
NEXT_PUBLIC_SWARM_API_URL=http://localhost:8010

# App Configuration
NEXT_PUBLIC_APP_NAME=Unrealon Admin
NEXT_PUBLIC_APP_VERSION=1.0.0
```

### Docker Configuration

When running in Docker, override these variables:

```yaml
environment:
  - NEXT_PUBLIC_ROUTER_API_URL=http://router-api:8083
  - NEXT_PUBLIC_ROUTER_WS_URL=ws://router-api:8083
  - NEXT_PUBLIC_SWARM_API_URL=http://swarm-api:8010
```

Or use Docker networks with service names:

```yaml
services:
  admin:
    environment:
      - NEXT_PUBLIC_ROUTER_API_URL=http://unrealon-router:8083
      - NEXT_PUBLIC_ROUTER_WS_URL=ws://unrealon-router:8083
      - NEXT_PUBLIC_SWARM_API_URL=http://unrealon-swarm:8010
```

## Development

```bash
# Install dependencies
npm install

# Start dev server
npm run dev

# Build for production
npm run build

# Start production server
npm start
```

## Tech Stack

- **Framework**: Next.js 15.5.4 (with Turbopack)
- **UI Library**: React 19
- **Styling**: Tailwind CSS 3.4.0
- **Components**: shadcn/ui + Radix UI
- **Icons**: Lucide React
- **Data Fetching**: SWR
- **WebSocket**: socket.io-client
- **Type Safety**: TypeScript 5.7

## Views

### Overview (/dashboard)
- Services status (Router & Swarm)
- Real-time metrics
- Recent sessions list
- Auto-refresh every 3 seconds

### Sessions (/sessions)
- List all Claude Router sessions
- Create new sessions with model selection
- Start/stop sessions
- Delete sessions
- Real-time status updates

### Jobs (/jobs)
- List all Swarm code generation jobs
- Create new jobs with framework selection
- Monitor job progress
- Download generated code
- Job status tracking (pending, running, completed, failed)

## Key Features

### Real-time Updates
- WebSocket connection to Router API
- Auto-refresh on data changes
- Connection status indicator

### Error Handling
- Global error boundaries
- API error handling with SWR
- User-friendly error messages
- Retry mechanisms

### Performance
- SWR caching and revalidation
- Optimized bundle size (~350 kB)
- Code splitting per route
- Lazy loading for heavy components

## Configuration

Edit `src/core/settings.ts` to customize:
- API endpoints
- Feature flags (search, notifications, dark mode)
- SWR refresh intervals
- App metadata

## Docker Compose Example

```yaml
version: '3.8'

services:
  admin:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "3100:3100"
    environment:
      - NEXT_PUBLIC_ROUTER_API_URL=http://unrealon-router:8083
      - NEXT_PUBLIC_ROUTER_WS_URL=ws://unrealon-router:8083
      - NEXT_PUBLIC_SWARM_API_URL=http://unrealon-swarm:8010
    networks:
      - unrealon
    depends_on:
      - router
      - swarm

  router:
    image: unrealon/router:latest
    ports:
      - "8083:8083"
    networks:
      - unrealon

  swarm:
    image: unrealon/swarm:latest
    ports:
      - "8010:8010"
    networks:
      - unrealon

networks:
  unrealon:
    driver: bridge
```

## License

Private - Unrealon Project
