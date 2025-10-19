# Django-CFG Frontend - Turbo Monorepo Docker Setup

Universal Docker configuration for building multiple Next.js apps from a Turbo monorepo.

## Structure

```
frontend/
├── Dockerfile              # Multi-stage build for all apps
├── docker-compose.yaml    # Standalone service definitions
└── README.md              # This file
```

## How It Works

The `Dockerfile` uses **multi-stage builds** with **target** parameter to build different apps:

### Adding a New App

1. **Add a new pruner stage** in `Dockerfile`:
```dockerfile
FROM base AS pruner-myapp
RUN corepack enable && corepack prepare pnpm@9.15.4 --activate
COPY . .
RUN npx turbo@^2 prune @djangocfg/myapp --docker
```

2. **Add installer stage**:
```dockerfile
FROM base AS installer-myapp
RUN corepack enable && corepack prepare pnpm@9.15.4 --activate
COPY --from=pruner-myapp /app/out/json/ .
RUN pnpm install
COPY --from=pruner-myapp /app/out/full/ .

ARG DJANGO_API_URL
ARG IPC_WS_URL
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1
ENV NEXT_PUBLIC_API_URL=${DJANGO_API_URL}
ENV NEXT_PUBLIC_WS_RPC_URL=${IPC_WS_URL}

RUN pnpm turbo run build --filter=@djangocfg/myapp
```

3. **Add runner stage**:
```dockerfile
FROM node:20-alpine AS myapp
WORKDIR /app
ENV NODE_ENV=production
ENV PORT=3xxx
ENV HOSTNAME="0.0.0.0"

RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

COPY --from=installer-myapp --chown=nextjs:nodejs /app/apps/myapp/.next/standalone ./
COPY --from=installer-myapp --chown=nextjs:nodejs /app/apps/myapp/.next/static ./apps/myapp/.next/static
COPY --from=installer-myapp --chown=nextjs:nodejs /app/apps/myapp/public ./apps/myapp/public

USER nextjs
EXPOSE 3xxx

CMD node apps/myapp/server.js
```

4. **Add service in docker-compose.yaml** or use in main compose:
```yaml
frontend-myapp:
  build:
    context: ../projects/frontend
    dockerfile: ../../docker/services/frontend/Dockerfile
    target: myapp
    args:
      DJANGO_API_URL: ${DJANGO_API_URL}
      IPC_WS_URL: ${IPC_WS_URL}
  image: djangocfg-frontend:myapp
  # ... rest of config
```

## Usage

### Build specific app:
```bash
docker compose build --build-arg target=demo frontend-demo
```

### Run specific app:
```bash
docker compose up frontend-demo
```

### Build all frontend apps:
```bash
docker compose build frontend-demo frontend-myapp
```

## Benefits

- ✅ **Single Dockerfile** for all apps
- ✅ **Efficient caching** - shared base layers
- ✅ **Turbo prune** - minimal dependencies per app
- ✅ **Standalone output** - smallest runtime image
- ✅ **Easy to extend** - just add new target stages
