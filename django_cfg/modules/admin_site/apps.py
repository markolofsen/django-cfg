"""``CfgAdminConfig``: takes the place of ``django.contrib.admin`` in INSTALLED_APPS.

Same app (label ``admin``, same autodiscovery); only ``default_site`` changes, so
``admin.site`` is ``CfgAdminSite``. Listed by django-cfg in ``DEFAULT_APPS``.
"""

from django.contrib.admin.apps import AdminConfig


class CfgAdminConfig(AdminConfig):
    default_site = "django_cfg.modules.admin_site.site.CfgAdminSite"
