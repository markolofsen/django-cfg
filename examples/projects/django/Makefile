# Django CFG Sample Project - Makefile
#
# Local Development Workflow:
# 1. make install          → Install from PyPI (production mode)
# 2. make install-local    → Switch to local ~/djangocfg (editable)
# 3. make check-django-cfg → Verify which version is active
# 4. make install-prod     → Switch back to PyPI
#
# How it works:
# - pyproject.toml always has: django-cfg = {version = "*", extras = ["full"]}
# - install-local uses pip to override PyPI version with local editable install
# - install-prod runs poetry install --sync to restore PyPI version
# - No modifications to pyproject.toml or poetry.lock required!

.PHONY: help install install-local install-prod check-django-cfg env docker test commit kill-ports kill-grpc dev dev-ngrok grpc manage migrate makemigrations shell show-urls check tree config superuser tasks-status tasks-worker api centrifugo claude populate list-urls check-endpoints

# Python from virtual environment (poetry)
PYTHON := .venv/bin/python
POETRY := poetry
# Path to local django-cfg for development
DJANGO_CFG_LOCAL := $(HOME)/djangocfg

help:
	@echo "Django CFG Sample Project - Make Commands"
	@echo ""
	@echo "Setup & Installation:"
	@echo "  make install          - Install dependencies (PyPI django-cfg)"
	@echo "  make install-local    - Switch to local django-cfg (editable)"
	@echo "  make install-prod     - Switch back to PyPI django-cfg"
	@echo "  make check-django-cfg - Check which django-cfg is installed"
	@echo ""
	@echo "Development:"
	@echo "  make dev           - Run development server (kills port 8000 first)"
	@echo "  make dev-ngrok     - Run development server with ngrok tunnel"
	@echo "  make grpc          - Run gRPC server (kills port 50051 first)"
	@echo "  make kill-ports    - Kill processes on port 8000"
	@echo "  make kill-grpc     - Kill gRPC processes on port 50051"
	@echo "  make shell         - Open Django shell"
	@echo "  make api           - Generate and deploy API clients (OpenAPI + Centrifugo)"
	@echo "  make centrifugo    - Generate Centrifugo WebSocket clients (opensdk)"
	@echo "  make claude        - Start Claude Code"
	@echo ""
	@echo "Database:"
	@echo "  make migrate       - Run all migrations"
	@echo "  make populate      - Populate database with sample data"
	@echo ""
	@echo "Configuration:"
	@echo "  make config        - Show current configuration"
	@echo "  make check         - Run Django system checks"
	@echo "  make check-settings- Check django-cfg settings"
	@echo ""
	@echo "URLs & Structure:"
	@echo "  make show-urls     - Show all URL patterns"
	@echo "  make list-urls     - List all URLs (Rich formatted)"
	@echo "  make check-endpoints - Check API endpoints status"
	@echo "  make tree          - Show project structure"
	@echo ""
	@echo "Users & Auth:"
	@echo "  make superuser     - Create superuser (interactive)"
	@echo ""
	@echo "Tasks (Dramatiq):"
	@echo "  make tasks-status  - Show task system status"
	@echo "  make tasks-worker  - Run Dramatiq worker"
	@echo "  make tasks-clear   - Clear all pending tasks"
	@echo ""
	@echo "Testing:"
	@echo "  make test          - Run tests"
	@echo ""
	@echo "Utils:"
	@echo "  make manage CMD=<command> - Run manage.py command"
	@echo ""
	@echo "Git:"
	@echo "  make commit        - Quick commit with message"
	@echo ""
	@echo "📖 Full command reference: see COMMANDS.md"

install:
	@echo "📦 Installing dependencies (PyPI django-cfg)..."
	$(POETRY) install
	@echo "✅ Installed django-cfg from PyPI"
	@echo "💡 To use local django-cfg: make install-local"

install-local:
	@echo "📦 Switching to local django-cfg..."
	@echo "   Path: $(DJANGO_CFG_LOCAL)"
	@# Check if local django-cfg exists
	@test -d $(DJANGO_CFG_LOCAL) || (echo "❌ Error: $(DJANGO_CFG_LOCAL) not found" && exit 1)
	@# Remove lock file to ensure clean state
	@rm -f poetry.lock
	@echo "🔄 Regenerating poetry.lock..."
	@# Install poetry dependencies (auto-creates new lock file)
	$(POETRY) install
	@# Then install local django-cfg with pip (overwrites PyPI version)
	@echo "🔧 Installing local django-cfg (editable mode)..."
	$(POETRY) run pip install -e "$(DJANGO_CFG_LOCAL)[full]"
	@echo ""
	@echo "✅ Local django-cfg installed (editable mode)"
	@echo "📍 Changes in $(DJANGO_CFG_LOCAL) will be immediately reflected"
	@echo "💡 To switch back to PyPI: make install-prod"

install-prod:
	@echo "📦 Switching back to PyPI django-cfg..."
	@# Reinstall all poetry dependencies (restores PyPI version)
	@$(POETRY) install --sync
	@echo "✅ PyPI django-cfg restored"
	@echo "💡 To use local version again: make install-local"

check-django-cfg:
	@echo "🔍 Checking django-cfg installation..."
	@$(POETRY) run pip show django-cfg | grep -E "^(Name|Version|Location|Editable)" || echo "❌ django-cfg not found"
	@echo ""
	@if $(POETRY) run pip show django-cfg | grep -q "Editable project location"; then \
		echo "✅ Using LOCAL django-cfg (editable mode)"; \
	else \
		echo "✅ Using PyPI django-cfg"; \
	fi

env:
	@$(POETRY) env info

docker:
	git pull && python3 devops/manage.py

test:
	$(PYTHON) manage.py test

commit:
	git add . && git commit && git push

kill-ports:
	lsof -i :8000 | awk 'NR>1 {print $$2}' | xargs kill -9 || true

kill-grpc:
	@echo "🔪 Killing gRPC processes..."
	@# Kill by process name (rungrpc)
	@pkill -9 -f "manage.py rungrpc" 2>/dev/null || true
	@# Kill by port (50051)
	@lsof -ti :50051 | xargs kill -9 2>/dev/null || true
	@# Kill any Python processes still holding port 50051
	@lsof -ti :50051 -sTCP:LISTEN | xargs kill -9 2>/dev/null || true
	@# Small delay to ensure ports are released
	@sleep 0.5
	@echo "✅ gRPC processes killed"

dev: kill-ports
	$(PYTHON) manage.py runserver

dev-ngrok: kill-ports
	$(PYTHON) manage.py runserver_ngrok

grpc: kill-grpc
	@echo "🚀 Starting gRPC server on port 50051..."
	$(PYTHON) manage.py rungrpc

manage:
	$(PYTHON) manage.py $(CMD)

migrate:
	$(PYTHON) manage.py migrate_all

shell:
	$(PYTHON) manage.py shell

show-urls:
	$(PYTHON) manage.py show_urls

list-urls:
	$(PYTHON) manage.py list_urls

check-endpoints:
	$(PYTHON) manage.py check_endpoints

tree:
	$(PYTHON) manage.py tree

config:
	$(PYTHON) manage.py show_config

check:
	$(PYTHON) manage.py check

check-settings:
	$(PYTHON) manage.py check_settings

superuser:
	$(PYTHON) manage.py superuser

tasks-status:
	$(PYTHON) manage.py task_status

tasks-worker:
	$(PYTHON) manage.py rundramatiq

tasks-clear:
	$(PYTHON) manage.py task_clear

# API Generation
api:
	$(PYTHON) manage.py generate_api

# Centrifugo WebSocket Client Generation
centrifugo:
	$(PYTHON) manage.py generate_centrifugo

# Populate database with sample data
populate:
	rm -f db/*.sqlite3
	$(PYTHON) manage.py migrate_all
	$(PYTHON) manage.py populate_sample_data

# Start Claude Code with dangerously-skip-permissions flag
claude:
	claude --dangerously-skip-permissions
