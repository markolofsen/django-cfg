"""
Pytest configuration and shared fixtures.

This file isolates model imports to avoid circular dependencies.
"""

import sys
import pytest
import pytest_asyncio
import asyncio
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))


# ============================================================================
# Redis fixtures (pytest-asyncio)
# ============================================================================

@pytest_asyncio.fixture
async def redis_client():
    """
    Redis client for tests.

    Uses database 15 (test database) to avoid conflicts with production.
    Automatically cleans up after each test.
    """
    from redis.asyncio import Redis

    client = Redis.from_url(
        "redis://localhost:6379/15",  # Test database
        decode_responses=False,
        socket_keepalive=True,
        socket_connect_timeout=5,
    )

    try:
        # Verify connection
        await client.ping()
        yield client
    finally:
        # Cleanup: flush test database
        await client.flushdb()
        await client.close()


@pytest_asyncio.fixture
async def redis_with_streams(redis_client):
    """
    Redis client with pre-created test streams.

    Creates:
    - test:stream with consumer group test-group
    """
    # Create test stream and consumer group
    try:
        await redis_client.xgroup_create(
            "test:stream",
            "test-group",
            id="0",
            mkstream=True,
        )
    except Exception as e:
        if "BUSYGROUP" not in str(e):
            raise

    yield redis_client


# ============================================================================
# Fake Redis fixture (for unit tests)
# ============================================================================

@pytest_asyncio.fixture
async def fake_redis():
    """
    Fake Redis client for unit tests.

    Uses fakeredis to simulate Redis in-memory without external dependencies.
    Perfect for unit tests that don't need real Redis.
    """
    from fakeredis import FakeAsyncRedis

    client = FakeAsyncRedis(decode_responses=False)
    yield client
    await client.flushall()
    await client.aclose()
