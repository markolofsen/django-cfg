# ═════════════════════════════════════════════════════════════════
# Django-CFG Frontend - Turbo Monorepo (demo + other apps)
# Optimized with turbo prune and standalone output
# ═════════════════════════════════════════════════════════════════

FROM node:20-alpine AS base
RUN apk update && apk add --no-cache libc6-compat
WORKDIR /app

# ─────────────────────────────────────────────────────────────────
# Pruner Stage - Extract minimal workspace for demo app
# ─────────────────────────────────────────────────────────────────

FROM base AS pruner-demo
RUN corepack enable && corepack prepare pnpm@9.15.4 --activate

COPY projects/frontend .

# Generate a pruned monorepo with only demo dependencies
RUN npx turbo@^2 prune @djangocfg/demo --docker

# ─────────────────────────────────────────────────────────────────
# Installer Stage - Install dependencies and build demo
# ─────────────────────────────────────────────────────────────────

FROM base AS installer-demo
RUN corepack enable && corepack prepare pnpm@9.15.4 --activate

# Copy pruned lockfile and package.json files
COPY --from=pruner-demo /app/out/json/ .

# Install dependencies
RUN pnpm install

# Copy pruned source code
COPY --from=pruner-demo /app/out/full/ .

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

# Build the demo app
RUN pnpm turbo run build --filter=@djangocfg/demo

# ─────────────────────────────────────────────────────────────────
# Runner Stage - Demo App (port 3200)
# ─────────────────────────────────────────────────────────────────

FROM node:20-alpine AS demo
WORKDIR /app

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1
ENV PORT=3200
ENV HOSTNAME="0.0.0.0"

# Create non-root user
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

# Copy only standalone output (Next.js automatically generates this)
COPY --from=installer-demo --chown=nextjs:nodejs /app/apps/demo/.next/standalone ./
COPY --from=installer-demo --chown=nextjs:nodejs /app/apps/demo/.next/static ./apps/demo/.next/static
COPY --from=installer-demo --chown=nextjs:nodejs /app/apps/demo/public ./apps/demo/public

USER nextjs

EXPOSE 3200

HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD node -e "require('http').get('http://localhost:3200/api/health', (r) => {process.exit(r.statusCode === 200 ? 0 : 1)})"

# Run standalone server
CMD node apps/demo/server.js
