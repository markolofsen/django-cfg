"""
Register the media types Python's table is missing.

`mimetypes.guess_type("photo.webp")` returns `(None, None)` in a slim
container: Alpine and the slim Debian images ship no `/etc/mime.types`, and
Python's built-in fallback table — 152 entries — predates webp. Everything
downstream that asks Python what a file is then gets no answer.

WHAT THAT COST: django-storages sets an S3 object's Content-Type from
`mimetypes`, so every `.webp` reached Cloudflare R2 as
`application/octet-stream`. Next's image optimiser reads the stored header,
refuses a non-image type, and the refusal takes the React streaming response
down with it — 331 truncated pages in two hours on carapis.com, surfacing in
the browser as `Cannot read properties of null` inside React's `$RS`. The
bucket held 3,090,803 photographs, every one of them mislabelled.

It is registered here rather than in the storage backend because `mimetypes`
is a process-global table and several callers read it — `django_llm`'s media
router guesses an upload's type the same way.

Registered `strict=True`, which is the only setting that works: `strict=False`
files a type under `common_types`, and `guess_type` does NOT read that table
unless the CALLER passes `strict=False` — django-storages does not. A test
written against `strict=False` passed on a developer Mac, where the system
mime database already knows webp, and would have changed nothing in the
container this exists for.

The guard below keeps a host that DOES ship a real database on its own answer.
"""

import mimetypes

# Only formats Python may not know AND that we store or serve. Each is the
# IANA-registered type.
MISSING_TYPES: dict[str, str] = {
    ".webp": "image/webp",
    ".avif": "image/avif",
    ".woff2": "font/woff2",
    ".woff": "font/woff",
}


def register_media_types() -> None:
    """Teach `mimetypes` the types a slim image leaves out. Idempotent."""
    for suffix, media_type in MISSING_TYPES.items():
        if mimetypes.guess_type(f"x{suffix}")[0] is None:
            # strict=True: the default `guess_type` call reads only this
            # table. See the module docstring.
            mimetypes.add_type(media_type, suffix, strict=True)
