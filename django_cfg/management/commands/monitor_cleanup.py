"""Django-CFG proxy for monitor_cleanup command."""

from django_cfg.modules.django_monitor.management.commands.monitor_cleanup import (
    Command as _Command,
)


class Command(_Command):
    pass
