#!/usr/bin/env python3
"""Material Icons Generator — entry point.

Run directly:
    python generate_icons.py

Or via Python:
    from django_cfg.modules.django_admin.icons.manager import run
    run()
"""
from manager.runner import main

if __name__ == "__main__":
    main()
