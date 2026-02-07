# ============================================================================
# Django-CFG API Server - Dockerfile
# ============================================================================

FROM python:3.12-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:0.6.0 /uv /uvx /bin/

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_SYSTEM_PYTHON=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    libpq-dev \
    netcat-openbsd \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Install grpc_health_probe for gRPC health checks
RUN GRPC_HEALTH_PROBE_VERSION=v0.4.25 && \
    curl -L https://github.com/grpc-ecosystem/grpc-health-probe/releases/download/${GRPC_HEALTH_PROBE_VERSION}/grpc_health_probe-linux-amd64 -o /usr/local/bin/grpc_health_probe && \
    chmod +x /usr/local/bin/grpc_health_probe

# Set working directory
WORKDIR /app

# Copy pyproject.toml only
COPY projects/django/pyproject.toml ./

# Install dependencies (production only)
# 1. uv pip installs all dependencies from pyproject.toml
# 2. Upgrades django-cfg to latest version (ensures fresh security patches)
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install -r pyproject.toml --no-dev && \
    uv pip install --upgrade django-cfg[full] uvicorn[standard]

# Copy application code
COPY projects/django /app

# Copy entrypoint script
COPY docker/services/django/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Create necessary directories
RUN mkdir -p /app/logs /app/staticfiles /app/media /app/logs

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/cfg/health/ || exit 1

# Set entrypoint
ENTRYPOINT ["/entrypoint.sh"]

# Default command (can be overridden in docker-compose)
# Using uvicorn with ASGI for async support (4 workers for production)
CMD ["uvicorn", "api.asgi:application", "--host", "0.0.0.0", "--port", "8000", "--workers", "4", "--timeout-keep-alive", "120", "--log-level", "info"]
