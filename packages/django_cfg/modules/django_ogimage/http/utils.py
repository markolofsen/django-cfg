from __future__ import annotations

import base64
import json


def build_og_url(params, request=None) -> str:
    """Build a public /og/<b64params>/ URL for the given OGImageParams.

    Args:
        params: OGImageParams instance.
        request: Django HttpRequest — used to build absolute URI.
                 If None, returns a relative path.
    """
    data = params.cache_stable_dict()
    b64 = (
        base64.urlsafe_b64encode(
            json.dumps(data, separators=(",", ":")).encode()
        )
        .decode()
        .rstrip("=")
    )
    path = f"/og/{b64}/"
    if request is not None:
        return request.build_absolute_uri(path)
    return path
