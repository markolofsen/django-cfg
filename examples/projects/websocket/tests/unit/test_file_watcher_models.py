"""
Unit tests for File Watcher Consumer Pydantic models.

Tests validation for nested file event structure.
"""

import pytest
from pydantic import ValidationError

# Import models directly without triggering full consumer initialization
import importlib.util
import sys
from pathlib import Path

# Mock Redis and loguru to avoid import errors
sys.modules['redis.asyncio'] = type('module', (), {'Redis': object})()
sys.modules['loguru'] = type('module', (), {'logger': type('logger', (), {
    'info': lambda *args: None,
    'debug': lambda *args: None,
    'warning': lambda *args: None,
    'error': lambda *args: None,
})()})()

# Load file_watcher_consumer module directly
spec = importlib.util.spec_from_file_location(
    "file_watcher_consumer",
    Path(__file__).parent.parent.parent / "src/consumers/file_watcher_consumer.py"
)
consumer_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(consumer_module)

WorkspaceInfo = consumer_module.WorkspaceInfo
FileInfo = consumer_module.FileInfo
ChangeInfo = consumer_module.ChangeInfo
GitInfo = consumer_module.GitInfo
FileEvent = consumer_module.FileEvent
BatchEvent = consumer_module.BatchEvent


class TestWorkspaceInfo:
    """Test WorkspaceInfo model."""

    def test_valid_workspace_with_name(self):
        """Test workspace with ID and name."""
        data = {"id": "workspace-123", "name": "My Project"}

        workspace = WorkspaceInfo.model_validate(data)

        assert workspace.id == "workspace-123"
        assert workspace.name == "My Project"

    def test_workspace_without_name(self):
        """Test workspace with only ID (name is optional)."""
        data = {"id": "workspace-456"}

        workspace = WorkspaceInfo.model_validate(data)

        assert workspace.id == "workspace-456"
        assert workspace.name is None

    def test_missing_id(self):
        """Test validation fails without workspace ID."""
        data = {"name": "My Project"}

        with pytest.raises(ValidationError) as exc_info:
            WorkspaceInfo.model_validate(data)

        assert "id" in str(exc_info.value)


class TestFileInfo:
    """Test FileInfo model."""

    def test_file_create_event(self):
        """Test file creation event."""
        data = {
            "path": "src/main.py",
            "event_type": "create",
        }

        file_info = FileInfo.model_validate(data)

        assert file_info.path == "src/main.py"
        assert file_info.event_type == "create"
        assert file_info.old_path is None

    def test_file_rename_event(self):
        """Test file rename with old_path."""
        data = {
            "path": "src/new_name.py",
            "event_type": "rename",
            "old_path": "src/old_name.py",
        }

        file_info = FileInfo.model_validate(data)

        assert file_info.path == "src/new_name.py"
        assert file_info.event_type == "rename"
        assert file_info.old_path == "src/old_name.py"

    def test_missing_path(self):
        """Test validation fails without file path."""
        data = {"event_type": "create"}

        with pytest.raises(ValidationError) as exc_info:
            FileInfo.model_validate(data)

        assert "path" in str(exc_info.value)


class TestChangeInfo:
    """Test ChangeInfo model."""

    def test_diff_change(self):
        """Test change with git diff."""
        data = {
            "type": "diff",
            "diff": "@@ -1,3 +1,4 @@\n+new line",
        }

        change = ChangeInfo.model_validate(data)

        assert change.type == "diff"
        assert change.diff == "@@ -1,3 +1,4 @@\n+new line"
        assert change.content is None

    def test_full_content_change(self):
        """Test change with full file content."""
        data = {
            "type": "full_content",
            "content": "print('Hello, World!')",
        }

        change = ChangeInfo.model_validate(data)

        assert change.type == "full_content"
        assert change.content == "print('Hello, World!')"
        assert change.diff is None

    def test_hash_change_binary(self):
        """Test binary file change (hash only)."""
        data = {
            "type": "hash",
            "hash": "a1b2c3d4e5f6",
            "size": 1024,
        }

        change = ChangeInfo.model_validate(data)

        assert change.type == "hash"
        assert change.hash == "a1b2c3d4e5f6"
        assert change.size == 1024
        assert change.content is None
        assert change.diff is None

    def test_delete_change(self):
        """Test file deletion."""
        data = {"type": "delete"}

        change = ChangeInfo.model_validate(data)

        assert change.type == "delete"
        assert change.diff is None
        assert change.content is None


class TestGitInfo:
    """Test GitInfo model."""

    def test_git_info_full(self):
        """Test git info with all fields."""
        data = {
            "branch": "main",
            "commit": "a1b2c3d",
            "author": "John Doe",
        }

        git = GitInfo.model_validate(data)

        assert git.branch == "main"
        assert git.commit == "a1b2c3d"
        assert git.author == "John Doe"

    def test_git_info_branch_only(self):
        """Test git info with only branch (commit and author optional)."""
        data = {"branch": "develop"}

        git = GitInfo.model_validate(data)

        assert git.branch == "develop"
        assert git.commit is None
        assert git.author is None


class TestFileEvent:
    """Test FileEvent nested model."""

    def test_complete_file_event(self):
        """Test complete file event with all nested structures."""
        data = {
            "event_id": "event-789",
            "timestamp": "2025-10-06T00:00:00Z",
            "batch_id": "batch-123",
            "workspace": {
                "id": "workspace-456",
                "name": "My Project",
            },
            "file": {
                "path": "src/main.py",
                "event_type": "modify",
            },
            "change": {
                "type": "diff",
                "diff": "@@ -1 +1 @@\n-old line\n+new line",
            },
            "git": {
                "branch": "feature/test",
                "commit": "abc123",
            },
        }

        event = FileEvent.model_validate(data)

        assert event.event_id == "event-789"
        assert event.workspace.id == "workspace-456"
        assert event.file.path == "src/main.py"
        assert event.change.type == "diff"
        assert event.git.branch == "feature/test"

    def test_file_event_without_git(self):
        """Test file event without git info (optional)."""
        data = {
            "event_id": "event-789",
            "timestamp": "2025-10-06T00:00:00Z",
            "workspace": {"id": "workspace-456"},
            "file": {
                "path": "README.md",
                "event_type": "create",
            },
            "change": {
                "type": "full_content",
                "content": "# My Project",
            },
        }

        event = FileEvent.model_validate(data)

        assert event.event_id == "event-789"
        assert event.git is None

    def test_missing_nested_workspace(self):
        """Test validation fails without workspace."""
        data = {
            "event_id": "event-789",
            "timestamp": "2025-10-06T00:00:00Z",
            # Missing workspace
            "file": {"path": "test.txt", "event_type": "create"},
            "change": {"type": "full_content", "content": "test"},
        }

        with pytest.raises(ValidationError) as exc_info:
            FileEvent.model_validate(data)

        assert "workspace" in str(exc_info.value)


class TestBatchEvent:
    """Test BatchEvent model."""

    def test_batch_with_multiple_events(self):
        """Test batch containing multiple file events."""
        data = {
            "batch_id": "batch-999",
            "timestamp": "2025-10-06T00:00:00Z",
            "batch_count": 2,
            "events": [
                {
                    "event_id": "event-1",
                    "timestamp": "2025-10-06T00:00:00Z",
                    "workspace": {"id": "workspace-1"},
                    "file": {"path": "file1.txt", "event_type": "create"},
                    "change": {"type": "full_content", "content": "content1"},
                },
                {
                    "event_id": "event-2",
                    "timestamp": "2025-10-06T00:00:01Z",
                    "workspace": {"id": "workspace-1"},
                    "file": {"path": "file2.txt", "event_type": "modify"},
                    "change": {"type": "diff", "diff": "+new line"},
                },
            ],
        }

        batch = BatchEvent.model_validate(data)

        assert batch.batch_id == "batch-999"
        assert batch.batch_count == 2
        assert len(batch.events) == 2
        assert batch.events[0].event_id == "event-1"
        assert batch.events[1].event_id == "event-2"

    def test_empty_batch(self):
        """Test batch with no events (edge case)."""
        data = {
            "batch_id": "batch-empty",
            "timestamp": "2025-10-06T00:00:00Z",
            "batch_count": 0,
            "events": [],
        }

        batch = BatchEvent.model_validate(data)

        assert batch.batch_count == 0
        assert len(batch.events) == 0
