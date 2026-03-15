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

from django.http import FileResponse, HttpResponseBadRequest
from django.views import View

from ..core.params import OGImageParams
from ..core.service import _cache_path, get_or_create_og_url
from ..cache._config import get_og_config

logger = logging.getLogger(__name__)


class OGImageRenderView(View):
    """GET /og/<b64params>/"""

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
            from ..core.params import compute_cache_key
            try:
                png_bytes = render(params)
            except Exception as exc:
                logger.error("OG image render failed: %s", exc)
                from django.http import HttpResponse
                return HttpResponse("Render failed", status=500)
            cache_key = compute_cache_key(params)
            abs_path, _ = _cache_path(cache_key)
            abs_path.parent.mkdir(parents=True, exist_ok=True)
            abs_path.write_bytes(png_bytes)
        else:
            try:
                get_or_create_og_url(params)
            except Exception as exc:
                logger.error("OG image generation failed: %s", exc)
                from django.http import HttpResponse
                return HttpResponse("Render failed", status=500)

        from ..core.params import compute_cache_key
        abs_path, _ = _cache_path(compute_cache_key(params))

        # 4. Serve
        response = FileResponse(open(abs_path, "rb"), content_type="image/png")
        response["Cache-Control"] = "public, max-age=86400, stale-while-revalidate=3600"
        return response
