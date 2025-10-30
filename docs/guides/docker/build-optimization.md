---
title: Docker Build Optimization
description: Critical Docker build lessons learned from Django-CFG development. Optimize multi-stage builds, reduce context size, and fix common issues.
sidebar_label: Build Optimization
sidebar_position: 4
keywords:
  - docker build optimization
  - reduce docker image size
  - docker multi-stage builds
  - docker context optimization
  - turborepo docker
---

# Docker Build Optimization

> **📚 Part of**: [Docker Guide](./overview) - Return to Docker overview

Critical lessons learned from optimizing Django-CFG Docker builds. Real issues, real solutions.

---

## Performance Results

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Context size | 2.13GB | 280KB | **99.98%** |
| Context transfer | 380s | 4s | **95x faster** |
| Build time | Timeout | ~10min | **Completes** |
| Image size (Next.js) | 4.84GB | ~300MB | **16x smaller** |

---

## Critical Issues & Solutions

### 1. Node.js Monorepo - 2GB Context Problem ⚠️

**Problem**: Docker build copying 2GB+ of `node_modules` into build context, taking 10+ minutes.

**Root Cause**:
- Dockerfile copying entire workspace including all `node_modules/`
- No `.dockerignore` file to exclude unnecessary files

**Solution**:

Create `.dockerignore`:
```dockerignore
**/node_modules/
**/.next/
**/dist/
**/.turbo/
**/build/
```

**Impact**: **2.13GB → 280KB** (7000x improvement)

---

### 2. Turborepo - Package Name Consistency ⚠️

**Problem**: Turbo commands failed with "Package with name demo not found"

**Errors**:
```bash
# During prune
Invalid scope. Package with name demo in `package.json` not found.

# During build
No package found with name 'demo' in workspace
```

**Root Cause**: Turborepo expects FULL package name from `package.json`, not folder name

**Solution**: Use full scoped package name consistently

```dockerfile
# ❌ WRONG
RUN turbo prune demo --docker
RUN pnpm turbo run build --filter=demo

# ✅ CORRECT - use full package name everywhere
RUN npx turbo@^2 prune @djangocfg/demo --docker
RUN pnpm turbo run build --filter=@djangocfg/demo
```

**Check package name**:
```bash
grep '"name"' apps/demo/package.json
# Output: "name": "@djangocfg/demo"
```

---

### 3. Global pnpm Installation in Alpine ⚠️

**Problem**: `pnpm add -g turbo@^2` failed with:

```
ERR_PNPM_NO_GLOBAL_BIN_DIR  Unable to find the global bin directory
```

**Root Cause**: pnpm global installation requires `PNPM_HOME` setup in Alpine Linux

**Solution**: Use `npx` instead of global installation

```dockerfile
# ❌ WRONG
RUN pnpm install -g turbo@^2
RUN turbo prune demo --docker

# ✅ CORRECT
RUN npx turbo@^2 prune @djangocfg/demo --docker
```

**Why it works**: `npx` downloads and executes packages on-demand without global setup

---

### 4. Next.js Standalone - Missing server.js ⚠️

**Problem**: CMD referenced non-existent `apps/demo/server.js`

**Root Cause**: Next.js standalone mode generates `server.js` at `.next/standalone/server.js`

**Documentation**: https://nextjs.org/docs/app/api-reference/config/next-config-js/output

**Solution**:
```dockerfile
# Copy standalone output structure
COPY --from=installer --chown=nextjs:nodejs /app/apps/demo/.next/standalone ./
COPY --from=installer --chown=nextjs:nodejs /app/apps/demo/.next/static ./apps/demo/.next/static
COPY --from=installer --chown=nextjs:nodejs /app/apps/demo/public ./apps/demo/public

# Run from root where standalone places server.js
CMD node server.js
```

**Important**:
- Standalone output creates self-contained deployment
- `server.js` is in root of standalone output, not in app directory
- Must also copy `.next/static` and `public` separately

---

### 5. Poetry Local Path Dependencies ⚠️

**Problem**: Poetry lockfile contains local path dependencies that don't exist in Docker

**Error Pattern**:
```python
[tool.poetry.dependencies]
some-package = { path = "../local-package", develop = true }
```

**Solution**: Remove local dependency groups before installing

```dockerfile
RUN python3 -c "\
    import re; \
    content = open('pyproject.toml').read(); \
    content = re.sub(r'\[tool\.poetry\.group\.local[^\]]*\][^\[]*', '', content, flags=re.DOTALL); \
    open('pyproject.toml', 'w').write(content)" \
    && poetry lock \
    && poetry install --only main --no-root
```

---

### 6. Next.js Image Size - 4.84GB Problem ⚠️⚠️

**Problem**: Docker image was 4.84GB instead of ~300MB

**Symptoms**:
```bash
docker images | grep djangocfg-demo
# djangocfg-demo   latest   dd77ab0d53f2   4.84GB  ❌
```

**Root Cause**: Docker was copying entire `/app` from installer stage, including:
- All source code
- All node_modules (~1.5GB+)
- All .next/cache folders
- Build artifacts
- Package manager caches

**Incorrect Pattern**:
```dockerfile
# ❌ WRONG - Copies everything from installer stage
FROM node:20-alpine AS runner
COPY --chown=nextjs:nodejs /app .
CMD ["pnpm", "--filter", "@djangocfg/demo", "start"]
```

**Correct Pattern**:
```dockerfile
# ✅ CORRECT - Copies only standalone output
FROM node:20-alpine AS runner
COPY --from=installer --chown=nextjs:nodejs /app/apps/demo/.next/standalone ./
COPY --from=installer --chown=nextjs:nodejs /app/apps/demo/.next/static ./apps/demo/.next/static
COPY --from=installer --chown=nextjs:nodejs /app/apps/demo/public ./apps/demo/public
CMD node server.js
```

**Why it matters**:
- Next.js `standalone` output already contains minimal `node_modules`
- Standalone output is self-contained and optimized
- Copying entire `/app` duplicates everything unnecessarily

**Expected Result**: **~300-500MB** (instead of 4.84GB)

**Debug**:
```bash
# Check image layer sizes
docker history djangocfg-demo:latest --human --no-trunc | head -20

# Look for large COPY layers - should be ~300MB max
```

---

### 7. Django Static Files - Whitenoise ⚠️

**Problem**: `collectstatic` causing infinite loops and container restarts

**Symptoms**:
- `django-rearq` container constantly restarting
- Stuck at `Collecting static files...` step
- Health checks never passing

**Root Cause**: Project uses **Whitenoise**, making `collectstatic` unnecessary

**Solution**: Remove `collectstatic` from entrypoint

```bash
# ❌ WRONG - Not needed with Whitenoise
echo "Collecting static files..."
python manage.py collectstatic --noinput

# ✅ CORRECT - Whitenoise handles static files
# Note: collectstatic not needed - using whitenoise for static files
```

**Why Whitenoise**:
- Serves static files directly from Django
- No separate web server needed for statics
- No volume mounts required
- Zero-configuration in production

---

### 8. WebSocket Service - File Structure ⚠️

**Problem**: WebSocket container failed with `can't open file '/app/main.py'`

**Root Cause**: Project has `src/main.py` but Dockerfile CMD referenced `/app/main.py`

**Solution**: Update CMD to match structure

```dockerfile
# ❌ WRONG
CMD ["python", "main.py"]

# ✅ CORRECT
CMD ["python", "src/main.py"]
```

---

### 9. PostgreSQL Extensions - Auto-initialization ⚠️

**Problem**: Django migrations failed with `type "vector" does not exist`

**Root Cause**: pgvector Docker image doesn't auto-enable the extension

**Solution**: Create init SQL script

```sql
-- /docker/services/postgres/init.sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS vector;  -- For AI/vector operations
SET timezone = 'UTC';
```

**Mount in docker-compose**:
```yaml
postgres:
  image: pgvector/pgvector:pg15
  volumes:
    - ./volumes/postgres:/var/lib/postgresql/data
    - ./services/postgres/init.sql:/docker-entrypoint-initdb.d/init.sql:ro
```

**Important**: Scripts in `/docker-entrypoint-initdb.d/` run ONLY on first initialization

---

### 10. Django-CFG CORS Configuration ⚠️

**Problem**: `DJANGO_CORS_ALLOWED_ORIGINS` causing parsing errors

**Error**:
```
error parsing value for field "cors_allowed_origins" from source "DotEnvSettingsSource"
```

**Root Cause**: Django-CFG manages CORS automatically through `security_domains`

**Solution**:

1. Remove explicit `CORS_ALLOWED_ORIGINS` env vars
2. Configure via `security_domains` in YAML:

```yaml
security_domains:
  - "localhost"
  - "127.0.0.1"
  - "example.com"
```

**Why it works**: Django-CFG auto-generates CORS settings from security_domains

---

## Optimal Multi-Stage Build Pattern

### For Next.js + Turborepo

```dockerfile
# Stage 1: Base with dependencies
FROM node:20-alpine AS base
RUN apk update && apk add --no-cache libc6-compat
WORKDIR /app

# Stage 2: Prune monorepo
FROM base AS pruner
RUN corepack enable && corepack prepare pnpm@9.15.4 --activate
COPY . .
RUN npx turbo@^2 prune @djangocfg/demo --docker

# Stage 3: Install and build
FROM base AS installer
RUN corepack enable && corepack prepare pnpm@9.15.4 --activate
COPY --from=pruner /app/out/json/ .
RUN pnpm install
COPY --from=pruner /app/out/full/ .
RUN pnpm turbo run build --filter=@djangocfg/demo

# Stage 4: Production runtime (minimal!)
FROM node:20-alpine AS runner
WORKDIR /app
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

# ✅ CRITICAL: Copy ONLY standalone output
COPY --from=installer --chown=nextjs:nodejs /app/apps/demo/.next/standalone ./
COPY --from=installer --chown=nextjs:nodejs /app/apps/demo/.next/static ./apps/demo/.next/static
COPY --from=installer --chown=nextjs:nodejs /app/apps/demo/public ./apps/demo/public

USER nextjs
CMD node server.js
```

---

## Key Takeaways

1. ✅ **Always use .dockerignore** - Exclude `node_modules`, `.next`, `dist`
2. ✅ **Turborepo needs full package names** - From `package.json`
3. ✅ **Use npx in Alpine** - Avoid global installation complexity
4. ✅ **Next.js standalone is self-contained** - Copy ONLY standalone output
5. ✅ **Remove local Poetry dependencies** - Before Docker lock
6. ✅ **Multi-stage builds are essential** - Separate deps/build/runtime
7. ✅ **Test context size first** - Check "transferring context" time
8. ✅ **Always check final image size** - Use `docker images` and `docker history`
9. ✅ **Whitenoise eliminates collectstatic** - Never run in Docker
10. ✅ **Match Dockerfile CMD to structure** - Check file paths

---

## Debugging Commands

```bash
# Check context transfer size
docker build --no-cache . 2>&1 | grep "transferring context"

# Verify package names in monorepo
grep -r '"name"' apps/*/package.json packages/*/package.json

# Test turbo prune locally
npx turbo@latest prune @package/name --docker
ls -la out/

# Check Next.js standalone output
cd apps/demo/.next/standalone
ls -la

# Check image sizes
docker images | grep djangocfg

# Inspect layer sizes
docker history djangocfg-demo:latest --human --no-trunc | head -20

# Monitor build in real-time
docker compose up --build 2>&1 | tee build.log
tail -f build.log
```

---

## Next Steps

**Apply optimizations**:
[Development Setup →](./development)

**Production deployment**:
[Production Guide →](./production)

**Common issues**:
[Troubleshooting →](./troubleshooting)

---

## See Also

### Docker Guides
- **[Docker Overview](./overview)** - Complete Docker guide
- **[Development Setup](./development)** - Local environment
- **[Production Setup](./production)** - Deploy to production
- **[Configuration](./configuration)** - YAML + env vars
- **[Troubleshooting](./troubleshooting)** - Quick fixes

### External Resources
- [Turborepo Docker Guide](https://turborepo.com/docs/guides/tools/docker)
- [Next.js Standalone Output](https://nextjs.org/docs/app/api-reference/config/next-config-js/output)
- [pnpm in Docker](https://pnpm.io/docker)
- [Docker Multi-stage Builds](https://docs.docker.com/build/building/multi-stage/)
- [Whitenoise Documentation](http://whitenoise.evans.io/)

---

TAGS: docker, build-optimization, multi-stage-builds, performance, turborepo, rearq
DEPENDS_ON: [docker, turborepo, nextjs, poetry]
USED_BY: [development, production, ci-cd]
