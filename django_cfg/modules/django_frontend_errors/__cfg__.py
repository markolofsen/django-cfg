"""django_frontend_errors configuration: ``DjangoConfig.frontend_errors``.

The class lives in ``core/base/config_model.py`` (the facade import budget has no room for
two more modules); it is re-exported here.
"""

from django_cfg.core.base.config_model import FrontendErrorsConfig  # noqa: F401

__all__ = ["FrontendErrorsConfig"]
