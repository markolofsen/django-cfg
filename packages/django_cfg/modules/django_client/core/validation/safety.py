"""
Safety Manager for Code Modifications.

Ensures all code modifications are:
- Backed up before changes
- Syntax-validated after changes
- Revertible via rollback
- Logged for audit trail
"""

import ast
import logging
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class SafetyManager:
    """
    Manages backups and rollbacks for safe code modification.

    Example:
        >>> safety = SafetyManager(workspace=Path('.'))
        >>> transaction_id = safety.start_transaction()
        >>> safety.backup_file(Path('serializers.py'))
        >>> # ... modify file ...
        >>> if safety.validate_syntax(Path('serializers.py')):
        ...     safety.commit_transaction()
        ... else:
        ...     safety.rollback_transaction()
    """

    def __init__(self, workspace: Path):
        """
        Initialize safety manager.

        Args:
            workspace: Root directory for project (usually project root)
        """
        self.workspace = workspace
        self.backup_dir = workspace / '.validation_backups'
        self.transaction_id: Optional[str] = None
        self.backed_up_files: Dict[Path, Path] = {}

        # Ensure backup directory exists
        self.backup_dir.mkdir(exist_ok=True)

    def start_transaction(self) -> str:
        """
        Start a new modification transaction.

        Returns:
            Transaction ID (timestamp-based)
        """
        self.transaction_id = f"fix_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        self.backed_up_files = {}

        logger.debug(f"Started transaction: {self.transaction_id}")
        return self.transaction_id

    def backup_file(self, file_path: Path) -> Path:
        """
        Create backup of file before modification.

        Args:
            file_path: Path to file to backup

        Returns:
            Path to backup file

        Raises:
            RuntimeError: If no active transaction
            FileNotFoundError: If file doesn't exist
        """
        if not self.transaction_id:
            raise RuntimeError("No active transaction. Call start_transaction() first.")

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Create transaction backup directory
        transaction_dir = self.backup_dir / self.transaction_id
        transaction_dir.mkdir(parents=True, exist_ok=True)

        # Create backup with relative path structure
        relative_path = file_path.relative_to(self.workspace)
        backup_path = transaction_dir / relative_path
        backup_path.parent.mkdir(parents=True, exist_ok=True)

        # Copy file
        shutil.copy2(file_path, backup_path)
        self.backed_up_files[file_path] = backup_path

        logger.debug(f"Backed up: {file_path} → {backup_path}")
        return backup_path

    def validate_syntax(self, file_path: Path) -> bool:
        """
        Validate Python syntax after modification.

        Args:
            file_path: Path to Python file to validate

        Returns:
            True if syntax is valid, False otherwise
        """
        try:
            content = file_path.read_text(encoding='utf-8')
            ast.parse(content)
            logger.debug(f"Syntax valid: {file_path}")
            return True
        except SyntaxError as e:
            logger.error(f"Syntax error in {file_path}: {e}")
            return False
        except Exception as e:
            logger.error(f"Error validating {file_path}: {e}")
            return False

    def rollback_file(self, file_path: Path) -> bool:
        """
        Rollback a single file to its backup.

        Args:
            file_path: Path to file to rollback

        Returns:
            True if rollback successful, False otherwise
        """
        backup_path = self.backed_up_files.get(file_path)
        if not backup_path or not backup_path.exists():
            logger.warning(f"No backup found for: {file_path}")
            return False

        try:
            shutil.copy2(backup_path, file_path)
            logger.debug(f"Rolled back: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error rolling back {file_path}: {e}")
            return False

    def commit_transaction(self) -> bool:
        """
        Finalize successful transaction.

        Keeps backups for 7 days then schedules cleanup.

        Returns:
            True if commit successful
        """
        if not self.transaction_id:
            logger.warning("No active transaction to commit")
            return False

        logger.debug(f"Committed transaction: {self.transaction_id}")

        # Schedule cleanup (delete backups after 7 days)
        self._schedule_cleanup(days=7)

        # Clear transaction state
        transaction_id = self.transaction_id
        self.transaction_id = None
        self.backed_up_files = {}

        return True

    def rollback_transaction(self) -> bool:
        """
        Revert all changes in current transaction.

        Returns:
            True if all files rolled back successfully
        """
        if not self.transaction_id:
            logger.warning("No active transaction to rollback")
            return False

        logger.warning(f"Rolling back transaction: {self.transaction_id}")

        success = True
        for file_path in self.backed_up_files.keys():
            if not self.rollback_file(file_path):
                success = False

        # Clear transaction state
        self.transaction_id = None
        self.backed_up_files = {}

        return success

    def _schedule_cleanup(self, days: int = 7) -> None:
        """
        Schedule cleanup of old backups.

        Note: Currently just marks with timestamp.
        Actual cleanup should be done by separate process.

        Args:
            days: Keep backups for this many days
        """
        cleanup_marker = self.backup_dir / self.transaction_id / '.cleanup_after'
        cleanup_date = datetime.now() + timedelta(days=days)
        cleanup_marker.write_text(cleanup_date.isoformat())

    def cleanup_old_backups(self, days: int = 7) -> int:
        """
        Remove backups older than specified days.

        Args:
            days: Remove backups older than this many days

        Returns:
            Number of backup directories removed
        """
        removed = 0
        cutoff_date = datetime.now() - timedelta(days=days)

        for transaction_dir in self.backup_dir.iterdir():
            if not transaction_dir.is_dir():
                continue

            # Check if marked for cleanup
            cleanup_marker = transaction_dir / '.cleanup_after'
            if cleanup_marker.exists():
                cleanup_date = datetime.fromisoformat(cleanup_marker.read_text())
                if datetime.now() >= cleanup_date:
                    shutil.rmtree(transaction_dir)
                    removed += 1
                    logger.debug(f"Removed old backup: {transaction_dir.name}")

        return removed

    def list_backups(self) -> List[Dict[str, any]]:
        """
        List all available backups.

        Returns:
            List of backup info dicts
        """
        backups = []

        for transaction_dir in sorted(self.backup_dir.iterdir()):
            if not transaction_dir.is_dir():
                continue

            # Parse transaction ID
            timestamp_str = transaction_dir.name.replace('fix_', '')
            try:
                timestamp = datetime.strptime(timestamp_str[:15], '%Y%m%d_%H%M%S')
            except ValueError:
                continue

            # Count files
            files = list(transaction_dir.rglob('*.py'))

            backups.append({
                'transaction_id': transaction_dir.name,
                'timestamp': timestamp,
                'file_count': len(files),
                'path': transaction_dir,
            })

        return backups
