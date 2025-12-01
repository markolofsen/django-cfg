"""
NextJsAdminConfig - Configuration model for Next.js admin integration.

Simple configuration with smart defaults - only project_path is required.
"""

from typing import Optional
from pydantic import BaseModel, Field, field_validator


class NextJsAdminConfig(BaseModel):
    """
    Next.js admin integration configuration.

    Minimal configuration:
        nextjs_admin = NextJsAdminConfig(
            project_path="../django_admin"
        )

    With custom settings:
        nextjs_admin = NextJsAdminConfig(
            project_path="../django_admin",
            dev_url="http://localhost:3002",
            static_url="/admin-ui/",
        )
    """

    model_config = {
        "validate_assignment": True,
        "extra": "forbid",
        "str_strip_whitespace": True,
    }

    # =================================================================
    # REQUIRED
    # =================================================================

    project_path: str = Field(
        ...,
        description=(
            "Path to Next.js project (relative or absolute). "
            "Relative paths resolved from Django BASE_DIR. "
            "Example: '../django_admin'"
        ),
    )

    # =================================================================
    # OPTIONAL (with smart defaults)
    # =================================================================

    api_output_path: Optional[str] = Field(
        default=None,
        description=(
            "Path for generated TypeScript clients (relative to project_path). "
            "Default: 'apps/admin/app/_lib/api/generated'"
        ),
    )

    static_output_path: Optional[str] = Field(
        default=None,
        description=(
            "Next.js build output directory (relative to project_path). "
            "Default: 'out'"
        ),
    )

    static_url: Optional[str] = Field(
        default=None,
        description=(
            "URL prefix for serving Next.js static files. "
            "Default: '/cfg/admin/'"
        ),
    )

    dev_url: Optional[str] = Field(
        default=None,
        description=(
            "Next.js development server URL. "
            "Default: 'http://localhost:3001'"
        ),
    )

    iframe_route: Optional[str] = Field(
        default=None,
        description=(
            "Next.js route to display in iframe. "
            "Default: '/private'"
        ),
    )

    iframe_sandbox: Optional[str] = Field(
        default=None,
        description="HTML5 iframe sandbox attribute (optional)",
    )

    tab_title: Optional[str] = Field(
        default=None,
        description=(
            "Title for Next.js admin tab. "
            "Default: 'Next.js Admin'"
        ),
    )

    # =================================================================
    # Computed properties with defaults
    # =================================================================

    def get_api_output_path(self) -> str:
        """Get API output path with default."""
        return self.api_output_path or "apps/admin/app/_lib/api/generated"

    def get_static_output_path(self) -> str:
        """Get static output path with default."""
        return self.static_output_path or "out"

    def get_static_url(self) -> str:
        """Get static URL with default (with trailing slash for Django URLs)."""
        url = self.static_url or "/cfg/nextjs-admin/"
        # Ensure slashes
        if not url.startswith("/"):
            url = f"/{url}"
        if not url.endswith("/"):
            url = f"{url}/"
        return url

    def get_base_path(self) -> str:
        """Get base path for Next.js basePath (WITHOUT trailing slash)."""
        url = self.static_url or "/cfg/nextjs-admin"
        # Ensure starts with slash
        if not url.startswith("/"):
            url = f"/{url}"
        # Remove trailing slash for Next.js basePath
        return url.rstrip("/")

    def get_dev_url(self) -> str:
        """Get dev URL with default."""
        return self.dev_url or "http://localhost:3001"

    def get_iframe_route(self) -> str:
        """Get iframe route with default."""
        return self.iframe_route or "/private"

    def get_iframe_sandbox(self) -> str:
        """Get iframe sandbox with default."""
        return self.iframe_sandbox or (
            "allow-same-origin allow-scripts allow-forms "
            "allow-popups allow-modals allow-storage-access-by-user-activation"
        )

    def get_tab_title(self) -> str:
        """Get tab title with default."""
        return self.tab_title or "Next.js Admin"

    def get_static_zip_path(self, solution_base_dir):
        """
        Get path to nextjs_admin.zip for Django static serving.

        Args:
            solution_base_dir: Solution project BASE_DIR (from settings.BASE_DIR)

        Returns:
            Path: Path to nextjs_admin.zip (e.g., solution/projects/django/static/nextjs_admin.zip)
        """
        from pathlib import Path
        return Path(solution_base_dir) / "static" / "nextjs_admin.zip"

    # =================================================================
    # Validators
    # =================================================================

    @field_validator("project_path")
    @classmethod
    def validate_project_path(cls, v: str) -> str:
        """Validate project path is not empty."""
        if not v or not v.strip():
            raise ValueError("project_path cannot be empty")
        return v.strip()

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
