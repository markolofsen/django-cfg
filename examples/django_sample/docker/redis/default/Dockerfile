FROM redis:7-alpine

# Copy Redis configuration
COPY redis.conf /usr/local/etc/redis/redis.conf

# Create data directory
RUN mkdir -p /data

# Expose Redis port
EXPOSE 6379

# Use custom configuration
CMD ["redis-server", "/usr/local/etc/redis/redis.conf"]
