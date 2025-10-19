"""
Unit tests for Session Handler Pydantic models.

Tests validation, required fields, and data types.
"""

import pytest
from pydantic import ValidationError

# Import only the Pydantic model classes (not the handler)
# This avoids triggering circular imports through django_ipc
import importlib.util
import sys
from pathlib import Path

# Load session_handler module directly without importing dependencies
spec = importlib.util.spec_from_file_location(
    "session_handler",
    Path(__file__).parent.parent.parent / "src/handlers/session_handler.py"
)
session_module = importlib.util.module_from_spec(spec)

# Temporarily mock django_ipc to avoid circular import
class MockBaseHandler:
    pass

sys.modules['django_ipc.handlers'] = type('module', (), {'BaseHandler': MockBaseHandler})()
sys.modules['django_ipc.server.connection_manager'] = type('module', (), {
    'ActiveConnection': object,
})()
sys.modules['django_ipc.server.message_router'] = type('module', (), {
    'MessageRouter': object,
})()
sys.modules['loguru'] = type('module', (), {'logger': type('logger', (), {
    'info': lambda *args: None,
    'debug': lambda *args: None,
    'warning': lambda *args: None,
})()})()

spec.loader.exec_module(session_module)

SessionMessageEvent = session_module.SessionMessageEvent
TaskStatusEvent = session_module.TaskStatusEvent


class TestSessionMessageEvent:
    """Test SessionMessageEvent Pydantic model."""

    def test_valid_message_event(self):
        """Test creating valid session message event."""
        data = {
            "session_id": "session-123",
            "message_id": "msg-456",
            "role": "assistant",
            "content": "Hello, how can I help?",
            "timestamp": "2025-10-06T00:00:00Z",
        }

        event = SessionMessageEvent.model_validate(data)

        assert event.session_id == "session-123"
        assert event.message_id == "msg-456"
        assert event.role == "assistant"
        assert event.content == "Hello, how can I help?"
        assert event.is_streaming is False  # Default
        assert event.is_final is True  # Default
        assert event.timestamp == "2025-10-06T00:00:00Z"

    def test_streaming_message(self):
        """Test streaming message with custom flags."""
        data = {
            "session_id": "session-123",
            "message_id": "msg-456",
            "role": "assistant",
            "content": "Partial response...",
            "is_streaming": True,
            "is_final": False,
            "timestamp": "2025-10-06T00:00:00Z",
        }

        event = SessionMessageEvent.model_validate(data)

        assert event.is_streaming is True
        assert event.is_final is False

    def test_missing_required_field(self):
        """Test validation fails with missing required field."""
        data = {
            "session_id": "session-123",
            # Missing message_id
            "role": "user",
            "content": "Hello",
            "timestamp": "2025-10-06T00:00:00Z",
        }

        with pytest.raises(ValidationError) as exc_info:
            SessionMessageEvent.model_validate(data)

        assert "message_id" in str(exc_info.value)

    def test_invalid_role_type(self):
        """Test validation with wrong data type."""
        data = {
            "session_id": "session-123",
            "message_id": "msg-456",
            "role": 123,  # Should be string
            "content": "Hello",
            "timestamp": "2025-10-06T00:00:00Z",
        }

        with pytest.raises(ValidationError):
            SessionMessageEvent.model_validate(data)


class TestTaskStatusEvent:
    """Test TaskStatusEvent Pydantic model."""

    def test_valid_task_pending(self):
        """Test creating valid pending task event."""
        data = {
            "task_id": "task-789",
            "status": "pending",
            "timestamp": "2025-10-06T00:00:00Z",
        }

        event = TaskStatusEvent.model_validate(data)

        assert event.task_id == "task-789"
        assert event.status == "pending"
        assert event.progress is None  # Optional
        assert event.result is None  # Optional
        assert event.error is None  # Optional

    def test_task_running_with_progress(self):
        """Test running task with progress."""
        data = {
            "task_id": "task-789",
            "status": "running",
            "progress": 45,
            "timestamp": "2025-10-06T00:00:00Z",
        }

        event = TaskStatusEvent.model_validate(data)

        assert event.status == "running"
        assert event.progress == 45

    def test_task_completed_with_result(self):
        """Test completed task with result."""
        data = {
            "task_id": "task-789",
            "status": "completed",
            "result": "Task finished successfully",
            "timestamp": "2025-10-06T00:00:00Z",
        }

        event = TaskStatusEvent.model_validate(data)

        assert event.status == "completed"
        assert event.result == "Task finished successfully"
        assert event.error is None

    def test_task_failed_with_error(self):
        """Test failed task with error message."""
        data = {
            "task_id": "task-789",
            "status": "failed",
            "error": "Connection timeout",
            "timestamp": "2025-10-06T00:00:00Z",
        }

        event = TaskStatusEvent.model_validate(data)

        assert event.status == "failed"
        assert event.error == "Connection timeout"
        assert event.result is None

    def test_missing_task_id(self):
        """Test validation fails without task_id."""
        data = {
            # Missing task_id
            "status": "pending",
            "timestamp": "2025-10-06T00:00:00Z",
        }

        with pytest.raises(ValidationError) as exc_info:
            TaskStatusEvent.model_validate(data)

        assert "task_id" in str(exc_info.value)

    def test_invalid_progress_type(self):
        """Test validation with invalid progress type."""
        data = {
            "task_id": "task-789",
            "status": "running",
            "progress": "fifty",  # Should be int
            "timestamp": "2025-10-06T00:00:00Z",
        }

        with pytest.raises(ValidationError):
            TaskStatusEvent.model_validate(data)
