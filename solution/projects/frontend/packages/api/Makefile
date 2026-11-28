# 🚀 API Package Makefile
# Shared API client generation for @djangocfg/api

# ============================================================================
# Path Configuration
# ============================================================================
ROOT_DIR := $(abspath $(dir $(lastword $(MAKEFILE_LIST)))/../../../../..)

# Django project paths
DJANGO_PROJECT_DIR := $(ROOT_DIR)/projects/solution/django
DJANGO_OPENAPI_DIR := $(DJANGO_PROJECT_DIR)/openapi/clients/typescript

# Django project's venv Python — direct path, NOT `uv run`.
# `uv run`/`uv sync` silently reinstall the PyPI django-cfg over an editable
# (`make install-local`) link, so generation would emit a STALE client that
# misses local django_cfg changes. The direct interpreter preserves the link.
# (Mirrors the PYTHON := .venv/bin/python pattern in the django Makefile.)
# `generate` also puts the local django-cfg source first on PYTHONPATH, as the
# django Makefile's GEN_RUN does: without it a plain run imports whatever
# django-cfg the venv has installed (2.4.104 on 2026-11-23), silently.
DJANGO_PYTHON := $(DJANGO_PROJECT_DIR)/.venv/bin/python

# Target directory
GENERATED_DIR := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))/src/generated

.PHONY: help generate build clean

help:
	@echo "🚀 API Package Commands"
	@echo ""
	@echo "📦 Generation:"
	@echo "  make generate    - Generate and copy TypeScript clients"
	@echo "  make build       - Build the API package"
	@echo "  make clean       - Clean generated files"
	@echo ""

generate:
	@test -x "$(DJANGO_PYTHON)" || { \
		echo "❌ $(DJANGO_PYTHON) not found."; \
		echo "   Run 'make install' (or 'make install-local' for local django-cfg) in $(DJANGO_PROJECT_DIR) first."; \
		exit 1; \
	}
	@cd $(DJANGO_PROJECT_DIR) && PYTHONPATH="$(ROOT_DIR)/projects/django-cfg/src:$${PYTHONPATH:-}" "$(DJANGO_PYTHON)" manage.py gen --target packages
	@echo "✅ API clients generated"
	@echo ""
	@echo "🏗️  Building API package..."
	@pnpm build
	@echo "✅ API package built!"
	@echo ""

clean:
	@echo "🧹 Cleaning generated files..."
	@rm -rf "$(GENERATED_DIR)"
	@rm -rf dist
	@echo "✅ Cleaned!"

# Shortcut: generate + build
all: generate build
