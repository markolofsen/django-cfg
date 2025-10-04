# 🐳 Django-CFG Example - PostgreSQL Database
FROM postgres:16-alpine

LABEL maintainer="Django-CFG Team" \
      description="PostgreSQL database for Django-CFG Example"

# Copy initialization scripts
COPY init-db.sh /docker-entrypoint-initdb.d/

# Set executable permissions
RUN chmod +x /docker-entrypoint-initdb.d/init-db.sh

# Health check
HEALTHCHECK --interval=10s --timeout=5s --retries=5 \
  CMD pg_isready -U ${POSTGRES_USER:-django_cfg_example} || exit 1
