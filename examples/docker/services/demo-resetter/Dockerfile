# ═════════════════════════════════════════════════════════════════
# Django-CFG Demo Database Auto-Resetter
# Lightweight container that resets demo database on schedule
# ═════════════════════════════════════════════════════════════════

FROM docker:27-cli

# Install bash and curl for scripting
RUN apk add --no-cache bash curl

# Set working directory
WORKDIR /app

# Copy the reset script
COPY docker/services/demo-resetter/db-reset.sh /app/db-reset.sh
RUN chmod +x /app/db-reset.sh

# Healthcheck - check if script is running
HEALTHCHECK --interval=60s --timeout=5s --start-period=10s --retries=3 \
    CMD pgrep -f db-reset.sh > /dev/null || exit 1

# Run the reset script
CMD ["/app/db-reset.sh"]
