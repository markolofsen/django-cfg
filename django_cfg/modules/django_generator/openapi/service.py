"""DjangoOpenAPI singleton — entry point used by the management command."""

from __future__ import annotations

from typing import Optional

from .pipeline.config import (
    GenerationTarget,
    OpenAPIConfig,
    OpenAPIGroupConfig,
    RunReport,
)


class DjangoOpenAPI:
    """Service wrapper around an OpenAPIConfig.

    Holds the active config and exposes `run()` which orchestrates the full
    pipeline (spec_load → postprocess → slice → external tool → ts_extras → fs).
    """

    def __init__(self, config: Optional[OpenAPIConfig] = None) -> None:
        self._config: Optional[OpenAPIConfig] = config

    def set_config(self, config: OpenAPIConfig) -> None:
        self._config = config

    @property
    def config(self) -> Optional[OpenAPIConfig]:
        return self._config

    def is_enabled(self) -> bool:
        return self._config is not None and self._config.enabled

    def list_groups(self) -> list[OpenAPIGroupConfig]:
        if not self._config:
            return []
        return list(self._config.groups)

    def get_group(self, name: str) -> Optional[OpenAPIGroupConfig]:
        for g in self.list_groups():
            if g.name == name:
                return g
        return None

    def get_group_names(self) -> list[str]:
        return [g.name for g in self.list_groups()]

    def run(
        self,
        *,
        targets: list[GenerationTarget],
        dry_run: bool = False,
    ) -> RunReport:
        """Execute the generator pipeline.

        Phase 1: stub (returns empty report).
        Phase 2+ wires spec_loader, slicer, external tools, ts_extras.
        """
        if not self.is_enabled():
            return RunReport()

        from .pipeline.runner import run_pipeline

        return run_pipeline(self._config, targets, dry_run=dry_run)


_service: Optional[DjangoOpenAPI] = None


def get_openapi_service() -> DjangoOpenAPI:
    global _service
    if _service is None:
        _service = DjangoOpenAPI()
    return _service


__all__ = ["DjangoOpenAPI", "get_openapi_service"]
