---
title: Docker Troubleshooting
description: Quick solutions for common Docker issues with Django-CFG. Fix build failures, connection problems, and configuration issues.
sidebar_label: Troubleshooting
sidebar_position: 5
keywords:
  - docker troubleshooting
  - docker debug
  - fix docker issues
  - docker common problems
---

# Docker Troubleshooting

> **📚 Part of**: [Docker Guide](./overview) - Return to Docker overview

Quick solutions for common Docker issues with Django-CFG.

---

## Quick Fixes

### ❌ "Package not found" with turbo prune

**Problem**: `turbo prune demo --docker` fails

**Solution**: Use FULL package name from `package.json`

```bash
# Check actual package name
grep '"name"' apps/demo/package.json

# Use full scoped name
RUN npx turbo@^2 prune @djangocfg/demo --docker  # ✅
RUN npx turbo@^2 prune demo --docker             # ❌
```

---

### ❌ 2GB+ context transfer

**Problem**: Docker build taking 10+ minutes to transfer context

**Solution**: Create or update `.dockerignore`

```dockerignore
**/node_modules/
**/.next/
**/dist/
**/.turbo/
**/build/
*.log
.git
```

**Verify**:
```bash
docker build . 2>&1 | grep "transferring context"
# Should be <1MB, not 2GB
```

---

### ❌ "ERR_PNPM_NO_GLOBAL_BIN_DIR"

**Problem**: `pnpm install -g` failing in Alpine

**Solution**: Use `npx` instead of global install

```dockerfile
# ❌ Don't use global install
RUN pnpm install -g turbo@^2

# ✅ Use npx instead
RUN npx turbo@^2 prune ...
```

---

### ❌ Next.js "server.js not found"

**Problem**: `Cannot find module '/app/server.js'`

**Solution**: Next.js standalone places server.js in root

```dockerfile
# Correct standalone output structure
COPY --from=builder /app/apps/demo/.next/standalone ./
CMD node server.js  # Root level, not apps/demo/server.js
```

---

### ❌ Poetry local path dependencies

**Problem**: `poetry install` failing with path dependencies

**Solution**: Remove local groups before lock

```dockerfile
RUN python3 -c "import re; \
    content = open('pyproject.toml').read(); \
    content = re.sub(r'\[tool\.poetry\.group\.local[^\]]*\][^\[]*', '', content, flags=re.DOTALL); \
    open('pyproject.toml', 'w').write(content)" \
    && poetry lock
```

---

### ❌ Docker image 4.84GB (should be ~300MB)

**Problem**: Next.js image too large

**Solution**: Copy ONLY standalone output, not entire `/app`

```dockerfile
# ❌ WRONG - copies everything
COPY --chown=nextjs:nodejs /app .

# ✅ CORRECT - copy only standalone
COPY --from=installer --chown=nextjs:nodejs /app/apps/demo/.next/standalone ./
COPY --from=installer --chown=nextjs:nodejs /app/apps/demo/.next/static ./apps/demo/.next/static
COPY --from=installer --chown=nextjs:nodejs /app/apps/demo/public ./apps/demo/public
```

**Verify**:
```bash
docker images | grep djangocfg-demo
# Should be ~300MB, not 4.84GB
```

---

## Build Issues

### Build Failing - Check Context Size

```bash
# Check what's being copied
docker build --no-cache . 2>&1 | grep "transferring context"

# If large (>10MB), update .dockerignore
echo "**/node_modules/" >> .dockerignore
echo "**/.next/" >> .dockerignore
```

### Build Cache Issues

```bash
# Full rebuild without cache
docker compose build --no-cache

# Remove all build cache
docker builder prune -af
```

### Out of Disk Space

```bash
# Check disk usage
docker system df

# Clean up
docker system prune -af --volumes
```

---

## Service Issues

### Services Won't Start

**Check status**:
```bash
docker compose ps
docker compose logs service-name
```

**Common causes**:
- Port already in use
- Configuration error
- Health check failing
- Dependency not ready

### Service Keeps Restarting

**Check logs**:
```bash
docker compose logs -f --tail=100 service-name
```

**Common issues**:
- Failed health check
- Incorrect CMD
- Missing environment variable
- Database not ready

### Health Check Failing

**Check health status**:
```bash
docker inspect container-name | grep -A 10 Health
```

**Test health endpoint manually**:
```bash
docker exec container-name curl -f http://localhost:8000/cfg/health/
```

---

## Configuration Issues

### Configuration Not Loading

**Check which config is loaded**:
```bash
docker exec django python -c "from api.environment.loader import env; print(env)"
```

**Verify file exists**:
```bash
docker exec django ls -la /app/api/environment/
```

**Check environment mode**:
```bash
docker exec django python -c "from api.environment.loader import env; print(env.env.env_mode)"
```

### Environment Variables Not Applied

**Check variable is set**:
```bash
docker exec django env | grep DATABASE_URL
```

**Verify docker-compose.yaml**:
```yaml
environment:
  DATABASE_URL: postgresql://...  # Make sure it's here
```

**Or check .env file**:
```bash
cat docker/.env | grep DATABASE_URL
```

---

## Database Issues

### Cannot Connect to Database

**Check PostgreSQL is running**:
```bash
docker compose ps djangocfg_postgres
docker exec djangocfg_postgres pg_isready -U postgres
```

**Test connection from Django**:
```bash
docker exec django python manage.py check --database default
```

**Check DATABASE_URL**:
```bash
docker exec django env | grep DATABASE_URL
```

### Database Extension Missing

**Problem**: `type "vector" does not exist`

**Solution**: Check init script is mounted

```yaml
postgres:
  volumes:
    - ./services/postgres/init.sql:/docker-entrypoint-initdb.d/init.sql:ro
```

**Verify extensions**:
```bash
docker exec djangocfg_postgres psql -U postgres -d djangocfg -c "\dx"
```

---

## Network Issues

### Port Already in Use

**Find process using port**:
```bash
lsof -i :8300
```

**Kill process**:
```bash
kill -9 <PID>
```

**Or change port** in docker-compose.yaml:
```yaml
ports:
  - "8301:8000"  # Changed from 8300
```

### Service Can't Reach Other Service

**Check networks**:
```bash
docker network ls
docker network inspect dockerdjangonetwork
```

**Verify service is in same network**:
```yaml
networks:
  - djangocfg-network  # Must be same
```

**Test connection**:
```bash
docker exec django ping postgres
```

---

## Performance Issues

### Slow Build Times

1. **Use .dockerignore** - Exclude unnecessary files
2. **Enable BuildKit** - `export DOCKER_BUILDKIT=1`
3. **Layer caching** - Don't change Dockerfile often
4. **Multi-stage builds** - Separate build/runtime stages

See [Build Optimization Guide](./build-optimization)

### Container Using Too Much Memory

**Check resource usage**:
```bash
docker stats
```

**Limit resources** in docker-compose.yaml:
```yaml
deploy:
  resources:
    limits:
      cpus: '2.0'
      memory: 4G
    reservations:
      memory: 512M
```

---

## Essential Commands

### Service Management

```bash
# Start all services
docker compose up -d

# Stop all services
docker compose stop

# Restart single service
docker compose restart django

# Remove all (keeps volumes)
docker compose down

# Remove all including volumes (⚠️ DELETES DATA)
docker compose down -v
```

### View Logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f django

# Last 50 lines
docker compose logs --tail=50 django

# With timestamps
docker compose logs -f --timestamps
```

### Execute Commands

```bash
# Django management
docker exec django python manage.py migrate
docker exec -it django python manage.py shell

# Database access
docker exec -it djangocfg_postgres psql -U postgres -d djangocfg

# Shell into container
docker exec -it django bash
```

### Check Status

```bash
# Service status
docker compose ps

# Container details
docker inspect django

# Resource usage
docker stats

# Disk usage
docker system df
```

---

## Clean Up Commands

### Remove Containers

```bash
# Stop and remove all
docker compose down

# Remove specific service
docker compose rm -f django
```

### Remove Images

```bash
# Remove specific image
docker rmi djangocfg-django:latest

# Remove all project images
docker compose down --rmi all

# Remove unused images
docker image prune -a
```

### Remove Volumes

```bash
# Remove all volumes (⚠️ DELETES DATA)
docker compose down -v

# Remove specific volume
docker volume rm docker_postgres_data

# Remove unused volumes
docker volume prune
```

### Complete Clean

```bash
# Nuclear option - removes everything
docker system prune -af --volumes
```

:::danger[Destructive Commands]
Commands with `-v` or `--volumes` flags will **permanently delete data**:
- Database files
- Uploaded media
- Application logs

**Always backup before running!**

```bash
# Backup database first
docker exec djangocfg_postgres pg_dump -U postgres djangocfg > backup.sql
```
:::

---

## Port Reference

| Service | Internal | External | Access |
|---------|----------|----------|--------|
| Django | 8000 | 8300 | http://localhost:8300 |
| Demo | 3000 | 3300 | http://localhost:3300 |
| Web | 3000 | 3301 | http://localhost:3301 |
| WebSocket | 9065 | 9065 | ws://localhost:9065 |
| Traefik | 80 | 380 | http://localhost:380 |
| Traefik HTTPS | 443 | 743 | https://localhost:743 |
| Traefik Dashboard | 8080 | 8390 | http://localhost:8390 |

---

## Troubleshooting Checklist

### Build Failures
- [ ] Check `.dockerignore` exists
- [ ] Verify package names in turbo prune
- [ ] Use `npx` instead of global install
- [ ] Check build context size
- [ ] Try build with `--no-cache`

### Service Won't Start
- [ ] Check logs: `docker compose logs service`
- [ ] Verify ports not in use: `lsof -i :port`
- [ ] Check environment variables set
- [ ] Verify dependencies healthy
- [ ] Test health endpoint

### Configuration Issues
- [ ] Check config file exists in container
- [ ] Verify environment mode (dev/prod)
- [ ] Test config loading in shell
- [ ] Check .env file values
- [ ] Verify docker-compose environment

### Database Problems
- [ ] PostgreSQL service healthy
- [ ] DATABASE_URL correct
- [ ] Extensions installed
- [ ] Migrations run
- [ ] Connection from Django works

### Performance Issues
- [ ] Check `.dockerignore` configured
- [ ] Verify multi-stage builds used
- [ ] Monitor with `docker stats`
- [ ] Check resource limits set
- [ ] Review build cache strategy

---

## Next Steps

**Build optimization**:
[Build Optimization Guide →](./build-optimization)

**Configuration deep dive**:
[Configuration Strategy →](./configuration)

**Production deployment**:
[Production Setup →](./production)

---

## See Also

### Docker Guides
- **[Docker Overview](./overview)** - Complete Docker guide
- **[Development Setup](./development)** - Local environment
- **[Production Setup](./production)** - Deploy to production
- **[Configuration](./configuration)** - YAML + env vars
- **[Build Optimization](./build-optimization)** - Performance tips

### External Resources
- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Reference](https://docs.docker.com/compose/)
- [Dockerfile Best Practices](https://docs.docker.com/develop/dev-best-practices/)

---

TAGS: docker, troubleshooting, debugging, quick-fixes
DEPENDS_ON: [docker, docker-compose]
USED_BY: [development, production, debugging]
