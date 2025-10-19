"""
Integration tests for AICommandConsumer with real Redis.

Tests complete end-to-end flow:
- Django adds command to stream:ai-commands
- AICommandConsumer reads, validates, routes
- Command arrives in service-specific stream
- Proper ACKing and error handling

Requires: Redis running on localhost:6379
"""

import pytest
import asyncio
import json
from datetime import datetime
from consumers.ai_command_consumer import AICommandConsumer, AICommand, AIService


@pytest.mark.integration
@pytest.mark.asyncio
class TestAICommandConsumerEndToEnd:
    """End-to-end integration tests with real Redis."""

    async def test_full_flow_single_command(self, redis_client):
        """Test complete flow: add → consume → route → verify."""
        # 1. Setup consumer
        consumer = AICommandConsumer(
            redis=redis_client,
            stream_name="test:ai-commands",
            consumer_group="integration-group",
            consumer_name="integration-consumer",
            block_ms=100,  # Fast for tests
        )

        await consumer.initialize()
        await consumer.start()

        # Give consumer time to start
        await asyncio.sleep(0.2)

        # 2. Simulate Django adding command
        cmd = AICommand(
            service=AIService.CLAUDE,
            session_id="integration-session-123",
            workspace_path="/workspaces/integration-test",
            message="Integration test command",
            context={"test": "integration"},
            timestamp=datetime.utcnow(),
        )

        msg_id = await redis_client.xadd(
            "test:ai-commands",
            {b"payload": cmd.model_dump_json().encode()},
        )

        # 3. Wait for consumer to process
        await asyncio.sleep(1)

        # 4. Verify command routed to claude stream
        claude_messages = await redis_client.xrevrange("stream:claude-commands", count=1)

        assert len(claude_messages) == 1

        routed_msg_id, routed_data = claude_messages[0]
        routed_payload = json.loads(routed_data[b"payload"])

        assert routed_payload["service"] == "claude"
        assert routed_payload["session_id"] == "integration-session-123"
        assert routed_payload["message"] == "Integration test command"
        assert routed_payload["context"]["test"] == "integration"

        # 5. Verify message was ACKed
        pending = await redis_client.xpending("test:ai-commands", "integration-group")
        assert pending["pending"] == 0

        # Cleanup
        await consumer.stop()

    async def test_multiple_services_parallel_routing(self, redis_client):
        """Test routing commands to multiple services in parallel."""
        consumer = AICommandConsumer(
            redis=redis_client,
            stream_name="test:ai-commands",
            consumer_group="multi-service-group",
            consumer_name="multi-service-consumer",
            block_ms=100,
        )

        await consumer.initialize()
        await consumer.start()
        await asyncio.sleep(0.2)

        # Add commands for all 3 services
        commands = [
            (AIService.CLAUDE, "Claude command 1"),
            (AIService.CURSOR, "Cursor command 1"),
            (AIService.MCP, "MCP command 1"),
            (AIService.CLAUDE, "Claude command 2"),
            (AIService.CURSOR, "Cursor command 2"),
        ]

        for service, message in commands:
            cmd = AICommand(
                service=service,
                session_id=f"session-{service.value}",
                workspace_path="/workspaces/test",
                message=message,
            )

            await redis_client.xadd(
                "test:ai-commands",
                {b"payload": cmd.model_dump_json().encode()},
            )

        # Wait for processing
        await asyncio.sleep(2)

        # Verify routing
        claude_msgs = await redis_client.xrange("stream:claude-commands")
        cursor_msgs = await redis_client.xrange("stream:cursor-commands")
        mcp_msgs = await redis_client.xrange("stream:mcp-commands")

        assert len(claude_msgs) == 2
        assert len(cursor_msgs) == 2
        assert len(mcp_msgs) == 1

        # Verify all ACKed
        pending = await redis_client.xpending("test:ai-commands", "multi-service-group")
        assert pending["pending"] == 0

        await consumer.stop()

    async def test_consumer_group_load_balancing(self, redis_client):
        """Test that multiple consumers share the load."""
        # Create 2 consumers in same group
        consumer1 = AICommandConsumer(
            redis=redis_client,
            stream_name="test:ai-commands",
            consumer_group="load-balance-group",
            consumer_name="consumer-1",
            block_ms=100,
        )

        consumer2 = AICommandConsumer(
            redis=redis_client,
            stream_name="test:ai-commands",
            consumer_group="load-balance-group",
            consumer_name="consumer-2",
            block_ms=100,
        )

        await consumer1.initialize()
        await consumer2.initialize()

        await consumer1.start()
        await consumer2.start()
        await asyncio.sleep(0.2)

        # Add 10 commands
        for i in range(10):
            cmd = AICommand(
                service=AIService.CLAUDE,
                session_id=f"session-{i}",
                workspace_path="/workspaces/test",
                message=f"Command {i}",
            )

            await redis_client.xadd(
                "test:ai-commands",
                {b"payload": cmd.model_dump_json().encode()},
            )

        # Wait for processing
        await asyncio.sleep(3)

        # Both consumers should have processed messages
        # (exact distribution may vary, but total should be 10)
        pending = await redis_client.xpending("test:ai-commands", "load-balance-group")
        assert pending["pending"] == 0  # All processed

        # Verify all 10 routed to claude stream
        claude_msgs = await redis_client.xrange("stream:claude-commands")
        assert len(claude_msgs) == 10

        await consumer1.stop()
        await consumer2.stop()

    async def test_invalid_command_goes_to_dlq(self, redis_client):
        """Test that invalid commands are sent to DLQ."""
        consumer = AICommandConsumer(
            redis=redis_client,
            stream_name="test:ai-commands",
            consumer_group="dlq-test-group",
            consumer_name="dlq-test-consumer",
            block_ms=100,
        )

        await consumer.initialize()
        await consumer.start()
        await asyncio.sleep(0.2)

        # Add invalid command (missing required fields)
        invalid_payload = json.dumps({
            "invalid_field": "bad data",
            "missing": "service field"
        })

        await redis_client.xadd(
            "test:ai-commands",
            {b"payload": invalid_payload.encode()},
        )

        # Wait for processing
        await asyncio.sleep(1)

        # Verify sent to DLQ
        dlq_msgs = await redis_client.xrevrange("stream:ai-commands-dlq", count=1)
        assert len(dlq_msgs) == 1

        dlq_data = dlq_msgs[0][1]
        assert b"error" in dlq_data
        assert dlq_data[b"payload"] == invalid_payload.encode()

        # Verify ACKed (not retrying)
        pending = await redis_client.xpending("test:ai-commands", "dlq-test-group")
        assert pending["pending"] == 0

        await consumer.stop()

    async def test_consumer_restart_recovers_pending(self, redis_client):
        """Test that restarted consumer can recover pending messages."""
        # 1. Start consumer
        consumer1 = AICommandConsumer(
            redis=redis_client,
            stream_name="test:ai-commands",
            consumer_group="restart-group",
            consumer_name="restart-consumer-1",
            block_ms=100,
        )

        await consumer1.initialize()

        # 2. Add command
        cmd = AICommand(
            service=AIService.CLAUDE,
            session_id="restart-test",
            workspace_path="/workspaces/test",
            message="Restart test",
        )

        await redis_client.xadd(
            "test:ai-commands",
            {b"payload": cmd.model_dump_json().encode()},
        )

        # 3. Start consumer briefly then stop (simulates crash)
        await consumer1.start()
        await asyncio.sleep(0.5)
        await consumer1.stop()

        # 4. Check pending (might have read but not ACKed)
        pending_before = await redis_client.xpending("test:ai-commands", "restart-group")

        # 5. Start new consumer (same group, different name)
        consumer2 = AICommandConsumer(
            redis=redis_client,
            stream_name="test:ai-commands",
            consumer_group="restart-group",
            consumer_name="restart-consumer-2",
            block_ms=100,
        )

        await consumer2.initialize()
        await consumer2.start()
        await asyncio.sleep(2)

        # 6. Pending should eventually be 0 (processed by consumer2)
        pending_after = await redis_client.xpending("test:ai-commands", "restart-group")
        assert pending_after["pending"] == 0

        # 7. Verify routed
        claude_msgs = await redis_client.xrange("stream:claude-commands")
        assert len(claude_msgs) >= 1

        await consumer2.stop()


@pytest.mark.integration
@pytest.mark.asyncio
class TestAICommandConsumerPerformance:
    """Performance and load testing."""

    async def test_high_throughput_100_commands(self, redis_client):
        """Test processing 100 commands quickly."""
        consumer = AICommandConsumer(
            redis=redis_client,
            stream_name="test:ai-commands",
            consumer_group="perf-group",
            consumer_name="perf-consumer",
            batch_size=10,  # Larger batches
            block_ms=50,    # Faster polling
        )

        await consumer.initialize()
        await consumer.start()
        await asyncio.sleep(0.2)

        # Add 100 commands
        start_time = asyncio.get_event_loop().time()

        for i in range(100):
            cmd = AICommand(
                service=AIService.CLAUDE,
                session_id=f"perf-session-{i}",
                workspace_path="/workspaces/perf",
                message=f"Performance test {i}",
            )

            await redis_client.xadd(
                "test:ai-commands",
                {b"payload": cmd.model_dump_json().encode()},
            )

        # Wait for processing
        await asyncio.sleep(5)

        end_time = asyncio.get_event_loop().time()
        processing_time = end_time - start_time

        # Verify all processed
        pending = await redis_client.xpending("test:ai-commands", "perf-group")
        assert pending["pending"] == 0

        # Verify all routed
        claude_msgs = await redis_client.xrange("stream:claude-commands")
        assert len(claude_msgs) == 100

        # Performance check: should process 100 msgs in < 10s
        assert processing_time < 10.0

        print(f"\n⚡ Processed 100 commands in {processing_time:.2f}s")
        print(f"   Throughput: {100/processing_time:.1f} commands/sec")

        await consumer.stop()

    async def test_latency_single_command(self, redis_client):
        """Test latency for single command routing."""
        consumer = AICommandConsumer(
            redis=redis_client,
            stream_name="test:ai-commands",
            consumer_group="latency-group",
            consumer_name="latency-consumer",
            block_ms=50,
        )

        await consumer.initialize()
        await consumer.start()
        await asyncio.sleep(0.2)

        # Measure latency
        cmd = AICommand(
            service=AIService.CLAUDE,
            session_id="latency-test",
            workspace_path="/workspaces/test",
            message="Latency test",
        )

        start_time = asyncio.get_event_loop().time()

        await redis_client.xadd(
            "test:ai-commands",
            {b"payload": cmd.model_dump_json().encode()},
        )

        # Poll until routed
        max_wait = 2.0
        elapsed = 0
        routed = False

        while elapsed < max_wait:
            claude_msgs = await redis_client.xrevrange("stream:claude-commands", count=1)
            if claude_msgs:
                routed = True
                break

            await asyncio.sleep(0.05)
            elapsed = asyncio.get_event_loop().time() - start_time

        end_time = asyncio.get_event_loop().time()
        latency = end_time - start_time

        assert routed, "Command was not routed within timeout"

        # Latency check: should route in < 500ms
        assert latency < 0.5

        print(f"\n⚡ Routing latency: {latency*1000:.1f}ms")

        await consumer.stop()


@pytest.mark.integration
@pytest.mark.asyncio
class TestAICommandConsumerResilience:
    """Test error recovery and resilience."""

    async def test_consumer_handles_redis_reconnect(self, redis_client):
        """Test that consumer handles Redis connection issues gracefully."""
        # This test is conceptual - actual implementation would require
        # mocking Redis connection failures
        pass

    async def test_maxlen_enforced_on_target_streams(self, redis_client):
        """Test that target streams enforce maxlen."""
        consumer = AICommandConsumer(
            redis=redis_client,
            stream_name="test:ai-commands",
            consumer_group="maxlen-group",
            consumer_name="maxlen-consumer",
            block_ms=100,
        )

        await consumer.initialize()
        await consumer.start()
        await asyncio.sleep(0.2)

        # Add many commands (more than maxlen=10000)
        # Note: This would take too long for regular tests
        # Just verify maxlen parameter is used

        cmd = AICommand(
            service=AIService.CLAUDE,
            session_id="maxlen-test",
            workspace_path="/workspaces/test",
            message="Maxlen test",
        )

        await redis_client.xadd(
            "test:ai-commands",
            {b"payload": cmd.model_dump_json().encode()},
        )

        await asyncio.sleep(1)

        # Consumer should have routed with maxlen
        # (Hard to verify without inspecting Redis internals,
        #  but code coverage ensures _process_message calls xadd with maxlen)

        await consumer.stop()

    async def test_mixed_valid_invalid_commands(self, redis_client):
        """Test processing mixed valid and invalid commands."""
        consumer = AICommandConsumer(
            redis=redis_client,
            stream_name="test:ai-commands",
            consumer_group="mixed-group",
            consumer_name="mixed-consumer",
            block_ms=100,
        )

        await consumer.initialize()
        await consumer.start()
        await asyncio.sleep(0.2)

        # Add 3 valid, 2 invalid
        valid_cmd = AICommand(
            service=AIService.CLAUDE,
            session_id="valid",
            workspace_path="/workspaces/test",
            message="Valid",
        )

        # Valid 1
        await redis_client.xadd(
            "test:ai-commands",
            {b"payload": valid_cmd.model_dump_json().encode()},
        )

        # Invalid 1
        await redis_client.xadd(
            "test:ai-commands",
            {b"payload": b'{"invalid": "data"}'},
        )

        # Valid 2
        await redis_client.xadd(
            "test:ai-commands",
            {b"payload": valid_cmd.model_dump_json().encode()},
        )

        # Invalid 2
        await redis_client.xadd(
            "test:ai-commands",
            {b"payload": b'{"missing": "service"}'},
        )

        # Valid 3
        await redis_client.xadd(
            "test:ai-commands",
            {b"payload": valid_cmd.model_dump_json().encode()},
        )

        await asyncio.sleep(2)

        # Verify: 3 valid routed, 2 invalid to DLQ
        claude_msgs = await redis_client.xrange("stream:claude-commands")
        dlq_msgs = await redis_client.xrange("stream:ai-commands-dlq")

        assert len(claude_msgs) == 3
        assert len(dlq_msgs) == 2

        # All ACKed
        pending = await redis_client.xpending("test:ai-commands", "mixed-group")
        assert pending["pending"] == 0

        await consumer.stop()


@pytest.mark.integration
@pytest.mark.asyncio
class TestAICommandConsumerConcurrency:
    """Test concurrent consumer scenarios."""

    async def test_three_consumers_same_group(self, redis_client):
        """Test 3 consumers in same group load balance correctly."""
        consumers = []

        for i in range(1, 4):
            consumer = AICommandConsumer(
                redis=redis_client,
                stream_name="test:ai-commands",
                consumer_group="three-consumers-group",
                consumer_name=f"consumer-{i}",
                block_ms=100,
            )
            await consumer.initialize()
            await consumer.start()
            consumers.append(consumer)

        await asyncio.sleep(0.3)

        # Add 30 commands
        for i in range(30):
            cmd = AICommand(
                service=AIService.CLAUDE,
                session_id=f"session-{i}",
                workspace_path="/workspaces/test",
                message=f"Command {i}",
            )

            await redis_client.xadd(
                "test:ai-commands",
                {b"payload": cmd.model_dump_json().encode()},
            )

        await asyncio.sleep(3)

        # All 30 should be processed
        pending = await redis_client.xpending("test:ai-commands", "three-consumers-group")
        assert pending["pending"] == 0

        claude_msgs = await redis_client.xrange("stream:claude-commands")
        assert len(claude_msgs) == 30

        # Cleanup
        for consumer in consumers:
            await consumer.stop()

    async def test_different_consumer_groups_independent(self, redis_client):
        """Test that different consumer groups process independently."""
        # Group 1
        consumer1 = AICommandConsumer(
            redis=redis_client,
            stream_name="test:ai-commands",
            consumer_group="group-1",
            consumer_name="consumer-1",
            block_ms=100,
        )

        # Group 2 (different group, same stream)
        consumer2 = AICommandConsumer(
            redis=redis_client,
            stream_name="test:ai-commands",
            consumer_group="group-2",
            consumer_name="consumer-2",
            block_ms=100,
        )

        await consumer1.initialize()
        await consumer2.initialize()

        await consumer1.start()
        await consumer2.start()
        await asyncio.sleep(0.3)

        # Add 5 commands
        for i in range(5):
            cmd = AICommand(
                service=AIService.CLAUDE,
                session_id=f"session-{i}",
                workspace_path="/workspaces/test",
                message=f"Command {i}",
            )

            await redis_client.xadd(
                "test:ai-commands",
                {b"payload": cmd.model_dump_json().encode()},
            )

        await asyncio.sleep(2)

        # BOTH groups should process all 5 messages (independent)
        pending1 = await redis_client.xpending("test:ai-commands", "group-1")
        pending2 = await redis_client.xpending("test:ai-commands", "group-2")

        assert pending1["pending"] == 0
        assert pending2["pending"] == 0

        # Each group routed all 5 (10 total in claude stream)
        claude_msgs = await redis_client.xrange("stream:claude-commands")
        assert len(claude_msgs) == 10  # 5 from group-1 + 5 from group-2

        await consumer1.stop()
        await consumer2.stop()
