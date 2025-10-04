#!/bin/bash
# 🐳 Django-CFG Example - PostgreSQL Initialization Script
set -e

echo "🔧 Initializing Django-CFG Example database..."

# Create database if it doesn't exist
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    -- Database already created by POSTGRES_DB env var
    SELECT 'Database created: $POSTGRES_DB' AS status;

    -- Create extensions
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
    CREATE EXTENSION IF NOT EXISTS "pg_trgm";

    -- Grant permissions
    GRANT ALL PRIVILEGES ON DATABASE $POSTGRES_DB TO $POSTGRES_USER;
EOSQL

echo "✅ Database initialization completed"
