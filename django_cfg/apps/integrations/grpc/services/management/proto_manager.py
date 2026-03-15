"""
Proto Files Manager Service.

Handles proto file operations: scanning, reading, generating, archiving.
"""

import io
import zipfile
from pathlib import Path
from typing import Dict, List, Optional

from django.conf import settings
from django_cfg.utils import get_logger

from .config_helper import get_grpc_config

logger = get_logger("grpc.proto_files_manager")


class ProtoFilesManager:
    """
    Service for managing proto files.

    Handles:
    - Scanning proto directory
    - Reading proto files
    - Generating proto files from Django models
    - Creating zip archives
    """

    def __init__(self):
        """Initialize proto files manager."""
        self.grpc_config = get_grpc_config()

    def get_proto_dir(self) -> Path:
        """
        Get proto files directory path.

        Returns:
            Path to proto files directory
        """
        if self.grpc_config and self.grpc_config.proto and self.grpc_config.proto.output_dir:
            proto_dir = Path(settings.BASE_DIR) / self.grpc_config.proto.output_dir
        else:
            proto_dir = Path(settings.MEDIA_ROOT) / "protos"

        return proto_dir

    def scan_proto_files(self, request=None) -> List[Dict]:
        """
        Scan proto directory and return list of proto files with metadata.

        Args:
            request: Optional Django request object for building download URLs

        Returns:
            List of dicts with proto file metadata:
            {
                "app_label": str,
                "filename": str,
                "size_bytes": int,
                "package": str,
                "messages_count": int,
                "services_count": int,
                "created_at": float,
                "modified_at": float,
                "download_url": str (if request provided),
            }
        """
        proto_dir = self.get_proto_dir()

        if not proto_dir.exists():
            logger.warning(f"Proto directory does not exist: {proto_dir}")
            return []

        proto_files = []
        for proto_file in proto_dir.glob("*.proto"):
            try:
                metadata = self._parse_proto_file(proto_file)
                if metadata:
                    # Add download URL if request provided
                    if request:
                        from django.urls import reverse
                        from django_cfg.core.state import get_current_config

                        app_label = metadata['app_label']
                        config = get_current_config()

                        # Use api_url from config (respects HTTPS behind reverse proxy)
                        # Falls back to request.build_absolute_uri if config not available
                        if config and hasattr(config, 'api_url'):
                            path = reverse('django_cfg_grpc:proto-files-detail', kwargs={'pk': app_label})
                            download_url = f"{config.api_url}{path}"
                        else:
                            download_url = request.build_absolute_uri(
                                reverse('django_cfg_grpc:proto-files-detail', kwargs={'pk': app_label})
                            )

                        metadata['download_url'] = download_url

                    proto_files.append(metadata)
            except Exception as e:
                logger.error(f"Error reading proto file {proto_file}: {e}")
                continue

        return proto_files

    def _parse_proto_file(self, proto_file: Path) -> Optional[Dict]:
        """
        Parse proto file and extract metadata.

        Args:
            proto_file: Path to proto file

        Returns:
            Dict with proto file metadata or None if failed
        """
        try:
            stat = proto_file.stat()
            content = proto_file.read_text()

            # Parse proto file for metadata
            package = ""
            messages_count = 0
            services_count = 0

            for line in content.split("\n"):
                line = line.strip()
                if line.startswith("package "):
                    package = line.replace("package ", "").replace(";", "").strip()
                elif line.startswith("message "):
                    messages_count += 1
                elif line.startswith("service "):
                    services_count += 1

            # Extract app_label from filename (crypto.proto -> crypto)
            app_label = proto_file.stem

            return {
                "app_label": app_label,
                "filename": proto_file.name,
                "size_bytes": stat.st_size,
                "package": package,
                "messages_count": messages_count,
                "services_count": services_count,
                "created_at": stat.st_ctime,
                "modified_at": stat.st_mtime,
            }

        except Exception as e:
            logger.error(f"Error parsing proto file {proto_file}: {e}")
            return None

    def get_proto_file(self, app_label: str) -> Optional[Path]:
        """
        Get path to proto file for specific app.

        Args:
            app_label: App label (e.g., 'crypto')

        Returns:
            Path to proto file or None if not found
        """
        proto_dir = self.get_proto_dir()
        proto_file = proto_dir / f"{app_label}.proto"

        if proto_file.exists():
            return proto_file

        logger.warning(f"Proto file not found for app '{app_label}'")
        return None

    def create_zip_archive(self) -> Optional[bytes]:
        """
        Create zip archive with all proto files.

        Returns:
            Zip archive bytes or None if failed
        """
        proto_dir = self.get_proto_dir()

        if not proto_dir.exists():
            logger.error(f"Proto directory does not exist: {proto_dir}")
            return None

        try:
            # Create zip in memory
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                proto_files = list(proto_dir.glob("*.proto"))

                if not proto_files:
                    logger.warning("No proto files found to archive")
                    return None

                for proto_file in proto_files:
                    zip_file.write(proto_file, arcname=proto_file.name)
                    logger.debug(f"Added to archive: {proto_file.name}")

            zip_buffer.seek(0)
            return zip_buffer.read()

        except Exception as e:
            logger.error(f"Error creating zip archive: {e}", exc_info=True)
            return None

    def generate_protos(self, apps: Optional[List[str]] = None, force: bool = False) -> Dict:
        """
        Generate proto files for specified apps.

        Args:
            apps: List of app labels (uses enabled_apps from config if None)
            force: Force regeneration even if proto file exists

        Returns:
            Dict with generation results:
            {
                "status": "success" | "failed",
                "generated": List[str],  # Successfully generated app labels
                "generated_count": int,
                "errors": List[Dict],  # Errors for failed apps
            }
        """
        from ..utils.proto_gen import generate_proto_for_app

        # Determine which apps to generate for
        if not apps:
            if self.grpc_config and self.grpc_config.enabled_apps:
                apps = self.grpc_config.enabled_apps
            else:
                logger.error("No apps specified and no enabled_apps in config")
                return {
                    "status": "failed",
                    "generated": [],
                    "generated_count": 0,
                    "errors": [{"app": "N/A", "error": "No apps specified"}],
                }

        generated = []
        errors = []

        for app_label in apps:
            try:
                logger.info(f"Generating proto for app: {app_label}")
                count = generate_proto_for_app(app_label)

                if count > 0:
                    generated.append(app_label)
                    logger.info(f"Successfully generated proto for {app_label}")
                else:
                    error_msg = "No models found"
                    logger.warning(f"No models found in app {app_label}")
                    errors.append({"app": app_label, "error": error_msg})

            except Exception as e:
                error_msg = str(e)
                logger.error(f"Proto generation error for {app_label}: {error_msg}", exc_info=True)
                errors.append({"app": app_label, "error": error_msg})

        return {
            "status": "success" if generated else "failed",
            "generated": generated,
            "generated_count": len(generated),
            "errors": errors,
        }


__all__ = ["ProtoFilesManager"]
