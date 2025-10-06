.PHONY: help install install-local env docker test commit kill-ports dev dev-ngrok manage migrate makemigrations shell show-urls check tree config superuser tasks-status tasks-worker

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
	@echo ""
	@echo "Database:"
	@echo "  make migrate       - Run all migrations"
	@echo "  make migrate-all   - Run migrations on all databases"
	@echo "  make makemigrations- Generate migrations"
	@echo ""
	@echo "Configuration:"
	@echo "  make config        - Show current configuration"
	@echo "  make check         - Run Django system checks"
	@echo "  make check-settings- Check django-cfg settings"
	@echo ""
	@echo "URLs & Structure:"
	@echo "  make show-urls     - Show all URL patterns"
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
	poetry install

install-local:
	@echo "📦 Installing with local django-cfg and django-ipc..."
	@rm -f poetry.lock
	@poetry add --group local --editable ~/djangocfg --lock
	@poetry add --group local --editable ~/djangoipc --lock
	@poetry install --with local --no-root

env:
	@poetry env info

docker:
	git pull && python3 devops/manage.py

test:
	poetry run python manage.py test

commit:
	git add . && git commit && git push

kill-ports:
	lsof -i :8000 | awk 'NR>1 {print $$2}' | xargs kill -9 || true

dev: kill-ports
	poetry run python manage.py runserver

dev-ngrok: kill-ports
	poetry run python manage.py runserver_ngrok

manage:
	poetry run python manage.py $(CMD)

migrate:
	poetry run python manage.py migrate

migrate-all:
	poetry run python manage.py migrate_all

makemigrations:
	poetry run python manage.py makemigrations

shell:
	poetry run python manage.py shell

show-urls:
	poetry run python manage.py show_urls

tree:
	poetry run python manage.py tree

config:
	poetry run python manage.py show_config

check:
	poetry run python manage.py check

check-settings:
	poetry run python manage.py check_settings

superuser:
	poetry run python manage.py superuser

tasks-status:
	poetry run python manage.py task_status

tasks-worker:
	poetry run python manage.py rundramatiq

tasks-clear:
	poetry run python manage.py task_clear
