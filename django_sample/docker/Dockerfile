# 🐳 UnrealOS Django - Production Docker Image
# Optimized build for production deployment

FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DJANGO_SETTINGS_MODULE=api.settings \
    ENVIRONMENT=production \
    DEBUG=false \
    IS_PROD=true \
    IS_DOCKER=true

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry==1.8.4

# Configure Poetry
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VENV_IN_PROJECT=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

# Skip user creation for development

# Set work directory
WORKDIR /app

# Copy Poetry files (with commented local dependencies)
COPY pyproject.toml ./

# Install dependencies using Poetry (in virtual environment)
RUN poetry config virtualenvs.create true && \
    poetry config virtualenvs.in-project true && \
    poetry lock --no-update && \
    poetry install --only=main && rm -rf $POETRY_CACHE_DIR

# Copy application code
COPY . .

# Set executable permissions for entrypoint and create directories
RUN chmod +x /app/docker/scripts/entrypoint.sh && \
    mkdir -p /app/logs /app/static /app/media

# Run as root for development (no user switch)

# No virtual environment - packages installed globally

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/cfg/health/ || exit 1

# Set entrypoint and default command
ENTRYPOINT ["/app/docker/scripts/entrypoint.sh"]
CMD ["runserver"]
