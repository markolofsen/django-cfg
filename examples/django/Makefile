.PHONY: help install install-local env docker test commit kill-ports dev dev-ngrok manage migrate makemigrations shell show-urls check tree config superuser tasks-status tasks-worker api claude populate list-urls check-endpoints

# Python from virtual environment (poetry)
PYTHON := .venv/bin/python
POETRY := poetry

help:
	@echo "Django CFG Sample Project - Make Commands"
	@echo ""
	@echo "Setup & Installation:"
	@echo "  make install       - Install dependencies (production mode)"
	@echo "  make install-local - Install with local django-cfg and django-ipc"
	@echo ""
	@echo "Development:"
	@echo "  make dev           - Run development server (kills port 8000 first)"
	@echo "  make dev-ngrok     - Run development server with ngrok tunnel"
	@echo "  make kill-ports    - Kill processes on port 8000"
	@echo "  make shell         - Open Django shell"
	@echo "  make api           - Generate and deploy API clients"
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
	@echo "📦 Installing dependencies (production mode)..."
	$(POETRY) install

install-local:
	@echo "📦 Installing with local django-cfg and django-ipc..."
	@rm -f poetry.lock
	$(POETRY) add --group local --editable ~/djangocfg --lock
	$(POETRY) add --group local --editable ~/djangoipc --lock
	$(POETRY) add --group local --editable ~/revolution --lock
	$(POETRY) install --with local --no-root

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

dev: kill-ports
	$(PYTHON) manage.py runserver

dev-ngrok: kill-ports
	$(PYTHON) manage.py runserver_ngrok

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

api-test:
	$(PYTHON) manage.py revolution --test-schemas

# Populate database with sample data
populate:
	rm -f db/*.sqlite3
	$(PYTHON) manage.py migrate_all
	$(PYTHON) manage.py populate_sample_data

# Start Claude Code with dangerously-skip-permissions flag
claude:
	claude --dangerously-skip-permissions
