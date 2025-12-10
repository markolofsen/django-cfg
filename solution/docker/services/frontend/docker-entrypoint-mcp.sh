#!/bin/sh
# Docker entrypoint for MCP server
# Runs database migrations before starting the server

set -e

echo "Running database migrations..."
npx drizzle-kit push --force 2>/dev/null || {
    echo "Warning: Migration failed (database may not be ready yet)"
    echo "The server will start anyway and retry on first request"
}

echo "Starting MCP server..."
exec "$@"
