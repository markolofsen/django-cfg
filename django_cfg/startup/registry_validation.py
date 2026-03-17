"""
django_cfg.startup.registry_validation — Validate DJANGO_CFG_REGISTRY at startup.

Iterates all registry entries, attempts importlib.import_module + getattr for each.
Optional-dependency entries that fail because their package isn't installed are
logged at DEBUG level only. Required entries that fail are logged as ERROR.

The lazy-import mechanism (__getattr__ in django_cfg/__init__.py) is NOT touched —
this is a read-only validation pass that surfaces broken entries at startup rather
than deferring failures until first use in production.
"""

import importlib
import logging

logger = logging.getLogger("django_cfg.registry")

# Module path prefixes for explicitly optional dependencies.
# ImportError from these is expected when the feature is not installed.
_OPTIONAL_PREFIXES = (
    "django_cfg.modules.django_grpc",
    "django_cfg.modules.django_centrifugo",
    "django_cfg.modules.django_ngrok",
    "django_cfg.modules.django_import_export",
    "django_cfg.modules.django_unfold",
    "django_cfg.modules.streamlit_admin",
    "django_cfg.modules.django_cf",
    "django_cfg.models.api.grpc",  # old flat gRPC API — optional same as grpc module
)


def validate_registry() -> None:
    """
    Validate all DJANGO_CFG_REGISTRY entries are importable.

    Safe to call multiple times (idempotent).
    Designed to be called from AppConfig.ready().
    """
    try:
        from django_cfg.registry import DJANGO_CFG_REGISTRY
    except Exception as exc:
        logger.error("Failed to import DJANGO_CFG_REGISTRY: %s", exc)
        return

    broken: list[str] = []
    for symbol, (module_path, attr_name) in DJANGO_CFG_REGISTRY.items():
        try:
            mod = importlib.import_module(module_path)
            if not hasattr(mod, attr_name):
                logger.error(
                    "Registry entry '%s': module '%s' has no attribute '%s'",
                    symbol, module_path, attr_name,
                )
                broken.append(symbol)
        except ImportError as exc:
            is_optional = any(module_path.startswith(p) for p in _OPTIONAL_PREFIXES)
            if is_optional:
                logger.debug(
                    "Registry entry '%s' skipped (optional dep not installed): %s",
                    symbol, exc,
                )
            else:
                logger.error(
                    "Registry entry '%s': cannot import '%s' — %s",
                    symbol, module_path, exc,
                )
                broken.append(symbol)
        except Exception as exc:
            logger.error(
                "Registry entry '%s': unexpected error importing '%s.%s' — %s",
                symbol, module_path, attr_name, exc,
            )
            broken.append(symbol)

    if broken:
        logger.warning(
            "django_cfg registry: %d broken entr%s at startup: %s",
            len(broken),
            "y" if len(broken) == 1 else "ies",
            ", ".join(broken),
        )
    else:
        logger.debug("django_cfg registry: all entries validated successfully")
