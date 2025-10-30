# ============================================================================
# ReArq Worker - Dockerfile
# ============================================================================
# Production-ready async task queue with web UI and monitoring
# Based on: https://github.com/long2ice/rearq

FROM python:3.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install rearq with database support
# Pin compatible versions to avoid Pydantic/Tortoise conflicts
RUN pip install --no-cache-dir \
    "pydantic>=2.0,<2.10" \
    "tortoise-orm>=0.20.0,<0.21" \
    aiosqlite \
    async-timeout \
    rearq \
    redis

# Copy worker code and configuration
COPY services/rearq/main.py /app/main.py
# Copy server.py to /rearq_config (not /app to avoid volume mount conflicts)
COPY services/rearq/server.py /rearq_config/server.py
COPY services/rearq/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Create necessary directories
RUN mkdir -p /app/logs

# Expose rearq web UI port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8080/ || exit 1

# Set entrypoint
ENTRYPOINT ["/entrypoint.sh"]

# Default command: run rearq server (web UI + API)
CMD ["rearq", "main:rearq", "server", "--host", "0.0.0.0", "--port", "8080"]
