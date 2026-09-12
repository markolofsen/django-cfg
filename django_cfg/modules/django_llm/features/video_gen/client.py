"""Official OpenRouter asynchronous video generation transport."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable, Sequence
from decimal import Decimal
import time
from urllib.parse import quote, urljoin, urlsplit

import httpx
from pydantic import ValidationError

from ..._integration import BaseCfgModule, get_api_keys
from ...providers import PROVIDER_BASE_URLS
from .errors import (
    VideoGenerationFailedError,
    VideoGenerationHTTPError,
    VideoGenerationTimeoutError,
    VideoPricingUnavailableError,
    VideoTransportSecurityError,
)
from .models import (
    VideoGenEstimate,
    VideoGenJob,
    VideoGenRequest,
    VideoGenResult,
    VideoModelCapability,
)

_TERMINAL_FAILURES = {"failed", "cancelled", "expired"}

_RESOLUTION_SHORT_SIDE = {
    "480p": 480,
    "720p": 720,
    "1080p": 1080,
    "1K": 720,
    "2K": 1080,
    "4K": 2160,
}


class OpenRouterVideoGenClient(BaseCfgModule):
    """Provider-neutral async client for OpenRouter's ``/api/v1/videos`` API.

    Submission is deliberately a single HTTP request. The client never retries
    or resubmits a paid generation behind the caller's back.
    """

    def __init__(
        self,
        api_key: str | None = None,
        *,
        base_url: str = PROVIDER_BASE_URLS["openrouter"],
        timeout: float = 60.0,
        transport: httpx.AsyncBaseTransport | None = None,
        app_title: str = "django_cfg.modules.django_llm-video_gen",
        app_url: str = "https://cmdop.com/",
        max_download_bytes: int = 512 * 1024 * 1024,
        sleep: Callable[[float], Awaitable[None]] = asyncio.sleep,
        monotonic: Callable[[], float] = time.monotonic,
    ) -> None:
        super().__init__()
        resolved_key = api_key or get_api_keys().get("openrouter") or ""
        if not resolved_key:
            raise RuntimeError(
                "OpenRouter key missing — set OPENROUTER_API_KEY or "
                "CMDOP_LLM_KEYS__OPENROUTER"
            )
        self.api_key = resolved_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.transport = transport
        self.app_title = app_title
        self.app_url = app_url
        self.max_download_bytes = max_download_bytes
        self._sleep = sleep
        self._monotonic = monotonic
        self._base = urlsplit(self.base_url)
        if (
            self._base.scheme != "https"
            or not self._base.hostname
            or self._base.username
            or self._base.password
            or self._base.query
            or self._base.fragment
        ):
            raise ValueError("base_url must be a credential-free HTTPS URL")
        if timeout <= 0:
            raise ValueError("timeout must be positive")
        if max_download_bytes < 1:
            raise ValueError("max_download_bytes must be positive")

    @property
    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": self.app_url,
            "X-Title": self.app_title,
        }

    def _client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(
            timeout=self.timeout,
            transport=self.transport,
            follow_redirects=False,
        )

    @staticmethod
    def _raise_for_status(response: httpx.Response, *, operation: str) -> None:
        if response.is_success:
            return
        # Provider validation messages are essential for correcting a rejected
        # request without blind paid retries.  Keep the body bounded and on the
        # response side only; request headers/payloads may contain credentials
        # or private media URLs and are never included.
        detail = " ".join(response.text.strip().split())[:1000] or None
        raise VideoGenerationHTTPError(
            operation=operation,
            status_code=response.status_code,
            detail=detail,
        )

    async def list_models(self) -> list[VideoModelCapability]:
        """Fetch current video capabilities; no local stale pricing registry."""
        async with self._client() as client:
            response = await client.get(
                f"{self.base_url}/videos/models",
                headers=self._headers,
            )
        self._raise_for_status(response, operation="list models")
        payload = response.json()
        try:
            return [VideoModelCapability.model_validate(item) for item in payload["data"]]
        except (KeyError, TypeError, ValidationError) as exc:
            raise VideoGenerationHTTPError(
                operation="parse model list",
                status_code=response.status_code,
            ) from exc

    async def estimate(
        self,
        request: VideoGenRequest,
        *,
        capabilities: Sequence[VideoModelCapability] | None = None,
    ) -> VideoGenEstimate:
        """Estimate spend from the current model capability pricing response.

        Known ``per-video-second*`` SKUs are multiplied by duration. A
        ``generate*`` SKU is treated as one fixed generation. Unknown units are
        rejected rather than converted into a misleading estimate.
        """
        current = list(capabilities) if capabilities is not None else await self.list_models()
        capability = next((item for item in current if item.id == request.model), None)
        if capability is None:
            raise VideoPricingUnavailableError(
                f"video model {request.model!r} is absent from the live capability list"
            )
        problems = capability.incompatibilities(request)
        if problems:
            raise ValueError(
                f"video model {request.model!r} does not support: {', '.join(problems)}"
            )

        sku, quantity = self._select_pricing_sku(request, capability)
        unit_price = capability.pricing_skus[sku]
        return VideoGenEstimate(
            model_id=capability.id,
            cost_usd=unit_price * quantity,
            pricing_sku=sku,
            unit_price_usd=unit_price,
            quantity=quantity,
        )

    @staticmethod
    def _select_pricing_sku(
        request: VideoGenRequest,
        capability: VideoModelCapability,
    ) -> tuple[str, Decimal]:
        resolution = request.resolution
        audio = "audio" if request.generate_audio else "no-audio"
        candidates: list[str] = []
        official_audio = "with_audio" if request.generate_audio else "without_audio"
        if resolution:
            candidates.append(f"duration_seconds_{official_audio}_{resolution}")
        candidates.append(f"duration_seconds_{official_audio}")
        for prefix in ("per-video-second", "generate"):
            if resolution:
                candidates.extend(
                    [
                        f"{prefix}-{resolution}-{audio}",
                        f"{prefix}-{audio}-{resolution}",
                    ]
                )
            candidates.append(f"{prefix}-{audio}")
            if resolution:
                candidates.append(f"{prefix}-{resolution}")
            candidates.append(prefix)
        for sku in candidates:
            if sku not in capability.pricing_skus:
                continue
            if sku.startswith(("duration_seconds_", "per-video-second")):
                if request.duration is None:
                    raise VideoPricingUnavailableError(
                        "duration is required to estimate a per-video-second SKU"
                    )
                return sku, Decimal(request.duration)
            return sku, Decimal(1)
        token_sku = (
            "video_tokens"
            if request.generate_audio
            else "video_tokens_without_audio"
        )
        if token_sku in capability.pricing_skus:
            return token_sku, OpenRouterVideoGenClient._video_token_quantity(
                request,
                capability,
            )
        advertised = ", ".join(sorted(capability.pricing_skus)) or "none"
        raise VideoPricingUnavailableError(
            f"no understood pricing SKU for {request.model!r}; advertised: {advertised}"
        )

    @staticmethod
    def _video_token_quantity(
        request: VideoGenRequest,
        capability: VideoModelCapability,
    ) -> Decimal:
        """Calculate OpenRouter's published Seedance video-token quantity.

        Seedance defines one video token as 1024 pixel-frames at 24 fps.  We
        intentionally scope this formula to the ByteDance Seedance family;
        another token-priced family must publish and implement its own unit
        contract instead of silently inheriting this one.
        """
        if not request.model.startswith("bytedance/seedance-"):
            raise VideoPricingUnavailableError(
                f"video-token formula is unknown for {request.model!r}"
            )
        if request.duration is None:
            raise VideoPricingUnavailableError(
                "duration is required to estimate Seedance video tokens"
            )
        if request.size:
            width, height = (int(value) for value in request.size.split("x", 1))
        else:
            short_side = _RESOLUTION_SHORT_SIDE.get(request.resolution or "")
            if short_side is None or not request.aspect_ratio:
                raise VideoPricingUnavailableError(
                    "Seedance token pricing requires size or resolution plus aspect ratio"
                )
            ratio_width, ratio_height = (
                int(value) for value in request.aspect_ratio.split(":", 1)
            )
            matching_sizes: list[tuple[int, int]] = []
            for raw_size in capability.supported_sizes or []:
                candidate_width, candidate_height = (
                    int(value) for value in raw_size.split("x", 1)
                )
                if (
                    min(candidate_width, candidate_height) == short_side
                    and candidate_width * ratio_height
                    == candidate_height * ratio_width
                ):
                    matching_sizes.append((candidate_width, candidate_height))
            if len(matching_sizes) != 1:
                raise VideoPricingUnavailableError(
                    "cannot resolve one exact Seedance output size from live capabilities"
                )
            width, height = matching_sizes[0]
        return (
            Decimal(width)
            * Decimal(height)
            * Decimal(request.duration)
            * Decimal(24)
            / Decimal(1024)
        )

    async def submit(self, request: VideoGenRequest) -> VideoGenJob:
        """Submit exactly one paid generation request."""
        async with self._client() as client:
            response = await client.post(
                f"{self.base_url}/videos",
                headers=self._headers,
                json=request.to_api_payload(),
            )
        self._raise_for_status(response, operation="submit")
        payload = response.json()
        if not isinstance(payload, dict):
            raise VideoGenerationHTTPError(
                operation="parse submitted job", status_code=response.status_code,
            )
        # The documented envelope is the job itself. Some provider routes also
        # return it under ``data``; accepting that wrapper preserves the paid
        # job id instead of misclassifying submission as ambiguous.
        job_payload = payload.get("data", payload)
        if not isinstance(job_payload, dict):
            raise VideoGenerationHTTPError(
                operation="parse submitted job envelope", status_code=response.status_code,
            )
        try:
            return VideoGenJob.model_validate(job_payload)
        except ValidationError as exc:
            raise VideoGenerationHTTPError(
                operation=f"parse submitted job envelope: {sorted(job_payload)}",
                status_code=response.status_code,
            ) from exc

    def _poll_url(self, job: VideoGenJob) -> str:
        value = job.polling_url
        parsed = urlsplit(value)
        if parsed.scheme or parsed.netloc:
            url = value
        elif value.startswith("/"):
            url = urljoin(f"{self._base.scheme}://{self._base.netloc}", value)
        else:
            # A missing/invalid provider polling URL does not prevent a safe
            # same-origin lookup by the already validated job id.
            job_id = quote(job.id, safe="")
            url = f"{self.base_url}/videos/{job_id}"
        self._require_openrouter_url(url, operation="poll")
        return url

    def _require_openrouter_url(self, value: str, *, operation: str) -> None:
        parsed = urlsplit(value)
        if (
            parsed.scheme != "https"
            or parsed.netloc != self._base.netloc
            or parsed.username
            or parsed.password
            or parsed.fragment
        ):
            raise VideoTransportSecurityError(
                f"{operation} URL must use the configured OpenRouter HTTPS origin"
            )
        videos_prefix = f"{self._base.path.rstrip('/')}/videos/"
        if not parsed.path.startswith(videos_prefix):
            raise VideoTransportSecurityError(
                f"{operation} URL must stay inside the OpenRouter videos API"
            )

    async def _poll(
        self,
        job: VideoGenJob,
        *,
        request_timeout: float,
    ) -> VideoGenJob:
        url = self._poll_url(job)
        async with self._client() as client:
            response = await client.get(
                url,
                headers=self._headers,
                timeout=min(self.timeout, request_timeout),
            )
        self._raise_for_status(response, operation="poll")
        try:
            updated = VideoGenJob.model_validate(response.json())
        except ValidationError as exc:
            raise VideoGenerationHTTPError(
                operation="parse polled job",
                status_code=response.status_code,
            ) from exc
        if updated.id != job.id:
            raise VideoTransportSecurityError("polled job id does not match submitted job id")
        return updated

    async def poll(self, job: VideoGenJob) -> VideoGenJob:
        """Poll one existing job exactly once."""
        return await self._poll(job, request_timeout=self.timeout)

    async def wait(
        self,
        job: VideoGenJob,
        *,
        timeout_seconds: float = 900.0,
        poll_interval_seconds: float = 5.0,
    ) -> VideoGenResult:
        """Poll until terminal status, bounded by an explicit wall-clock deadline."""
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        if poll_interval_seconds <= 0:
            raise ValueError("poll_interval_seconds must be positive")
        deadline = self._monotonic() + timeout_seconds
        current = job
        while True:
            if current.status == "completed":
                return VideoGenResult.from_job(current)
            if current.status in _TERMINAL_FAILURES:
                raise VideoGenerationFailedError(
                    f"video job {current.id} ended with status {current.status}"
                )
            remaining = deadline - self._monotonic()
            if remaining <= 0:
                raise VideoGenerationTimeoutError(
                    f"video job {current.id} did not complete within {timeout_seconds:g}s"
                )
            current = await self._poll(current, request_timeout=remaining)
            if not current.terminal:
                remaining = deadline - self._monotonic()
                if remaining <= 0:
                    continue
                await self._sleep(min(poll_interval_seconds, remaining))

    async def download(
        self,
        result: VideoGenResult,
        *,
        index: int = 0,
    ) -> bytes:
        """Download one output; only same-origin requests receive API auth."""
        if index < 0 or index >= len(result.output_urls):
            raise IndexError("video output index is out of range")
        url = result.output_urls[index]
        parsed = urlsplit(url)
        if (
            parsed.scheme != "https"
            or not parsed.hostname
            or parsed.username
            or parsed.password
            or parsed.fragment
        ):
            raise VideoTransportSecurityError(
                "download URL must be credential-free HTTPS"
            )
        same_origin = parsed.netloc == self._base.netloc
        if same_origin:
            self._require_openrouter_url(url, operation="download")
            headers = self._headers
        else:
            # Provider-supplied unsigned HTTPS storage URLs must never receive
            # the caller's OpenRouter bearer token.
            headers = {"Accept": "video/*,application/octet-stream"}
        async with self._client() as client:
            response = await client.get(url, headers=headers)
        self._raise_for_status(response, operation="download")
        if len(response.content) > self.max_download_bytes:
            raise VideoGenerationHTTPError(
                operation="download size limit",
                status_code=response.status_code,
            )
        return response.content


__all__ = ["OpenRouterVideoGenClient"]
