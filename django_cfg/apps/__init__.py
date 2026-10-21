"""
django_cfg.apps — package of django-cfg sub-apps (system, api, payments, tools).

Django resolves the INSTALLED_APPS entry "django_cfg" by importing
`django_cfg.apps` and picking the AppConfig subclass found there. This package
(not a module) is what that import returns, so the config is re-exported here.
Keep this file light: no models and no heavy imports at import time.
"""

from django_cfg.appconfig import DjangoCfgConfig  # noqa: F401
