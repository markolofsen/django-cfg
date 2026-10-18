"""One POST to the IndexNow endpoint, its log row, and `submit()` for request paths."""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Iterable

from . import IndexNowError
from .urls import by_host

if TYPE_CHECKING:
    from django_cfg.models.django.indexnow import IndexNowConfig, IndexNowSite

logger = logging.getLogger(__name__)

#: The protocol's cap per POST.
MAX_URLS_PER_REQUEST = 10_000

#: Statuses the protocol defines as "received". Anything else is a refusal.
ACCEPTED = (200, 202)

#: What a refusal means, for the log line a person reads at 3 a.m.
REFUSALS = {
    400: "bad request: malformed payload",
    403: "key not valid: the key file is not served at keyLocation, or does not hold the key",
    422: "URLs do not belong to the host, or the key does not match the host",
    429: "too many requests: back off",
}


@dataclass
class SubmitResult:
    sent: int = 0
    accepted: int = 0
    statuses: list[int] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors


def batches(urls: list[str]) -> Iterable[list[str]]:
    for i in range(0, len(urls), MAX_URLS_PER_REQUEST):
        yield urls[i : i + MAX_URLS_PER_REQUEST]


def open_client(config: "IndexNowConfig", client=None):
    """(client, owned). A passed client is the caller's to close."""
    if client is not None:
        return client, False
    import httpx

    return httpx.Client(timeout=config.timeout), True


def post(client, config: "IndexNowConfig", site: "IndexNowSite", batch: list[str]) -> tuple[int | None, str | None]:
    """POST one batch and log it. Returns (status, error); error is None when accepted."""
    import httpx

    from ..models import IndexNowSubmission

    key_location = config.key_location_for(site)
    status, excerpt, error = None, "", None
    try:
        res = client.post(config.endpoint, json={
            "host": site.host,
            "key": config.key_for(site),
            "keyLocation": key_location,
            "urlList": batch,
        })
        status, excerpt = res.status_code, (res.text or "")[:500]
        if status not in ACCEPTED:
            error = f"{site.host}: HTTP {status} ({REFUSALS.get(status, 'unexpected status')}): {excerpt[:200]}"
    except httpx.HTTPError as exc:
        # `str()` of an httpx error is often empty; name the type.
        error = f"{site.host}: {type(exc).__name__}: {exc!s}" if str(exc) else f"{site.host}: {type(exc).__name__}"
        excerpt = error[:500]

    try:
        IndexNowSubmission.objects.create(
            host=site.host, url_count=len(batch), http_status=status,
            response_excerpt=excerpt, sample_urls=batch[:5],
        )
    except Exception:
        # The log must not turn an accepted batch into a failed run.
        logger.exception("indexnow: could not log a submission for %s", site.host)
    if error:
        logger.warning("indexnow: batch of %d refused: %s", len(batch), error,
                       extra={"host": site.host, "key_location": key_location})
    return status, error


def submit(
    urls: Iterable[str],
    *,
    config: "IndexNowConfig | None" = None,
    raise_errors: bool = False,
    client=None,
) -> SubmitResult:
    """POST the URLs now, one request per host.

    For request paths: never raises unless asked, and not diffed — a URL the
    next run also sends costs one recrawl.
    """
    from . import get_config

    config = config or get_config()
    result = SubmitResult()
    urls = list(dict.fromkeys(urls))
    if config is None or not urls:
        return result

    sites = {site.host: site for site in config.resolved_sites()}
    client, owned = open_client(config, client)
    try:
        for host, host_urls in by_host(urls).items():
            site = sites.get(host)
            if site is None:
                message = f"{len(host_urls)} URL(s) on {host or '(no host)'}, which is not a configured site"
                result.errors.append(message)
                logger.warning("indexnow: %s", message)
                continue
            for batch in batches(host_urls):
                result.sent += len(batch)
                status, error = post(client, config, site, batch)
                if status is not None:
                    result.statuses.append(status)
                if error:
                    result.errors.append(error)
                else:
                    result.accepted += len(batch)
    finally:
        if owned:
            client.close()

    if raise_errors and result.errors:
        raise IndexNowError(f"{len(result.errors)} batch(es) failed: {result.errors[0]}")
    return result
