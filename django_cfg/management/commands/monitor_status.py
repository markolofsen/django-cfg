"""Django-CFG proxy for monitor_status command."""

from django_cfg.modules.django_monitor.management.commands.monitor_status import (
    Command as _Command,
)


class Command(_Command):
    pass
