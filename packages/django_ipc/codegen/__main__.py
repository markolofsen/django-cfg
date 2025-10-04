"""
CLI entry point for django_ipc codegen.

Allows running: python -m django_ipc.codegen
"""

import sys
from .cli import main

if __name__ == '__main__':
    sys.exit(main())
