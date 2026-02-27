"""
StreamlitAdminConfig — Configuration model for Streamlit admin integration.

Follows patterns from python_module_dev_guide:
- Pydantic v2 with ConfigDict
- Field validators
- Computed properties with defaults
"""

from typing import Optional, Annotated
from pydantic import BaseModel, Field, field_validator, ConfigDict


class StreamlitAdminConfig(BaseModel):
    """
    Streamlit admin integration configuration.

    Minimal configuration:
        streamlit_admin = StreamlitAdminConfig(
            app_path="admin_app"
        )

    Full configuration:
        streamlit_admin = StreamlitAdminConfig(
            app_path="admin_app",
            port=8501,
            theme="vercel-dark",
            auto_start=True,
            tab_title="Admin Panel",
        )
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        str_strip_whitespace=True,
    )

    # =================================================================
    # REQUIRED
    # =================================================================

    app_path: str = Field(
        ...,
        description=(
            "Path to Streamlit app directory (relative or absolute). "
            "Relative paths resolved from Django BASE_DIR. "
            "Example: 'admin_app' or '../streamlit_admin'"
        ),
    )

    # =================================================================
    # OPTIONAL (with smart defaults)
    # =================================================================

    port: Annotated[int, Field(ge=1024, le=65535)] = Field(
        default=8501,
        description="Port for Streamlit server",
    )

    host: str = Field(
        default="0.0.0.0",
        description="Host to bind Streamlit server",
    )

    static_url: Optional[str] = Field(
        default=None,
        description=(
            "URL prefix for reverse proxy. "
            "Default: '/cfg/streamlit/'"
        ),
    )

    dev_url: Optional[str] = Field(
        default=None,
        description=(
            "Streamlit development server URL. "
            "Default: 'http://localhost:{port}'"
        ),
    )

    iframe_route: Optional[str] = Field(
        default=None,
        description=(
            "Streamlit route to display in iframe. "
            "Default: '/'"
        ),
    )

    tab_title: Optional[str] = Field(
        default=None,
        description=(
            "Title for Streamlit admin tab. "
            "Default: 'Streamlit Admin'"
        ),
    )

    theme: str = Field(
        default="vercel-dark",
        description=(
            "Theme preset: 'vercel-dark', 'light', 'custom'. "
            "Default: 'vercel-dark'"
        ),
    )

    auto_start: bool = Field(
        default=True,
        description=(
            "Auto-start Streamlit server as Django child process in DEBUG mode. "
            "Streamlit will die when Django dies. No separate service needed. "
            "Default: True"
        ),
    )

    api_clients_path: Optional[str] = Field(
        default=None,
        description=(
            "Path for generated Python API clients (relative to app_path). "
            "Default: 'generated'"
        ),
    )

    jwt_secret: Optional[str] = Field(
        default=None,
        description=(
            "JWT secret for token validation. "
            "Default: Uses Django SECRET_KEY"
        ),
    )

    iframe_sandbox: Optional[str] = Field(
        default=None,
        description="HTML5 iframe sandbox attribute (optional)",
    )

    public_url: Optional[str] = Field(
        default=None,
        description=(
            "Public URL for Streamlit in production (bypasses Django proxy). "
            "Required for WebSocket support. Streamlit needs WebSocket for "
            "its _stcore/stream endpoint, which Django cannot proxy. "
            "Set this to a direct URL to Streamlit (e.g. via Traefik/nginx). "
            "Example: 'https://st.cmdop.com'"
        ),
    )

    # =================================================================
    # Computed properties with defaults
    # =================================================================

    def get_static_url(self) -> str:
        """Get static URL with default (with trailing slash)."""
        url = self.static_url or "/cfg/streamlit/"
        if not url.startswith("/"):
            url = f"/{url}"
        if not url.endswith("/"):
            url = f"{url}/"
        return url

    def get_dev_url(self) -> str:
        """Get dev URL with default."""
        return self.dev_url or f"http://localhost:{self.port}"

    def get_iframe_route(self) -> str:
        """Get iframe route with default."""
        return self.iframe_route or "/"

    def get_tab_title(self) -> str:
        """Get tab title with default."""
        return self.tab_title or "Streamlit Admin"

    def get_api_clients_path(self) -> str:
        """Get API clients path with default."""
        return self.api_clients_path or "generated"

    def get_iframe_sandbox(self) -> str:
        """Get iframe sandbox with default."""
        return self.iframe_sandbox or (
            "allow-same-origin allow-scripts allow-forms "
            "allow-popups allow-modals allow-storage-access-by-user-activation"
        )

    def get_jwt_secret(self, django_secret: str) -> str:
        """Get JWT secret, falling back to Django SECRET_KEY."""
        return self.jwt_secret or django_secret

    def get_full_iframe_url(self) -> str:
        """Get full iframe URL for embedding."""
        route = self.get_iframe_route()
        if not route.startswith("/"):
            route = f"/{route}"
        return f"{self.get_dev_url()}{route}"

    def get_runtime_url(self) -> str:
        """
        Get actual runtime URL for iframe.

        Priority:
        1. Development: direct localhost URL (auto-start subprocess)
        2. Production + public_url: direct access (supports WebSocket)
        3. Production without public_url: api_url + /cfg/streamlit/ (HTTP-only proxy)
        """
        from django_cfg.core.config import get_current_config

        config = get_current_config()

        # Development — always use localhost, ignore public_url
        if config and config.is_development:
            try:
                from django.apps import apps
                app_config = apps.get_app_config("streamlit_admin")
                url = app_config.get_streamlit_url()
                if url:
                    return url
            except Exception:
                pass
            return self.get_dev_url()

        # Production — use public_url if set (WebSocket support)
        if self.public_url:
            return self.public_url.rstrip("/")

        # Production fallback — Django proxy (HTTP only, no WebSocket)
        if config:
            api_url = config.api_url.rstrip("/")
            return f"{api_url}/cfg/streamlit"

        return self.get_dev_url()

    def get_runtime_port(self) -> int:
        """
        Get actual runtime port (may differ if auto-assigned).

        Falls back to configured port if Streamlit not running.
        """
        import os

        # First check environment variable (set by autostart, survives reloader)
        env_port = os.environ.get("STREAMLIT_RUNTIME_PORT")
        if env_port:
            try:
                return int(env_port)
            except ValueError:
                pass

        # Then try app config
        try:
            from django.apps import apps
            app_config = apps.get_app_config("streamlit_admin")
            port = app_config.get_streamlit_port()
            if port:
                return port
        except Exception:
            pass

        return self.port

    # =================================================================
    # Validators
    # =================================================================

    @field_validator("app_path")
    @classmethod
    def validate_app_path(cls, v: str) -> str:
        """Validate app path is not empty."""
        if not v or not v.strip():
            raise ValueError("app_path cannot be empty")
        return v.strip()

    @field_validator("theme")
    @classmethod
    def validate_theme(cls, v: str) -> str:
        """Validate theme is supported."""
        allowed = {"vercel-dark", "light", "custom"}
        if v not in allowed:
            raise ValueError(f"theme must be one of: {allowed}")
        return v

    @field_validator("static_url")
    @classmethod
    def validate_static_url(cls, v: Optional[str]) -> Optional[str]:
        """Normalize static_url with slashes if provided."""
        if v is None:
            return None
        v = v.strip()
        if not v.startswith("/"):
            v = f"/{v}"
        if not v.endswith("/"):
            v = f"{v}/"
        return v

    @field_validator("host")
    @classmethod
    def validate_host(cls, v: str) -> str:
        """Validate host is not empty."""
        if not v or not v.strip():
            raise ValueError("host cannot be empty")
        return v.strip()

    @field_validator("public_url")
    @classmethod
    def validate_public_url(cls, v: Optional[str]) -> Optional[str]:
        """Validate and normalize public_url."""
        if v is None:
            return None
        v = v.strip().rstrip("/")
        if not v.startswith(("http://", "https://")):
            raise ValueError("public_url must start with http:// or https://")
        return v
