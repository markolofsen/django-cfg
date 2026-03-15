"""Django-CFG proxy for cf_sync_users command."""

from django_cfg.modules.django_cf.management.commands.cf_sync_users import (
    Command as _Command,
)


class Command(_Command):
    pass
