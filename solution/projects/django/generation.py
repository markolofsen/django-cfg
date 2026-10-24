"""
Client generation config for djangocfg solution.

Run modes:
  python manage.py gen           # via Django management cmd
  python generation.py           # standalone — bootstraps Django itself

v5.3: Groups only in Target, no inheritance.
"""

from pathlib import Path

from django_cfg.modules.django_generator import (
    Config,
    OpenAPI,
    Target,
    ExtensionTarget,
    Language,
    TargetType,
)

ROOT = Path(__file__).resolve().parent
FRONTEND = ROOT.parent / "frontend"

# Source-of-truth root inside the Django project. Every target is generated
# here first; the pipeline copies trees to consumer paths (frontend) after.
SOURCE_ROOT = ROOT / "openapi" / "clients"

DEMO_API = FRONTEND / "apps" / "demo" / "app" / "_lib" / "api" / "generated"
PACKAGES_API = FRONTEND / "packages" / "api" / "src" / "_api" / "generated"
EXTENSIONS = FRONTEND / "extensions"

# NOTE: there is deliberately no target for cfg_monitor or cfg_analytics.
#
# Both are single-endpoint, fire-and-forget ingest APIs, and a generated client
# for them is pure overhead: it would be 2k+ lines to describe one POST that
# always answers 202 and whose response nobody reads. @djangocfg/devtools and
# @djangocfg/analytics each hand-write the ~40 lines of types they need, which is
# also what lets them ship without pulling the generated client's runtime.
#
# (A `MONITOR_API` target used to live here, pointing at `packages/monitor/` — a
# package that does not exist. It had been generating into nowhere. Removed.)

config = Config(
    openapi=OpenAPI(
        source_root=SOURCE_ROOT,
        targets=[
            Target(
                lang=Language.TYPESCRIPT,
                type=TargetType.WEB,
                path=DEMO_API,
                groups=["profiles", "crypto"],
            ),
            Target(
                lang=Language.TYPESCRIPT,
                type=TargetType.PACKAGES,
                path=PACKAGES_API,
                groups=["cfg_accounts", "cfg_totp"],
            ),
        ],

        # Auto-discover extensions
        # extensions=ExtensionTarget(
        #     lang=Language.TYPESCRIPT,
        #     frontend_path=EXTENSIONS,
        #     package_pattern="ext-{name}",
        #     output_pattern="src/api/generated",
        #     group_prefix="ext_",
        # ),
    ),
)


if __name__ == "__main__":
    """Standalone runner — `python generation.py` works from any cwd.

    Bootstraps Django (settings = api.settings.base) and runs the pipeline.
    """
    import os
    import sys

    sys.path.insert(0, str(ROOT))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "api.settings.base")

    import django
    django.setup()

    from django_cfg.modules.django_generator import run

    logger = run(config)
    sys.exit(1 if logger.stats.errors else 0)
