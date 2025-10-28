# Django-CFG Admin - Next.js Docker Setup

Docker configuration for building the Django-CFG Admin Next.js application.

## Structure

```
frontend/
├── Dockerfile              # Multi-stage build for admin app
├── docker-compose.yaml    # Standalone service definitions
└── README.md              # This file
```

## How It Works

The `Dockerfile` uses **multi-stage builds** to create an optimized production image:

### Build Stages

1. **Base Stage** - Alpine Linux with Node.js 20
2. **Installer Stage** - Installs dependencies and builds the admin app
3. **Runner Stage** - Minimal runtime image with standalone output

### Key Features

- ✅ **Standalone output** - Next.js generates a self-contained server
- ✅ **Minimal runtime** - Only production dependencies included
- ✅ **Non-root user** - Runs as `nextjs` user for security
- ✅ **Health checks** - Built-in health monitoring
- ✅ **Optimized caching** - Efficient Docker layer caching

## Usage

### Build admin app:
```bash
docker compose build admin
```

### Run admin app:
```bash
docker compose up admin
```

### Build with custom environment:
```bash
docker compose build admin --build-arg NEXT_PUBLIC_API_URL=https://api.example.com
```

## Environment Variables

- `NODE_ENV` - Set to `production`
- `PORT` - Server port (default: 3000)
- `HOSTNAME` - Server hostname (default: 0.0.0.0)
- `NEXT_PUBLIC_API_URL` - Django API URL
- `NEXT_PUBLIC_BASE_PATH` - Base path for Next.js app
