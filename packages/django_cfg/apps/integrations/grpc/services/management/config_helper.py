"""
gRPC Config Helper.

Utility functions for accessing gRPC configuration from django-cfg.
Follows the same pattern as centrifugo and rq modules.
"""

from typing import Optional

from django_cfg.utils import get_logger

logger = get_logger("grpc.config")


def get_grpc_config() -> Optional["GRPCConfig"]:
    """
    Get gRPC configuration from django-cfg global state.

    Returns:
        GRPCConfig instance or None if not configured

    Example:
        >>> config = get_grpc_config()
        >>> if config and config.enabled:
        ...     print(config.server.port)
    """
    try:
        from django_cfg.core import get_current_config
        from django_cfg.models.api.grpc.config import GRPCConfig

        config = get_current_config()
        logger.info(f"get_grpc_config: get_current_config() = {type(config)}")

        if not config:
            logger.warning("get_grpc_config: config is None!")
            return None

        grpc_config = getattr(config, "grpc", None)
        logger.info(f"get_grpc_config: grpc_config = {type(grpc_config)}")

        # Type validation
        if grpc_config and isinstance(grpc_config, GRPCConfig):
            logger.info(f"get_grpc_config: handlers_hook = {grpc_config.handlers_hook}")
            return grpc_config

        logger.warning(f"get_grpc_config: grpc_config is not GRPCConfig type: {grpc_config}")
        return None

    except Exception as e:
        logger.error(f"Failed to get gRPC config: {e}", exc_info=True)
        return None


def get_grpc_config_or_default() -> "GRPCConfig":
    """
    Get gRPC configuration from django-cfg or return default.

    Returns:
        GRPCConfig instance (always)

    Example:
        >>> config = get_grpc_config_or_default()
        >>> print(config.server.port)  # Always works, fallback to default
    """
    config = get_grpc_config()

    if config:
        return config

    # Fallback to default config
    from django_cfg.models.api.grpc.config import GRPCConfig

    logger.warning("Django-CFG gRPC config not found, using default config")
    return GRPCConfig()


def is_grpc_enabled() -> bool:
    """
    Check if gRPC is enabled in django-cfg.

    Returns:
        True if gRPC is enabled, False otherwise

    Example:
        >>> if is_grpc_enabled():
        ...     # Start gRPC server
        ...     pass
    """
    config = get_grpc_config()
    return config.enabled if config else False


def get_grpc_server_config() -> Optional["GRPCServerConfig"]:
    """
    Get gRPC server configuration.

    Returns:
        GRPCServerConfig instance or None

    Example:
        >>> server_config = get_grpc_server_config()
        >>> if server_config and server_config.enabled:
        ...     print(f"Server on {server_config.host}:{server_config.port}")
    """
    config = get_grpc_config()
    return config.server if config else None


def get_grpc_auth_config() -> Optional["GRPCAuthConfig"]:
    """
    Get gRPC authentication configuration.

    Returns:
        GRPCAuthConfig instance or None

    Example:
        >>> auth_config = get_grpc_auth_config()
        >>> if auth_config and auth_config.enabled:
        ...     print("Auth is enabled")
    """
    config = get_grpc_config()
    return config.auth if config else None


def get_enabled_apps() -> list:
    """
    Get list of enabled Django-CFG apps for gRPC.

    Returns:
        List of app names

    Example:
        >>> apps = get_enabled_apps()
        >>> print(apps)  # ['accounts', 'support', 'knowbase']
    """
    config = get_grpc_config()
    if not config:
        return []

    if config.auto_register_apps:
        return config.enabled_apps
    return []


__all__ = [
    "get_grpc_config",
    "get_grpc_config_or_default",
    "is_grpc_enabled",
    "get_grpc_server_config",
    "get_grpc_auth_config",
    "get_enabled_apps",
]
