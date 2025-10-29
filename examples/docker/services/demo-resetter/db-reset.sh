#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════
# Django-CFG Demo Database Auto-Reset Script
# Automatically resets the database every N minutes for demo purposes
# ═══════════════════════════════════════════════════════════════════════════

set -e

# Configuration from environment variables
RESET_INTERVAL=${DEMO_RESET_INTERVAL_MINUTES:-10}
DJANGO_CONTAINER=${DJANGO_CONTAINER_NAME:-django-cfg-django}
ADMIN_USERNAME=${DEMO_ADMIN_USERNAME:-admin}
ADMIN_EMAIL=${DEMO_ADMIN_EMAIL:-admin@example.com}
ADMIN_PASSWORD=${DEMO_ADMIN_PASSWORD:-admin123}
ADMIN_FIRSTNAME=${DEMO_ADMIN_FIRSTNAME:-Demo}
ADMIN_LASTNAME=${DEMO_ADMIN_LASTNAME:-Admin}

echo "═══════════════════════════════════════════════════════════════"
echo "🔄 Django-CFG Demo Database Auto-Resetter"
echo "═══════════════════════════════════════════════════════════════"
echo "📅 Reset interval: ${RESET_INTERVAL} minutes"
echo "🐳 Target container: ${DJANGO_CONTAINER}"
echo "👤 Admin user: ${ADMIN_USERNAME} (${ADMIN_EMAIL})"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Function to check if Django container is healthy
wait_for_django() {
    echo "⏳ Waiting for Django container to be healthy..."
    local max_attempts=60
    local attempt=0

    while [ $attempt -lt $max_attempts ]; do
        if docker exec $DJANGO_CONTAINER curl -f -s http://localhost:8000/cfg/health/ > /dev/null 2>&1; then
            echo "✅ Django is healthy!"
            return 0
        fi
        attempt=$((attempt + 1))
        sleep 2
    done

    echo "❌ Django container did not become healthy in time"
    return 1
}

# Function to reset database
reset_database() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo ""
    echo "╔═══════════════════════════════════════════════════════════════╗"
    echo "║  🔄 Starting Database Reset - $timestamp"
    echo "╚═══════════════════════════════════════════════════════════════╝"

    # Step 1: Drop and recreate all tables (flush)
    echo "🗑️  Step 1/4: Flushing database..."
    if docker exec $DJANGO_CONTAINER python manage.py flush --noinput 2>&1 | grep -v "RuntimeWarning"; then
        echo "   ✅ Database flushed successfully"
    else
        echo "   ❌ Failed to flush database"
        return 1
    fi

    # Step 2: Run migrations (ensure schema is up to date)
    echo "📦 Step 2/4: Running migrations..."
    if docker exec $DJANGO_CONTAINER python manage.py migrate --noinput 2>&1 | grep -v "RuntimeWarning"; then
        echo "   ✅ Migrations completed"
    else
        echo "   ❌ Failed to run migrations"
        return 1
    fi

    # Step 3: Create superuser
    echo "👤 Step 3/4: Creating admin user..."
    if docker exec $DJANGO_CONTAINER python manage.py superuser \
        --username "$ADMIN_USERNAME" \
        --email "$ADMIN_EMAIL" \
        --password "$ADMIN_PASSWORD" \
        --first-name "$ADMIN_FIRSTNAME" \
        --last-name "$ADMIN_LASTNAME" 2>&1 | grep -E "(✅|created|already exists)" | head -1; then
        echo "   ✅ Admin user ready"
    else
        echo "   ⚠️  Admin user creation skipped (may already exist)"
    fi

    # Step 4: Populate sample data
    echo "📊 Step 4/4: Populating sample data..."
    if docker exec $DJANGO_CONTAINER python manage.py populate_sample_data 2>&1 | grep -v "RuntimeWarning"; then
        echo "   ✅ Sample data populated"
    else
        echo "   ⚠️  Sample data population completed with warnings"
    fi

    echo ""
    echo "✅ Database reset completed successfully!"
    echo "═══════════════════════════════════════════════════════════════"
}

# Initial wait for Django to be ready
if ! wait_for_django; then
    echo "❌ Failed to connect to Django. Exiting..."
    exit 1
fi

echo "🚀 Demo resetter is running!"
echo "⏰ Next reset will happen in ${RESET_INTERVAL} minutes"
echo ""

# Main loop - reset database on interval
reset_count=0
while true; do
    # Calculate sleep time in seconds
    sleep_seconds=$((RESET_INTERVAL * 60))

    # Wait for the interval
    echo "💤 Sleeping for ${RESET_INTERVAL} minutes until next reset..."
    sleep $sleep_seconds

    # Increment reset counter
    reset_count=$((reset_count + 1))

    # Reset the database
    echo ""
    echo "🔔 Reset #${reset_count} triggered!"
    if reset_database; then
        echo "🎉 Reset #${reset_count} completed successfully!"
    else
        echo "⚠️  Reset #${reset_count} completed with errors"
    fi

    echo ""
    echo "⏰ Next reset will happen in ${RESET_INTERVAL} minutes"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
done
