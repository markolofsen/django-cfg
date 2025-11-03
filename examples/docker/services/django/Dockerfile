# ============================================================================
# Django-CFG API Server - Dockerfile
# ============================================================================

FROM python:3.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    POETRY_VERSION=1.8.3 \
    POETRY_HOME="/opt/poetry" \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false

# Add poetry to PATH
ENV PATH="$POETRY_HOME/bin:$PATH"

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    libpq-dev \
    netcat-openbsd \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 - \
    && poetry --version

# Set working directory
WORKDIR /app

# Copy pyproject.toml only (poetry.lock excluded in .dockerignore)
COPY projects/django/pyproject.toml ./

# Remove local dependencies group from pyproject.toml and install
RUN sed -i '/^\[tool\.poetry\.group\.local\]/,/^\[tool\.poetry\.group\.dev\]/{ /^\[tool\.poetry\.group\.dev\]/!d; }' pyproject.toml && \
    poetry install --only main --no-root --no-cache && \
    pip install --upgrade django-cfg[full] && \
    rm -rf $POETRY_CACHE_DIR

# Copy application code
COPY projects/django /app

# Copy entrypoint script
COPY docker/services/django/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Create necessary directories
RUN mkdir -p /app/logs /app/staticfiles /app/media /app/logs

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/cfg/health/ || exit 1

# Set entrypoint
ENTRYPOINT ["/entrypoint.sh"]

# Default command (can be overridden in docker-compose)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
