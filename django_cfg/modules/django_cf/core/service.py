"""
django_cf.core.service — BaseD1Service.

Abstract base that every D1-backed service inherits.
Provides _get_client(), _get_api_url(), _ensure_schema() so subclasses
focus only on their domain logic.

Usage:
    from django_cfg.modules.django_cf.core import BaseD1Service

    class MyFeatureService(BaseD1Service):
        def _get_schema_statements(self) -> list[str]:
            return [CREATE_MY_TABLE]

        def push_something(self, obj) -> D1QueryResult:
            self._ensure_schema()
            return self._get_client().execute(MY_SQL, [...])
"""

from __future__ import annotations

import logging

from django_cfg.core.state.registry import get_current_config  # module-level: patchable
from .client import CloudflareD1Client  # module-level: patchable in tests
from ..exceptions import CloudflareConfigError, CloudflareSchemaError

logger = logging.getLogger(__name__)


class BaseD1Service:
    """Base class for all D1-backed services in django_cf and dependent modules.

    Subclasses must implement _get_schema_statements().
    """

    # Per-subclass schema flag: stored on the concrete class, not the instance,
    # so _ensure_schema() runs only once per process per subclass.
    _schema_ready: bool = False

    # ── Abstract ──────────────────────────────────────────────────────────────

    def _get_schema_statements(self) -> list[str]:
        """Return DDL statements to run on first use. Override in subclasses."""
        return []

    # ── Shared infrastructure ─────────────────────────────────────────────────

    def _get_client(self) -> CloudflareD1Client:
        """Build a D1 client from the live CloudflareConfig."""
        try:
            from django_cfg.modules.django_cf import _get_config  # lazy: avoids circular
            config = _get_config()
            if config is None or not config.is_ready():
                raise CloudflareConfigError(
                    "BaseD1Service: CloudflareConfig not configured or not ready"
                )
            return CloudflareD1Client(
                account_id=config.account_id,
                api_token=config.api_token,
                database_id=config.d1_database_id,
            )
        except CloudflareConfigError:
            raise
        except Exception as exc:
            raise CloudflareConfigError(
                "BaseD1Service: cannot build D1 client — is CloudflareConfig enabled? "
                "Add CloudflareConfig(enabled=True, ...) to DjangoConfig",
            ) from exc

    def _get_api_url(self) -> str:
        """Resolve api_url from the live DjangoConfig."""
        config = get_current_config()
        if config and hasattr(config, "api_url") and config.api_url:
            return str(config.api_url).rstrip("/")
        raise CloudflareConfigError(
            "BaseD1Service: cannot resolve api_url — DjangoConfig.api_url not set"
        )

    def _ensure_schema(self) -> None:
        """Run schema statements idempotently — once per process per subclass."""
        if type(self)._schema_ready:
            return
        client = self._get_client()
        for sql in self._get_schema_statements():
            try:
                client.execute(sql)
            except Exception as exc:
                raise CloudflareSchemaError(
                    f"{self.__class__.__name__}: schema migration failed: {exc}"
                ) from exc
        type(self)._schema_ready = True


__all__ = ["BaseD1Service"]
