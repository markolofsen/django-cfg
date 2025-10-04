# 🐳 Django-CFG Example - Redis Cache & Message Broker
FROM redis:7-alpine

LABEL maintainer="Django-CFG Team" \
      description="Redis cache and message broker for Django-CFG Example"

# Copy custom redis configuration
COPY redis.conf /usr/local/etc/redis/redis.conf

# Health check
HEALTHCHECK --interval=10s --timeout=3s --retries=5 \
  CMD redis-cli ping || exit 1

# Use custom config
CMD ["redis-server", "/usr/local/etc/redis/redis.conf"]
