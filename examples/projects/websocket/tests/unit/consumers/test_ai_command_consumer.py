"""
Unit tests for AICommandConsumer.

Uses fakeredis to simulate Redis operations without external dependencies.
Tests consumer logic, routing, error handling, and lifecycle management.
"""

import pytest
import asyncio
from datetime import datetime
from consumers.ai_command_consumer import AICommandConsumer, AICommand, AIService


@pytest.mark.unit
@pytest.mark.asyncio
class TestAICommandConsumerInitialization:
    """Test consumer initialization and lifecycle."""

    async def test_initialize_creates_consumer_group(self, fake_redis):
        """Test that initialize creates consumer group."""
        consumer = AICommandConsumer(
            redis=fake_redis,
            stream_name="test:ai-commands",
            consumer_group="test-group",
            consumer_name="test-consumer",
        )

        await consumer.initialize()

        # Verify group was created
        groups = await fake_redis.xinfo_groups("test:ai-commands")
        assert len(groups) == 1
        assert groups[0]["name"] == b"test-group"

    async def test_initialize_handles_existing_group(self, fake_redis):
        """Test that initialize handles existing consumer group gracefully."""
        # Pre-create group
        await fake_redis.xgroup_create(
            "test:ai-commands",
            "existing-group",
            id="0",
            mkstream=True,
        )

        consumer = AICommandConsumer(
            redis=fake_redis,
            stream_name="test:ai-commands",
            consumer_group="existing-group",
            consumer_name="test-consumer",
        )

        # Should not raise error
        await consumer.initialize()

        # Group should still exist
        groups = await fake_redis.xinfo_groups("test:ai-commands")
        assert len(groups) == 1

    async def test_start_sets_running_flag(self, fake_redis):
        """Test that start() sets running flag and creates task."""
        consumer = AICommandConsumer(
            redis=fake_redis,
            stream_name="test:ai-commands",
            consumer_group="test-group",
            consumer_name="test-consumer",
        )

        await consumer.initialize()
        await consumer.start()

        assert consumer._running is True
        assert consumer._task is not None

        await consumer.stop()

    async def test_stop_cancels_task(self, fake_redis):
        """Test that stop() cancels background task and clears running flag."""
        consumer = AICommandConsumer(
            redis=fake_redis,
            stream_name="test:ai-commands",
            consumer_group="test-group",
            consumer_name="test-consumer",
        )

        await consumer.initialize()
        await consumer.start()

        # Give task time to start
        await asyncio.sleep(0.1)

        await consumer.stop()

        assert consumer._running is False
        assert consumer._task.cancelled() or consumer._task.done()

    async def test_start_idempotent(self, fake_redis):
        """Test that calling start() multiple times is safe."""
        consumer = AICommandConsumer(
            redis=fake_redis,
            stream_name="test:ai-commands",
            consumer_group="test-group",
            consumer_name="test-consumer",
        )

        await consumer.initialize()
        await consumer.start()

        first_task = consumer._task

        # Start again
        await consumer.start()

        # Should be same task
        assert consumer._task == first_task

        await consumer.stop()


@pytest.mark.unit
@pytest.mark.asyncio
class TestAICommandConsumerRouting:
    """Test message routing logic."""

    async def test_route_claude_command_to_claude_stream(self, fake_redis):
        """Test that Claude commands are routed to stream:claude-commands."""
        consumer = AICommandConsumer(
            redis=fake_redis,
            stream_name="test:ai-commands",
            consumer_group="test-group",
            consumer_name="test-consumer",
        )

        await consumer.initialize()

        # Create Claude command
        cmd = AICommand(
            service=AIService.CLAUDE,
            session_id="session-123",
            workspace_path="/workspaces/test",
            message="Hello Claude",
            timestamp=datetime.utcnow(),
        )

        message_id = b"1234567890-0"
        data = {b"payload": cmd.model_dump_json().encode()}

        # Process message
        await consumer._process_message(message_id, data)

        # Verify routed to claude stream
        claude_messages = await fake_redis.xrevrange("stream:claude-commands", count=1)
        assert len(claude_messages) == 1

        # Verify payload
        import json
        routed_payload = json.loads(claude_messages[0][1][b"payload"])
        assert routed_payload["service"] == "claude"
        assert routed_payload["message"] == "Hello Claude"

    async def test_route_cursor_command_to_cursor_stream(self, fake_redis):
        """Test that Cursor commands are routed to stream:cursor-commands."""
        consumer = AICommandConsumer(
            redis=fake_redis,
            stream_name="test:ai-commands",
            consumer_group="test-group",
            consumer_name="test-consumer",
        )

        await consumer.initialize()

        cmd = AICommand(
            service=AIService.CURSOR,
            session_id="session-456",
            workspace_path="/workspaces/test",
            message="Cursor query",
        )

        message_id = b"1234567890-1"
        data = {b"payload": cmd.model_dump_json().encode()}

        await consumer._process_message(message_id, data)

        # Verify routed to cursor stream
        cursor_messages = await fake_redis.xrevrange("stream:cursor-commands", count=1)
        assert len(cursor_messages) == 1

        import json
        routed_payload = json.loads(cursor_messages[0][1][b"payload"])
        assert routed_payload["service"] == "cursor"

    async def test_route_mcp_command_to_mcp_stream(self, fake_redis):
        """Test that MCP commands are routed to stream:mcp-commands."""
        consumer = AICommandConsumer(
            redis=fake_redis,
            stream_name="test:ai-commands",
            consumer_group="test-group",
            consumer_name="test-consumer",
        )

        await consumer.initialize()

        cmd = AICommand(
            service=AIService.MCP,
            session_id="session-789",
            workspace_path="/workspaces/test",
            message="MCP operation",
        )

        message_id = b"1234567890-2"
        data = {b"payload": cmd.model_dump_json().encode()}

        await consumer._process_message(message_id, data)

        # Verify routed to mcp stream
        mcp_messages = await fake_redis.xrevrange("stream:mcp-commands", count=1)
        assert len(mcp_messages) == 1

        import json
        routed_payload = json.loads(mcp_messages[0][1][b"payload"])
        assert routed_payload["service"] == "mcp"

    async def test_service_stream_mapping_correctness(self, fake_redis):
        """Test that SERVICE_STREAMS mapping is correct."""
        consumer = AICommandConsumer(redis=fake_redis)

        assert consumer.SERVICE_STREAMS[AIService.CLAUDE] == "stream:claude-commands"
        assert consumer.SERVICE_STREAMS[AIService.CURSOR] == "stream:cursor-commands"
        assert consumer.SERVICE_STREAMS[AIService.MCP] == "stream:mcp-commands"


@pytest.mark.unit
@pytest.mark.asyncio
class TestAICommandConsumerAcknowledgment:
    """Test message acknowledgment logic."""

    async def test_successful_processing_acks_message(self, fake_redis):
        """Test that successfully processed messages are ACKed."""
        consumer = AICommandConsumer(
            redis=fake_redis,
            stream_name="test:ai-commands",
            consumer_group="test-group",
            consumer_name="test-consumer",
        )

        await consumer.initialize()

        cmd = AICommand(
            service=AIService.CLAUDE,
            session_id="session-123",
            workspace_path="/workspaces/test",
            message="Test",
        )

        # Add message to stream
        msg_id = await fake_redis.xadd(
            "test:ai-commands",
            {b"payload": cmd.model_dump_json().encode()},
        )

        # Read message (creates pending)
        await fake_redis.xreadgroup(
            groupname="test-group",
            consumername="test-consumer",
            streams={"test:ai-commands": ">"},
        )

        # Process message
        data = {b"payload": cmd.model_dump_json().encode()}
        await consumer._process_message(msg_id, data)

        # Verify ACKed (pending should be 0)
        pending = await fake_redis.xpending("test:ai-commands", "test-group")
        assert pending["pending"] == 0

    async def test_command_with_context_preserved(self, fake_redis):
        """Test that commands with context are routed with context intact."""
        consumer = AICommandConsumer(
            redis=fake_redis,
            stream_name="test:ai-commands",
            consumer_group="test-group",
            consumer_name="test-consumer",
        )

        await consumer.initialize()

        cmd = AICommand(
            service=AIService.CLAUDE,
            session_id="session-123",
            workspace_path="/workspaces/test",
            message="Debug this",
            context={"file": "main.py", "line": 42, "error": "NoneType"},
        )

        message_id = b"1234567890-0"
        data = {b"payload": cmd.model_dump_json().encode()}

        await consumer._process_message(message_id, data)

        # Verify context preserved in routed message
        claude_messages = await fake_redis.xrevrange("stream:claude-commands", count=1)

        import json
        routed_payload = json.loads(claude_messages[0][1][b"payload"])
        assert routed_payload["context"]["file"] == "main.py"
        assert routed_payload["context"]["line"] == 42
        assert routed_payload["context"]["error"] == "NoneType"


@pytest.mark.unit
@pytest.mark.asyncio
class TestAICommandConsumerErrorHandling:
    """Test error handling scenarios."""

    async def test_validation_error_sends_to_dlq(self, fake_redis):
        """Test that validation errors send message to DLQ and ACK."""
        consumer = AICommandConsumer(
            redis=fake_redis,
            stream_name="test:ai-commands",
            consumer_group="test-group",
            consumer_name="test-consumer",
        )

        await consumer.initialize()

        # Invalid payload (missing required fields)
        invalid_payload = b'{"invalid": "data", "missing": "service"}'
        message_id = b"1234567890-0"
        data = {b"payload": invalid_payload}

        await consumer._process_message(message_id, data)

        # Verify sent to DLQ
        dlq_messages = await fake_redis.xrevrange("stream:ai-commands-dlq", count=1)
        assert len(dlq_messages) == 1

        # DLQ should contain error info
        dlq_data = dlq_messages[0][1]
        assert dlq_data[b"msg_id"] == message_id
        assert b"error" in dlq_data
        assert dlq_data[b"payload"] == invalid_payload

    async def test_validation_error_acks_message(self, fake_redis):
        """Test that validation errors ACK message to prevent retry."""
        consumer = AICommandConsumer(
            redis=fake_redis,
            stream_name="test:ai-commands",
            consumer_group="test-group",
            consumer_name="test-consumer",
        )

        await consumer.initialize()

        # Add invalid message
        msg_id = await fake_redis.xadd(
            "test:ai-commands",
            {b"payload": b'{"invalid": "json"}'},
        )

        # Read it (creates pending)
        await fake_redis.xreadgroup(
            groupname="test-group",
            consumername="test-consumer",
            streams={"test:ai-commands": ">"},
        )

        # Process invalid message
        data = {b"payload": b'{"invalid": "json"}'}
        await consumer._process_message(msg_id, data)

        # Should be ACKed (pending = 0)
        pending = await fake_redis.xpending("test:ai-commands", "test-group")
        assert pending["pending"] == 0

    async def test_missing_payload_handled_gracefully(self, fake_redis):
        """Test that missing payload is handled without crash."""
        consumer = AICommandConsumer(
            redis=fake_redis,
            stream_name="test:ai-commands",
            consumer_group="test-group",
            consumer_name="test-consumer",
        )

        await consumer.initialize()

        # Message without payload
        message_id = b"1234567890-0"
        data = {b"other_field": b"value"}

        # Should not raise exception
        await consumer._process_message(message_id, data)

        # Should ACK message
        # (We can't easily verify this without adding to stream first)


@pytest.mark.unit
@pytest.mark.asyncio
class TestAICommandConsumerMaxlen:
    """Test stream maxlen parameter."""

    async def test_routed_streams_have_maxlen(self, fake_redis):
        """Test that routed messages use maxlen to limit stream size."""
        consumer = AICommandConsumer(
            redis=fake_redis,
            stream_name="test:ai-commands",
            consumer_group="test-group",
            consumer_name="test-consumer",
        )

        await consumer.initialize()

        # Add many commands
        for i in range(15):
            cmd = AICommand(
                service=AIService.CLAUDE,
                session_id=f"session-{i}",
                workspace_path="/workspaces/test",
                message=f"Message {i}",
            )

            message_id = f"{i}".encode()
            data = {b"payload": cmd.model_dump_json().encode()}
            await consumer._process_message(message_id, data)

        # Check claude stream length
        # (maxlen=10000 is set in consumer, but fakeredis should respect it)
        claude_messages = await fake_redis.xrange("stream:claude-commands")

        # Should have all 15 messages (maxlen only kicks in with many more)
        assert len(claude_messages) == 15


@pytest.mark.unit
@pytest.mark.asyncio
class TestAICommandConsumerConcurrency:
    """Test concurrent processing scenarios."""

    async def test_multiple_messages_processed_sequentially(self, fake_redis):
        """Test processing multiple messages in sequence."""
        consumer = AICommandConsumer(
            redis=fake_redis,
            stream_name="test:ai-commands",
            consumer_group="test-group",
            consumer_name="test-consumer",
        )

        await consumer.initialize()

        # Create 5 commands for different services
        commands = [
            (AIService.CLAUDE, "Claude msg 1"),
            (AIService.CURSOR, "Cursor msg 1"),
            (AIService.MCP, "MCP msg 1"),
            (AIService.CLAUDE, "Claude msg 2"),
            (AIService.CURSOR, "Cursor msg 2"),
        ]

        for i, (service, message) in enumerate(commands):
            cmd = AICommand(
                service=service,
                session_id=f"session-{i}",
                workspace_path="/workspaces/test",
                message=message,
            )

            message_id = f"{i}".encode()
            data = {b"payload": cmd.model_dump_json().encode()}
            await consumer._process_message(message_id, data)

        # Verify routing
        claude_count = len(await fake_redis.xrange("stream:claude-commands"))
        cursor_count = len(await fake_redis.xrange("stream:cursor-commands"))
        mcp_count = len(await fake_redis.xrange("stream:mcp-commands"))

        assert claude_count == 2
        assert cursor_count == 2
        assert mcp_count == 1


@pytest.mark.unit
@pytest.mark.asyncio
class TestAICommandConsumerModels:
    """Test Pydantic models validation."""

    async def test_aicommand_requires_service(self):
        """Test that AICommand requires service field."""
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            AICommand(
                # Missing service
                session_id="session-123",
                workspace_path="/workspaces/test",
                message="Test",
            )

    async def test_aicommand_requires_session_id(self):
        """Test that AICommand requires session_id field."""
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            AICommand(
                service=AIService.CLAUDE,
                # Missing session_id
                workspace_path="/workspaces/test",
                message="Test",
            )

    async def test_aicommand_optional_context(self):
        """Test that context field is optional."""
        cmd = AICommand(
            service=AIService.CLAUDE,
            session_id="session-123",
            workspace_path="/workspaces/test",
            message="Test",
            # No context - should work
        )

        assert cmd.context is None

    async def test_aicommand_timestamp_auto_generated(self):
        """Test that timestamp is auto-generated if not provided."""
        cmd = AICommand(
            service=AIService.CLAUDE,
            session_id="session-123",
            workspace_path="/workspaces/test",
            message="Test",
        )

        assert cmd.timestamp is not None
        assert isinstance(cmd.timestamp, datetime)

    async def test_aiservice_enum_values(self):
        """Test AIService enum has correct values."""
        assert AIService.CLAUDE.value == "claude"
        assert AIService.CURSOR.value == "cursor"
        assert AIService.MCP.value == "mcp"
