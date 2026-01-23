"""
Configuration model for FastAPI ORM Generator.

Defines all settings for code generation including output format,
target apps, and PostgreSQL-specific options.
"""

from pathlib import Path
from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator


class FastAPIConfig(BaseModel):
    """
    Configuration for FastAPI ORM code generation.

    Example:
        config = FastAPIConfig(
            output_dir="fastapi/",
            format="sqlmodel",
            apps=["users", "products"],
            include_crud=True,
        )
    """

    # Enable/disable module
    enabled: bool = Field(default=False, description="Enable FastAPI ORM generation")

    # Output configuration
    output_dir: str = Field(
        default="fastapi_orm/",
        description="Output directory for generated files"
    )
    format: Literal["sqlmodel", "pydantic", "sqlalchemy"] = Field(
        default="sqlmodel",
        description="ORM format to generate"
    )

    # Generation options
    include_crud: bool = Field(default=True, description="Generate async CRUD repositories")
    include_schemas: bool = Field(default=True, description="Generate Pydantic schemas")
    include_relationships: bool = Field(default=False, description="Generate SQLModel Relationship() definitions (can cause issues with duplicate model names)")
    include_alembic: bool = Field(default=False, description="Generate Alembic configuration")
    include_database_config: bool = Field(default=True, description="Generate database.py setup")
    async_mode: bool = Field(default=True, description="Generate async code (vs sync)")

    # Apps selection
    apps: list[str] = Field(
        default_factory=list,
        description="Apps to process (empty = all apps)"
    )
    exclude_apps: list[str] = Field(
        default_factory=lambda: [
            "admin",
            "contenttypes",
            "sessions",
            "auth",
            "messages",
            "staticfiles",
        ],
        description="Apps to exclude from generation"
    )
    exclude_models: list[str] = Field(
        default_factory=list,
        description="Specific models to exclude (format: app_label.ModelName)"
    )

    # PostgreSQL-specific options
    use_jsonb: bool = Field(default=True, description="Use JSONB for JSONField (PostgreSQL)")
    use_array_fields: bool = Field(default=True, description="Use native ARRAY type (PostgreSQL)")
    use_uuid_type: bool = Field(default=True, description="Use native UUID type (PostgreSQL)")

    # Naming conventions
    schema_suffix: str = Field(default="Schema", description="Suffix for Pydantic schemas")
    repository_suffix: str = Field(default="Repository", description="Suffix for CRUD repositories")

    # Code style
    add_docstrings: bool = Field(default=True, description="Add docstrings to generated code")
    add_type_hints: bool = Field(default=True, description="Add comprehensive type hints")

    # Database configuration (for database.py generation)
    database_env_var: str = Field(
        default="DATABASE_URL",
        description="Environment variable name for database URL"
    )
    database_default_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/postgres",
        description="Default database URL if env var is not set"
    )

    @field_validator("output_dir")
    @classmethod
    def validate_output_dir(cls, v: str) -> str:
        """Ensure output_dir ends with /."""
        if not v.endswith("/"):
            v = f"{v}/"
        return v

    @property
    def output_path(self) -> Path:
        """Get output directory as Path."""
        return Path(self.output_dir)

    model_config = {
        "extra": "forbid",
    }
