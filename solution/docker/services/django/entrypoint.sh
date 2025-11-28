#!/bin/bash
set -e

# Remove host's .venv if it exists (incompatible with container environment)
if [ -d "/app/.venv" ]; then
  echo "Removing incompatible host .venv directory..."
  rm -rf /app/.venv
fi

# Extract DB host from DATABASE__URL or use default
DB_HOST="${DB_HOST:-$(echo $DATABASE__URL | sed -E 's/.*@([^:]+):.*/\1/' || echo 'postgres')}"

echo "Waiting for postgres at ${DB_HOST}:5432..."
while ! nc -z ${DB_HOST} 5432; do
  sleep 0.1
done
echo "PostgreSQL started at ${DB_HOST}:5432"

echo "Waiting for redis..."
while ! nc -z redis 6379; do
  sleep 0.1
done
echo "Redis started"

# Run migrations
echo "Running migrations..."
python manage.py migrate --noinput

# Create default superuser for development
if [ "${DJANGO_CREATE_ADMIN:-true}" = "true" ]; then
  echo "Creating default admin user..."
  python manage.py superuser \
    --username admin \
    --email admin@example.com \
    --password admin123 \
    --first-name Admin \
    --last-name User 2>&1 | grep -E "(✅|❌|already exists)" || true
fi

# Note: collectstatic not needed - using whitenoise for static files

# Execute the command passed to the script
exec "$@"
