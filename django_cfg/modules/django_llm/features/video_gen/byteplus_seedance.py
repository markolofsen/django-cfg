"""Direct BytePlus ModelArk transport for Dreamina Seedance 2.0 series."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from decimal import Decimal
import os
import time
from urllib.parse import quote, urlsplit

import httpx
from pydantic import ValidationError

from ..._integration import BaseCfgModule
from .errors import (
    VideoGenerationFailedError,
    VideoGenerationHTTPError,
    VideoGenerationTimeoutError,
    VideoTransportSecurityError,
)
from .seedance_models import (
    MediaReference,
    SeedanceGenerationRequest,
    SeedanceJob,
    SeedanceResult,
    SeedanceUsage,
)

BYTEPLUS_MODELARK_BASE_URL = "https://ark.ap-southeast.bytepluses.com/api/v3"
_TERMINAL_FAILURES = {"failed", "cancelled", "expired"}


def compile_byteplus_seedance_request(
    request: SeedanceGenerationRequest,
) -> dict[str, object]:
    """Compile the portable contract to the official ordered BytePlus body."""
    content: list[dict[str, object]] = [
        {"type": "text", "text": _compile_prompt(request)}
    ]
    content.extend(_compile_reference(reference) for reference in request.references)
    payload: dict[str, object] = {
        "model": request.model.provider_model_id,
        "content": content,
        "resolution": request.output.resolution,
        "ratio": request.output.ratio,
        "duration": request.output.duration_seconds,
        "generate_audio": request.output.generate_audio,
        "watermark": request.output.watermark,
        "return_last_frame": request.output.return_last_frame,
    }
    if request.safety_identifier is not None:
        payload["safety_identifier"] = request.safety_identifier
    return payload


def _compile_prompt(request: SeedanceGenerationRequest) -> str:
    """Preserve portable roles in the only provider channel that understands them."""
    counters = {"image": 0, "video": 0, "audio": 0}
    labels: list[str] = []
    for reference in request.references:
        counters[reference.kind] += 1
        ordinal = counters[reference.kind]
        provider_label = f"{reference.kind.title()} {ordinal}"
        semantic_role = reference.role.replace("_", " ")
        labels.append(f"{provider_label} = {semantic_role}")
    if not labels:
        return request.prompt
    return f"Reference roles: {'; '.join(labels)}.\n\n{request.prompt}"


def _compile_reference(reference: MediaReference) -> dict[str, object]:
    wire_role = {
        "image": (
            reference.role
            if reference.role in {"first_frame", "last_frame"}
            else "reference_image"
        ),
        "video": "reference_video",
        "audio": "reference_audio",
    }[reference.kind]
    wire_key = f"{reference.kind}_url"
    return {
        "type": wire_key,
        wire_key: {"url": reference.source},
        "role": wire_role,
    }


class BytePlusSeedanceClient(BaseCfgModule):
    """Single-submit asynchronous Seedance client with bounded polling.

    The transport never retries, resubmits, or falls back to another model. A
    caller that wants another candidate must create another explicit request.
    """

    def __init__(
        self,
        api_key: str | None = None,
        *,
        base_url: str = BYTEPLUS_MODELARK_BASE_URL,
        timeout: float = 60.0,
        transport: httpx.AsyncBaseTransport | None = None,
        max_download_bytes: int = 1024 * 1024 * 1024,
        usd_per_k_completion_tokens: Decimal | None = None,
        sleep: Callable[[float], Awaitable[None]] = asyncio.sleep,
        monotonic: Callable[[], float] = time.monotonic,
    ) -> None:
        super().__init__()
        resolved_key = (
            api_key or os.getenv("BYTEPLUS_API_KEY") or os.getenv("ARK_API_KEY")
        )
        if not resolved_key:
            raise RuntimeError(
                "BytePlus key missing — set BYTEPLUS_API_KEY/ARK_API_KEY or pass api_key"
            )
        self.api_key = resolved_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.transport = transport
        self.max_download_bytes = max_download_bytes
        self.usd_per_k_completion_tokens = usd_per_k_completion_tokens
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
        if usd_per_k_completion_tokens is not None and usd_per_k_completion_tokens < 0:
            raise ValueError("usd_per_k_completion_tokens cannot be negative")

    @property
    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
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
        raise VideoGenerationHTTPError(
            operation=operation,
            status_code=response.status_code,
            provider="BytePlus",
        )

    @staticmethod
    def _response_object(
        response: httpx.Response,
        *,
        operation: str,
    ) -> dict[str, object]:
        try:
            payload = response.json()
        except ValueError as exc:
            raise VideoGenerationHTTPError(
                operation=operation,
                status_code=response.status_code,
                provider="BytePlus",
            ) from exc
        if not isinstance(payload, dict):
            raise VideoGenerationHTTPError(
                operation=operation,
                status_code=response.status_code,
                provider="BytePlus",
            )
        return payload

    @property
    def _tasks_url(self) -> str:
        return f"{self.base_url}/contents/generations/tasks"

    async def submit(self, request: SeedanceGenerationRequest) -> SeedanceJob:
        """Submit exactly one paid generation request."""
        async with self._client() as client:
            response = await client.post(
                self._tasks_url,
                headers=self._headers,
                json=compile_byteplus_seedance_request(request),
            )
        self._raise_for_status(response, operation="submit")
        payload = self._response_object(response, operation="parse submitted task")
        if not isinstance(payload.get("id"), str):
            raise VideoGenerationHTTPError(
                operation="parse submitted task",
                status_code=response.status_code,
                provider="BytePlus",
            )
        return SeedanceJob(id=payload["id"], status="queued", raw=payload)

    async def _poll(
        self,
        job: SeedanceJob,
        *,
        request_timeout: float,
    ) -> SeedanceJob:
        url = f"{self._tasks_url}/{quote(job.id, safe='')}"
        async with self._client() as client:
            response = await client.get(
                url,
                headers=self._headers,
                timeout=min(self.timeout, request_timeout),
            )
        self._raise_for_status(response, operation="poll")
        payload = self._response_object(response, operation="parse polled task")
        updated = self._parse_job(payload, status_code=response.status_code)
        if updated.id != job.id:
            raise VideoTransportSecurityError(
                "polled BytePlus task id does not match submitted task id"
            )
        return updated

    async def poll(self, job: SeedanceJob) -> SeedanceJob:
        """Retrieve one existing task exactly once."""
        return await self._poll(job, request_timeout=self.timeout)

    @staticmethod
    def _parse_job(payload: dict[str, object], *, status_code: int) -> SeedanceJob:
        content = payload.get("content")
        content_payload = content if isinstance(content, dict) else {}
        usage = payload.get("usage")
        usage_payload = usage if isinstance(usage, dict) else None
        error = payload.get("error")
        try:
            return SeedanceJob(
                id=payload["id"],
                status=payload["status"],
                provider_reported_model_id=payload.get("model"),
                video_url=content_payload.get("video_url"),
                last_frame_url=content_payload.get("last_frame_url"),
                usage=SeedanceUsage.model_validate(usage_payload)
                if usage_payload
                else None,
                error=error if isinstance(error, dict) else None,
                raw=payload,
            )
        except (KeyError, ValidationError) as exc:
            raise VideoGenerationHTTPError(
                operation="parse polled task",
                status_code=status_code,
                provider="BytePlus",
            ) from exc

    async def wait(
        self,
        job: SeedanceJob,
        *,
        request: SeedanceGenerationRequest,
        timeout_seconds: float = 900.0,
        poll_interval_seconds: float = 5.0,
    ) -> SeedanceResult:
        """Wait for terminal state within an explicit wall-clock deadline."""
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        if poll_interval_seconds <= 0:
            raise ValueError("poll_interval_seconds must be positive")
        deadline = self._monotonic() + timeout_seconds
        current = job
        while True:
            if current.status == "succeeded":
                return self._result(current, request=request)
            if current.status in _TERMINAL_FAILURES:
                raise VideoGenerationFailedError(
                    f"Seedance task {current.id} ended with status {current.status}: "
                    f"{current.error or 'no provider error'}"
                )
            remaining = deadline - self._monotonic()
            if remaining <= 0:
                raise VideoGenerationTimeoutError(
                    f"Seedance task {current.id} did not complete within "
                    f"{timeout_seconds:g}s"
                )
            current = await self._poll(current, request_timeout=remaining)
            if not current.terminal:
                remaining = deadline - self._monotonic()
                if remaining <= 0:
                    continue
                await self._sleep(min(poll_interval_seconds, remaining))

    def _result(
        self,
        job: SeedanceJob,
        *,
        request: SeedanceGenerationRequest,
    ) -> SeedanceResult:
        if job.video_url is None:
            raise VideoGenerationHTTPError(
                operation="parse completed task without video_url",
                status_code=200,
                provider="BytePlus",
            )
        completion_tokens = job.usage.completion_tokens if job.usage else None
        total_tokens = job.usage.total_tokens if job.usage else None
        cost_usd: Decimal | None = None
        cost_source = None
        if (
            completion_tokens is not None
            and self.usd_per_k_completion_tokens is not None
        ):
            cost_usd = (
                Decimal(completion_tokens)
                / Decimal(1000)
                * self.usd_per_k_completion_tokens
            )
            cost_source = "caller-supplied-token-rate"
        return SeedanceResult(
            job_id=job.id,
            canonical_model_family=request.model.family,
            provider_model_id=request.model.provider_model_id,
            provider_model_alias=request.model.provider_alias,
            provider_reported_model_id=job.provider_reported_model_id,
            video_url=job.video_url,
            last_frame_url=job.last_frame_url,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            cost_usd=cost_usd,
            cost_source=cost_source,
        )

    async def download(self, url: str) -> bytes:
        """Download an expiring result URL without leaking provider auth."""
        parsed = urlsplit(url)
        if (
            parsed.scheme != "https"
            or not parsed.hostname
            or parsed.username
            or parsed.password
            or parsed.fragment
        ):
            raise VideoTransportSecurityError(
                "Seedance download URL must be credential-free HTTPS"
            )
        headers: dict[str, str]
        if parsed.netloc == self._base.netloc:
            tasks_path = f"{self._base.path.rstrip('/')}/contents/generations/tasks/"
            if not parsed.path.startswith(tasks_path):
                raise VideoTransportSecurityError(
                    "same-origin download must stay inside the BytePlus tasks API"
                )
            headers = self._headers
        else:
            headers = {"Accept": "video/*,image/*,application/octet-stream"}
        async with self._client() as client:
            response = await client.get(url, headers=headers)
        self._raise_for_status(response, operation="download")
        if len(response.content) > self.max_download_bytes:
            raise VideoGenerationHTTPError(
                operation="download size limit",
                status_code=response.status_code,
                provider="BytePlus",
            )
        return response.content


__all__ = [
    "BYTEPLUS_MODELARK_BASE_URL",
    "BytePlusSeedanceClient",
    "compile_byteplus_seedance_request",
]
