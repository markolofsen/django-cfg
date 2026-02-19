"""
Pydantic configuration models for client generation.

v5.3: Groups only in Target, no inheritance.
"""

from enum import Enum
from pathlib import Path

from pydantic import BaseModel, ConfigDict, model_validator


# =============================================================================
# Enums
# =============================================================================


class Platform(str, Enum):
    """Supported generation platforms/languages."""

    TYPESCRIPT = "typescript"
    PYTHON = "python"
    GO = "go"
    SWIFT = "swift"
    SWIFT_CODABLE = "swift_codable"  # Simple Codable types without OpenAPIRuntime
    PROTO = "proto"  # Protocol Buffers / gRPC

    @classmethod
    def api_platforms(cls) -> set["Platform"]:
        """Platforms for API client generation (OpenAPI)."""
        return {cls.TYPESCRIPT, cls.PYTHON, cls.GO, cls.SWIFT, cls.SWIFT_CODABLE, cls.PROTO}

    @classmethod
    def default_platforms(cls) -> set["Platform"]:
        """Default platforms for generation."""
        return {cls.TYPESCRIPT, cls.PYTHON, cls.GO}

    @property
    def is_external(self) -> bool:
        """Whether this platform uses external generator."""
        return self == Platform.SWIFT


# Alias for backwards compatibility
Language = Platform


class TargetType(str, Enum):
    """
    Predefined target types.

    Projects can use these or define custom strings.
    """

    ADMIN = "admin"
    WEB = "web"
    PACKAGES = "packages"
    EXTENSIONS = "extensions"
    PARSERS = "parsers"
    SDK = "sdk"


# =============================================================================
# Target Models
# =============================================================================


class Target(BaseModel):
    """
    Single generation target.

    Example:
        Target(
            lang=Language.TYPESCRIPT,
            type=TargetType.ADMIN,
            path=Path("frontend/apps/admin/api/generated"),
            groups=["cfg_*", "profiles"],
        )
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    lang: Language
    type: TargetType | str
    path: Path
    groups: list[str]  # Required, no inheritance
    post_build: str | None = None  # e.g., "pnpm build"

    def matches_filter(self, filter_type: str | None) -> bool:
        """Check if target matches --target filter."""
        if filter_type is None:
            return True
        if isinstance(self.type, TargetType):
            return self.type.value == filter_type
        return self.type == filter_type

    def matches_lang(self, lang: Language | str | None) -> bool:
        """Check if target matches language filter."""
        if lang is None:
            return True
        if isinstance(lang, Language):
            return self.lang == lang
        return self.lang.value == lang


class ExtensionTarget(BaseModel):
    """
    Auto-discovered extension targets.

    Scans frontend_path for packages matching pattern,
    maps them to Django groups by prefix.

    Example:
        ExtensionTarget(
            frontend_path=Path("frontend/extensions"),
            package_pattern="ext-{name}",  # ext-support, ext-leads
            output_pattern="src/api/generated",
            group_prefix="ext_",  # maps to ext_support, ext_leads
        )
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    lang: Language = Language.TYPESCRIPT  # Extensions are usually TypeScript
    frontend_path: Path
    package_pattern: str = "ext-{name}"
    output_pattern: str = "src/api/generated"
    group_prefix: str = "ext_"
    post_build: str | None = None

    def discover(self) -> list[Target]:
        """
        Auto-discover extension packages.

        Returns list of Target objects for each discovered extension.
        Only includes packages that have a generated/ folder (indicating they have API).
        """
        targets = []

        if not self.frontend_path.exists():
            return targets

        # Parse pattern to extract prefix
        prefix = self.package_pattern.split("{name}")[0]  # "ext-"

        for path in sorted(self.frontend_path.iterdir()):
            if not path.is_dir():
                continue
            if not path.name.startswith(prefix):
                continue

            # Build output path
            output = path / self.output_pattern

            # Skip packages without generated/ folder (e.g., ext-base has no API)
            if not output.exists():
                continue

            # Extract name: ext-support -> support
            name = path.name[len(prefix) :]

            # Map to group: support -> ext_support
            group = f"{self.group_prefix}{name}"

            targets.append(
                Target(
                    lang=self.lang,
                    type=TargetType.EXTENSIONS,
                    path=output,
                    groups=[group],
                    post_build=self.post_build,
                )
            )

        return targets


# =============================================================================
# OpenAPI Config
# =============================================================================


class OpenAPI(BaseModel):
    """
    OpenAPI client generation config.

    New format (v5.3):
        OpenAPI(
            targets=[
                Target(lang=Language.TYPESCRIPT, type=TargetType.ADMIN, path=..., groups=["cfg_*"]),
                Target(lang=Language.PYTHON, type=TargetType.PARSERS, path=..., groups=["normalizer"]),
            ],
        )

    Legacy format (v5.0) - still supported:
        OpenAPI(
            typescript=["profiles", "catalog"],
            legacy_targets={"typescript": Path("frontend/api/generated")},
        )
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    # New format (v5.3) - list of targets
    targets: list[Target] = []

    # Auto-discovered extensions
    extensions: ExtensionTarget | None = None

    # Go-specific
    go_module: str | None = None

    # Legacy format (v5.0) - still supported
    typescript: list[str] = []
    python: list[str] = []
    go: list[str] = []
    swift: list[str] = []
    legacy_targets: dict[str, Path] = {}

    def is_legacy_format(self) -> bool:
        """Check if using legacy v5.0 format."""
        return bool(self.typescript or self.python or self.go or self.swift) and not self.targets

    def get_targets_for_lang(self, lang: Language) -> list[Target]:
        """Get all targets for a language including auto-discovered extensions."""
        result = []

        if self.is_legacy_format():
            # Convert legacy format to Target
            if lang.value in self.legacy_targets:
                result.append(
                    Target(
                        lang=lang,
                        type=TargetType.ADMIN,  # Default type for legacy
                        path=self.legacy_targets[lang.value],
                        groups=getattr(self, lang.value, []),
                    )
                )
        else:
            # Filter targets by language
            result.extend([t for t in self.targets if t.lang == lang])

        # Add auto-discovered extensions
        if self.extensions and self.extensions.lang == lang:
            result.extend(self.extensions.discover())

        return result


# =============================================================================
# Centrifugo Config
# =============================================================================


class Centrifugo(BaseModel):
    """Centrifugo RPC client generation config."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    # New format (v5.3)
    targets: list[Target] = []

    # Legacy format
    typescript: list[str] = []
    swift: list[str] = []
    go: list[str] = []
    legacy_targets: dict[str, Path] = {}

    def is_legacy_format(self) -> bool:
        """Check if using legacy format."""
        return bool(self.typescript or self.swift or self.go) and not self.targets


# =============================================================================
# SDK Config
# =============================================================================


class SDKPackage(BaseModel):
    """Single SDK package config."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    name: str
    groups: list[str]
    target: Path
    platform: Platform = Platform.PYTHON


class SDK(BaseModel):
    """SDK packages generation config."""

    packages: list[SDKPackage] = []


# =============================================================================
# ORM Config (FastAPI models generation)
# =============================================================================


class ORMGenerator(str, Enum):
    """ORM model generator types."""

    FASTAPI = "fastapi"
    PYDANTIC = "pydantic"
    SQLALCHEMY = "sqlalchemy"


class ORMTarget(BaseModel):
    """Single ORM generation target."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    output: Path
    generator: ORMGenerator = ORMGenerator.FASTAPI
    apps: list[str] = []  # Apps to process (empty = all apps)


class ORM(BaseModel):
    """
    ORM/FastAPI model generation config.

    Generates SQLModel models, Pydantic schemas, and async CRUD repositories
    from Django models.

    Example:
        ORM(
            targets=[
                ORMTarget(
                    output=Path("fastapi_server/src/orm"),
                    generator=ORMGenerator.FASTAPI,
                    apps=["profiles", "catalog"],
                ),
            ],
            include_crud=True,
            async_mode=True,
        )
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    targets: list[ORMTarget] = []

    # Generation options
    include_crud: bool = True  # Generate async CRUD repositories
    include_schemas: bool = True  # Generate Pydantic schemas
    include_relationships: bool = False  # Generate SQLModel Relationship() definitions
    include_database_config: bool = True  # Generate database.py setup
    async_mode: bool = True  # Generate async code (vs sync)

    # Apps to exclude from generation
    exclude_apps: list[str] = [
        "admin",
        "contenttypes",
        "sessions",
        "auth",
        "messages",
        "staticfiles",
        "django_rq",
    ]

    # PostgreSQL-specific options
    use_jsonb: bool = True  # Use JSONB for JSONField
    use_array_fields: bool = True  # Use native ARRAY type

    # Database configuration
    database_env_var: str = "DATABASE_URL"
    database_default_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/postgres"


# =============================================================================
# Generation Options (typed interface for generate_clients)
# =============================================================================


class GeneratorOptions(BaseModel):
    """
    Typed options for generation.

    Use this instead of raw dict when calling generators programmatically.

    Example:
        options = GeneratorOptions(
            platforms={Platform.TYPESCRIPT, Platform.PYTHON},
            groups=["profiles", "catalog"],
        )
        run_generation(options)
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    # Platform selection
    platforms: set[Platform] = Platform.default_platforms()

    # Groups filter
    groups: list[str] | None = None  # None = all groups

    # Behavior
    dry_run: bool = False
    verbose: bool = False

    # Streamlit integration
    streamlit: bool = False  # Copy Python clients to Streamlit

    # External generators
    external_go: bool = False  # Use oapi-codegen instead of built-in
    external_python: bool = False  # Use openapi-python-client

    def has_platform(self, platform: Platform) -> bool:
        """Check if platform is enabled."""
        return platform in self.platforms

    def to_command_options(self) -> dict:
        """
        Convert to Django management command options.

        For compatibility with generate_clients command.
        """
        opts: dict = {}

        # Single platform mode
        if len(self.platforms) == 1:
            platform = list(self.platforms)[0]
            opts[platform.value] = True
        else:
            # Skip platforms not selected
            all_default = {Platform.TYPESCRIPT, Platform.PYTHON, Platform.GO, Platform.PROTO}
            for platform in all_default - self.platforms:
                if platform in all_default:
                    opts[f"no_{platform.value}"] = True

            # Enable non-default platforms
            if Platform.SWIFT in self.platforms:
                opts["swift"] = True
            if Platform.SWIFT_CODABLE in self.platforms:
                opts["swift_codable"] = True

        if self.groups:
            opts["groups"] = self.groups
        if self.dry_run:
            opts["dry_run"] = True
        if self.verbose:
            opts["verbose"] = True
        if self.streamlit:
            opts["streamlit"] = True
        if self.external_go:
            opts["external_go"] = True
        if self.external_python:
            opts["external_python"] = True

        return opts


# =============================================================================
# Main Config
# =============================================================================


class Config(BaseModel):
    """
    Main generation config.

    Example (v5.3):
        config = Config(
            openapi=OpenAPI(
                targets=[
                    Target(
                        lang=Language.TYPESCRIPT,
                        type=TargetType.ADMIN,
                        path=FRONTEND / "apps/admin/api/generated",
                        groups=["cfg_*", "profiles"],
                    ),
                ],
            ),
        )

    Example (v5.0 legacy):
        config = Config(
            openapi=OpenAPI(
                typescript=["profiles", "catalog"],
                legacy_targets={"typescript": FRONTEND / "api/generated"},
            ),
        )
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    openapi: OpenAPI | None = None
    centrifugo: Centrifugo | None = None
    sdk: SDK | None = None
    orm: ORM | None = None  # FastAPI/Pydantic model generation
