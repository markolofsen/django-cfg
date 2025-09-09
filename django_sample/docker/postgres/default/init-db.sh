#!/bin/bash
# UnrealOS Django Database Initialization Script
# Creates unrealos_db database with proper configuration

# Use POSTGRES_USER environment variable or default to postgres
DB_USER=${POSTGRES_USER:-postgres}
MAIN_DB=${POSTGRES_DB:-unrealos_db}

echo "🔧 Initializing UnrealOS Django database..."

# Connect to postgres database (which always exists) to create databases
echo "📁 Creating main database: $MAIN_DB"
psql -U "$DB_USER" -d postgres -tc "SELECT 1 FROM pg_database WHERE datname = '$MAIN_DB'" | grep -q 1 || \
psql -U "$DB_USER" -d postgres -c "CREATE DATABASE $MAIN_DB;"

# Create user if it doesn't exist (for databases that need specific users)
if [ "$DB_USER" != "postgres" ]; then
    echo "👤 Creating user: $DB_USER"
    psql -U postgres -d postgres -tc "SELECT 1 FROM pg_user WHERE usename = '$DB_USER'" | grep -q 1 || \
    psql -U postgres -d postgres -c "CREATE USER $DB_USER WITH PASSWORD '$POSTGRES_PASSWORD';"

    # Grant privileges to the user on the database
    echo "🔐 Granting privileges on $MAIN_DB to $DB_USER"
    psql -U postgres -d postgres -c "GRANT ALL PRIVILEGES ON DATABASE $MAIN_DB TO $DB_USER;"
fi

# Set up database extensions and configuration
echo "🔧 Setting up database extensions..."
psql -U "$DB_USER" -d "$MAIN_DB" -c "CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";"
psql -U "$DB_USER" -d "$MAIN_DB" -c "CREATE EXTENSION IF NOT EXISTS \"pg_trgm\";"

# Set timezone
echo "🕐 Setting timezone to UTC..."
psql -U "$DB_USER" -d "$MAIN_DB" -c "SET timezone = 'UTC';"

echo "✅ UnrealOS Django database initialized successfully!"