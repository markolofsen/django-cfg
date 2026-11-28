"""
Pydantic configuration models for client generation.

v5.3: Groups only in Target, no inheritance.
"""

from enum import Enum
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, model_validator

# =============================================================================
# Enums
# =============================================================================


class Platform(str, Enum):
    """Supported generation platforms/languages."""

    TYPESCRIPT = "typescript"
    PYTHON = "python"
    GO = "go"
    RUST = "rust"  # progenitor: one reqwest crate per target
    SWIFT = "swift"
    SWIFT_CODABLE = "swift_codable"  # Simple Codable types without OpenAPIRuntime
    PROTO = "proto"  # Protocol Buffers / gRPC

    @classmethod
    def api_platforms(cls) -> set["Platform"]:
        """Platforms for API client generation (OpenAPI)."""
        return {cls.TYPESCRIPT, cls.PYTHON, cls.GO, cls.RUST, cls.SWIFT, cls.SWIFT_CODABLE, cls.PROTO}

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
            type=TargetType.WEB,
            path=Path("frontend/apps/web/api/generated"),
            groups=["cfg_*", "profiles"],
        )
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    lang: Language
    type: TargetType | str
    path: Path
    groups: list[str]  # Required, no inheritance
    post_build: str | None = None  # e.g., "pnpm build"

    # TypeScript (Orval) options; the generator README lists them under "Target options".
    #: "public": every request of this client goes without the session (`auth: 'none'` in the generated shim).
    auth_mode: Literal["default", "public"] = "default"
    #: Raw OpenAPI tags whose operations go straight to the API host (`origin: 'direct'`), never through the proxy.
    direct_origin_tags: list[str] = []
    #: Also generate `use<Op>Infinite` for every GET that takes a `page` or `cursor` query parameter.
    infinite: bool = False
    #: "cli": standalone Fetch operations/Zod, without frontend hooks, session runtime or mocks.
    typescript_profile: Literal["web", "cli"] = "web"

    # Rust (progenitor) options.
    #: Cargo package name of the generated crate; default: the target folder's name, kebab-cased.
    rust_crate: str | None = None
    #: The crate is a member of the Cargo workspace above ``path``: inherited package keys and lints,
    #: ``dep.workspace = true``, and ``workspace-dependencies.toml`` with the entries for the root.
    rust_workspace: bool = False

    @model_validator(mode="after")
    def _typescript_options_only_on_typescript(self) -> "Target":
        if self.typescript_profile == "cli" and (self.infinite or self.direct_origin_tags):
            raise ValueError("typescript_profile='cli' does not support infinite or direct_origin_tags; pass an explicit baseUrl per call")
        if self.lang != Language.TYPESCRIPT:
            set_options = sorted(self.typescript_options())
            if set_options:
                raise ValueError(
                    f"{', '.join(set_options)} only apply to a TypeScript target, not {self.lang.value} ({self.path})"
                )
        if self.lang != Language.RUST and (self.rust_crate is not None or self.rust_workspace):
            raise ValueError(
                f"rust_crate and rust_workspace only apply to a Rust target, not {self.lang.value} ({self.path})"
            )
        return self

    def rust_options(self) -> dict[str, Any]:
        """The Rust options set away from their defaults, as the pipeline's ``GenerationTarget.options``."""
        options: dict[str, Any] = {}
        if self.rust_crate:
            options["crate_name"] = self.rust_crate
        if self.rust_workspace:
            options["workspace"] = True
        return options

    def typescript_options(self) -> dict[str, Any]:
        """The TypeScript options set away from their defaults, as the pipeline's ``GenerationTarget.options``."""
        options: dict[str, Any] = {}
        if self.typescript_profile != "web":
            options["typescript_profile"] = self.typescript_profile
        if self.auth_mode != "default":
            options["auth_mode"] = self.auth_mode
        if self.direct_origin_tags:
            options["direct_origin_tags"] = list(self.direct_origin_tags)
        if self.infinite:
            options["infinite"] = True
        return options

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

    Example:
        OpenAPI(
            targets=[
                Target(lang=Language.TYPESCRIPT, type=TargetType.WEB, path=..., groups=["cfg_*"]),
                Target(lang=Language.PYTHON, type=TargetType.PARSERS, path=..., groups=["normalizer"]),
            ],
        )
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    targets: list[Target] = []
    extensions: ExtensionTarget | None = None
    go_module: str | None = None

    # Source-of-truth root inside the Django project. When set, every
    # TS/Python/Go target is generated into `source_root/<target-name>/`
    # first, then copied to its `path` (the consumer location).
    source_root: Path | None = None

    def get_targets_for_lang(self, lang: Language) -> list[Target]:
        """Get all targets for a language including auto-discovered extensions."""
        result = [t for t in self.targets if t.lang == lang]

        if self.extensions and self.extensions.lang == lang:
            result.extend(self.extensions.discover())

        return result


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
                        type=TargetType.WEB,
                        path=FRONTEND / "apps/web/api/generated",
                        groups=["cfg_*", "profiles"],
                    ),
                ],
            ),
        )

    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    openapi: OpenAPI | None = None
    sdk: SDK | None = None
    orm: ORM | None = None  # FastAPI/Pydantic model generation
