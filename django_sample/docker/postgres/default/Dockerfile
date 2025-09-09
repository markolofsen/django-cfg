FROM postgres:16-alpine

# Copy initialization script
COPY init-db.sh /docker-entrypoint-initdb.d/

# Make script executable
RUN chmod +x /docker-entrypoint-initdb.d/init-db.sh

# Set default environment variables (password will be set via docker-compose)
ENV POSTGRES_DB=unrealos_db
ENV POSTGRES_USER=unrealos

# Expose PostgreSQL port
EXPOSE 5432

# Use the default PostgreSQL entrypoint
ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["postgres"]