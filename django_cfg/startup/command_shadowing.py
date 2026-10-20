"""System check: a project command that a django-cfg command silently replaces.

Django keeps ONE management command per name. When a django-cfg module and a
project app both define `indexnow_submit`, the one from the app that comes
earlier in INSTALLED_APPS wins and the other simply stops existing: nothing
fails at startup, nothing fails at deploy, and the first sign is a command that
now does something else. That is how django-cfg 2.3.326 took over a project's
own `indexnow_submit` while a scheduled job kept running the original, so only
manual use broke.

This check names the clash. It is a warning, not an error: a project may mean
to override a framework command.

Only the PROJECT's own apps count. django-cfg deliberately wraps third-party
commands (`rqworker`, `rqstats`, `show_urls`), and warning on those would put
noise on every project; an installed package is recognised by living in
site-packages or dist-packages.
"""

from __future__ import annotations

import os

from django.apps import apps
from django.core.checks import Tags, Warning, register


def _is_installed_package(path: str) -> bool:
    return "site-packages" in path or "dist-packages" in path


def _commands_by_app() -> dict[str, list[tuple[str, bool]]]:
    """name -> [(app name, is the project's own code)] in INSTALLED_APPS order."""
    owners: dict[str, list[tuple[str, bool]]] = {}
    for config in apps.get_app_configs():
        directory = os.path.join(config.path, "management", "commands")
        if not os.path.isdir(directory):
            continue
        for entry in sorted(os.listdir(directory)):
            if entry.endswith(".py") and not entry.startswith("_"):
                owners.setdefault(entry[:-3], []).append(
                    (config.name, not _is_installed_package(config.path))
                )
    return owners


@register(Tags.models)
def check_command_shadowing(app_configs, **kwargs):
    from django.core.management import get_commands

    running = get_commands()
    problems = []
    for name, owners in sorted(_commands_by_app().items()):
        names = [o for o, _ in owners]
        framework = [o for o in names if o == "django_cfg" or o.startswith("django_cfg.")]
        project = [o for o, own in owners if own and o not in framework]
        if not framework or not project:
            continue
        problems.append(
            Warning(
                f"Management command '{name}' is defined by {', '.join(names)}; "
                f"Django runs the one from '{running.get(name)}'.",
                hint=(
                    "Rename the project's command (or the framework's) so a name means one "
                    "thing, or order INSTALLED_APPS deliberately if overriding is the intent."
                ),
                id="django_cfg.W010",
            )
        )
    return problems
