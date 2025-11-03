"""Django CFG Frontend App - Serves Next.js static builds."""

default_app_config = 'django_cfg.apps.system.frontend.apps.FrontendConfig'

# Convenience imports
from .setup import (
    setup_frontend_serving,
    get_frontend_urls,
    get_frontend_path,
    is_frontend_built,
)

__all__ = [
    'setup_frontend_serving',
    'get_frontend_urls',
    'get_frontend_path',
    'is_frontend_built',
]
