"""
S3-compatible storage backend configuration.

One model covers every S3-compatible store; vendor differences live in the
`r2()` / `minio()` / `s3()` presets rather than in user configs. Requires
`pip install django-cfg[s3]` (django-storages + boto3).
"""

import os
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field, SecretStr, field_validator, model_validator

# Storage backend class provided by django-storages.
S3_BACKEND = "storages.backends.s3.S3Storage"


def _env(*names: str) -> Optional[str]:
    """First non-empty value among the given environment variables."""
    for name in names:
        value = os.environ.get(name)
        if value:
            return value
    return None


def _secret_from_env(*names: str) -> Optional[SecretStr]:
    value = _env(*names)
    return SecretStr(value) if value else None


class S3StorageConfig(BaseModel):
    """
    S3-compatible object storage for media files.

    Use a preset unless the store is plain AWS S3:

        storage = StorageConfig(backend=S3StorageConfig.r2(account_id="…", bucket_name="media"))
        storage = StorageConfig(backend=S3StorageConfig.minio(endpoint_url="…", bucket_name="media"))
        storage = StorageConfig(backend=S3StorageConfig(bucket_name="media", region_name="eu-west-1"))

    Credentials fall back to the environment, so they need not appear in code:
    `S3__ACCESS_KEY_ID` / `S3__SECRET_ACCESS_KEY`, and additionally `R2__*` for
    the R2 preset.
    """

    bucket_name: str = Field(
        description="Bucket that holds uploaded media",
    )

    endpoint_url: Optional[str] = Field(
        default=None,
        description="S3 API endpoint; None targets AWS S3",
    )

    access_key_id: Optional[SecretStr] = Field(
        default_factory=lambda: _secret_from_env("S3__ACCESS_KEY_ID"),
        description="Access key (env fallback: S3__ACCESS_KEY_ID)",
    )

    secret_access_key: Optional[SecretStr] = Field(
        default_factory=lambda: _secret_from_env("S3__SECRET_ACCESS_KEY"),
        description="Secret key (env fallback: S3__SECRET_ACCESS_KEY)",
    )

    region_name: str = Field(
        default="us-east-1",
        description="Region; 'auto' for R2",
    )

    signature_version: str = Field(
        default="s3v4",
        description="SigV4 everywhere; SigV2 is unsupported by most stores",
    )

    addressing_style: str = Field(
        default="virtual",
        description="'virtual' (bucket.host) or 'path' (host/bucket, needed by MinIO)",
    )

    custom_domain: Optional[str] = Field(
        default=None,
        description="Public host serving the bucket (CDN or R2 custom domain), no scheme",
    )

    default_acl: Optional[str] = Field(
        default=None,
        description="Object ACL; must stay None on stores without ACL support (R2)",
    )

    querystring_auth: bool = Field(
        default=False,
        description="Sign media URLs. False suits a public bucket behind a CDN",
    )

    file_overwrite: bool = Field(
        default=False,
        description="Overwrite on name collision instead of suffixing",
    )

    location: str = Field(
        default="",
        description="Key prefix inside the bucket (e.g. 'media')",
    )

    # Sharing one bucket across environments is a data-loss risk, not just
    # untidiness: cleanup signals call storage.delete(), so a dev run that
    # clears test rows deletes the production objects behind the same keys.
    # A separate bucket per environment is safer; when that is not possible,
    # this prefixes every key so the environments cannot collide.
    environment: Optional[str] = Field(
        default=None,
        description="Environment segment prepended to location (e.g. 'prod', 'dev')",
    )

    object_parameters: Dict[str, str] = Field(
        default_factory=dict,
        description="Extra S3 object headers, e.g. {'CacheControl': 'max-age=86400'}",
    )

    serve_static: bool = Field(
        default=False,
        description="Also serve collected static files. Off by default: static stays on WhiteNoise",
    )

    # Checksum behavior. Recent botocore sends CRC32 by default, which R2
    # rejects with 501 Not Implemented; presets that need it set "when_required".
    request_checksum_calculation: Optional[str] = Field(
        default=None,
        description="botocore checksum mode: 'when_supported' or 'when_required'",
    )

    response_checksum_validation: Optional[str] = Field(
        default=None,
        description="botocore response checksum validation mode",
    )

    @field_validator("custom_domain")
    @classmethod
    def _validate_custom_domain(cls, v: Optional[str]) -> Optional[str]:
        """A scheme or trailing slash here produces subtly broken URLs."""
        if v is None:
            return v
        if "://" in v:
            raise ValueError(
                f"custom_domain must not include a scheme: {v!r}. "
                f"Use {v.split('://', 1)[1]!r}."
            )
        if v.endswith("/"):
            raise ValueError(f"custom_domain must not end with '/': {v!r}")
        return v

    @field_validator("addressing_style")
    @classmethod
    def _validate_addressing_style(cls, v: str) -> str:
        if v not in {"virtual", "path"}:
            raise ValueError(f"addressing_style must be 'virtual' or 'path', got {v!r}")
        return v

    @field_validator("location")
    @classmethod
    def _normalize_location(cls, v: str) -> str:
        return v.strip("/")

    @field_validator("environment")
    @classmethod
    def _normalize_environment(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        v = v.strip("/")
        if not v:
            raise ValueError(
                "environment must be a non-empty segment (e.g. 'prod', 'dev') "
                "or None; an empty value would silently share the prefix."
            )
        return v

    @model_validator(mode="after")
    def _validate_credentials(self) -> "S3StorageConfig":
        """Half-configured credentials fail at upload time, not at startup."""
        has_key = self.access_key_id is not None
        has_secret = self.secret_access_key is not None
        if has_key != has_secret:
            missing = "secret_access_key" if has_key else "access_key_id"
            raise ValueError(
                f"S3StorageConfig is missing {missing}. Provide both credentials "
                f"or neither (to use the ambient AWS credential chain)."
            )
        return self

    # --- Presets ------------------------------------------------------------

    @classmethod
    def r2(
        cls,
        *,
        account_id: str,
        bucket_name: str,
        endpoint_url: Optional[str] = None,
        **kwargs: Any,
    ) -> "S3StorageConfig":
        """
        Cloudflare R2.

        Applies what R2 requires and rejects what it does not implement:
        `region_name="auto"`, SigV4, no ACLs, and checksums only when required
        (botocore's default CRC32 makes R2 answer 501 Not Implemented).
        """
        if kwargs.get("default_acl") is not None:
            raise ValueError(
                "Cloudflare R2 does not support ACLs; leave default_acl unset "
                "and control access in the Cloudflare dashboard."
            )

        kwargs.setdefault("access_key_id", _secret_from_env("R2__ACCESS_KEY_ID", "S3__ACCESS_KEY_ID"))
        kwargs.setdefault("secret_access_key", _secret_from_env("R2__SECRET_ACCESS_KEY", "S3__SECRET_ACCESS_KEY"))

        return cls(
            bucket_name=bucket_name,
            endpoint_url=endpoint_url or f"https://{account_id}.r2.cloudflarestorage.com",
            region_name="auto",
            signature_version="s3v4",
            addressing_style="virtual",
            default_acl=None,
            request_checksum_calculation="when_required",
            response_checksum_validation="when_required",
            **kwargs,
        )

    @classmethod
    def minio(
        cls,
        *,
        endpoint_url: str,
        bucket_name: str,
        **kwargs: Any,
    ) -> "S3StorageConfig":
        """MinIO. Path-style addressing; virtual-host style needs wildcard DNS."""
        kwargs.setdefault("region_name", "us-east-1")
        return cls(
            bucket_name=bucket_name,
            endpoint_url=endpoint_url,
            addressing_style="path",
            signature_version="s3v4",
            **kwargs,
        )

    @classmethod
    def s3(cls, *, bucket_name: str, region_name: str, **kwargs: Any) -> "S3StorageConfig":
        """Amazon S3."""
        return cls(bucket_name=bucket_name, region_name=region_name, **kwargs)

    # --- Settings emission --------------------------------------------------

    def storage_options(self) -> Dict[str, Any]:
        """OPTIONS for the django-storages S3 backend."""
        options: Dict[str, Any] = {
            "bucket_name": self.bucket_name,
            "region_name": self.region_name,
            "signature_version": self.signature_version,
            "addressing_style": self.addressing_style,
            "querystring_auth": self.querystring_auth,
            "file_overwrite": self.file_overwrite,
        }

        if self.endpoint_url:
            options["endpoint_url"] = self.endpoint_url
        if self.access_key_id:
            options["access_key"] = self.access_key_id.get_secret_value()
        if self.secret_access_key:
            options["secret_key"] = self.secret_access_key.get_secret_value()
        if self.custom_domain:
            options["custom_domain"] = self.custom_domain
        if self.default_acl:
            options["default_acl"] = self.default_acl
        if self.key_prefix:
            options["location"] = self.key_prefix
        if self.object_parameters:
            options["object_parameters"] = dict(self.object_parameters)

        return options

    def checksum_params(self) -> Dict[str, str]:
        """Checksum overrides for `botocore.config.Config`; empty when none apply."""
        params: Dict[str, str] = {}
        if self.request_checksum_calculation:
            params["request_checksum_calculation"] = self.request_checksum_calculation
        if self.response_checksum_validation:
            params["response_checksum_validation"] = self.response_checksum_validation
        return params

    def client_config(self) -> Optional[Any]:
        """
        `botocore.config.Config` carrying the checksum overrides, when needed.

        Imports botocore lazily, so building or inspecting a config never
        requires the extra — only generating live settings does. Returns None
        when no override applies, leaving botocore's defaults alone.
        """
        params = self.checksum_params()
        if not params:
            return None

        from botocore.config import Config  # noqa: PLC0415 — optional extra

        return Config(**params)

    @property
    def key_prefix(self) -> str:
        """
        Effective key prefix: `environment` before `location`.

        Both `storage_options()` and `media_url()` read this, so the stored
        objects and the URLs that serve them cannot disagree.
        """
        return "/".join(p for p in (self.environment, self.location) if p)

    @property
    def static_key_prefix(self) -> str:
        """Key prefix for collected static files, environment included."""
        return "/".join(p for p in (self.environment, "static") if p)

    def media_url(self) -> Optional[str]:
        """Public MEDIA_URL when a custom domain is set; None keeps the default."""
        if not self.custom_domain:
            return None
        prefix = self.key_prefix
        path = f"/{prefix}/" if prefix else "/"
        return f"https://{self.custom_domain}{path}"

    def check_dependencies(self) -> None:
        """Fail loudly when the extra is missing, rather than writing to local disk."""
        try:
            import storages  # noqa: F401
            import boto3  # noqa: F401
        except ImportError as exc:
            from django.core.exceptions import ImproperlyConfigured

            raise ImproperlyConfigured(
                "S3StorageConfig requires django-storages and boto3. "
                "Install them with: pip install django-cfg[s3]"
            ) from exc


__all__ = ["S3StorageConfig", "S3_BACKEND"]
