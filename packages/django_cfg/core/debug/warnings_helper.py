"""
Warnings debug helper for Django-CFG.

Shows full traceback for specific warnings to help identify the source.

Usage:
    Set environment variable:
    export DJANGO_CFG_DEBUG_WARNINGS=1

    Or call manually in manage.py/wsgi.py BEFORE django.setup():
    from django_cfg.core.debug import setup_warnings_debug
    setup_warnings_debug()
"""

import os
import sys
import traceback
import warnings


def warning_with_traceback(message, category, filename, lineno, file=None, line=None):
    """
    Custom warning handler that shows full stack traceback.

    This helps identify WHERE in the code the warning is triggered from.
    """
    # Skip known third-party library warnings
    message_str = str(message)
    if 'crontab' in filename or 'rq_scheduler' in filename:
        return  # Ignore crontab/rq-scheduler FutureWarnings

    log = file if hasattr(file, 'write') else sys.stderr

    # Print separator for clarity
    log.write("\n" + "="*80 + "\n")
    log.write(f"⚠️  WARNING TRACEBACK (to help find the source)\n")
    log.write("="*80 + "\n")

    # Print the full stack trace
    traceback.print_stack(file=log)

    # Print the actual warning
    log.write("\n" + "-"*80 + "\n")
    log.write(f"⚠️  WARNING MESSAGE:\n")
    log.write(warnings.formatwarning(message, category, filename, lineno, line))
    log.write("="*80 + "\n\n")

    # Add helpful hints for common async issues
    if 'coroutine' in message_str and 'never awaited' in message_str:
        hint = """
╔══════════════════════════════════════════════════════════════════════════════╗
║  💡 ASYNC VIEW HINT                                                          ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  This error typically occurs when using async def in DRF ViewSets.           ║
║  Standard DRF doesn't support async views natively!                          ║
║                                                                              ║
║  SOLUTIONS:                                                                  ║
║                                                                              ║
║  1. Use 'adrf' package for async-enabled ViewSets:                           ║
║     from adrf.viewsets import ViewSet as AsyncViewSet                        ║
║                                                                              ║
║     class MyViewSet(AsyncViewSet):                                           ║
║         async def list(self, request):                                       ║
║             items = await Item.objects.aall()                                ║
║             return Response(items)                                           ║
║                                                                              ║
║  2. Make sure you're running with ASGI (uvicorn):                            ║
║     make asgi   (instead of make dev)                                        ║
║                                                                              ║
║  3. Or use sync views with sync_to_async for async operations                ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
        log.write(hint)


def setup_warnings_debug(
    enabled: bool = None,
    categories: list = None,
    patterns: list = None
):
    """
    Setup warnings to show full traceback.

    Args:
        enabled: Whether to enable debug mode. If None, checks:
                 1. DjangoConfig.debug_warnings setting (if config exists)
                 2. DJANGO_CFG_DEBUG_WARNINGS environment variable
        categories: List of warning categories to track (default: [RuntimeWarning])
        patterns: List of regex patterns to match in warning messages
                 (default: ['.*database.*', '.*APPS_NOT_READY.*'])

    Example:
        # Enable all RuntimeWarnings with traceback
        setup_warnings_debug(enabled=True)

        # Enable only specific warnings
        setup_warnings_debug(
            enabled=True,
            categories=[RuntimeWarning, DeprecationWarning],
            patterns=['.*database.*']
        )

        # In your config.py:
        class MyConfig(DjangoConfig):
            debug_warnings: bool = True  # Enable warnings traceback
    """
    # Check if enabled (priority: explicit param > config > env var)
    if enabled is None:
        # Try to get from config first (if available)
        try:
            from django_cfg.core.config import get_current_config
            config = get_current_config()
            if config and hasattr(config, 'debug_warnings'):
                enabled = config.debug_warnings
            else:
                enabled = False
        except Exception:
            # Config not available yet, check env var
            enabled = False

        # Fallback to environment variable
        if not enabled:
            enabled = os.environ.get('DJANGO_CFG_DEBUG_WARNINGS', '').lower() in ('1', 'true', 'yes')

    if not enabled:
        return

    # Default categories
    if categories is None:
        categories = [RuntimeWarning]

    # Default patterns
    if patterns is None:
        patterns = [
            '.*database.*',
            '.*APPS_NOT_READY.*',
            '.*app.*initialization.*',
        ]

    # Install custom warning handler
    warnings.showwarning = warning_with_traceback

    # Configure filters for each category and pattern
    for category in categories:
        for pattern in patterns:
            warnings.filterwarnings(
                'default',
                category=category,
                message=pattern
            )

    print(f"🔍 Django-CFG Warnings Debug enabled for: {[c.__name__ for c in categories]}")
    print(f"   Patterns: {patterns}")
