# Setup Guide

First-time setup for your Django-CFG project.

## Prerequisites

- Python 3.12+
- Poetry (recommended) or pip
- PostgreSQL (recommended) or SQLite

## Step 1: Navigate to Django Project

```bash
cd projects/django
```

## Step 2: Configure Environment

Edit the environment file:

```bash
nano api/environment/.env
```

**Required settings:**

```env
# Database (PostgreSQL recommended)
DATABASE__URL=postgresql://user:password@localhost:5432/mydb

# For SQLite (development only)
DATABASE__URL=sqlite:///db/default.sqlite3

# Security (generate with: python -c "import secrets; print(secrets.token_hex(32))")
SECRET_KEY=your-secret-key-at-least-32-characters
```

## Step 3: Install Dependencies

```bash
poetry install
```

Or with pip:

```bash
pip install -r requirements.txt
```

## Step 4: Run Migrations

```bash
poetry run python manage.py migrate
```

## Step 5: Create Superuser

```bash
poetry run python manage.py superuser
```

Follow the interactive prompts to create an admin account.

## Step 6: Start Development Server

```bash
poetry run python manage.py runserver
```

Access your application:
- Admin: http://localhost:8000/admin/
- API Docs: http://localhost:8000/api/docs/
- Health Check: http://localhost:8000/cfg/health/

## Next Steps

- Configure additional services in `api/environment/.env`
- Customize `api/config.py` for your needs
- Read [Configuration Guide](./CONFIGURATION.md)
- Set up [Docker](./DOCKER.md) for deployment

## Troubleshooting

### Database Connection Error

Ensure PostgreSQL is running and credentials are correct:

```bash
# Test connection
psql -h localhost -U user -d mydb
```

### Poetry Not Found

Install Poetry:

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

### Permission Denied

Make sure you have write permissions:

```bash
chmod -R 755 .
```
