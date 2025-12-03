"""
Frontend Asset Downloader

Utility for downloading frontend assets (admin.zip) from GitHub
when they are not bundled in the PyPI package.

This allows the PyPI package to be lightweight (~34MB smaller)
while still providing the full admin panel functionality.

Version tracking:
- After download, saves package version to .version file
- On startup, compares local .version with django_cfg.__version__
- If different → re-downloads (handles package upgrades automatically)

Features:
- Progress bar with Rich (beautiful CLI output)
- Retry logic with Tenacity (handles temporary network issues)
- Version-based auto-updates
"""

import logging
import tempfile
import shutil
import sys
from pathlib import Path
from typing import Optional

import requests
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
)

logger = logging.getLogger(__name__)


def _get_package_version() -> str:
    """Get current django-cfg package version."""
    import django_cfg
    return getattr(django_cfg, '__version__', '0.0.0')


# Download timeout in seconds
DOWNLOAD_TIMEOUT = 120

# User agent for GitHub requests
USER_AGENT = "django-cfg/1.0"

# Retry configuration
MAX_RETRY_ATTEMPTS = 3
RETRY_MIN_WAIT = 2  # seconds
RETRY_MAX_WAIT = 10  # seconds


def _is_interactive() -> bool:
    """Check if running in interactive terminal (not CI/CD or redirected output)."""
    return sys.stdout.isatty()


def _download_with_progress(
    response: requests.Response,
    temp_file,
    app_name: str,
    total_size: int,
) -> None:
    """Download with Rich progress bar if in interactive mode."""
    if _is_interactive() and total_size > 0:
        try:
            from rich.progress import (
                Progress,
                DownloadColumn,
                TransferSpeedColumn,
                BarColumn,
                TextColumn,
                TimeRemainingColumn,
            )

            with Progress(
                TextColumn("[bold blue]{task.description}"),
                BarColumn(),
                DownloadColumn(),
                TransferSpeedColumn(),
                TimeRemainingColumn(),
            ) as progress:
                task = progress.add_task(
                    f"[cyan]Downloading {app_name}.zip...",
                    total=total_size
                )
                for chunk in response.iter_content(chunk_size=8192):
                    temp_file.write(chunk)
                    progress.update(task, advance=len(chunk))
        except ImportError:
            # Rich not available, fallback to simple download
            _download_simple(response, temp_file, app_name, total_size)
    else:
        # Non-interactive mode (CI/CD, logs)
        _download_simple(response, temp_file, app_name, total_size)


def _download_simple(
    response: requests.Response,
    temp_file,
    app_name: str,
    total_size: int,
) -> None:
    """Simple download without progress bar (for CI/CD)."""
    downloaded = 0
    last_percent = 0

    for chunk in response.iter_content(chunk_size=8192):
        temp_file.write(chunk)
        downloaded += len(chunk)

        # Log progress every 10%
        if total_size > 0:
            percent = int(downloaded * 100 / total_size)
            if percent >= last_percent + 10:
                last_percent = percent
                logger.info(f"[{app_name}] Downloaded {percent}%")


@retry(
    stop=stop_after_attempt(MAX_RETRY_ATTEMPTS),
    wait=wait_exponential(multiplier=1, min=RETRY_MIN_WAIT, max=RETRY_MAX_WAIT),
    retry=retry_if_exception_type((
        requests.exceptions.ConnectionError,
        requests.exceptions.Timeout,
        requests.exceptions.ChunkedEncodingError,
    )),
    before_sleep=before_sleep_log(logger, logging.WARNING),
    reraise=True,
)
def _download_file(
    download_url: str,
    target_path: Path,
    app_name: str,
) -> bool:
    """
    Download file with retry logic.

    Retries on:
    - ConnectionError (network issues)
    - Timeout (slow connection)
    - ChunkedEncodingError (connection dropped during download)

    Does NOT retry on:
    - HTTPError (404, 500, etc.) - these are permanent failures
    """
    temp_path = None

    try:
        response = requests.get(
            download_url,
            headers={"User-Agent": USER_AGENT},
            timeout=DOWNLOAD_TIMEOUT,
            stream=True,
        )
        response.raise_for_status()

        # Get content length for progress
        content_length = response.headers.get("Content-Length")
        total_size = int(content_length) if content_length else 0

        if total_size > 0:
            size_mb = total_size / (1024 * 1024)
            logger.info(f"[{app_name}] File size: {size_mb:.1f} MB")

        # Download to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as temp_file:
            temp_path = Path(temp_file.name)
            _download_with_progress(response, temp_file, app_name, total_size)

        # Move to final location
        shutil.move(str(temp_path), str(target_path))
        temp_path = None  # Clear so finally doesn't try to delete

        return True

    finally:
        # Clean up temp file if download failed
        if temp_path and temp_path.exists():
            try:
                temp_path.unlink()
            except Exception:
                pass


def download_frontend_asset(
    app_name: str,
    target_dir: Optional[Path] = None,
    force: bool = False,
    show_progress: bool = True,
) -> bool:
    """
    Download frontend asset from GitHub if not present locally.

    Args:
        app_name: Name of the frontend app (e.g., 'admin')
        target_dir: Target directory for the asset. If None, uses default location.
        force: Force re-download even if file exists
        show_progress: Show progress bar (default: True, auto-disabled in non-interactive mode)

    Returns:
        bool: True if download successful or file already exists, False on error

    Example:
        >>> from django_cfg.apps.system.frontend.utils import download_frontend_asset
        >>> download_frontend_asset('admin')
        True
    """
    from django_cfg.config import FRONTEND_ASSETS

    # Get asset configuration
    asset_config = FRONTEND_ASSETS.get(app_name)
    if not asset_config:
        logger.error(f"Unknown frontend asset: {app_name}")
        return False

    # Determine target path
    if target_dir is None:
        import django_cfg
        target_dir = Path(django_cfg.__file__).parent / asset_config["relative_path"]

    target_path = target_dir / asset_config["filename"]
    download_url = asset_config["download_url"]

    # Check if already exists
    if target_path.exists() and not force:
        logger.debug(f"[{app_name}] Asset already exists: {target_path}")
        return True

    # Create target directory if needed
    target_dir.mkdir(parents=True, exist_ok=True)

    logger.info(f"[{app_name}] Downloading frontend asset from GitHub...")
    logger.info(f"[{app_name}] URL: {download_url}")

    try:
        success = _download_file(download_url, target_path, app_name)

        if success:
            # Save version marker
            version_file = target_path.with_suffix('.version')
            version_file.write_text(_get_package_version())
            logger.info(f"[{app_name}] Successfully downloaded to: {target_path}")

        return success

    except requests.exceptions.HTTPError as e:
        logger.error(f"[{app_name}] HTTP error downloading asset: {e}")
        return False
    except requests.exceptions.RequestException as e:
        logger.error(f"[{app_name}] Error downloading asset after {MAX_RETRY_ATTEMPTS} attempts: {e}")
        return False
    except Exception as e:
        logger.error(f"[{app_name}] Unexpected error downloading asset: {e}")
        return False


def _needs_update(asset_path: Path) -> bool:
    """
    Check if asset needs to be downloaded/updated.

    Returns True if:
    - Asset file doesn't exist
    - Version file doesn't exist
    - Version doesn't match current package version
    """
    if not asset_path.exists():
        return True

    version_file = asset_path.with_suffix('.version')
    if not version_file.exists():
        return True

    local_version = version_file.read_text().strip()
    current_version = _get_package_version()

    if local_version != current_version:
        logger.info(f"Version mismatch: local={local_version}, package={current_version}")
        return True

    return False


def ensure_frontend_asset(app_name: str) -> bool:
    """
    Ensure frontend asset is available and up-to-date.

    Checks version and downloads if:
    - Asset doesn't exist
    - Version doesn't match current package version (handles upgrades)

    Args:
        app_name: Name of the frontend app (e.g., 'admin')

    Returns:
        bool: True if asset is available (existed or downloaded), False on error
    """
    from django_cfg.config import FRONTEND_ASSETS
    import django_cfg

    asset_config = FRONTEND_ASSETS.get(app_name)
    if not asset_config:
        logger.error(f"Unknown frontend asset: {app_name}")
        return False

    target_dir = Path(django_cfg.__file__).parent / asset_config["relative_path"]
    target_path = target_dir / asset_config["filename"]

    # Check if update needed (missing or version mismatch)
    if not _needs_update(target_path):
        logger.debug(f"[{app_name}] Asset up-to-date: {target_path}")
        return True

    # Download (will overwrite if exists)
    reason = "not found" if not target_path.exists() else "version outdated"
    logger.info(f"[{app_name}] Frontend asset {reason}, downloading...")
    return download_frontend_asset(app_name, force=True)


def get_asset_path(app_name: str) -> Optional[Path]:
    """
    Get the path to a frontend asset.

    Args:
        app_name: Name of the frontend app (e.g., 'admin')

    Returns:
        Path to the asset file, or None if not configured
    """
    from django_cfg.config import FRONTEND_ASSETS
    import django_cfg

    asset_config = FRONTEND_ASSETS.get(app_name)
    if not asset_config:
        return None

    return Path(django_cfg.__file__).parent / asset_config["relative_path"] / asset_config["filename"]
