"""
django_cf.core.client — CloudflareD1Client.

Thin wrapper around the official `cloudflare` SDK:
- Holds credentials
- Exposes execute() / execute_batch() with typed D1QueryResult
- Maps SDK errors to local CloudflareError subclasses
"""

from __future__ import annotations

import logging
from typing import Any

from cloudflare import (
    Cloudflare,
    BadRequestError,
    AuthenticationError,
    PermissionDeniedError,
    RateLimitError,
    APIConnectionError,
    APITimeoutError,
    APIStatusError,
)

from ..exceptions import CloudflareConfigError, CloudflareQueryError
from .types import D1QueryResult

logger = logging.getLogger(__name__)


class CloudflareD1Client:
    """Synchronous D1 client backed by the official cloudflare SDK."""

    __slots__ = ("_account_id", "_database_id", "_sdk")

    def __init__(
        self,
        account_id: str,
        api_token: str,
        database_id: str,
    ) -> None:
        if not account_id or not api_token or not database_id:
            missing = [k for k, v in {
                "account_id": account_id,
                "api_token": api_token,
                "database_id": database_id,
            }.items() if not v]
            raise CloudflareConfigError(
                "CloudflareD1Client: missing credentials",
                missing_fields=missing,
            )
        self._account_id = account_id
        self._database_id = database_id
        self._sdk = Cloudflare(api_token=api_token)

    def execute(self, sql: str, params: list[str] | None = None) -> D1QueryResult:
        """Execute a single SQL statement. Returns typed D1QueryResult."""
        try:
            pages = list(self._sdk.d1.database.query(
                database_id=self._database_id,
                account_id=self._account_id,
                sql=sql.strip(),
                params=params or [],
            ))
            if not pages:
                return D1QueryResult()
            result = D1QueryResult.from_sdk_page(pages[0])
            if not result.success:
                raise CloudflareQueryError("D1 query returned success=False", sql=sql)
            return result
        except CloudflareQueryError:
            raise
        except BadRequestError as exc:
            # D1 SQL errors — 400 with SQLITE_ERROR code
            # Gracefully handle missing schema (table/column not yet created)
            msg = str(exc)
            if "no such table" in msg or "no such column" in msg:
                logger.debug("django_cf: D1 schema not ready — %s", msg)
                return D1QueryResult()
            raise CloudflareQueryError(f"D1 bad request: {exc}", sql=sql) from exc
        except AuthenticationError as exc:
            raise CloudflareConfigError(f"D1 authentication failed — check api_token: {exc}") from exc
        except PermissionDeniedError as exc:
            raise CloudflareConfigError(f"D1 permission denied — check account_id/database_id: {exc}") from exc
        except RateLimitError as exc:
            raise CloudflareQueryError(f"D1 rate limit exceeded: {exc}", sql=sql) from exc
        except (APIConnectionError, APITimeoutError) as exc:
            raise CloudflareQueryError(f"D1 connection error: {exc}", sql=sql) from exc
        except APIStatusError as exc:
            raise CloudflareQueryError(f"D1 API error {exc.status_code}: {exc}", sql=sql) from exc
        except Exception as exc:
            raise CloudflareQueryError(f"D1 execute failed: {exc}", sql=sql) from exc

    def execute_batch(self, statements: list[dict[str, Any]]) -> list[D1QueryResult]:
        """Execute multiple statements sequentially.

        The installed SDK version does not support native batch with per-statement params.
        Each item: {"sql": "...", "params": [...]}
        """
        return [self.execute(s["sql"], s.get("params")) for s in statements]


__all__ = ["CloudflareD1Client"]
