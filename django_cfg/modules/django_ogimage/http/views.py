"""Public OG image render view.

GET /og/<b64params>/

Flow:
  1. Decode base64 params
  2. Check sharded file cache (MEDIA_ROOT/ogimage/<key[:2]>/<key[2:4]>/<key>.png)
  3. On miss — render and save
  4. Serve FileResponse
"""
from __future__ import annotations

import base64
import json
import logging

from django.conf import settings
from django.http import FileResponse, HttpResponse, HttpResponseBadRequest
from django.views import View

from ..core.params import OGImageParams, compute_cache_key
from ..core.service import _cache_path, get_or_create_og_url
from ..cache._config import get_og_config

logger = logging.getLogger(__name__)


def _render_error_response(exc: Exception) -> HttpResponse:
    """500 for a render failure.

    Always logs the full traceback. The response body carries the real
    exception type+message only when DEBUG is on — in production it stays a
    neutral string so internals (paths, missing .so names) aren't leaked to
    crawlers, while ops still get the traceback from the logs.
    """
    logger.exception("OG image render failed")
    if settings.DEBUG:
        body = f"OG image render failed: {type(exc).__name__}: {exc}"
    else:
        body = "OG image render failed"
    return HttpResponse(body, status=500, content_type="text/plain; charset=utf-8")


class OGImageRenderView(View):
    """GET /cfg/og/<b64params>/"""

    def get(self, request, b64params: str):
        # 1. Decode
        try:
            padding = 4 - len(b64params) % 4
            raw = base64.urlsafe_b64decode(b64params + "=" * (padding % 4)).decode()
            data = json.loads(raw)
        except Exception:
            return HttpResponseBadRequest("Invalid params")

        try:
            params = OGImageParams(**data)
        except Exception as exc:
            return HttpResponseBadRequest(f"Invalid params: {exc}")

        # 2+3. Get or create (handles sharded cache internally)
        cfg = get_og_config()
        if not cfg.cache_enabled:
            # Force re-render by rendering directly
            from ..core.renderer import render
            try:
                png_bytes = render(params)
            except Exception as exc:
                return _render_error_response(exc)
            abs_path, _ = _cache_path(compute_cache_key(params))
            abs_path.parent.mkdir(parents=True, exist_ok=True)
            abs_path.write_bytes(png_bytes)
        else:
            try:
                get_or_create_og_url(params)
            except Exception as exc:
                return _render_error_response(exc)

        abs_path, _ = _cache_path(compute_cache_key(params))

        # 4. Serve
        response = FileResponse(open(abs_path, "rb"), content_type="image/png")
        response["Cache-Control"] = "public, max-age=86400, stale-while-revalidate=3600"
        return response
