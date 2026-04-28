"""Pydantic v2 configuration models for django_generator.

Public surface mirrors django_client for drop-in compatibility. New module
adds: tag-based slicing input (`tags`), `mirror_to_tmp` knob, dataclass
`GenerationTarget` shaped after cmdop's OpenAPITarget.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class OpenAPIGroupConfig(BaseModel):
    """One logical client bundle. Drives the slicer's tag selection."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",
    )

    name: str = Field(..., min_length=1)
    apps: list[str] = Field(..., min_length=1)
    title: str = Field(..., min_length=1)
    description: str = ""
    version: str = "v1"

    # NEW vs legacy: explicit OpenAPI tag set. If empty, resolver derives it
    # from `apps` via x-django-app extension + path heuristic.
    tags: list[str] = Field(default_factory=list)

    auth_required: bool = False

    @field_validator("name")
    @classmethod
    def _validate_name(cls, v: str) -> str:
        v = v.strip()
        if not re.match(r"^[a-zA-Z0-9_-]+$", v):
            raise ValueError("name must be alphanumeric / _ / -")
        return v


class OpenAPIConfig(BaseModel):
    """Top-level generator configuration.

    Same field names as django_client.OpenAPIConfig where they overlap so
    `solution/django/api/config.py` only needs an import path change.
    """

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",
    )

    enabled: bool = False

    # Schema metadata (passed to drf-spectacular)
    drf_title: str = "API"
    drf_description: str = ""
    drf_version: str = "1.0.0"

    # API routing
    api_prefix: str = "apix"

    # Output
    output_dir: str = Field(default="openapi")

    # Groups
    groups: list[OpenAPIGroupConfig] = Field(default_factory=list)

    # Per-language toggles (mirror legacy names)
    generate_python: bool = True
    generate_typescript: bool = True
    generate_package_files: bool = False

    # TS extras (default-on; legacy was opt-in)
    generate_zod_schemas: bool = True
    generate_fetchers: bool = True
    generate_swr_hooks: bool = True
    generate_events_bridge: bool = True

    client_structure: Literal["flat", "namespaced"] = "namespaced"

    # Devx: copy each generated tree to <project>/.tmp/generated/<name>/
    mirror_to_tmp: bool = True

    # Performance
    max_workers: int = Field(default=1, ge=1, le=20)

    @model_validator(mode="after")
    def _validate_groups(self) -> "OpenAPIConfig":
        if self.enabled and not self.groups:
            raise ValueError("at least one group required when enabled")
        names = [g.name for g in self.groups]
        if len(names) != len(set(names)):
            dups = sorted({n for n in names if names.count(n) > 1})
            raise ValueError(f"duplicate group names: {', '.join(dups)}")
        return self

    @field_validator("api_prefix")
    @classmethod
    def _strip_api_prefix(cls, v: str) -> str:
        v = v.strip().strip("/")
        if not v:
            raise ValueError("must not be empty")
        return v

    @field_validator("output_dir")
    @classmethod
    def _strip_output_dir(cls, v: str) -> str:
        # Trim whitespace but preserve leading '/' so absolute paths survive.
        v = v.strip()
        if not v or v.strip("/") == "":
            raise ValueError("must not be empty")
        return v

    # ----- Path helpers (same names as legacy) -----

    def get_output_path(self) -> Path:
        return Path(self.output_dir).resolve()

    def get_schemas_dir(self) -> Path:
        return self.get_output_path() / "schemas"

    def get_clients_dir(self) -> Path:
        return self.get_output_path() / "clients"

    def get_group_schema_path(self, group_name: str) -> Path:
        return self.get_schemas_dir() / f"{group_name}.yaml"

    def get_group_typescript_dir(self, group_name: str) -> Path:
        return self.get_clients_dir() / "typescript" / group_name

    def get_group_python_dir(self, group_name: str) -> Path:
        return self.get_clients_dir() / "python" / group_name

    def get_group_go_dir(self, group_name: str) -> Path:
        return self.get_clients_dir() / "go" / group_name


@dataclass(slots=True)
class GenerationTarget:
    """One concrete codegen target: language × tool × destination × tag set.

    Built by the runner from `solution/django/generation.py` Target objects
    × OpenAPIConfig groups. Internal contract — not part of the public API.
    """

    name: str
    lang: Literal["python", "typescript", "go", "swift", "proto"]
    tool: Literal[
        "ogen",
        "hey-api",
        "openapi-python-client",
        "swift-openapi",
        "buf",
        "grpc-python",
    ]
    path: Path
    groups: list[str]
    tags: list[str] = field(default_factory=list)
    options: dict[str, Any] = field(default_factory=dict)
    # Optional source-of-truth root inside the Django project. When set,
    # the pipeline writes to `source_path / <target_subdir>` first, then
    # copies the tree to `path` (the consumer location, e.g. frontend).
    # When None, the pipeline writes directly to `path` (legacy behavior).
    source_path: Path | None = None


@dataclass(slots=True)
class RunReport:
    """Per-run summary returned by DjangoOpenAPI.run().

    ``timings`` keys are target names; values are wallclock seconds the
    runner spent on that target (slicing + tool dispatch + cache I/O).
    The orchestrator also records the spec-load step under the synthetic
    name ``__spec__`` and the run total under ``__total__``.

    ``cache_hits`` mirrors ``timings`` keys and tells whether the per-
    target output cache served the result without invoking the external
    tool. The same dict carries a ``__spec__`` entry indicating whether
    the global spec was replayed from cache.
    """

    targets_run: list[str] = field(default_factory=list)
    targets_skipped: list[str] = field(default_factory=list)
    failures: list[tuple[str, str]] = field(default_factory=list)
    timings: dict[str, float] = field(default_factory=dict)
    cache_hits: dict[str, bool] = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return not self.failures


__all__ = [
    "OpenAPIConfig",
    "OpenAPIGroupConfig",
    "GenerationTarget",
    "RunReport",
]
