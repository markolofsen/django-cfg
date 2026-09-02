"""Runtime-editable settings (django-constance).

Split out of ``api/settings/config.py``. These are values an admin may change
without a deploy, which makes them a different *kind* of configuration from
everything else in ``config.py``: that file describes how this build is
wired, this one describes what an operator may retune while it runs.
"""

from __future__ import annotations

from django_cfg import ConstanceConfig, ConstanceField

from api.environment import env


def build_constance_config() -> ConstanceConfig:
    """Fields exposed in the admin for runtime tuning."""
    return ConstanceConfig(
        fields=[
            ConstanceField(name="SITE_NAME", default=env.app.name, help_text="The name of the site", field_type="str", group="General"),
            ConstanceField(name="SITE_DESCRIPTION", default="A complete demonstration of django_cfg features", help_text="Brief description of the site", field_type="str", group="General"),
        ],
    )
