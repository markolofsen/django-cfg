"""
IndexNow configuration model.
"""

import re
from typing import TYPE_CHECKING, List, Optional

from pydantic import BaseModel, Field, field_validator, model_validator

if TYPE_CHECKING:
    from django_cfg.models.django.django_rq import RQScheduleConfig

# The protocol's key alphabet and length.
_KEY = re.compile(r"^[A-Za-z0-9-]{8,128}$")


def _valid_key(v: str) -> str:
    if not _KEY.match(v):
        raise ValueError("IndexNow key must be 8–128 characters of A-Z, a-z, 0-9 or '-'")
    return v


def _bare_host(v: str) -> str:
    v = v.strip().lower()
    if "://" in v or "/" in v:
        raise ValueError("host is a bare hostname like 'example.com', without scheme or path")
    return v


class IndexNowSite(BaseModel):
    """One public host and the sitemap sources whose URLs live on it.

    For a backend that serves several sites — one Django, several brands, each
    on its own domain. IndexNow takes one host per request, and every URL in it
    must be on that host, so each site is submitted separately.
    """

    host: str = Field(..., description="Bare public hostname: 'example.com'.")
    key: Optional[str] = Field(
        default=None, description="This host's own key. Default: the config's shared key.",
    )
    sources: Optional[List[str]] = Field(
        default=None, description="Sitemap source names on this host.",
    )
    source_suffix: Optional[str] = Field(
        default=None,
        description="Every source whose name ends in this, e.g. '-caribbean' for 'properties-caribbean'.",
    )
    key_location: Optional[str] = Field(
        default=None, description="Default https://<host>/<key>.txt.",
    )
    trailing_slash: Optional[bool] = Field(
        default=None, description="Override the config's trailing_slash for this host.",
    )

    @field_validator("host")
    @classmethod
    def _host(cls, v: str) -> str:
        return _bare_host(v)

    @field_validator("key")
    @classmethod
    def _key(cls, v: Optional[str]) -> Optional[str]:
        return None if v is None else _valid_key(v)

    def takes(self, source_name: str) -> bool:
        if self.sources is None and self.source_suffix is None:
            return True
        if self.sources is not None and source_name in self.sources:
            return True
        return bool(self.source_suffix) and source_name.endswith(self.source_suffix)


class IndexNowConfig(BaseModel):
    """
    IndexNow: push changed URLs to Bing, Yandex, Seznam, Naver and others.

    One submission to `api.indexnow.org` is shared by every participating
    engine. Google does not take part — the sitemap stays its channel.

    The URLs come from the sitemap sources you already registered
    (`sitemap_sources.py`). Each run diffs them against what was last
    submitted for the host: new URLs, URLs whose lastmod moved, and URLs that
    left a source are sent. Only an accepted batch is recorded, so a failed
    run is retried by the next one. The first run records and sends nothing.

    The key is PUBLIC by protocol: it must be served as plain text at
    `https://<host>/<key>.txt`. Django serves it at
    `/cfg/sitemap/indexnow/<key>.txt`; a Next.js frontend rewrites to that
    with `indexNowKeyRewrite()` from `@djangocfg/nextjs/config`.

    Example:
        ```python
        from django_cfg import DjangoConfig, IndexNowConfig

        class MyConfig(DjangoConfig):
            indexnow = IndexNowConfig(
                key="865178f53dba1db23f3fc4fe95e9b64a",
                host="example.com",
                trailing_slash=True,
            )

            # One backend, several sites: each host takes its own sources.
            indexnow = IndexNowConfig(
                key="865178f53dba1db23f3fc4fe95e9b64a",
                trailing_slash=True,
                sites=[
                    IndexNowSite(host="caribbean.example", source_suffix="-caribbean"),
                    IndexNowSite(host="bali.example", source_suffix="-bali"),
                ],
            )
        ```
    """

    enabled: bool = Field(default=True, description="Submit at all. False keeps the config but sends nothing.")

    key: str = Field(..., description="8–128 chars of [A-Za-z0-9-]. Public: served at /<key>.txt.")

    host: Optional[str] = Field(
        default=None,
        description="One public host, without scheme: 'example.com'. Or use `sites` for several.",
    )

    sites: List[IndexNowSite] = Field(
        default_factory=list,
        description="Several public hosts served by this backend, each with its own sitemap sources.",
    )

    key_location: Optional[str] = Field(
        default=None,
        description="Where the engines fetch the key. Default https://<host>/<key>.txt.",
    )

    endpoint: str = Field(
        default="https://api.indexnow.org/indexnow",
        description="Submission endpoint. api.indexnow.org forwards to every engine.",
    )

    trailing_slash: bool = Field(
        default=False,
        description="Append '/' to each path, for sites whose canonical URLs end in one.",
    )

    sources: Optional[List[str]] = Field(
        default=None,
        description=(
            "Single-site only: sitemap source names to read. None means every enabled source. "
            "With `sites`, each site names its own."
        ),
    )

    extra_urls: Optional[str] = Field(
        default=None,
        description=(
            "Dotted path to `callable(since: datetime) -> list[str]`: URLs the sitemap never "
            "listed, sent once and not diffed. `since` is the host's last fully successful "
            "run, so a failed run loses nothing."
        ),
    )

    max_urls_per_run: int = Field(
        default=10_000,
        ge=1,
        description="Per host per run. The rest is found again by the next run.",
    )

    shrink_share: float = Field(
        default=0.2,
        gt=0,
        le=1,
        description=(
            "If more than this share of known URLs vanish in one run (and more than "
            "`shrink_floor`), the read is treated as degraded and nothing is sent."
        ),
    )

    shrink_floor: int = Field(default=50, ge=0, description="See `shrink_share`.")

    schedule_interval: int = Field(
        default=3600,
        ge=0,
        description="Seconds between scheduled runs (RQ). 0 disables the schedule; the command still works.",
    )

    timeout: float = Field(default=30.0, gt=0, description="Seconds per HTTP request.")

    @field_validator("key")
    @classmethod
    def _valid_key(cls, v: str) -> str:
        return _valid_key(v)

    @field_validator("host")
    @classmethod
    def _host(cls, v: Optional[str]) -> Optional[str]:
        return None if v is None else _bare_host(v)

    @model_validator(mode="after")
    def _one_shape(self) -> "IndexNowConfig":
        if bool(self.host) == bool(self.sites):
            raise ValueError("set exactly one of `host` (one site) or `sites` (several)")
        hosts = [s.host for s in self.sites]
        if len(hosts) != len(set(hosts)):
            raise ValueError("each host may appear in `sites` once")
        return self

    def resolved_sites(self) -> List[IndexNowSite]:
        """Every site, with the config's defaults filled in."""
        if self.host:
            return [IndexNowSite(
                host=self.host, sources=self.sources,
                key_location=self.key_location, trailing_slash=self.trailing_slash,
            )]
        return [
            s.model_copy(update={
                "trailing_slash": self.trailing_slash if s.trailing_slash is None else s.trailing_slash,
            })
            for s in self.sites
        ]

    def key_for(self, site: IndexNowSite) -> str:
        return site.key or self.key

    def all_keys(self) -> set[str]:
        """Every key a host may serve: the shared one and each site's own."""
        return {self.key, *(s.key for s in self.sites if s.key)}

    def key_location_for(self, site: IndexNowSite) -> str:
        return site.key_location or f"https://{site.host}/{self.key_for(site)}.txt"

    def resolved_key_location(self) -> str:
        """The single-site key location. With `sites`, use `key_location_for`."""
        return self.key_location_for(self.resolved_sites()[0])

    def get_rq_schedules(self) -> List["RQScheduleConfig"]:
        if not self.enabled or not self.schedule_interval:
            return []

        from django_cfg.models.django.django_rq import RQScheduleConfig

        return [
            RQScheduleConfig(
                func="django_cfg.modules.django_sitemap.indexnow.submit_changed",
                interval=self.schedule_interval,
                timeout=900,
                queue="default",
                description=f"Submit changed URLs to IndexNow (every {self.schedule_interval}s)",
            )
        ]


__all__ = ["IndexNowConfig", "IndexNowSite"]
