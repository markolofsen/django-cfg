"""OpenAPI: API keys and the generated-client groups.

Split out of ``api/settings/config.py``.
"""

from __future__ import annotations

from django_cfg import ApiKeys, OpenAPIClientConfig, OpenAPIGroupConfig

from api.environment import env


def build_api_keys() -> ApiKeys:
    return ApiKeys(
        openai=env.api_keys.openai,
        openrouter=env.api_keys.openrouter,
    )


def build_openapi_client_config() -> OpenAPIClientConfig:
    """Which apps land in which generated client package."""
    return OpenAPIClientConfig(
        enabled=True,
        generate_package_files=True,
        generate_zod_schemas=True,
        generate_fetchers=True,
        generate_swr_hooks=True,
        api_prefix="apix",
        output_dir="openapi",
        drf_title=f"{env.app.name} API",
        drf_description="Complete API documentation for Django CFG Demo Project",
        drf_version="1.0.0",
        groups=[
            OpenAPIGroupConfig(name="profiles", apps=["apps.profiles"], title="Profiles API", description="User profiles management", version="1.0.0"),
            OpenAPIGroupConfig(name="trading", apps=["apps.trading"], title="Trading API", description="Trading operations management", version="1.0.0"),
            OpenAPIGroupConfig(name="crypto", apps=["apps.crypto"], title="Crypto API", description="Crypto operations management", version="1.0.0"),
        ],
    )
