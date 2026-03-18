"""Django-CFG proxy for d1_logs command."""

from django_cfg.modules.django_cf.management.commands.d1_logs import (
    Command as _Command,
)


class Command(_Command):
    pass
