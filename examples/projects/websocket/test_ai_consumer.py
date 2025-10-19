#!/usr/bin/env python3
"""
Test script for AI Command Consumer.

This script simulates Django sending AI commands to Redis Streams
and verifies that AICommandConsumer routes them correctly.

Usage:
    python test_ai_consumer.py
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime
from redis.asyncio import Redis

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from config import server_config
from loguru import logger


async def test_ai_command_routing():
    """Test AI command routing through AICommandConsumer."""

    logger.info("=" * 80)
    logger.info("🧪 Testing AI Command Consumer")
    logger.info("=" * 80)

    # Connect to Redis
    redis = Redis.from_url(
        server_config.server.redis_url,
        decode_responses=False,
    )

    try:
        # Test 1: Send Claude command
        logger.info("\n📤 Test 1: Sending Claude command...")

        claude_command = {
            "service": "claude",
            "session_id": "test-session-123",
            "workspace_path": "/workspaces/test",
            "message": "Hello Claude!",
            "context": {"file": "main.py"},
            "timestamp": datetime.utcnow().isoformat(),
        }

        import json
        msg_id = await redis.xadd(
            "stream:ai-commands",
            {b'payload': json.dumps(claude_command).encode()},
        )

        logger.info(f"✅ Sent Claude command: {msg_id.decode()}")

        # Wait for consumer to process
        await asyncio.sleep(2)

        # Check if routed to stream:claude-commands
        claude_messages = await redis.xrevrange(
            "stream:claude-commands",
            count=1,
        )

        if claude_messages:
            logger.info(f"✅ Claude command routed successfully: {claude_messages[0][0].decode()}")
        else:
            logger.warning("⚠️  No messages in stream:claude-commands")

        # Test 2: Send Cursor command
        logger.info("\n📤 Test 2: Sending Cursor command...")

        cursor_command = {
            "service": "cursor",
            "session_id": "test-session-456",
            "workspace_path": "/workspaces/test",
            "message": "Help me with this code",
            "timestamp": datetime.utcnow().isoformat(),
        }

        msg_id = await redis.xadd(
            "stream:ai-commands",
            {b'payload': json.dumps(cursor_command).encode()},
        )

        logger.info(f"✅ Sent Cursor command: {msg_id.decode()}")

        # Wait for consumer to process
        await asyncio.sleep(2)

        # Check if routed to stream:cursor-commands
        cursor_messages = await redis.xrevrange(
            "stream:cursor-commands",
            count=1,
        )

        if cursor_messages:
            logger.info(f"✅ Cursor command routed successfully: {cursor_messages[0][0].decode()}")
        else:
            logger.warning("⚠️  No messages in stream:cursor-commands")

        # Test 3: Send invalid command
        logger.info("\n📤 Test 3: Sending invalid command...")

        invalid_command = {
            "invalid_field": "bad data",
        }

        msg_id = await redis.xadd(
            "stream:ai-commands",
            {b'payload': json.dumps(invalid_command).encode()},
        )

        logger.info(f"✅ Sent invalid command: {msg_id.decode()}")

        # Wait for consumer to process
        await asyncio.sleep(2)

        # Check DLQ
        dlq_messages = await redis.xrevrange(
            "stream:ai-commands-dlq",
            count=1,
        )

        if dlq_messages:
            logger.info(f"✅ Invalid command sent to DLQ: {dlq_messages[0][0].decode()}")
        else:
            logger.warning("⚠️  No messages in DLQ")

        # Summary
        logger.info("\n" + "=" * 80)
        logger.info("📊 Test Summary")
        logger.info("=" * 80)

        # Check consumer group status
        info = await redis.xinfo_groups("stream:ai-commands")
        if info:
            for group in info:
                logger.info(f"Consumer Group: {group['name'].decode()}")
                logger.info(f"  Pending: {group['pending']}")
                logger.info(f"  Consumers: {group['consumers']}")

        logger.info("\n✅ All tests completed!")

    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        raise

    finally:
        await redis.close()


if __name__ == "__main__":
    try:
        asyncio.run(test_ai_command_routing())
    except KeyboardInterrupt:
        logger.info("👋 Test interrupted")
        sys.exit(0)
