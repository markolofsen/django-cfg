#!/usr/bin/env python
"""
Standalone script to check gRPC dependencies.

Usage:
    python -m django_cfg.apps.integrations.grpc._cfg.check_deps
    python src/django_cfg/apps/grpc/_cfg/check_deps.py
"""

from __future__ import annotations

import sys

from .dependencies import print_dependency_status


def main():
    """Run dependency check and print status."""
    print("\n" + "=" * 80)
    print("Django-CFG gRPC Dependency Checker")
    print("=" * 80)

    try:
        print_dependency_status()
        print("✅ All required dependencies are installed!")
        print("\nYou can now run: python manage.py rungrpc")
        return 0
    except Exception as e:
        print(f"\n❌ Dependency check failed:\n{e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
