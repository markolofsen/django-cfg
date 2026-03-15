"""Django-CFG proxy for cf_status command."""

from django_cfg.modules.django_cf.management.commands.cf_status import (
    Command as _Command,
)


class Command(_Command):
    pass
