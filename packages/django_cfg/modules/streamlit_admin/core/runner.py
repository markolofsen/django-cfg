"""
Streamlit Runner — Process management for Streamlit server.

Handles starting, stopping, and monitoring Streamlit processes.
"""

from __future__ import annotations

import os
import signal
import subprocess
import sys
from pathlib import Path
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..models import StreamlitAdminConfig as StreamlitConfig


class StreamlitRunner:
    """
    Manages Streamlit server process.

    Usage:
        runner = StreamlitRunner.from_config()
        runner.start()
        # ... later ...
        runner.stop()
    """

    __slots__ = ("_config", "_app_path", "_process", "_pid_file")

    def __init__(
        self,
        config: "StreamlitConfig",
        app_path: Path,
    ):
        self._config = config
        self._app_path = app_path
        self._process: Optional[subprocess.Popen] = None
        self._pid_file = app_path / ".streamlit.pid"

    @classmethod
    def from_config(cls) -> "StreamlitRunner":
        """Create runner from Django configuration."""
        from django.conf import settings
        from django_cfg.core.config import get_current_config

        config = get_current_config()
        if not config.streamlit_admin:
            raise ValueError("streamlit_admin not configured in DjangoConfig")

        streamlit_config = config.streamlit_admin

        # Resolve app path
        app_path = Path(streamlit_config.app_path)
        if not app_path.is_absolute():
            app_path = Path(settings.BASE_DIR) / app_path

        if not app_path.exists():
            raise FileNotFoundError(f"Streamlit app not found: {app_path}")

        return cls(streamlit_config, app_path)

    def start(
        self,
        *,
        port: Optional[int] = None,
        reload: bool = True,
        background: bool = False,
    ) -> Optional[subprocess.Popen]:
        """
        Start Streamlit server.

        Args:
            port: Override port from config
            reload: Enable auto-reload on file changes
            background: Run in background (return process)

        Returns:
            Popen object if background=True, else None
        """
        if self.is_running():
            raise RuntimeError(
                f"Streamlit already running on port {self._config.port}"
            )

        # Build command
        cmd = self._build_command(port=port, reload=reload)

        # Environment
        env = os.environ.copy()
        env["STREAMLIT_SERVER_HEADLESS"] = "true"

        if background:
            # Start in background
            self._process = subprocess.Popen(
                cmd,
                cwd=str(self._app_path),
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            self._write_pid()
            return self._process
        else:
            # Run in foreground (blocks)
            try:
                subprocess.run(cmd, cwd=str(self._app_path), env=env)
            except KeyboardInterrupt:
                pass
            return None

    def stop(self) -> bool:
        """
        Stop Streamlit server.

        Returns:
            True if stopped, False if not running
        """
        pid = self._read_pid()

        if pid:
            try:
                os.kill(pid, signal.SIGTERM)
                self._pid_file.unlink(missing_ok=True)
                return True
            except ProcessLookupError:
                self._pid_file.unlink(missing_ok=True)
                return False

        if self._process:
            self._process.terminate()
            self._process.wait(timeout=5)
            self._process = None
            return True

        return False

    def is_running(self) -> bool:
        """Check if Streamlit server is running."""
        pid = self._read_pid()
        if pid:
            try:
                os.kill(pid, 0)  # Check if process exists
                return True
            except ProcessLookupError:
                self._pid_file.unlink(missing_ok=True)

        if self._process and self._process.poll() is None:
            return True

        return False

    def get_url(self) -> str:
        """Get Streamlit server URL."""
        return self._config.get_dev_url()

    def _build_command(
        self,
        *,
        port: Optional[int] = None,
        reload: bool = True,
    ) -> list[str]:
        """Build streamlit run command."""
        actual_port = port or self._config.port

        # Find app entry point
        app_file = self._find_app_file()

        cmd = [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            str(app_file),
            "--server.port",
            str(actual_port),
            "--server.address",
            self._config.host,
            "--server.headless",
            "true",
        ]

        if not reload:
            cmd.extend(["--server.runOnSave", "false"])

        return cmd

    def _find_app_file(self) -> Path:
        """Find Streamlit app entry point."""
        # Try common names
        candidates = ["app.py", "main.py", "streamlit_app.py"]

        for name in candidates:
            path = self._app_path / name
            if path.exists():
                return path

        raise FileNotFoundError(
            f"No Streamlit app found in {self._app_path}. "
            f"Expected one of: {candidates}"
        )

    def _write_pid(self) -> None:
        """Write process ID to file."""
        if self._process:
            self._pid_file.write_text(str(self._process.pid))

    def _read_pid(self) -> Optional[int]:
        """Read process ID from file."""
        if self._pid_file.exists():
            try:
                return int(self._pid_file.read_text().strip())
            except (ValueError, OSError):
                return None
        return None
