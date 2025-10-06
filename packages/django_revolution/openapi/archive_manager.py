"""
Archive Manager for Django Revolution

Manages archiving of generated clients with versioning and compression.
"""

import json
import shutil
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from ..config import DjangoRevolutionSettings, GenerationResult
from ..utils import Logger, ensure_directories


class ArchiveManager:
    """Manages archiving of generated client libraries."""

    def __init__(
        self, config: DjangoRevolutionSettings, logger: Logger, output_dir: Path
    ):
        """
        Initialize archive manager.

        Args:
            config: Django Revolution settings
            logger: Logger instance
            output_dir: Base output directory
        """
        self.config = config
        self.logger = logger
        self.output_dir = output_dir

        # Base archive directory
        self.archive_dir = output_dir / "archive"
        ensure_directories(self.archive_dir)

    def archive_zone_clients(
        self,
        zone_name: str,
        typescript_path: Optional[Path] = None,
        python_path: Optional[Path] = None,
    ) -> Dict[str, Any]:
        """
        Archive both TypeScript and Python clients for a zone in a single archive.

        Args:
            zone_name: Name of the zone
            typescript_path: Path to the generated TypeScript client (optional)
            python_path: Path to the generated Python client (optional)

        Returns:
            Archive operation result
        """
        if not typescript_path and not python_path:
            error_msg = f"No clients provided for zone {zone_name}"
            self.logger.error(error_msg)
            return {"success": False, "error": error_msg, "zone_name": zone_name}

        try:
            # Generate timestamp for versioning
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            date_folder = datetime.now().strftime("%Y-%m-%d")

            # Create timestamp-based archive directory
            files_dir = self.archive_dir / "files"
            timestamp_dir = files_dir / timestamp
            timestamp_dir.mkdir(parents=True, exist_ok=True)

            # Create latest directory
            latest_dir = self.archive_dir / "latest"
            latest_dir.mkdir(parents=True, exist_ok=True)

            self.logger.debug(
                f"Ensured archive directories exist: {timestamp_dir}, {latest_dir}"
            )

            # Create archive filename
            archive_filename = f"{zone_name}.zip"

            # Create temporary directory for combined clients
            temp_dir = self.archive_dir / f"temp_{zone_name}_{timestamp}"
            temp_dir.mkdir(exist_ok=True)

            try:
                # Copy TypeScript client if available
                ts_available = False
                if typescript_path and typescript_path.exists():
                    ts_dest = temp_dir / "typescript"
                    if ts_dest.exists():
                        import shutil

                        shutil.rmtree(ts_dest)
                    import shutil

                    shutil.copytree(typescript_path, ts_dest)
                    ts_available = True
                    self.logger.debug(
                        f"Added TypeScript client to archive: {typescript_path}"
                    )

                # Copy Python client if available
                py_available = False
                if python_path and python_path.exists():
                    py_dest = temp_dir / "python"
                    py_dest.mkdir(exist_ok=True)

                    # Handle both file and directory cases
                    if python_path.is_file():
                        # datamodel-code-generator creates a single file
                        import shutil

                        shutil.copy2(python_path, py_dest / python_path.name)

                        # Also copy any additional files in the same directory
                        python_dir = python_path.parent
                        for additional_file in python_dir.iterdir():
                            if (
                                additional_file.is_file()
                                and additional_file != python_path
                            ):
                                shutil.copy2(
                                    additional_file, py_dest / additional_file.name
                                )
                    else:
                        # datamodel-code-generator creates a file
                        if py_dest.exists():
                            import shutil

                            shutil.rmtree(py_dest)
                        import shutil

                        shutil.copytree(python_path, py_dest)

                    py_available = True
                    self.logger.debug(f"Added Python client to archive: {python_path}")

                # Create timestamped archive
                timestamped_path = timestamp_dir / archive_filename
                self._create_zip_archive(temp_dir, timestamped_path)

                # Create latest archive (overwrite if exists)
                latest_path = latest_dir / archive_filename
                self._create_zip_archive(temp_dir, latest_path)

                # Verify archives were created
                if not timestamped_path.exists():
                    raise FileNotFoundError(
                        f"Timestamped archive was not created: {timestamped_path}"
                    )
                if not latest_path.exists():
                    raise FileNotFoundError(
                        f"Latest archive was not created: {latest_path}"
                    )

                self.logger.debug(
                    f"Verified archives exist: {timestamped_path.name}, {latest_path.name}"
                )

                # Log archive sizes
                timestamped_size = timestamped_path.stat().st_size / (1024 * 1024)  # MB
                latest_size = latest_path.stat().st_size / (1024 * 1024)  # MB
                self.logger.debug(
                    f"Archive sizes - Timestamped: {timestamped_size:.2f}MB, Latest: {latest_size:.2f}MB"
                )

                # Generate metadata
                metadata = self._generate_zone_metadata(
                    zone_name,
                    typescript_path,
                    python_path,
                    timestamp,
                    ts_available,
                    py_available,
                )
                metadata_path = timestamp_dir / f"{zone_name}_metadata.json"
                self._write_metadata(metadata, metadata_path)

                self.logger.success(
                    f"Archived zone {zone_name} with TypeScript: {ts_available}, Python: {py_available}"
                )

                return {
                    "success": True,
                    "zone_name": zone_name,
                    "timestamped_archive": str(timestamped_path),
                    "latest_archive": str(latest_path),
                    "metadata": str(metadata_path),
                    "timestamp": timestamp,
                    "date_folder": date_folder,
                    "typescript_available": ts_available,
                    "python_available": py_available,
                }

            finally:
                # Clean up temporary directory
                if temp_dir.exists():
                    shutil.rmtree(temp_dir)
                    self.logger.debug(f"Cleaned up temporary directory: {temp_dir}")

        except Exception as e:
            error_msg = f"Failed to archive zone {zone_name}: {str(e)}"
            self.logger.error(error_msg)

            return {"success": False, "error": error_msg, "zone_name": zone_name}

    def archive_typescript_client(
        self, zone_name: str, client_path: Path
    ) -> Dict[str, Any]:
        """
        Archive a TypeScript client (legacy method for backward compatibility).

        Args:
            zone_name: Name of the zone
            client_path: Path to the generated client

        Returns:
            Archive operation result
        """
        return self.archive_zone_clients(zone_name, typescript_path=client_path)

    def archive_python_client(
        self, zone_name: str, client_path: Path
    ) -> Dict[str, Any]:
        """
        Archive a Python client (legacy method for backward compatibility).

        Args:
            zone_name: Name of the zone
            client_path: Path to the generated client

        Returns:
            Archive operation result
        """
        return self.archive_zone_clients(zone_name, python_path=client_path)

    def _create_zip_archive(self, source_path: Path, archive_path: Path):
        """Create a zip archive."""
        try:
            with zipfile.ZipFile(archive_path, "w", zipfile.ZIP_DEFLATED) as zipf:
                file_count = 0
                for file_path in source_path.rglob("*"):
                    if file_path.is_file():
                        # Skip error log files
                        if (
                            file_path.name.startswith("error_")
                            and file_path.suffix == ".log"
                        ):
                            continue

                        # Create relative path for archive
                        relative_path = file_path.relative_to(source_path)
                        zipf.write(file_path, relative_path)
                        file_count += 1

                self.logger.debug(
                    f"Created ZIP archive with {file_count} files: {archive_path}"
                )
        except Exception as e:
            self.logger.error(f"Failed to create ZIP archive {archive_path}: {e}")
            raise

    def _generate_zone_metadata(
        self,
        zone_name: str,
        typescript_path: Optional[Path],
        python_path: Optional[Path],
        timestamp: str,
        ts_available: bool,
        py_available: bool,
    ) -> Dict[str, Any]:
        """Generate metadata for the archived zone."""
        metadata = {
            "zone_name": zone_name,
            "timestamp": timestamp,
            "archive_date": datetime.now().isoformat(),
            "generator_version": "2.0.0",
            "clients": {
                "typescript": {
                    "available": ts_available,
                    "path": str(typescript_path) if typescript_path else None,
                    "file_count": 0,
                    "size_bytes": 0,
                },
                "python": {
                    "available": py_available,
                    "path": str(python_path) if python_path else None,
                    "file_count": 0,
                    "size_bytes": 0,
                },
            },
        }

        # Calculate TypeScript stats
        if ts_available and typescript_path:
            ts_stats = self._calculate_client_stats(typescript_path)
            metadata["clients"]["typescript"].update(ts_stats)

        # Calculate Python stats
        if py_available and python_path:
            py_stats = self._calculate_client_stats(python_path)
            metadata["clients"]["python"].update(py_stats)

        # Calculate total stats
        total_files = (
            metadata["clients"]["typescript"]["file_count"]
            + metadata["clients"]["python"]["file_count"]
        )
        total_size = (
            metadata["clients"]["typescript"]["size_bytes"]
            + metadata["clients"]["python"]["size_bytes"]
        )

        metadata["total_files"] = total_files
        metadata["total_size_bytes"] = total_size
        metadata["total_size_mb"] = round(total_size / (1024 * 1024), 2)

        return metadata

    def _calculate_client_stats(self, client_path: Path) -> Dict[str, Any]:
        """Calculate file count and size for a client."""
        file_count = 0
        total_size = 0

        for file_path in client_path.rglob("*"):
            if file_path.is_file():
                file_count += 1
                total_size += file_path.stat().st_size

        return {
            "file_count": file_count,
            "size_bytes": total_size,
            "size_mb": round(total_size / (1024 * 1024), 2),
        }

    def _write_metadata(self, metadata: Dict[str, Any], metadata_path: Path):
        """Write metadata to file."""
        try:
            with open(metadata_path, "w", encoding="utf-8") as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)

            self.logger.debug(f"Written metadata: {metadata_path}")
        except Exception as e:
            self.logger.error(f"Failed to write metadata {metadata_path}: {e}")
            raise

    def archive_all_clients(
        self,
        clients_dir: Path,
        typescript_results: Dict[str, GenerationResult],
        python_results: Dict[str, GenerationResult],
    ) -> Dict[str, Any]:
        """
        Archive all generated clients by zone.

        Args:
            clients_dir: Base clients directory
            typescript_results: TypeScript generation results
            python_results: Python generation results

        Returns:
            Overall archive operation results
        """
        archive_results = {
            "zones": {},
            "summary": {"total_zones": 0, "successful": 0, "failed": 0},
        }

        # Get all unique zones
        all_zones = set(typescript_results.keys()) | set(python_results.keys())

        for zone_name in all_zones:
            archive_results["summary"]["total_zones"] += 1

            # Get TypeScript and Python paths for this zone
            ts_path = (
                typescript_results[zone_name].output_path
                if zone_name in typescript_results
                and typescript_results[zone_name].success
                else None
            )
            py_path = (
                python_results[zone_name].output_path
                if zone_name in python_results and python_results[zone_name].success
                else None
            )

            # Archive the zone
            archive_result = self.archive_zone_clients(zone_name, ts_path, py_path)
            archive_results["zones"][zone_name] = archive_result

            if archive_result["success"]:
                archive_results["summary"]["successful"] += 1
            else:
                archive_results["summary"]["failed"] += 1

        self.logger.info(
            f"Archive completed: {archive_results['summary']['successful']} successful, "
            f"{archive_results['summary']['failed']} failed"
        )

        return archive_results

    def list_archives(self) -> Dict[str, Any]:
        """
        List available archives.

        Returns:
            Dictionary of available archives
        """
        if not self.archive_dir.exists():
            return {"latest": [], "files": []}

        # List latest archives
        latest_archives = []
        latest_dir = self.archive_dir / "latest"
        if latest_dir.exists():
            for archive_file in latest_dir.glob("*.zip"):
                metadata_file = latest_dir / f"{archive_file.stem}_metadata.json"

                archive_info = {
                    "zone_name": archive_file.stem,
                    "filename": archive_file.name,
                    "path": str(archive_file),
                    "size_mb": round(archive_file.stat().st_size / (1024 * 1024), 2),
                    "created": datetime.fromtimestamp(
                        archive_file.stat().st_ctime
                    ).isoformat(),
                    "metadata_available": metadata_file.exists(),
                }

                # Add metadata if available
                if metadata_file.exists():
                    try:
                        with open(metadata_file, "r") as f:
                            metadata = json.load(f)
                            archive_info["typescript_available"] = (
                                metadata.get("clients", {})
                                .get("typescript", {})
                                .get("available", False)
                            )
                            archive_info["python_available"] = (
                                metadata.get("clients", {})
                                .get("python", {})
                                .get("available", False)
                            )
                    except Exception:
                        pass

                latest_archives.append(archive_info)

        # List timestamp-based archives
        files_archives = []
        files_dir = self.archive_dir / "files"
        if files_dir.exists():
            for timestamp_dir in files_dir.iterdir():
                if timestamp_dir.is_dir():
                    timestamp_info = {"timestamp": timestamp_dir.name, "archives": []}

                    for archive_file in timestamp_dir.glob("*.zip"):
                        if "_metadata" not in archive_file.name:
                            metadata_file = (
                                timestamp_dir / f"{archive_file.stem}_metadata.json"
                            )

                            archive_info = {
                                "zone_name": archive_file.stem,
                                "filename": archive_file.name,
                                "path": str(archive_file),
                                "size_mb": round(
                                    archive_file.stat().st_size / (1024 * 1024), 2
                                ),
                                "created": datetime.fromtimestamp(
                                    archive_file.stat().st_ctime
                                ).isoformat(),
                                "metadata_available": metadata_file.exists(),
                            }

                            # Add metadata if available
                            if metadata_file.exists():
                                try:
                                    with open(metadata_file, "r") as f:
                                        metadata = json.load(f)
                                        archive_info["typescript_available"] = (
                                            metadata.get("clients", {})
                                            .get("typescript", {})
                                            .get("available", False)
                                        )
                                        archive_info["python_available"] = (
                                            metadata.get("clients", {})
                                            .get("python", {})
                                            .get("available", False)
                                        )
                                except Exception:
                                    pass

                            timestamp_info["archives"].append(archive_info)

                    # Sort archives by creation time (newest first)
                    timestamp_info["archives"].sort(
                        key=lambda x: x["created"], reverse=True
                    )
                    files_archives.append(timestamp_info)

        # Sort timestamps (newest first)
        files_archives.sort(key=lambda x: x["timestamp"], reverse=True)

        return {"latest": latest_archives, "files": files_archives}

    def clean_old_archives(self, keep_days: int = 30) -> Dict[str, Any]:
        """
        Clean old archives, keeping only archives from the last N days.

        Args:
            keep_days: Number of days to keep archives

        Returns:
            Cleanup operation results
        """
        if not self.archive_dir.exists():
            return {"removed": 0, "kept": 0}

        from datetime import timedelta

        cutoff_date = datetime.now() - timedelta(days=keep_days)
        removed_count = 0
        kept_count = 0

        # Clean timestamp-based archives
        files_dir = self.archive_dir / "files"
        if files_dir.exists():
            for timestamp_dir in files_dir.iterdir():
                if timestamp_dir.is_dir():
                    try:
                        # Extract date from timestamp (YYYYMMDD_HHMMSS)
                        date_str = timestamp_dir.name.split("_")[0]
                        dir_date = datetime.strptime(date_str, "%Y%m%d")
                        if dir_date < cutoff_date:
                            # Remove entire timestamp directory
                            shutil.rmtree(timestamp_dir)
                            removed_count += 1
                            self.logger.info(
                                f"Removed old archive directory: {timestamp_dir}"
                            )
                        else:
                            kept_count += 1
                    except (ValueError, IndexError):
                        # Skip directories that don't match timestamp format
                        continue

        self.logger.info(
            f"Archive cleanup completed: {removed_count} directories removed, {kept_count} kept"
        )

        return {"removed": removed_count, "kept": kept_count}
