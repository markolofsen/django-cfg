"""
Streamlit Auto-Start — Automatic subprocess management.

Starts Streamlit as a child process of Django, ensuring:
- Streamlit starts with Django
- Streamlit dies when Django dies
- No separate Docker service needed
- Automatic port management
"""

from __future__ import annotations

import atexit
import logging
import os
import signal
import socket
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..models import StreamlitAdminConfig

logger = logging.getLogger("django_cfg.streamlit_admin")


class StreamlitAutoStart:
    """
    Manages Streamlit as a Django child process.

    Features:
    - Auto-start in DEBUG mode
    - Automatic cleanup on Django exit
    - Free port detection
    - Health monitoring

    Usage:
        # Usually called from AppConfig.ready()
        autostart = StreamlitAutoStart.from_django_config()
        autostart.start()
    """

    _instance: Optional["StreamlitAutoStart"] = None
    _lock = threading.Lock()

    def __init__(
        self,
        config: "StreamlitAdminConfig",
        app_path: Path,
        base_dir: Path,
    ):
        self._config = config
        self._app_path = app_path
        self._base_dir = base_dir
        self._process: Optional[subprocess.Popen] = None
        self._actual_port: Optional[int] = None
        self._started = False

    @classmethod
    def get_instance(cls) -> Optional["StreamlitAutoStart"]:
        """Get singleton instance if exists."""
        return cls._instance

    @classmethod
    def from_django_config(cls) -> "StreamlitAutoStart":
        """
        Create auto-start manager from Django configuration.

        Returns:
            StreamlitAutoStart instance

        Raises:
            ValueError: If streamlit_admin not configured
        """
        with cls._lock:
            if cls._instance is not None:
                return cls._instance

            from django.conf import settings
            from django_cfg.core.config import get_current_config

            config = get_current_config()
            if not config or not config.streamlit_admin:
                raise ValueError("streamlit_admin not configured in DjangoConfig")

            streamlit_config = config.streamlit_admin
            base_dir = Path(settings.BASE_DIR)

            # Resolve app path - use scaffold from module if not found
            app_path = Path(streamlit_config.app_path)
            if not app_path.is_absolute():
                app_path = base_dir / app_path

            # Store project extensions path for later (even if we use module's app.py)
            extensions_path = app_path if app_path.exists() else None

            # Check if app.py exists in project path, otherwise use module's app.py
            # This allows projects to have only extensions.py without full app
            app_file_candidates = ["app.py", "main.py", "streamlit_app.py"]
            has_app_file = any((app_path / f).exists() for f in app_file_candidates)

            if not has_app_file:
                # Fallback to module directory (app.py is in streamlit_admin root)
                module_dir = Path(__file__).parent.parent
                app_path = module_dir

            cls._instance = cls(streamlit_config, app_path, base_dir)
            # Store extensions path separately
            cls._instance._extensions_path = extensions_path
            return cls._instance

    @property
    def port(self) -> int:
        """Get actual port (may differ from config if auto-assigned)."""
        return self._actual_port or self._config.port

    @property
    def url(self) -> str:
        """Get Streamlit server URL."""
        return f"http://localhost:{self.port}"

    @property
    def is_running(self) -> bool:
        """Check if Streamlit process is running."""
        if self._process is None:
            return False
        return self._process.poll() is None

    def start(self, *, force: bool = False) -> bool:
        """
        Start Streamlit subprocess.

        Args:
            force: Start even if already running

        Returns:
            True if started, False if skipped
        """
        if self._started and not force:
            logger.debug("Streamlit already started, skipping")
            return False

        if not self._app_path.exists():
            logger.warning(f"Streamlit app path not found: {self._app_path}")
            return False

        # Check if Streamlit is already running on preferred port
        # This prevents Django hot-reload from restarting Streamlit unnecessarily
        preferred_port = self._config.port
        if self._is_streamlit_running_on_port(preferred_port):
            logger.info(f"Streamlit already running on port {preferred_port}, reusing")
            self._actual_port = preferred_port
            self._started = True
            os.environ["STREAMLIT_RUNTIME_PORT"] = str(preferred_port)
            return True

        # Only kill existing Streamlit if we need to start fresh
        if force:
            self._kill_existing_streamlit()

        # Use preferred port (don't auto-find to keep it stable)
        self._actual_port = preferred_port

        # Build command
        cmd = self._build_command()

        # Environment
        env = os.environ.copy()
        env["STREAMLIT_SERVER_HEADLESS"] = "true"
        env["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"
        # Pass extensions path so Streamlit can load project extensions without Django
        extensions_path = getattr(self, "_extensions_path", None)
        if extensions_path:
            env["STREAMLIT_EXTENSIONS_PATH"] = str(extensions_path)

        try:
            # Start subprocess
            self._process = subprocess.Popen(
                cmd,
                cwd=str(self._app_path),
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                # Important: Create new process group
                start_new_session=False,
            )

            # Register cleanup handlers
            atexit.register(self.stop)
            signal.signal(signal.SIGTERM, self._signal_handler)
            signal.signal(signal.SIGINT, self._signal_handler)

            self._started = True

            # Save port to environment for other processes/reloads to find
            os.environ["STREAMLIT_RUNTIME_PORT"] = str(self._actual_port)

            logger.info(
                f"Streamlit started on port {self._actual_port} "
                f"(PID: {self._process.pid})"
            )

            # Wait a bit and check if process started successfully
            time.sleep(0.5)
            if not self.is_running:
                stderr = self._process.stderr.read().decode() if self._process.stderr else ""
                logger.error(f"Streamlit failed to start: {stderr}")
                return False

            return True

        except Exception as e:
            logger.error(f"Failed to start Streamlit: {e}")
            return False

    def stop(self) -> bool:
        """
        Stop Streamlit subprocess.

        Returns:
            True if stopped, False if not running
        """
        process = self._process
        if process is None:
            return False

        pid = process.pid  # Capture PID before process reference might change

        try:
            # Try graceful shutdown first
            process.terminate()

            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                # Force kill if not responding
                process.kill()
                process.wait(timeout=2)

            logger.info(f"Streamlit stopped (was PID: {pid})")
            self._process = None
            self._started = False
            return True

        except Exception as e:
            logger.error(f"Error stopping Streamlit: {e}")
            self._process = None
            self._started = False
            return False

    def restart(self) -> bool:
        """Restart Streamlit subprocess."""
        self.stop()
        time.sleep(0.5)
        return self.start(force=True)

    def _build_command(self) -> list[str]:
        """Build streamlit run command."""
        app_file = self._find_app_file()

        # Use host from config, default to 127.0.0.1 for local dev
        # In Docker, config.host might be "0.0.0.0" to accept external connections
        host = self._config.host
        # Normalize "localhost" to "127.0.0.1" to avoid DNS issues
        if host == "localhost":
            host = "127.0.0.1"

        # Use project's venv Python if available, otherwise sys.executable
        # This ensures Streamlit runs in the same environment as Django
        python_exe = self._get_python_executable()

        cmd = [
            python_exe,
            "-m",
            "streamlit",
            "run",
            str(app_file),
            "--server.port",
            str(self._actual_port),
            "--server.address",
            host,
            "--server.headless",
            "true",
            "--server.enableCORS",
            "false",
            "--server.enableXsrfProtection",
            "false",
            "--browser.gatherUsageStats",
            "false",
            # Theme settings from config
            "--theme.base",
            "dark",
            "--theme.primaryColor",
            "#0070F3",
            "--theme.backgroundColor",
            "#000000",
            "--theme.secondaryBackgroundColor",
            "#111111",
            "--theme.textColor",
            "#EDEDED",
        ]

        return cmd

    def _find_app_file(self) -> Path:
        """Find Streamlit app entry point."""
        candidates = ["app.py", "main.py", "streamlit_app.py"]

        for name in candidates:
            path = self._app_path / name
            if path.exists():
                return path

        raise FileNotFoundError(
            f"No Streamlit app found in {self._app_path}. "
            f"Expected one of: {candidates}"
        )

    def _get_python_executable(self) -> str:
        """
        Get Python executable path for Streamlit subprocess.

        Uses project's venv Python if available to ensure Streamlit
        runs in the same environment as Django (with django_cfg installed).
        """
        # Check for venv in base_dir (project root)
        venv_python = self._base_dir / ".venv" / "bin" / "python"
        if venv_python.exists():
            return str(venv_python)

        # Check for venv in common locations
        for venv_name in [".venv", "venv", "env"]:
            venv_python = self._base_dir / venv_name / "bin" / "python"
            if venv_python.exists():
                return str(venv_python)

        # Fallback to current Python
        return sys.executable

    def _get_bind_host(self) -> str:
        """Get host for socket binding, normalizing localhost to IP."""
        host = self._config.host
        # Normalize "localhost" to "127.0.0.1" to avoid DNS issues
        if host == "localhost":
            return "127.0.0.1"
        # For "0.0.0.0" we still bind to 127.0.0.1 for port checking
        if host == "0.0.0.0":
            return "127.0.0.1"
        return host

    def _find_free_port(self, preferred: int) -> int:
        """
        Find a free port, starting with preferred.

        Args:
            preferred: Preferred port number

        Returns:
            Available port number
        """
        bind_host = self._get_bind_host()

        # Try preferred port first
        if self._is_port_free(preferred, bind_host):
            return preferred

        # Try a few ports around preferred
        for offset in range(1, 10):
            port = preferred + offset
            if self._is_port_free(port, bind_host):
                logger.info(
                    f"Port {preferred} busy, using {port} instead"
                )
                return port

        # Let OS assign a free port
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((bind_host, 0))
            port = s.getsockname()[1]
            logger.info(f"Auto-assigned port {port} for Streamlit")
            return port

    def _is_port_free(self, port: int, host: str = "127.0.0.1") -> bool:
        """Check if port is available."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind((host, port))
                return True
            except OSError:
                return False

    def _is_streamlit_running_on_port(self, port: int) -> bool:
        """Check if Streamlit is already running on the given port."""
        import urllib.request
        import urllib.error

        try:
            # Try to connect to Streamlit health endpoint
            url = f"http://127.0.0.1:{port}/_stcore/health"
            req = urllib.request.Request(url, method="GET")
            with urllib.request.urlopen(req, timeout=2) as response:
                return response.status == 200
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError):
            return False

    def _signal_handler(self, signum: int, frame) -> None:
        """Handle termination signals."""
        logger.debug(f"Received signal {signum}, stopping Streamlit")
        self.stop()
        # Re-raise the signal for Django to handle
        signal.signal(signum, signal.SIG_DFL)
        os.kill(os.getpid(), signum)

    def _kill_existing_streamlit(self) -> None:
        """
        Kill any existing Streamlit processes.

        Streamlit doesn't auto-reload imported modules, so we need to kill
        existing processes to ensure fresh imports on Django restart.
        """
        import subprocess

        try:
            # Kill streamlit run processes
            subprocess.run(
                ["pkill", "-f", "streamlit run"],
                capture_output=True,
                timeout=5,
            )
            logger.debug("Killed existing Streamlit processes")
        except Exception as e:
            logger.debug(f"No existing Streamlit processes to kill: {e}")


def should_auto_start() -> bool:
    """
    Determine if Streamlit should auto-start.

    Returns True if:
    - streamlit_admin.auto_start is True
    - Not running under gunicorn/uwsgi (production WSGI servers)
    - Not running migrations or other management commands
    """
    # Check if running under production WSGI server (gunicorn/uwsgi)
    # These don't work well with subprocesses
    if _is_production_server():
        return False

    # Check if running management command (not runserver)
    if _is_management_command():
        return False

    # Check config
    try:
        from django_cfg.core.config import get_current_config
        config = get_current_config()
        if config and config.streamlit_admin:
            return config.streamlit_admin.auto_start
    except Exception:
        pass

    return False


def _is_production_server() -> bool:
    """
    Check if running under multi-worker WSGI server.

    Note: uvicorn is OK because we check for workers via RUN_MAIN env var.
    gunicorn/uwsgi spawn multiple processes that would each try to start Streamlit.
    """
    # Check for gunicorn (multi-worker by default)
    if "gunicorn" in sys.modules:
        return True

    # Check for uwsgi (multi-worker by default)
    if "uwsgi" in sys.modules:
        return True

    # Check environment hints
    server_software = os.environ.get("SERVER_SOFTWARE", "")
    if "gunicorn" in server_software.lower():
        return True
    if "uwsgi" in server_software.lower():
        return True

    return False


def _is_management_command() -> bool:
    """Check if running a management command (not runserver)."""
    if len(sys.argv) < 2:
        return False

    command = sys.argv[1] if len(sys.argv) > 1 else ""

    # Whitelist: runserver should allow auto-start
    if command in ("runserver", "runserver_plus"):
        return False

    # Blacklist: common management commands
    management_commands = {
        "migrate",
        "makemigrations",
        "collectstatic",
        "createsuperuser",
        "shell",
        "dbshell",
        "check",
        "test",
        "startapp",
        "startproject",
        "dumpdata",
        "loaddata",
        "flush",
        "inspectdb",
        "showmigrations",
        "sqlmigrate",
        "squashmigrations",
        # Our commands
        "run_streamlit",
        "create_streamlit_app",
        "generate_client",
    }

    return command in management_commands


def auto_start_streamlit() -> Optional[StreamlitAutoStart]:
    """
    Auto-start Streamlit if conditions are met.

    Called from AppConfig.ready().

    Returns:
        StreamlitAutoStart instance if started, None otherwise
    """
    if not should_auto_start():
        return None

    try:
        autostart = StreamlitAutoStart.from_django_config()
        if autostart.start():
            return autostart
    except Exception as e:
        logger.warning(f"Failed to auto-start Streamlit: {e}")

    return None
