"""
Next.js Integration Utilities.

Handles copying clients to Next.js project and building static exports.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    pass


class NextJsUtils:
    """
    Utilities for Next.js admin integration.

    Handles:
    - Copying TypeScript clients to Next.js project
    - Building static exports
    - Creating ZIP archives for Django static serving
    """

    def __init__(
        self,
        log: Callable[[str], None] | None = None,
        log_success: Callable[[str], None] | None = None,
        log_warning: Callable[[str], None] | None = None,
        log_error: Callable[[str], None] | None = None,
    ):
        self.log = log or print
        self.log_success = log_success or self.log
        self.log_warning = log_warning or self.log
        self.log_error = log_error or self.log

    def copy_clients(
        self,
        ts_source: Path,
        api_output_path: Path,
        project_path: Path,
        *,
        copy_cfg_clients: bool = False,
    ) -> int:
        """
        Copy TypeScript clients to Next.js project.

        Args:
            ts_source: Source directory with TypeScript clients
            api_output_path: Target directory in Next.js project
            project_path: Next.js project root
            copy_cfg_clients: Whether to copy cfg_* clients

        Returns:
            Number of groups copied
        """
        if not ts_source.exists():
            return 0

        self.log(f"\n📦 Copying TypeScript clients to Next.js admin...")

        # Clean target directory
        if api_output_path.exists():
            self.log(f"  🧹 Cleaning: {api_output_path.relative_to(project_path)}")
            shutil.rmtree(api_output_path)

        api_output_path.mkdir(parents=True, exist_ok=True)

        copied_count = 0
        for group_dir in ts_source.iterdir():
            if not group_dir.is_dir():
                continue

            group_name = group_dir.name

            # Skip ext_* groups
            if group_name.startswith('ext_'):
                self.log(f"  ⏭️  Skipping '{group_name}' (extension package)")
                continue

            # Skip combined 'cfg' group
            if group_name == 'cfg':
                self.log(f"  ⏭️  Skipping '{group_name}' (combined group)")
                continue

            # Skip cfg_* unless explicitly requested
            if group_name.startswith('cfg_') and not copy_cfg_clients:
                self.log(f"  ⏭️  Skipping '{group_name}' (@djangocfg/api package)")
                continue

            target_dir = api_output_path / group_name
            shutil.copytree(group_dir, target_dir)
            copied_count += 1

            self.log(f"  ✅ {group_name} → {target_dir.relative_to(project_path)}")

        if copied_count > 0:
            self.log_success(f"\n✅ Copied {copied_count} group(s) to Next.js admin!")

        return copied_count

    def build_static_export(
        self,
        project_path: Path,
        static_output_path: Path,
        static_zip_path: Path,
        *,
        timeout: int = 300,
        confirm: bool = True,
    ) -> bool:
        """
        Build Next.js static export and create ZIP archive.

        Args:
            project_path: Next.js project root
            static_output_path: Path to build output (e.g., out/)
            static_zip_path: Path for output ZIP file
            timeout: Build timeout in seconds
            confirm: Whether to ask for confirmation

        Returns:
            True if build succeeded
        """
        # Check pnpm
        pnpm_path = shutil.which('pnpm')
        if not pnpm_path:
            self.log_warning("⚠️  pnpm not found. Skipping build.")
            return False

        # Optional confirmation
        if confirm:
            try:
                import questionary
                should_build = questionary.confirm(
                    f"🏗️  Build Next.js static export?",
                    default=True,
                    auto_enter=False,
                ).ask()
                if not should_build:
                    self.log_warning("⏭️  Skipping Next.js build")
                    return False
            except ImportError:
                pass  # No questionary, proceed without confirmation

        self.log(f"\n🏗️  Building Next.js admin static export...")

        import os
        env = os.environ.copy()
        env['NEXT_PUBLIC_STATIC_BUILD'] = 'true'

        try:
            result = subprocess.run(
                [pnpm_path, 'build'],
                cwd=str(project_path),
                capture_output=True,
                text=True,
                timeout=timeout,
                env=env,
            )

            if result.returncode != 0:
                self.log_error(f"❌ Build failed (exit code {result.returncode})")
                if result.stderr:
                    self.log_error(f"stderr: {result.stderr[:500]}")
                return False

            self.log_success("✅ Next.js build succeeded!")

            # Create ZIP archive
            if static_output_path.exists():
                self._create_zip_archive(static_output_path, static_zip_path)

            return True

        except subprocess.TimeoutExpired:
            self.log_error(f"❌ Build timed out ({timeout}s)")
            return False

    def _create_zip_archive(self, source_dir: Path, zip_path: Path) -> bool:
        """Create ZIP archive from build output."""
        try:
            zip_path.parent.mkdir(parents=True, exist_ok=True)

            if zip_path.exists():
                zip_path.unlink()

            zip_cmd = shutil.which('zip')
            if zip_cmd:
                subprocess.run(
                    [zip_cmd, '-r', '-q', str(zip_path), '.'],
                    cwd=str(source_dir),
                    check=True
                )
            else:
                import zipfile
                with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for file_path in source_dir.rglob('*'):
                        if file_path.is_file():
                            arcname = file_path.relative_to(source_dir)
                            zipf.write(file_path, arcname)

            size_mb = zip_path.stat().st_size / (1024 * 1024)
            self.log_success(f"✅ Created ZIP: {zip_path.name} ({size_mb:.1f}MB)")
            return True

        except Exception as e:
            self.log_error(f"❌ Failed to create ZIP: {e}")
            return False


__all__ = ["NextJsUtils"]
