"""IndexNow — push changed URLs to Bing, Yandex, Seznam, Naver and others.

Configured by `IndexNowConfig` on `DjangoConfig.indexnow`; without it every
function here is inert. Google does not take part: the sitemap is its channel.

Each run diffs what the sitemap sources produce for a host against what was
last submitted for it, and sends new, changed and removed URLs. Only an
accepted batch is recorded, so a failed run is retried by the next one. The
first run for a host records and sends nothing.

- `urls`      what the sitemap sources produce, as absolute URLs
- `transport` one POST, its log, and `submit()` for request paths
- `state`     the diff against what was last accepted
- `sweep`     one run per host, and the scheduled `submit_changed()`

The scheduled job is `django_cfg.modules.django_sitemap.indexnow.submit_changed`;
keep it importable from here, or every project's registered schedule breaks.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django_cfg.models.django.indexnow import IndexNowConfig


class IndexNowError(RuntimeError):
    """A batch was refused. Raised only by `submit_changed` / `submit(..., raise_errors=True)`."""


def get_config() -> "IndexNowConfig | None":
    """The active `IndexNowConfig`, or None when absent or disabled."""
    from django_cfg.core.state import get_current_config

    cfg = get_current_config()
    ix = getattr(cfg, "indexnow", None) if cfg else None
    return ix if ix and ix.enabled else None


from .state import reseed  # noqa: E402
from .sweep import submit_changed, sweep_site  # noqa: E402
from .transport import SubmitResult, submit  # noqa: E402
from .urls import absolute_url, site_urls  # noqa: E402

__all__ = [
    "IndexNowError",
    "SubmitResult",
    "absolute_url",
    "get_config",
    "reseed",
    "site_urls",
    "submit",
    "submit_changed",
    "sweep_site",
]
