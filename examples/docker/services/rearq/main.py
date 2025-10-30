"""
ReArq Worker Configuration
===========================
Main configuration file for ReArq async task queue with web UI

Documentation: https://github.com/long2ice/rearq
"""

import os
from rearq import ReArq
from tortoise import Tortoise

# Import rearq server app to add Tortoise initialization
try:
    from rearq.server.app import app as rearq_server_app
except ImportError:
    rearq_server_app = None

# ─────────────────────────────────────────────────────────────────
# Redis Configuration
# ─────────────────────────────────────────────────────────────────
# ReArq uses Redis as backend for task queue
REDIS_HOST = os.getenv("REARQ_REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REARQ_REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REARQ_REDIS_DB", "1"))
REDIS_PASSWORD = os.getenv("REARQ_REDIS_PASSWORD", None)

# Build Redis URL
if REDIS_PASSWORD:
    REDIS_URL = f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
else:
    REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"

# Allow override via full URL
REDIS_URL = os.getenv("REARQ_REDIS_URL", REDIS_URL)

# ─────────────────────────────────────────────────────────────────
# Database Configuration (for Web UI)
# ─────────────────────────────────────────────────────────────────
# ReArq Web UI requires Tortoise ORM database
DB_URL = os.getenv("REARQ_DB_URL", "sqlite:///app/rearq.db")

# ─────────────────────────────────────────────────────────────────
# ReArq Instance
# ─────────────────────────────────────────────────────────────────
# IMPORTANT: Do NOT pass db_url to ReArq constructor!
# Database is initialized separately via Tortoise in on_startup hook
rearq = ReArq(
    redis_url=REDIS_URL,
    job_retry=3,              # Number of retries for failed jobs
    job_retry_after=60,       # Retry after seconds
    max_jobs=10,              # Max concurrent jobs
    job_timeout=300,          # Job timeout in seconds (5 minutes)
    keep_job_days=7,          # Keep job history for 7 days
)


# ─────────────────────────────────────────────────────────────────
# Example Tasks
# ─────────────────────────────────────────────────────────────────

@rearq.task(queue="default")
async def example_task(a: int, b: int) -> int:
    """
    Example async task that adds two numbers.

    Usage:
        await example_task.delay(a=10, b=20)
    """
    return a + b


@rearq.task(queue="high_priority")
async def send_email_task(email: str, subject: str, body: str) -> dict:
    """
    Example task for sending emails.

    Usage:
        await send_email_task.delay(
            email="user@example.com",
            subject="Hello",
            body="Welcome!"
        )
    """
    # TODO: Implement actual email sending logic
    print(f"Sending email to {email}: {subject}")
    return {"status": "sent", "email": email}


@rearq.task(queue="low_priority")
async def process_file_task(file_path: str) -> dict:
    """
    Example task for processing files.

    Usage:
        await process_file_task.delay(file_path="/path/to/file.txt")
    """
    # TODO: Implement actual file processing logic
    print(f"Processing file: {file_path}")
    return {"status": "processed", "file": file_path}


# ─────────────────────────────────────────────────────────────────
# Cron Tasks (Scheduled Tasks)
# ─────────────────────────────────────────────────────────────────
# Note: ReArq cron support requires additional setup
# For now, use regular tasks and schedule them externally


# ─────────────────────────────────────────────────────────────────
# Startup Hook
# ─────────────────────────────────────────────────────────────────

@rearq.on_startup
async def startup():
    """
    Runs when ReArq worker/server starts.
    Initialize Tortoise ORM for Web UI.
    """
    print("ReArq starting up...")
    print(f"Redis: {REDIS_URL}")
    print(f"Database: {DB_URL}")

    # Initialize Tortoise ORM for Web UI (required for rearq server)
    await Tortoise.init(
        db_url=DB_URL,
        modules={"rearq": ["rearq.server.models"]},
    )
    # Note: generate_schemas() is handled automatically by Tortoise init


# ─────────────────────────────────────────────────────────────────
# Shutdown Hook
# ─────────────────────────────────────────────────────────────────

@rearq.on_shutdown
async def shutdown():
    """
    Runs when ReArq worker/server shuts down.
    Close connections, cleanup resources, etc.
    """
    print("ReArq shutting down...")
    # Close Tortoise ORM connections
    await Tortoise.close_connections()


# ─────────────────────────────────────────────────────────────────
# FastAPI Server Initialization (for Web UI)
# ─────────────────────────────────────────────────────────────────
# Add Tortoise initialization to rearq server app
if rearq_server_app:
    @rearq_server_app.on_event("startup")
    async def init_tortoise_for_server():
        """
        Initialize Tortoise ORM when running rearq server.
        This is required for the Web UI to work.
        """
        print("Initializing Tortoise ORM for rearq server...")
        print(f"Database: {DB_URL}")

        await Tortoise.init(
            db_url=DB_URL,
            modules={"rearq": ["rearq.server.models"]},
        )
        await Tortoise.generate_schemas()
        print("Tortoise ORM initialized successfully!")

    @rearq_server_app.on_event("shutdown")
    async def close_tortoise_for_server():
        """
        Close Tortoise ORM connections when server shuts down.
        """
        print("Closing Tortoise ORM connections...")
        await Tortoise.close_connections()
