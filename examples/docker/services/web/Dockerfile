# ═════════════════════════════════════════════════════════════════
# Django-CFG Main Site - Docusaurus
# ═════════════════════════════════════════════════════════════════

FROM node:20-alpine AS base
WORKDIR /app
RUN corepack enable && corepack prepare npm@latest --activate

# Install dependencies
FROM base AS deps
COPY projects/web/package.json projects/web/package-lock.json* ./
RUN npm ci

# Build stage
FROM base AS builder
WORKDIR /app

# Copy dependencies from deps stage
COPY --from=deps /app/node_modules ./node_modules
COPY projects/web ./

# Build arguments
ARG DJANGO_API_URL
ARG DEMO_URL

ENV NODE_ENV=production

RUN npm run build

# ─────────────────────────────────────────────────────────────────
# Runner Stage - Docusaurus Site (port 3201)
# ─────────────────────────────────────────────────────────────────

FROM node:20-alpine AS runner
WORKDIR /app

ENV NODE_ENV=production
ENV PORT=3201
ENV HOST=0.0.0.0

RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 docusaurus

# Install serve for static file serving
RUN npm install -g serve

# Copy build output
COPY --from=builder --chown=docusaurus:nodejs /app/build ./build

USER docusaurus

EXPOSE 3201

HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:3201/ || exit 1

CMD ["serve", "-s", "build", "-l", "3201"]
