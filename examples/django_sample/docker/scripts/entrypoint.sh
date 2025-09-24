#!/bin/bash
# 🚀 ReformsAI Django - Application Entrypoint
# Handles Django startup, migrations, and static files

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to wait for service
wait_for_service() {
    local host=$1
    local port=$2
    local service_name=$3
    local max_attempts=30
    local attempt=1

    log_info "Waiting for $service_name at $host:$port..."
    
    while ! nc -z "$host" "$port" >/dev/null 2>&1; do
        if [ $attempt -eq $max_attempts ]; then
            log_error "Failed to connect to $service_name after $max_attempts attempts"
            exit 1
        fi
        sleep 2
        ((attempt++))
    done
    
    log_info "$service_name is ready!"
}

# Function to wait for database
wait_for_database() {
    if [[ -n "${DATABASE_URL}" ]]; then
        # Parse DATABASE_URL (format: postgresql://user:pass@host:port/db)
        DB_HOST=$(echo "$DATABASE_URL" | sed -n 's/.*@\([^:]*\):.*/\1/p')
        DB_PORT=$(echo "$DATABASE_URL" | sed -n 's/.*:\([0-9]*\)\/.*/\1/p')
        
        if [[ -n "$DB_HOST" && -n "$DB_PORT" ]]; then
            wait_for_service "$DB_HOST" "$DB_PORT" "PostgreSQL"
        fi
    else
        log_warn "DATABASE_URL not set, skipping database check"
    fi
}

# Function to run migrations
run_migrations() {
    log_info "Running Django CFG smart migrations..."
    # Use poetry run to execute migrator with proper environment
    poetry run migrator --auto
    log_info "Migrations completed"
}

# Function to start Django server
start_server() {
    log_info "Starting Django server..."
    log_info "Port: ${PORT:-8000}"
    log_info "Environment: ${ENVIRONMENT:-development}"
    
    exec python manage.py runserver "0.0.0.0:${PORT:-8000}" --noreload
}

# Function to show help
show_help() {
    echo "ReformsAI Django Docker Entrypoint"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  runserver    Start Django development server (default)"
    echo "  migrate      Run migrations only"
    echo "  shell        Start Django shell"
    echo "  help         Show this help message"
    echo ""
    echo "Environment Variables:"
    echo "  DATABASE_URL              PostgreSQL connection URL"
    echo "  PORT                      Server port (default: 8000)"
    echo "  DJANGO_SUPERUSER_USERNAME Superuser username"
    echo "  DJANGO_SUPERUSER_EMAIL    Superuser email"
    echo "  DJANGO_SUPERUSER_PASSWORD Superuser password"
}

# Main execution
main() {
    local command=${1:-runserver}
    
    log_info "ReformsAI Django Container Starting..."
    log_info "Command: $command"
    log_info "Environment: ${ENVIRONMENT:-development}"
    
    # No virtual environment - packages installed globally
    
    case "$command" in
        "runserver")
            wait_for_database
            run_migrations
            log_info "Starting Django development server..."
            # Use poetry run for consistent environment
            exec poetry run python manage.py runserver "0.0.0.0:${PORT:-8000}" --noreload
            ;;
        "migrate")
            wait_for_database
            run_migrations
            log_info "Migrations completed, exiting"
            ;;
        "shell")
            wait_for_database
            log_info "Starting Django shell..."
            # Use poetry run for consistent environment
            exec poetry run python manage.py shell
            ;;
        "help"|"--help"|"-h")
            show_help
            ;;
        *)
            log_error "Unknown command: $command"
            show_help
            exit 1
            ;;
    esac
}

# Execute main function with all arguments
main "$@"