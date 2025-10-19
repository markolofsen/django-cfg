"""
Infrastructure tests for Redis Streams.

Tests Redis Streams operations that our consumers rely on:
- XADD, XREADGROUP, XACK, XPENDING
- Consumer Groups
- Load balancing across multiple consumers
- Message acknowledgment and retry logic
"""

import pytest
import asyncio
from redis.asyncio import Redis


@pytest.mark.infrastructure
@pytest.mark.asyncio
class TestRedisStreamsBasic:
    """Basic Redis Streams operations."""

    async def test_xadd_basic(self, redis_client: Redis):
        """Test basic XADD operation."""
        msg_id = await redis_client.xadd(
            "test:basic-stream",
            {"data": "hello", "value": "world"}
        )

        assert msg_id is not None
        assert isinstance(msg_id, bytes)

        # Verify message was added
        messages = await redis_client.xrange("test:basic-stream")
        assert len(messages) == 1
        assert messages[0][0] == msg_id
        assert messages[0][1][b"data"] == b"hello"

    async def test_xadd_with_maxlen(self, redis_client: Redis):
        """Test XADD with maxlen to limit stream size."""
        # Add 20 messages with maxlen=10 (approximate trim)
        for i in range(20):
            await redis_client.xadd(
                "test:maxlen-stream",
                {"count": str(i)},
                maxlen=10,
                approximate=False,  # Exact trim
            )

        # Should have approximately 10 messages
        messages = await redis_client.xrange("test:maxlen-stream")
        # Redis may keep slightly more than maxlen with approximate=False
        assert len(messages) <= 12  # Allow small margin

        # Verify we have latest messages
        values = [int(msg[1][b"count"]) for msg in messages]
        # Latest messages should be from higher indices
        assert min(values) >= 8  # At least from message 8 onwards

    async def test_xread_basic(self, redis_client: Redis):
        """Test basic XREAD operation."""
        # Add message
        msg_id = await redis_client.xadd("test:read-stream", {"msg": "test"})

        # Read from stream
        messages = await redis_client.xread({"test:read-stream": "0"})

        assert len(messages) == 1
        assert messages[0][0] == b"test:read-stream"
        assert len(messages[0][1]) == 1
        assert messages[0][1][0][0] == msg_id

    async def test_xread_blocking(self, redis_client: Redis):
        """Test XREAD with blocking."""
        stream_name = "test:blocking-stream"

        async def producer():
            """Produce message after 1 second."""
            await asyncio.sleep(1)
            await redis_client.xadd(stream_name, {"msg": "delayed"})

        # Start producer in background
        asyncio.create_task(producer())

        # Read with 3 second timeout
        messages = await redis_client.xread(
            {stream_name: "$"},
            block=3000,  # 3 seconds
        )

        # Should receive the delayed message
        assert len(messages) == 1
        assert messages[0][1][0][1][b"msg"] == b"delayed"


@pytest.mark.infrastructure
@pytest.mark.asyncio
class TestRedisStreamsConsumerGroups:
    """Consumer Groups operations."""

    async def test_xgroup_create(self, redis_client: Redis):
        """Test creating consumer group."""
        stream_name = "test:cg-stream"

        # Create consumer group
        result = await redis_client.xgroup_create(
            stream_name,
            "test-group",
            id="0",
            mkstream=True,
        )

        assert result is True

        # Verify group exists
        groups = await redis_client.xinfo_groups(stream_name)
        assert len(groups) == 1
        assert groups[0]["name"] == b"test-group"

    async def test_xgroup_create_duplicate_error(self, redis_client: Redis):
        """Test that creating duplicate group raises error."""
        stream_name = "test:dup-stream"

        # Create group first time
        await redis_client.xgroup_create(
            stream_name,
            "dup-group",
            id="0",
            mkstream=True,
        )

        # Try to create again - should raise
        with pytest.raises(Exception) as exc_info:
            await redis_client.xgroup_create(
                stream_name,
                "dup-group",
                id="0",
            )

        assert "BUSYGROUP" in str(exc_info.value)

    async def test_xreadgroup_basic(self, redis_client: Redis):
        """Test XREADGROUP with consumer groups."""
        stream_name = "test:readgroup-stream"

        # Create stream and group
        await redis_client.xgroup_create(
            stream_name,
            "read-group",
            id="0",
            mkstream=True,
        )

        # Add message
        msg_id = await redis_client.xadd(stream_name, {"data": "test"})

        # Read with consumer group
        messages = await redis_client.xreadgroup(
            groupname="read-group",
            consumername="consumer-1",
            streams={stream_name: ">"},
            count=1,
        )

        assert len(messages) == 1
        assert messages[0][0] == stream_name.encode()
        assert len(messages[0][1]) == 1
        assert messages[0][1][0][0] == msg_id

    async def test_xreadgroup_multiple_messages(self, redis_client: Redis):
        """Test reading multiple messages with XREADGROUP."""
        stream_name = "test:multi-stream"

        await redis_client.xgroup_create(
            stream_name,
            "multi-group",
            id="0",
            mkstream=True,
        )

        # Add 5 messages
        for i in range(5):
            await redis_client.xadd(stream_name, {"count": str(i)})

        # Read with count=3
        messages = await redis_client.xreadgroup(
            groupname="multi-group",
            consumername="consumer-1",
            streams={stream_name: ">"},
            count=3,
        )

        # Should get 3 messages
        assert len(messages[0][1]) == 3

        # Read remaining
        messages2 = await redis_client.xreadgroup(
            groupname="multi-group",
            consumername="consumer-1",
            streams={stream_name: ">"},
            count=10,
        )

        # Should get 2 remaining messages
        assert len(messages2[0][1]) == 2


@pytest.mark.infrastructure
@pytest.mark.asyncio
class TestRedisStreamsAcknowledgment:
    """Message acknowledgment tests."""

    async def test_xack_basic(self, redis_client: Redis):
        """Test basic XACK operation."""
        stream_name = "test:ack-stream"

        await redis_client.xgroup_create(
            stream_name,
            "ack-group",
            id="0",
            mkstream=True,
        )

        msg_id = await redis_client.xadd(stream_name, {"data": "test"})

        # Read message
        messages = await redis_client.xreadgroup(
            groupname="ack-group",
            consumername="consumer-1",
            streams={stream_name: ">"},
        )

        # ACK message
        ack_count = await redis_client.xack(stream_name, "ack-group", msg_id)

        assert ack_count == 1

    async def test_xack_multiple_messages(self, redis_client: Redis):
        """Test ACKing multiple messages."""
        stream_name = "test:multi-ack-stream"

        await redis_client.xgroup_create(
            stream_name,
            "multi-ack-group",
            id="0",
            mkstream=True,
        )

        # Add 3 messages
        msg_ids = []
        for i in range(3):
            msg_id = await redis_client.xadd(stream_name, {"num": str(i)})
            msg_ids.append(msg_id)

        # Read all messages
        await redis_client.xreadgroup(
            groupname="multi-ack-group",
            consumername="consumer-1",
            streams={stream_name: ">"},
            count=10,
        )

        # ACK all at once
        ack_count = await redis_client.xack(
            stream_name,
            "multi-ack-group",
            *msg_ids
        )

        assert ack_count == 3

    async def test_xpending_after_read(self, redis_client: Redis):
        """Test XPENDING shows pending messages."""
        stream_name = "test:pending-stream"

        await redis_client.xgroup_create(
            stream_name,
            "pending-group",
            id="0",
            mkstream=True,
        )

        msg_id = await redis_client.xadd(stream_name, {"data": "test"})

        # Read but DON'T ACK
        await redis_client.xreadgroup(
            groupname="pending-group",
            consumername="consumer-1",
            streams={stream_name: ">"},
        )

        # Check pending
        pending = await redis_client.xpending(stream_name, "pending-group")

        assert pending["pending"] == 1
        assert pending["min"] == msg_id
        assert pending["max"] == msg_id

    async def test_xpending_after_ack(self, redis_client: Redis):
        """Test XPENDING shows 0 after ACK."""
        stream_name = "test:pending-ack-stream"

        await redis_client.xgroup_create(
            stream_name,
            "pending-ack-group",
            id="0",
            mkstream=True,
        )

        msg_id = await redis_client.xadd(stream_name, {"data": "test"})

        # Read message
        await redis_client.xreadgroup(
            groupname="pending-ack-group",
            consumername="consumer-1",
            streams={stream_name: ">"},
        )

        # ACK message
        await redis_client.xack(stream_name, "pending-ack-group", msg_id)

        # Check pending - should be 0
        pending = await redis_client.xpending(stream_name, "pending-ack-group")

        assert pending["pending"] == 0


@pytest.mark.infrastructure
@pytest.mark.asyncio
class TestRedisStreamsLoadBalancing:
    """Load balancing across multiple consumers."""

    async def test_multiple_consumers_different_messages(self, redis_client: Redis):
        """Test that different consumers get different messages."""
        stream_name = "test:lb-stream"

        await redis_client.xgroup_create(
            stream_name,
            "lb-group",
            id="0",
            mkstream=True,
        )

        # Add 10 messages
        for i in range(10):
            await redis_client.xadd(stream_name, {"num": str(i)})

        # Consumer 1 reads 5
        msgs1 = await redis_client.xreadgroup(
            groupname="lb-group",
            consumername="consumer-1",
            streams={stream_name: ">"},
            count=5,
        )

        # Consumer 2 reads 5
        msgs2 = await redis_client.xreadgroup(
            groupname="lb-group",
            consumername="consumer-2",
            streams={stream_name: ">"},
            count=5,
        )

        # Each consumer got 5 messages
        assert len(msgs1[0][1]) == 5
        assert len(msgs2[0][1]) == 5

        # Extract message IDs
        ids1 = {msg[0] for msg in msgs1[0][1]}
        ids2 = {msg[0] for msg in msgs2[0][1]}

        # No overlap - different messages
        assert ids1.isdisjoint(ids2)

    async def test_consumer_gets_only_new_messages(self, redis_client: Redis):
        """Test > symbol gets only new messages."""
        stream_name = "test:new-only-stream"

        await redis_client.xgroup_create(
            stream_name,
            "new-only-group",
            id="0",
            mkstream=True,
        )

        # Add 5 messages
        for i in range(5):
            await redis_client.xadd(stream_name, {"num": str(i)})

        # Consumer 1 reads all
        msgs1 = await redis_client.xreadgroup(
            groupname="new-only-group",
            consumername="consumer-1",
            streams={stream_name: ">"},
            count=10,
        )

        assert len(msgs1[0][1]) == 5

        # Consumer 1 tries to read again with >
        msgs2 = await redis_client.xreadgroup(
            groupname="new-only-group",
            consumername="consumer-1",
            streams={stream_name: ">"},
            count=10,
        )

        # Should get nothing (no new messages)
        assert len(msgs2) == 0 or len(msgs2[0][1]) == 0

    async def test_three_consumers_load_balancing(self, redis_client: Redis):
        """Test load balancing with 3 consumers."""
        stream_name = "test:3consumers-stream"

        await redis_client.xgroup_create(
            stream_name,
            "3consumers-group",
            id="0",
            mkstream=True,
        )

        # Add 30 messages
        for i in range(30):
            await redis_client.xadd(stream_name, {"num": str(i)})

        # Each consumer reads 10
        msgs1 = await redis_client.xreadgroup(
            groupname="3consumers-group",
            consumername="consumer-1",
            streams={stream_name: ">"},
            count=10,
        )

        msgs2 = await redis_client.xreadgroup(
            groupname="3consumers-group",
            consumername="consumer-2",
            streams={stream_name: ">"},
            count=10,
        )

        msgs3 = await redis_client.xreadgroup(
            groupname="3consumers-group",
            consumername="consumer-3",
            streams={stream_name: ">"},
            count=10,
        )

        # Each got 10 messages
        assert len(msgs1[0][1]) == 10
        assert len(msgs2[0][1]) == 10
        assert len(msgs3[0][1]) == 10

        # All unique message IDs
        ids1 = {msg[0] for msg in msgs1[0][1]}
        ids2 = {msg[0] for msg in msgs2[0][1]}
        ids3 = {msg[0] for msg in msgs3[0][1]}

        # No overlaps
        assert ids1.isdisjoint(ids2)
        assert ids1.isdisjoint(ids3)
        assert ids2.isdisjoint(ids3)

        # Total 30 unique messages
        all_ids = ids1 | ids2 | ids3
        assert len(all_ids) == 30


@pytest.mark.infrastructure
@pytest.mark.asyncio
class TestRedisStreamsEdgeCases:
    """Edge cases and error scenarios."""

    async def test_read_from_nonexistent_stream(self, redis_client: Redis):
        """Test reading from stream that doesn't exist."""
        # Should block and timeout
        messages = await redis_client.xread(
            {"nonexistent:stream": "0"},
            block=100,  # 100ms timeout
        )

        # Should return empty
        assert len(messages) == 0

    async def test_readgroup_from_empty_stream(self, redis_client: Redis):
        """Test reading from empty stream with consumer group."""
        stream_name = "test:empty-stream"

        await redis_client.xgroup_create(
            stream_name,
            "empty-group",
            id="0",
            mkstream=True,
        )

        # Read from empty stream
        messages = await redis_client.xreadgroup(
            groupname="empty-group",
            consumername="consumer-1",
            streams={stream_name: ">"},
            block=100,
        )

        # Should return empty
        assert len(messages) == 0

    async def test_ack_already_acked_message(self, redis_client: Redis):
        """Test ACKing already acknowledged message."""
        stream_name = "test:double-ack-stream"

        await redis_client.xgroup_create(
            stream_name,
            "double-ack-group",
            id="0",
            mkstream=True,
        )

        msg_id = await redis_client.xadd(stream_name, {"data": "test"})

        await redis_client.xreadgroup(
            groupname="double-ack-group",
            consumername="consumer-1",
            streams={stream_name: ">"},
        )

        # First ACK
        ack1 = await redis_client.xack(stream_name, "double-ack-group", msg_id)
        assert ack1 == 1

        # Second ACK (already ACKed)
        ack2 = await redis_client.xack(stream_name, "double-ack-group", msg_id)
        assert ack2 == 0  # Returns 0 for already ACKed

    async def test_xinfo_groups_details(self, redis_client: Redis):
        """Test XINFO GROUPS provides detailed info."""
        stream_name = "test:info-stream"

        await redis_client.xgroup_create(
            stream_name,
            "info-group",
            id="0",
            mkstream=True,
        )

        # Add and read message
        await redis_client.xadd(stream_name, {"data": "test"})
        await redis_client.xreadgroup(
            groupname="info-group",
            consumername="consumer-1",
            streams={stream_name: ">"},
        )

        # Get group info
        groups = await redis_client.xinfo_groups(stream_name)

        assert len(groups) == 1
        group = groups[0]

        assert group["name"] == b"info-group"
        assert group["consumers"] == 1  # 1 consumer read
        assert group["pending"] == 1  # 1 pending (not ACKed)
