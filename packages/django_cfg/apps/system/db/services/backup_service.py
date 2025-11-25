"""
Database Backup Service.

Provides backup and restore functionality for PostgreSQL, MySQL, and SQLite.
"""

import gzip
import hashlib
import logging
import os
import shutil
import subprocess
import tempfile
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Type

from django.conf import settings
from django.db import connections

logger = logging.getLogger(__name__)


class DatabaseBackupError(Exception):
    """Base exception for backup errors."""

    pass


class BackupDriver(ABC):
    """Abstract base class for database-specific backup drivers."""

    def __init__(self, database_config: Dict[str, Any]):
        self.config = database_config
        self.name = database_config.get("NAME", "")
        self.host = database_config.get("HOST", "localhost")
        self.port = database_config.get("PORT", "")
        self.user = database_config.get("USER", "")
        self.password = database_config.get("PASSWORD", "")

    @abstractmethod
    def create_backup(
        self,
        output_path: Path,
        exclude_tables: List[str] = None,
        include_tables: List[str] = None,
        extra_options: List[str] = None,
    ) -> Tuple[bool, str]:
        """
        Create database backup.

        Returns:
            Tuple of (success, message)
        """
        pass

    @abstractmethod
    def restore_backup(
        self,
        input_path: Path,
        extra_options: List[str] = None,
    ) -> Tuple[bool, str]:
        """
        Restore database from backup.

        Returns:
            Tuple of (success, message)
        """
        pass

    @abstractmethod
    def get_tables_info(self) -> Dict[str, int]:
        """
        Get table names and approximate row counts.

        Returns:
            Dict mapping table name to row count
        """
        pass


class PostgreSQLDriver(BackupDriver):
    """PostgreSQL backup driver using pg_dump/pg_restore."""

    def create_backup(
        self,
        output_path: Path,
        exclude_tables: List[str] = None,
        include_tables: List[str] = None,
        extra_options: List[str] = None,
    ) -> Tuple[bool, str]:
        """Create PostgreSQL backup using pg_dump."""
        cmd = ["pg_dump", "--format=custom", "--no-password"]

        # Connection options
        if self.host:
            cmd.extend(["--host", self.host])
        if self.port:
            cmd.extend(["--port", str(self.port)])
        if self.user:
            cmd.extend(["--username", self.user])

        # Table filtering
        if include_tables:
            for table in include_tables:
                cmd.extend(["--table", table])
        elif exclude_tables:
            for table in exclude_tables:
                cmd.extend(["--exclude-table", table])

        # Extra options
        if extra_options:
            cmd.extend(extra_options)

        # Database name
        cmd.append(self.name)

        # Output file
        cmd.extend(["--file", str(output_path)])

        # Set password environment variable
        env = os.environ.copy()
        if self.password:
            env["PGPASSWORD"] = self.password

        try:
            result = subprocess.run(
                cmd,
                env=env,
                capture_output=True,
                text=True,
                timeout=3600,  # 1 hour timeout
            )

            if result.returncode != 0:
                return False, f"pg_dump failed: {result.stderr}"

            return True, "PostgreSQL backup completed successfully"

        except subprocess.TimeoutExpired:
            return False, "pg_dump timed out after 1 hour"
        except Exception as e:
            return False, f"pg_dump error: {str(e)}"

    def restore_backup(
        self,
        input_path: Path,
        extra_options: List[str] = None,
    ) -> Tuple[bool, str]:
        """Restore PostgreSQL backup using pg_restore."""
        cmd = ["pg_restore", "--no-password", "--clean", "--if-exists"]

        # Connection options
        if self.host:
            cmd.extend(["--host", self.host])
        if self.port:
            cmd.extend(["--port", str(self.port)])
        if self.user:
            cmd.extend(["--username", self.user])

        # Database name
        cmd.extend(["--dbname", self.name])

        # Extra options
        if extra_options:
            cmd.extend(extra_options)

        # Input file
        cmd.append(str(input_path))

        # Set password environment variable
        env = os.environ.copy()
        if self.password:
            env["PGPASSWORD"] = self.password

        try:
            result = subprocess.run(
                cmd,
                env=env,
                capture_output=True,
                text=True,
                timeout=3600,
            )

            # pg_restore returns warnings as errors, check for actual failures
            if result.returncode != 0 and "ERROR" in result.stderr:
                return False, f"pg_restore failed: {result.stderr}"

            return True, "PostgreSQL restore completed successfully"

        except subprocess.TimeoutExpired:
            return False, "pg_restore timed out after 1 hour"
        except Exception as e:
            return False, f"pg_restore error: {str(e)}"

    def get_tables_info(self) -> Dict[str, int]:
        """Get PostgreSQL tables and row counts."""
        from django.db import connection

        tables = {}
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT schemaname, tablename
                FROM pg_tables
                WHERE schemaname = 'public'
                """
            )
            for row in cursor.fetchall():
                table_name = row[1]
                try:
                    cursor.execute(f'SELECT COUNT(*) FROM "{table_name}"')
                    count = cursor.fetchone()[0]
                    tables[table_name] = count
                except Exception:
                    tables[table_name] = 0
        return tables


class MySQLDriver(BackupDriver):
    """MySQL backup driver using mysqldump/mysql."""

    def create_backup(
        self,
        output_path: Path,
        exclude_tables: List[str] = None,
        include_tables: List[str] = None,
        extra_options: List[str] = None,
    ) -> Tuple[bool, str]:
        """Create MySQL backup using mysqldump."""
        cmd = ["mysqldump", "--single-transaction", "--routines", "--triggers"]

        # Connection options
        if self.host:
            cmd.extend(["--host", self.host])
        if self.port:
            cmd.extend(["--port", str(self.port)])
        if self.user:
            cmd.extend(["--user", self.user])
        if self.password:
            cmd.extend([f"--password={self.password}"])

        # Extra options
        if extra_options:
            cmd.extend(extra_options)

        # Database and tables
        cmd.append(self.name)
        if include_tables:
            cmd.extend(include_tables)
        elif exclude_tables:
            for table in exclude_tables:
                cmd.extend(["--ignore-table", f"{self.name}.{table}"])

        try:
            with open(output_path, "w") as f:
                result = subprocess.run(
                    cmd,
                    stdout=f,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=3600,
                )

            if result.returncode != 0:
                return False, f"mysqldump failed: {result.stderr}"

            return True, "MySQL backup completed successfully"

        except subprocess.TimeoutExpired:
            return False, "mysqldump timed out after 1 hour"
        except Exception as e:
            return False, f"mysqldump error: {str(e)}"

    def restore_backup(
        self,
        input_path: Path,
        extra_options: List[str] = None,
    ) -> Tuple[bool, str]:
        """Restore MySQL backup using mysql."""
        cmd = ["mysql"]

        # Connection options
        if self.host:
            cmd.extend(["--host", self.host])
        if self.port:
            cmd.extend(["--port", str(self.port)])
        if self.user:
            cmd.extend(["--user", self.user])
        if self.password:
            cmd.extend([f"--password={self.password}"])

        # Extra options
        if extra_options:
            cmd.extend(extra_options)

        # Database
        cmd.append(self.name)

        try:
            with open(input_path, "r") as f:
                result = subprocess.run(
                    cmd,
                    stdin=f,
                    capture_output=True,
                    text=True,
                    timeout=3600,
                )

            if result.returncode != 0:
                return False, f"mysql restore failed: {result.stderr}"

            return True, "MySQL restore completed successfully"

        except subprocess.TimeoutExpired:
            return False, "mysql restore timed out after 1 hour"
        except Exception as e:
            return False, f"mysql restore error: {str(e)}"

    def get_tables_info(self) -> Dict[str, int]:
        """Get MySQL tables and row counts."""
        from django.db import connection

        tables = {}
        with connection.cursor() as cursor:
            cursor.execute("SHOW TABLES")
            for row in cursor.fetchall():
                table_name = row[0]
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM `{table_name}`")
                    count = cursor.fetchone()[0]
                    tables[table_name] = count
                except Exception:
                    tables[table_name] = 0
        return tables


class SQLiteDriver(BackupDriver):
    """SQLite backup driver using file copy."""

    def create_backup(
        self,
        output_path: Path,
        exclude_tables: List[str] = None,
        include_tables: List[str] = None,
        extra_options: List[str] = None,
    ) -> Tuple[bool, str]:
        """Create SQLite backup using file copy."""
        try:
            db_path = Path(self.name)
            if not db_path.exists():
                return False, f"SQLite database not found: {self.name}"

            # Use VACUUM INTO for consistent backup (SQLite 3.27+)
            from django.db import connection

            with connection.cursor() as cursor:
                cursor.execute(f"VACUUM INTO '{output_path}'")

            return True, "SQLite backup completed successfully"

        except Exception as e:
            # Fallback to simple copy
            try:
                shutil.copy2(self.name, output_path)
                return True, "SQLite backup completed (file copy)"
            except Exception as copy_error:
                return False, f"SQLite backup error: {str(e)}, copy error: {str(copy_error)}"

    def restore_backup(
        self,
        input_path: Path,
        extra_options: List[str] = None,
    ) -> Tuple[bool, str]:
        """Restore SQLite backup by replacing database file."""
        try:
            db_path = Path(self.name)

            # Backup current database
            if db_path.exists():
                backup_path = db_path.with_suffix(".db.old")
                shutil.move(str(db_path), str(backup_path))

            # Copy backup to database location
            shutil.copy2(str(input_path), str(db_path))

            return True, "SQLite restore completed successfully"

        except Exception as e:
            return False, f"SQLite restore error: {str(e)}"

    def get_tables_info(self) -> Dict[str, int]:
        """Get SQLite tables and row counts."""
        from django.db import connection

        tables = {}
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
            )
            for row in cursor.fetchall():
                table_name = row[0]
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM '{table_name}'")
                    count = cursor.fetchone()[0]
                    tables[table_name] = count
                except Exception:
                    tables[table_name] = 0
        return tables


class BackupService:
    """
    Main backup service.

    Provides high-level backup and restore operations with:
    - Auto-detection of database type
    - Compression support
    - Storage backends (local, S3)
    - Backup record management
    """

    # Database engine to driver mapping
    DRIVERS: Dict[str, Type[BackupDriver]] = {
        "django.db.backends.postgresql": PostgreSQLDriver,
        "django.db.backends.postgresql_psycopg2": PostgreSQLDriver,
        "django.contrib.gis.db.backends.postgis": PostgreSQLDriver,
        "django.db.backends.mysql": MySQLDriver,
        "django.db.backends.sqlite3": SQLiteDriver,
    }

    def __init__(self):
        self.config = self._get_backup_config()

    def _get_backup_config(self):
        """Get backup configuration from DjangoConfig."""
        try:
            from django_cfg.core.state.registry import get_current_config

            config = get_current_config()
            if config:
                return getattr(config, "backup", None)
        except Exception:
            pass
        return None

    def get_driver(self, database_alias: str = "default") -> BackupDriver:
        """
        Get appropriate backup driver for database.

        Args:
            database_alias: Django database alias

        Returns:
            BackupDriver instance

        Raises:
            DatabaseBackupError: If database or driver not found
        """
        if database_alias not in settings.DATABASES:
            raise DatabaseBackupError(f"Database '{database_alias}' not found in settings")

        db_config = settings.DATABASES[database_alias]
        engine = db_config.get("ENGINE", "")

        driver_class = self.DRIVERS.get(engine)
        if not driver_class:
            raise DatabaseBackupError(
                f"Unsupported database engine: {engine}. "
                f"Supported: {', '.join(self.DRIVERS.keys())}"
            )

        return driver_class(db_config)

    def detect_database_engine(self, database_alias: str = "default") -> str:
        """
        Detect database engine type.

        Returns:
            Engine type: 'postgresql', 'mysql', 'sqlite', or 'unknown'
        """
        if database_alias not in settings.DATABASES:
            return "unknown"

        engine = settings.DATABASES[database_alias].get("ENGINE", "")

        if "postgresql" in engine or "postgis" in engine:
            return "postgresql"
        elif "mysql" in engine:
            return "mysql"
        elif "sqlite" in engine:
            return "sqlite"
        else:
            return "unknown"

    def create_backup(
        self,
        database_alias: str = "default",
        is_scheduled: bool = False,
        is_manual: bool = True,
    ) -> "BackupRecord":
        """
        Create database backup.

        Args:
            database_alias: Django database alias
            is_scheduled: Whether backup is scheduled
            is_manual: Whether backup is manual

        Returns:
            BackupRecord instance
        """
        from .models import BackupRecord

        # Get configuration
        backup_config = self.config
        compression = backup_config.compression if backup_config else "gzip"
        storage_config = backup_config.storage if backup_config else None

        # Get database info
        db_config = settings.DATABASES.get(database_alias, {})
        db_name = db_config.get("NAME", database_alias)
        engine_type = self.detect_database_engine(database_alias)

        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        env = getattr(settings, "ENVIRONMENT", "unknown")

        if backup_config and backup_config.filename_template:
            filename = backup_config.filename_template.format(
                database=database_alias,
                timestamp=timestamp,
                env=env,
            )
        else:
            filename = f"{database_alias}_{timestamp}_{env}"

        # Add extension
        ext = ".sql" if engine_type != "postgresql" else ".dump"
        if compression == "gzip":
            ext += ".gz"
        elif compression == "bz2":
            ext += ".bz2"
        elif compression == "xz":
            ext += ".xz"
        filename += ext

        # Determine storage path
        if storage_config and storage_config.backend == "local":
            base_path = Path(storage_config.local_path)
            if not base_path.is_absolute():
                base_path = Path(settings.BASE_DIR) / base_path
            base_path.mkdir(parents=True, exist_ok=True)
            file_path = base_path / filename
        else:
            base_path = Path(settings.BASE_DIR) / "backups"
            base_path.mkdir(parents=True, exist_ok=True)
            file_path = base_path / filename

        # Create backup record
        record = BackupRecord.objects.create(
            database_alias=database_alias,
            database_name=db_name,
            database_engine=engine_type,
            filename=filename,
            file_path=str(file_path),
            compression=compression,
            storage_backend=storage_config.backend if storage_config else "local",
            is_scheduled=is_scheduled,
            is_manual=is_manual,
        )

        # Start backup
        record.mark_running()

        try:
            driver = self.get_driver(database_alias)

            # Get database config for exclude/include tables
            db_backup_config = None
            if backup_config:
                db_backup_config = backup_config.get_database_config(database_alias)

            exclude_tables = db_backup_config.exclude_tables if db_backup_config else []
            include_tables = db_backup_config.include_tables if db_backup_config else []
            extra_options = db_backup_config.extra_options if db_backup_config else []

            # Create temporary file for backup
            with tempfile.NamedTemporaryFile(delete=False, suffix=".tmp") as tmp_file:
                tmp_path = Path(tmp_file.name)

            try:
                # Create backup
                success, message = driver.create_backup(
                    output_path=tmp_path,
                    exclude_tables=exclude_tables,
                    include_tables=include_tables,
                    extra_options=extra_options,
                )

                if not success:
                    record.mark_failed(message)
                    return record

                # Compress if needed
                if compression == "gzip":
                    with open(tmp_path, "rb") as f_in:
                        with gzip.open(file_path, "wb") as f_out:
                            shutil.copyfileobj(f_in, f_out)
                elif compression in ("bz2", "xz"):
                    import lzma
                    import bz2

                    open_func = bz2.open if compression == "bz2" else lzma.open
                    with open(tmp_path, "rb") as f_in:
                        with open_func(file_path, "wb") as f_out:
                            shutil.copyfileobj(f_in, f_out)
                else:
                    shutil.move(str(tmp_path), str(file_path))

                # Calculate file size and checksum
                file_size = file_path.stat().st_size
                checksum = self._calculate_checksum(file_path)

                # Get tables info
                try:
                    tables_info = driver.get_tables_info()
                    record.tables_count = len(tables_info)
                    record.rows_count = sum(tables_info.values())
                except Exception:
                    pass

                # Upload to S3 if configured
                if storage_config and storage_config.backend == "s3":
                    s3_key = self._upload_to_s3(file_path, filename, storage_config)
                    record.file_path = s3_key
                    record.storage_bucket = storage_config.s3_bucket
                    # Remove local file after upload
                    file_path.unlink()

                record.mark_completed(file_size=file_size, checksum=checksum)

            finally:
                # Cleanup temp file
                if tmp_path.exists():
                    tmp_path.unlink()

        except Exception as e:
            logger.exception(f"Backup failed for {database_alias}")
            record.mark_failed(str(e))

        # Send notification
        self._send_notification(record)

        return record

    def restore_backup(
        self,
        backup_id: str,
        target_database_alias: str = None,
        created_by: str = "",
    ) -> "RestoreRecord":
        """
        Restore database from backup.

        Args:
            backup_id: BackupRecord UUID
            target_database_alias: Target database (defaults to original)
            created_by: User or system initiating restore

        Returns:
            RestoreRecord instance
        """
        from .models import BackupRecord, RestoreRecord

        # Get backup record
        backup = BackupRecord.objects.get(id=backup_id)
        target_alias = target_database_alias or backup.database_alias

        # Create restore record
        record = RestoreRecord.objects.create(
            backup=backup,
            target_database_alias=target_alias,
            created_by=created_by,
        )

        record.mark_running()

        try:
            # Download from S3 if needed
            if backup.storage_backend == "s3":
                local_path = self._download_from_s3(backup)
            else:
                local_path = Path(backup.file_path)

            if not local_path.exists():
                raise DatabaseBackupError(f"Backup file not found: {local_path}")

            # Decompress if needed
            decompressed_path = self._decompress_backup(local_path, backup.compression)

            try:
                # Get driver and restore
                driver = self.get_driver(target_alias)
                success, message = driver.restore_backup(decompressed_path)

                if not success:
                    record.mark_failed(message)
                else:
                    record.mark_completed()

            finally:
                # Cleanup decompressed file if different from original
                if decompressed_path != local_path and decompressed_path.exists():
                    decompressed_path.unlink()

                # Cleanup downloaded S3 file
                if backup.storage_backend == "s3" and local_path.exists():
                    local_path.unlink()

        except Exception as e:
            logger.exception(f"Restore failed for backup {backup_id}")
            record.mark_failed(str(e))

        return record

    def cleanup_old_backups(self):
        """
        Clean up old backups according to retention policy.
        """
        if not self.config or not self.config.retention.enabled:
            return

        from .models import BackupRecord
        from datetime import timedelta
        from django.utils import timezone

        retention = self.config.retention

        # Get cutoff dates
        daily_cutoff = timezone.now() - timedelta(days=retention.keep_daily)
        weekly_cutoff = timezone.now() - timedelta(weeks=retention.keep_weekly)
        monthly_cutoff = timezone.now() - timedelta(days=retention.keep_monthly * 30)

        # Find old backups to delete
        old_backups = BackupRecord.objects.filter(
            status=BackupRecord.Status.COMPLETED,
            created_at__lt=daily_cutoff,
        ).exclude(
            status=BackupRecord.Status.DELETED,
        )

        for backup in old_backups:
            try:
                # Delete file
                if backup.storage_backend == "s3":
                    self._delete_from_s3(backup)
                else:
                    path = Path(backup.file_path)
                    if path.exists():
                        path.unlink()

                backup.mark_deleted()
                logger.info(f"Deleted old backup: {backup.filename}")

            except Exception as e:
                logger.error(f"Failed to delete backup {backup.filename}: {e}")

    def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate SHA256 checksum of file."""
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256.update(chunk)
        return sha256.hexdigest()

    def _decompress_backup(self, file_path: Path, compression: str) -> Path:
        """Decompress backup file if needed."""
        if compression == "none":
            return file_path

        # Create temp file for decompressed content
        decompressed_path = file_path.with_suffix("")

        if compression == "gzip":
            with gzip.open(file_path, "rb") as f_in:
                with open(decompressed_path, "wb") as f_out:
                    shutil.copyfileobj(f_in, f_out)
        elif compression == "bz2":
            import bz2

            with bz2.open(file_path, "rb") as f_in:
                with open(decompressed_path, "wb") as f_out:
                    shutil.copyfileobj(f_in, f_out)
        elif compression == "xz":
            import lzma

            with lzma.open(file_path, "rb") as f_in:
                with open(decompressed_path, "wb") as f_out:
                    shutil.copyfileobj(f_in, f_out)

        return decompressed_path

    def _upload_to_s3(self, file_path: Path, filename: str, storage_config) -> str:
        """Upload backup to S3-compatible storage."""
        try:
            import boto3
            from botocore.config import Config

            config = Config(
                region_name=storage_config.s3_region,
                signature_version="s3v4",
            )

            client = boto3.client(
                "s3",
                endpoint_url=storage_config.s3_endpoint_url,
                aws_access_key_id=storage_config.s3_access_key,
                aws_secret_access_key=storage_config.s3_secret_key,
                config=config,
            )

            s3_key = f"{storage_config.s3_prefix}{filename}"

            client.upload_file(
                str(file_path),
                storage_config.s3_bucket,
                s3_key,
            )

            return s3_key

        except ImportError:
            raise DatabaseBackupError("boto3 is required for S3 storage. Install with: pip install boto3")

    def _download_from_s3(self, backup: "BackupRecord") -> Path:
        """Download backup from S3-compatible storage."""
        try:
            import boto3
            from botocore.config import Config

            storage_config = self.config.storage

            config = Config(
                region_name=storage_config.s3_region,
                signature_version="s3v4",
            )

            client = boto3.client(
                "s3",
                endpoint_url=storage_config.s3_endpoint_url,
                aws_access_key_id=storage_config.s3_access_key,
                aws_secret_access_key=storage_config.s3_secret_key,
                config=config,
            )

            local_path = Path(tempfile.gettempdir()) / backup.filename

            client.download_file(
                backup.storage_bucket,
                backup.file_path,
                str(local_path),
            )

            return local_path

        except ImportError:
            raise DatabaseBackupError("boto3 is required for S3 storage")

    def _delete_from_s3(self, backup: "BackupRecord"):
        """Delete backup from S3-compatible storage."""
        try:
            import boto3
            from botocore.config import Config

            storage_config = self.config.storage

            config = Config(
                region_name=storage_config.s3_region,
                signature_version="s3v4",
            )

            client = boto3.client(
                "s3",
                endpoint_url=storage_config.s3_endpoint_url,
                aws_access_key_id=storage_config.s3_access_key,
                aws_secret_access_key=storage_config.s3_secret_key,
                config=config,
            )

            client.delete_object(
                Bucket=backup.storage_bucket,
                Key=backup.file_path,
            )

        except ImportError:
            raise DatabaseBackupError("boto3 is required for S3 storage")

    def _send_notification(self, record: "BackupRecord"):
        """
        Send notification about backup result via Telegram and Email.

        Uses send_admin_notification to send to both channels.
        Email recipients come from config.admin_emails or Django ADMINS.
        """
        if not self.config:
            return

        try:
            from django_cfg.modules.django_email import send_admin_notification

            if record.status == "completed" and self.config.notify_on_success:
                # Success notification
                subject = f"[Backup] {record.database_alias} completed"
                message = (
                    f"Database: {record.database_alias}\n"
                    f"File: {record.filename}\n"
                    f"Size: {record.file_size_human}\n"
                    f"Duration: {record.duration_human}\n"
                    f"Engine: {record.database_engine}\n"
                    f"Tables: {record.tables_count or 'N/A'}\n"
                    f"Rows: {record.rows_count or 'N/A'}"
                )

                html_message = f"""
                <h2>Database Backup Completed</h2>
                <table style="border-collapse: collapse;">
                    <tr><td style="padding: 5px;"><strong>Database:</strong></td><td style="padding: 5px;">{record.database_alias}</td></tr>
                    <tr><td style="padding: 5px;"><strong>File:</strong></td><td style="padding: 5px;">{record.filename}</td></tr>
                    <tr><td style="padding: 5px;"><strong>Size:</strong></td><td style="padding: 5px;">{record.file_size_human}</td></tr>
                    <tr><td style="padding: 5px;"><strong>Duration:</strong></td><td style="padding: 5px;">{record.duration_human}</td></tr>
                    <tr><td style="padding: 5px;"><strong>Engine:</strong></td><td style="padding: 5px;">{record.database_engine}</td></tr>
                    <tr><td style="padding: 5px;"><strong>Tables:</strong></td><td style="padding: 5px;">{record.tables_count or 'N/A'}</td></tr>
                    <tr><td style="padding: 5px;"><strong>Rows:</strong></td><td style="padding: 5px;">{record.rows_count or 'N/A'}</td></tr>
                </table>
                """

                send_admin_notification(
                    subject=subject,
                    message=message,
                    html_message=html_message,
                    send_telegram=True,
                    send_email=True,
                    fail_silently=True,
                )

            elif record.status == "failed" and self.config.notify_on_failure:
                # Failure notification
                subject = f"[ALERT] Backup FAILED: {record.database_alias}"
                message = (
                    f"Database: {record.database_alias}\n"
                    f"File: {record.filename}\n"
                    f"Error: {record.error_message}\n"
                    f"Engine: {record.database_engine}\n"
                    f"Time: {record.started_at}"
                )

                html_message = f"""
                <h2 style="color: #dc3545;">Database Backup Failed</h2>
                <table style="border-collapse: collapse;">
                    <tr><td style="padding: 5px;"><strong>Database:</strong></td><td style="padding: 5px;">{record.database_alias}</td></tr>
                    <tr><td style="padding: 5px;"><strong>File:</strong></td><td style="padding: 5px;">{record.filename}</td></tr>
                    <tr><td style="padding: 5px;"><strong>Engine:</strong></td><td style="padding: 5px;">{record.database_engine}</td></tr>
                    <tr><td style="padding: 5px;"><strong>Time:</strong></td><td style="padding: 5px;">{record.started_at}</td></tr>
                </table>
                <div style="margin-top: 15px; padding: 10px; background: #f8d7da; border-radius: 5px;">
                    <strong>Error:</strong><br>
                    <pre style="white-space: pre-wrap;">{record.error_message}</pre>
                </div>
                """

                send_admin_notification(
                    subject=subject,
                    message=message,
                    html_message=html_message,
                    send_telegram=True,
                    send_email=True,
                    fail_silently=True,
                )

        except Exception as e:
            logger.warning(f"Failed to send backup notification: {e}")
