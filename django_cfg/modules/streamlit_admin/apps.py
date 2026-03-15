"""
Django app configuration for Streamlit Admin.

Auto-starts Streamlit as a child process when:
- DEBUG mode is enabled
- auto_start=True in StreamlitAdminConfig
- Running via runserver (not migrations, etc.)
"""

import logging
from typing import Optional, TYPE_CHECKING

from django.apps import AppConfig

if TYPE_CHECKING:
    from .core.autostart import StreamlitAutoStart

logger = logging.getLogger("django_cfg.streamlit_admin")


class StreamlitAdminConfig(AppConfig):
    """
    Streamlit Admin Django app configuration.

    Features:
    - Auto-starts Streamlit subprocess in DEBUG mode
    - Streamlit dies when Django dies (no orphan processes)
    - No separate Docker service needed
    """

    name = "django_cfg.modules.streamlit_admin"
    label = "streamlit_admin"
    verbose_name = "Streamlit Admin"
    default_auto_field = "django.db.models.BigAutoField"

    _streamlit: Optional["StreamlitAutoStart"] = None

    def ready(self) -> None:
        """
        Called when Django starts.

        Auto-starts Streamlit if configured.
        """
        # Avoid running twice (Django calls ready() multiple times in some cases)
        if self._streamlit is not None:
            return

        # Import here to avoid circular imports
        from .core.autostart import auto_start_streamlit

        # Try to auto-start (will check conditions internally)
        self._streamlit = auto_start_streamlit()

        if self._streamlit:
            logger.info(
                f"Streamlit admin available at: {self._streamlit.url}"
            )

    @classmethod
    def get_streamlit_instance(cls) -> Optional["StreamlitAutoStart"]:
        """
        Get running Streamlit instance.

        Returns:
            StreamlitAutoStart if running, None otherwise
        """
        # Try class variable first, then singleton
        if cls._streamlit:
            return cls._streamlit
        # Fallback to singleton (survives Django reloader)
        from .core.autostart import StreamlitAutoStart
        return StreamlitAutoStart.get_instance()

    @classmethod
    def get_streamlit_url(cls) -> Optional[str]:
        """
        Get Streamlit server URL.

        Returns:
            URL string if running, None otherwise
        """
        instance = cls.get_streamlit_instance()
        if instance and instance.is_running:
            return instance.url
        return None

    @classmethod
    def get_streamlit_port(cls) -> Optional[int]:
        """
        Get Streamlit server port.

        Returns:
            Port number if running, None otherwise
        """
        instance = cls.get_streamlit_instance()
        if instance:
            return instance.port
        return None
