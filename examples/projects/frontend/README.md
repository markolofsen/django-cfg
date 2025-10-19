# Unrealon Web Monorepo

Turborepo monorepo for Unrealon web applications.

## 🏗️ Structure

```
web/
├── apps/
│   └── admin/          # Admin panel (Next.js Pages Router)
└── packages/
    ├── ui/             # Shared UI components (shadcn/ui)
    └── config/         # Shared configurations
```

## 🚀 Quick Start

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build all apps
npm run build

# Run linting
npm run lint

# Type checking
npm run type-check
```

## 📦 Apps

### Admin (`apps/admin`)

Admin panel for managing Claude Router sessions.

- **Framework**: Next.js 15 (Pages Router)
- **UI**: shadcn/ui + Tailwind CSS 4
- **Port**: 3000
- **Features**:
  - Dashboard with real-time metrics
  - Session management
  - WebSocket support
  - Prometheus metrics integration

**Development**:
```bash
cd apps/admin
npm run dev
```

## 📚 Packages

### UI (`packages/ui`)

Shared UI component library based on shadcn/ui.

- Button
- Card
- Dialog
- Select
- Tabs
- Toast
- And more...

**Usage**:
```tsx
import { Button, Card } from "@djangocfg/ui";
```

### Config (`packages/config`)

Shared configuration files:
- TypeScript configs
- ESLint configs
- Tailwind configs

## 🔧 Tech Stack

- **Framework**: Next.js 15
- **Build Tool**: Turborepo
- **Styling**: Tailwind CSS 4
- **UI Components**: shadcn/ui + Radix UI
- **Language**: TypeScript 5.7
- **Icons**: Lucide React
- **Real-time**: Socket.io
- **Data Fetching**: SWR

## 🌐 Environment Variables

Create `.env.local` in `apps/admin`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8083
NEXT_PUBLIC_API_KEY=ReformsClaude
NEXT_PUBLIC_WS_URL=ws://localhost:8083
```

## 📖 Scripts

| Command | Description |
|---------|-------------|
| `npm run dev` | Start all apps in development mode |
| `npm run build` | Build all apps |
| `npm run lint` | Lint all apps and packages |
| `npm run type-check` | Run TypeScript type checking |
| `npm run clean` | Clean all build artifacts |
| `npm run format` | Format code with Prettier |

## 🔗 Links

- [Turborepo Docs](https://turbo.build/repo/docs)
- [Next.js Docs](https://nextjs.org/docs)
- [shadcn/ui Docs](https://ui.shadcn.com)
- [Tailwind CSS Docs](https://tailwindcss.com/docs)
