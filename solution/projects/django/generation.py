"""
Client generation config for djangocfg solution.

v5.3: Groups only in Target, no inheritance.
"""

from pathlib import Path

from django_cfg.modules.django_codegen import (
    Config,
    OpenAPI,
    Target,
    ExtensionTarget,
    Language,
    TargetType,
)

ROOT = Path(__file__).parent
FRONTEND = ROOT.parent / "frontend"

ADMIN_API = FRONTEND / "apps" / "admin" / "app" / "_lib" / "api" / "generated"
EXTENSIONS = FRONTEND / "extensions"

config = Config(
    openapi=OpenAPI(
        targets=[
            Target(
                lang=Language.TYPESCRIPT,
                type=TargetType.ADMIN,
                path=ADMIN_API,
                groups=["profiles", "trading", "crypto"],
            ),
        ],

        # Auto-discover extensions
        extensions=ExtensionTarget(
            lang=Language.TYPESCRIPT,
            frontend_path=EXTENSIONS,
            package_pattern="ext-{name}",
            output_pattern="src/api/generated",
            group_prefix="ext_",
        ),
    ),
)
