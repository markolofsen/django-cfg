"""Real-time and infra integrations: Centrifugo, gRPC, ngrok, Cloudflare D1.

Split out of ``api/settings/config.py`` — grouped together because each is a
self-contained "is this feature on, and how is it reached" declaration.
"""

from __future__ import annotations

from typing import Optional

from django_cfg import (
    CloudflareConfig,
    DjangoCfgCentrifugoConfig,
    DjangoGrpcModuleConfig,
    GrpcObservabilityConfig,
    GrpcServerConfig,
    GrpcTelegramNotifyConfig,
    NgrokConfig,
)

from api.environment import env


def build_centrifugo_config() -> Optional[DjangoCfgCentrifugoConfig]:
    if not env.centrifugo.enabled:
        return None
    return DjangoCfgCentrifugoConfig(
        enabled=env.centrifugo.enabled,
        wrapper_url=env.centrifugo.wrapper_url,
        wrapper_api_key=env.centrifugo.wrapper_api_key,
        centrifugo_url=env.centrifugo.centrifugo_url,
        centrifugo_api_url=env.centrifugo.centrifugo_api_url,
        centrifugo_api_key=env.centrifugo.centrifugo_api_key,
        centrifugo_token_hmac_secret=env.centrifugo.centrifugo_token_hmac_secret,
        ack_timeout=env.centrifugo.default_ack_timeout,
        log_level=env.centrifugo.log_level,
        log_all_calls=env.centrifugo.log_all_calls,
        log_only_with_ack=env.centrifugo.log_only_with_ack,
    )


def build_grpc_module_config() -> Optional[DjangoGrpcModuleConfig]:
    return DjangoGrpcModuleConfig(
        enabled=True,
        server=GrpcServerConfig(host="0.0.0.0", port=50051),
        enabled_apps=[],
        package_prefix="api",
        public_url=env.grpc_url,
        observability=GrpcObservabilityConfig(telegram=GrpcTelegramNotifyConfig(enabled=True)),
        handlers_hook=[
            # "apps.*.grpc.services.handlers.grpc_handlers",
        ],
    )


def build_ngrok_config() -> Optional[NgrokConfig]:
    if not env.debug:
        return None
    return NgrokConfig(enabled=True, compression=True)


def build_cloudflare_config() -> Optional[CloudflareConfig]:
    return CloudflareConfig(
        enabled=bool(env.cloudflare.account_id),
        account_id=env.cloudflare.account_id,
        api_token=env.cloudflare.api_token,
        d1_database_id=env.cloudflare.d1_database_id,
        telegram_alerts_enabled=bool(env.telegram.bot_token),
    )
