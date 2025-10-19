# ============================================================================
# Django-CFG WebSocket Server - Dockerfile
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
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_CACHE_DIR=/tmp/poetry_cache

# Add poetry to PATH
ENV PATH="$POETRY_HOME/bin:$PATH"

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 - \
    && poetry --version

# Set working directory
WORKDIR /app

# Copy pyproject.toml only (poetry.lock excluded in .dockerignore)
COPY projects/websocket/pyproject.toml ./

# Remove local dependencies group from pyproject.toml, then generate fresh lock file and install
RUN python3 -c "import re; content = open('pyproject.toml').read(); content = re.sub(r'\[tool\.poetry\.group\.local[^\]]*\][^\[]*', '', content, flags=re.DOTALL); open('pyproject.toml', 'w').write(content)" && \
    poetry lock && \
    poetry install --only main --no-root && \
    rm -rf $POETRY_CACHE_DIR

# Copy application code
COPY projects/websocket /app

# Create necessary directories
RUN mkdir -p /app/logs

# Expose ports
EXPOSE 8965 8966

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8966/health || exit 1

# Run the application
CMD ["python", "src/main.py"]
