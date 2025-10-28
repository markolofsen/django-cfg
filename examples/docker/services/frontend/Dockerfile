# ═════════════════════════════════════════════════════════════════
# Django-CFG Frontend - Admin App
# Optimized with standalone output
# ═════════════════════════════════════════════════════════════════

FROM node:20-alpine AS base
RUN apk update && apk add --no-cache libc6-compat
WORKDIR /app

# ─────────────────────────────────────────────────────────────────
# Installer Stage - Install dependencies and build admin
# ─────────────────────────────────────────────────────────────────

FROM base AS installer-admin
RUN corepack enable && corepack prepare pnpm@9.15.4 --activate

# Copy workspace files
COPY projects/django_admin/apps/admin/package.json ./
COPY projects/django_admin/apps/admin/pnpm-lock.yaml ./

# Install dependencies
RUN pnpm install --frozen-lockfile

# Copy source code
COPY projects/django_admin/apps/admin .

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

# Build the admin app
RUN pnpm build:docker

# ─────────────────────────────────────────────────────────────────
# Runner Stage - Admin App (port 3200)
# ─────────────────────────────────────────────────────────────────

FROM node:20-alpine AS admin
WORKDIR /app

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1
ENV PORT=3200
ENV HOSTNAME="0.0.0.0"

# Create non-root user
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

# Copy only standalone output (Next.js automatically generates this)
COPY --from=installer-admin --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=installer-admin --chown=nextjs:nodejs /app/.next/static ./.next/static
COPY --from=installer-admin --chown=nextjs:nodejs /app/public ./public

USER nextjs

EXPOSE 3200

HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD node -e "require('http').get('http://localhost:3200/api/health', (r) => {process.exit(r.statusCode === 200 ? 0 : 1)})"

# Run standalone server
CMD node server.js
