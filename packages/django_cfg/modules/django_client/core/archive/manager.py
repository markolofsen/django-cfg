"""
Simple Archive Manager.

Lightweight client archiving without complex dependencies.
"""

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional


class ArchiveManager:
    """
    Simple archive manager for generated clients.

    Creates timestamped copies + 'latest' symlink.
    """

    def __init__(self, base_dir: Path):
        """
        Initialize archive manager.

        Args:
            base_dir: Base directory for archives
        """
        self.base_dir = Path(base_dir)
        self.archive_dir = self.base_dir / "archive"
        self.archive_dir.mkdir(parents=True, exist_ok=True)

    def archive_clients(
        self,
        group_name: str,
        python_dir: Optional[Path] = None,
        typescript_dir: Optional[Path] = None,
        go_dir: Optional[Path] = None,
        proto_dir: Optional[Path] = None,
    ) -> Dict:
        """
        Archive generated clients.

        Args:
            group_name: Name of the group
            python_dir: Python client directory
            typescript_dir: TypeScript client directory
            go_dir: Go client directory
            proto_dir: Protocol Buffer definitions directory

        Returns:
            Archive result dictionary
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Create timestamped directory
        archive_path = self.archive_dir / timestamp / group_name
        archive_path.mkdir(parents=True, exist_ok=True)

        # Copy clients
        copied = {}

        if python_dir and python_dir.exists():
            dest = archive_path / "python"
            shutil.copytree(python_dir, dest, dirs_exist_ok=True)
            copied["python"] = str(dest)

        if typescript_dir and typescript_dir.exists():
            dest = archive_path / "typescript"
            shutil.copytree(typescript_dir, dest, dirs_exist_ok=True)
            copied["typescript"] = str(dest)

        if go_dir and go_dir.exists():
            dest = archive_path / "go"
            shutil.copytree(go_dir, dest, dirs_exist_ok=True)
            copied["go"] = str(dest)

        if proto_dir and proto_dir.exists():
            dest = archive_path / "proto"
            shutil.copytree(proto_dir, dest, dirs_exist_ok=True)
            copied["proto"] = str(dest)

        # Create metadata
        metadata = {
            "group": group_name,
            "timestamp": timestamp,
            "datetime": datetime.now().isoformat(),
            "clients": copied,
        }

        metadata_file = archive_path / "metadata.json"
        metadata_file.write_text(json.dumps(metadata, indent=2))

        # Create/update 'latest' symlink
        latest_link = self.archive_dir / "latest" / group_name
        latest_link.parent.mkdir(parents=True, exist_ok=True)

        if latest_link.exists() or latest_link.is_symlink():
            latest_link.unlink()

        try:
            latest_link.symlink_to(archive_path, target_is_directory=True)
        except OSError:
            # Fallback: copy instead of symlink (Windows)
            if latest_link.exists():
                shutil.rmtree(latest_link)
            shutil.copytree(archive_path, latest_link)

        return {
            "success": True,
            "archive_path": str(archive_path),
            "timestamp": timestamp,
            "clients": list(copied.keys()),
        }

    def list_archives(self, group_name: Optional[str] = None) -> list:
        """
        List available archives.

        Args:
            group_name: Optional group filter

        Returns:
            List of archive info dictionaries
        """
        archives = []

        for timestamp_dir in sorted(self.archive_dir.iterdir()):
            if timestamp_dir.name == "latest":
                continue

            if not timestamp_dir.is_dir():
                continue

            for group_dir in timestamp_dir.iterdir():
                if group_name and group_dir.name != group_name:
                    continue

                metadata_file = group_dir / "metadata.json"
                if metadata_file.exists():
                    metadata = json.loads(metadata_file.read_text())
                    archives.append(metadata)

        return archives


__all__ = [
    "ArchiveManager",
]
