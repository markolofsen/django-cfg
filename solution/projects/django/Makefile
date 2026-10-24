# Django CFG Sample Project - Makefile
#
# Local Development Workflow:
# 1. make install          -> Install from PyPI (production mode)
# 2. make install-local    -> Switch to local ~/djangocfg (editable)
#
# How it works:
# - pyproject.toml has django-cfg[full] as dependency
# - [tool.uv.sources] configures local editable path
# - uv sync automatically uses the local path when available

.PHONY: help install install-local install-local-uv env test commit kill-ports kill-grpc kill-all dev asgi grpc run-all manage migrate shell show-urls list-urls check-endpoints tree check config superuser api api-web api-ws gen gen-ts gen-py gen-admin gen-api gen-dry gen-list claude codex

# uv binary (full path for Make compatibility — Make uses a restricted PATH)
UV := $(HOME)/.local/bin/uv
# Python from virtual environment — direct path avoids uv run which auto-syncs and reverts editable installs
PYTHON := .venv/bin/python
# Path to local django-cfg for development (~/djangocfg symlink → @projects/djangocfg/projects/django-cfg)
DJANGO_CFG_LOCAL := $(HOME)/djangocfg

help:
	@echo "Django Project - Make Commands"
	@echo ""
	@echo "Development:"
	@echo "  make dev       - Run dev server (port 8000)"
	@echo "  make asgi      - Run ASGI server (uvicorn)"
	@echo "  make grpc      - Run gRPC server (port 50051)"
	@echo "  make run-all   - Run ASGI + gRPC + RQ worker"
	@echo ""
	@echo "Management:"
	@echo "  make migrate   - Run migrations"
	@echo "  make shell     - Django shell"
	@echo "  make superuser - Create superuser"
	@echo "  make api       - Generate API clients"
	@echo "  make api-web   - Generate web API clients"
	@echo ""
	@echo "RQ:"
	@echo "  make rq            - Start RQ worker (all queues)"
	@echo "  make rq-scheduler  - Start RQ scheduler"
	@echo "  make rq-clear      - Clear all RQ queues (Redis FLUSHDB)"
	@echo "  make rq-stats      - Show RQ statistics"
	@echo ""
	@echo "Cleanup:"
	@echo "  make kill-all  - Stop all services"
	@echo ""
	@echo "Other: install, install-local, test, commit, check, config"

install:
	@echo "Installing dependencies (PyPI django-cfg)..."
	@# Remove local source override if exists
	@grep -q '^\[tool\.uv\.sources\]' pyproject.toml && \
		sed -i '' '/^\[tool\.uv\.sources\]/,/^$$/d' pyproject.toml || true
	$(UV) sync
	@echo "Installed django-cfg from PyPI"
	@echo "To use local django-cfg: make install-local or make install-local-uv"

# Install local django-cfg using the project's install script (pip editable, no pyproject.toml changes)
install-local:
	@echo "Installing dependencies from PyPI first..."
	@grep -q '^\[tool\.uv\.sources\]' pyproject.toml && \
		sed -i '' '/^\[tool\.uv\.sources\]/,/^$$/d' pyproject.toml || true
	$(UV) sync
	@echo "Switching django-cfg to local editable (via install script)..."
	@bash $(DJANGO_CFG_LOCAL)/scripts/install_local_djangocfg.sh --venv .venv
	@# uv copies files into site-packages even for editable installs — remove so .pth takes effect
	@SITE=$$(.venv/bin/python -c "import sysconfig; print(sysconfig.get_path('purelib'))") && \
		rm -rf "$$SITE/django_cfg"
	@echo ""
	@echo "✅ Local django-cfg installed (editable mode, pyproject.toml unchanged)"
	@echo "📍 Changes in $(DJANGO_CFG_LOCAL) will be immediately reflected"
	@echo "⚠️  Do not run uv sync — it will revert to PyPI"

# Install local django-cfg using uv sources (adds path to pyproject.toml temporarily)
install-local-uv:
	@echo "Configuring [tool.uv.sources] for local django-cfg..."
	@grep -q '^\[tool\.uv\.sources\]' pyproject.toml || \
		printf '\n[tool.uv.sources]\ndjango-cfg = { path = "$(DJANGO_CFG_LOCAL)", editable = true }\n' >> pyproject.toml
	$(UV) sync
	@echo ""
	@echo "✅ Done — django-cfg installed from $(DJANGO_CFG_LOCAL) (uv editable)"
	@echo "📍 Run: uv run python manage.py ..."
	@echo "⚠️  pyproject.toml now has local path — run 'make install' to revert to PyPI"

env:
	@$(UV) run python -c "import sys; print(sys.prefix)"

test:
	$(PYTHON) manage.py test

commit:
	git add . && git commit && git push

kill-ports:
	lsof -i :8000 | awk 'NR>1 {print $$2}' | xargs kill -9 || true

kill-grpc:
	@echo "Killing all Django manage.py, gRPC and ASGI processes..."
	@# Kill ALL manage.py processes (runserver, rungrpc, shell, etc.)
	@pkill -9 -f "manage.py" 2>/dev/null || true
	@# Kill uvicorn processes
	@pkill -9 -f "uvicorn api.asgi" 2>/dev/null || true
	@# Kill by port (50051 - gRPC)
	@lsof -ti :50051 | xargs kill -9 2>/dev/null || true
	@# Kill by port (8000 - ASGI/Django)
	@lsof -ti :8000 | xargs kill -9 2>/dev/null || true
	@# Kill any Python processes still holding ports
	@lsof -ti :50051 -sTCP:LISTEN | xargs kill -9 2>/dev/null || true
	@lsof -ti :8000 -sTCP:LISTEN | xargs kill -9 2>/dev/null || true
	@# Small delay to ensure ports are released
	@sleep 0.5
	@echo "All Django processes, gRPC and ASGI killed"

kill-all:
	@echo "Killing ASGI, gRPC, and RQ worker processes..."
	@# Kill manage.py processes
	@pkill -9 -f "manage.py rungrpc" 2>/dev/null || true
	@pkill -9 -f "manage.py rqworker" 2>/dev/null || true
	@# Kill uvicorn
	@pkill -9 -f "uvicorn api.asgi" 2>/dev/null || true
	@# Kill by ports
	@lsof -ti :50051 | xargs kill -9 2>/dev/null || true
	@lsof -ti :8000 | xargs kill -9 2>/dev/null || true
	@sleep 0.5
	@echo "All services stopped"

dev: kill-ports
	$(PYTHON) manage.py runserver


asgi: kill-ports
	@echo "Starting ASGI server on port 8000 (uvicorn)..."
	$(UV) run uvicorn api.asgi:application --host 0.0.0.0 --port 8000 --reload

grpc:
	@echo "Starting gRPC server on port 50051..."
	@lsof -ti :50051 | xargs kill -9 2>/dev/null || true
	$(PYTHON) manage.py rungrpc --noreload

run-all: kill-all
	@echo "Starting ASGI + gRPC + RQ worker..."
	@echo ""
	@bash -c ' \
		cleanup() { \
			echo ""; \
			echo "Stopping all services..."; \
			pkill -9 -f "manage.py rungrpc" 2>/dev/null || true; \
			pkill -9 -f "manage.py rqworker" 2>/dev/null || true; \
			pkill -9 -f "uvicorn api.asgi" 2>/dev/null || true; \
			lsof -ti :50051 | xargs kill -9 2>/dev/null || true; \
			lsof -ti :8000 | xargs kill -9 2>/dev/null || true; \
			echo "All services stopped"; \
		}; \
		trap cleanup EXIT SIGINT SIGTERM; \
		echo "Starting gRPC server on port 50051..."; \
		$(PYTHON) manage.py rungrpc --noreload & \
		GRPC_PID=$$!; \
		sleep 1; \
		echo "Starting ASGI server on port 8000 (uvicorn)..."; \
		$(UV) run uvicorn api.asgi:application --host 0.0.0.0 --port 8000 --reload & \
		ASGI_PID=$$!; \
		sleep 1; \
		echo "Starting RQ worker (all queues)..."; \
		OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES $(PYTHON) manage.py rqworker high default low --worker-class rq.SimpleWorker & \
		RQ_PID=$$!; \
		echo ""; \
		echo "All services started:"; \
		echo "   - gRPC:  http://localhost:50051 (PID: $$GRPC_PID)"; \
		echo "   - ASGI:  http://localhost:8000 (PID: $$ASGI_PID)"; \
		echo "   - RQ:    high, default, low queues (PID: $$RQ_PID)"; \
		echo ""; \
		echo "Press Ctrl+C to stop all services"; \
		echo ""; \
		wait; \
	'

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

superuser:
	$(PYTHON) manage.py superuser

# API Generation (unified via generation.py config).
#
# Two ways to run:
#   make gen                          — via Django manage.py wrapper (supports flags)
#   python generation.py              — standalone (self-bootstrapping)
gen:
	$(PYTHON) manage.py gen

gen-ts:
	$(PYTHON) manage.py gen --ts

gen-py:
	$(PYTHON) manage.py gen --py

gen-go:
	$(PYTHON) manage.py gen --go

gen-target:
	$(PYTHON) manage.py gen --target $(T)

gen-groups:
	$(PYTHON) manage.py gen --groups $(G)

gen-dry:
	$(PYTHON) manage.py gen --dry-run

gen-list:
	$(PYTHON) manage.py gen --list-targets

# Legacy aliases (deprecated - use gen commands)
api: gen
api-web: gen-ts
# Start Claude Code with dangerously-skip-permissions flag
claude:
	claude --dangerously-skip-permissions --chrome

# Start Codex CLI with bypassed approvals and sandbox
codex:
	codex --dangerously-bypass-approvals-and-sandbox

# RQ Workers and Scheduler (macOS optimized - uses SimpleWorker to prevent fork crashes)
rq: rq-clear
	@echo "Starting RQ worker (high, default, low queues)..."
	@OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES $(PYTHON) manage.py rqworker high default low --worker-class rq.SimpleWorker

rq-scheduler:
	@echo "Starting RQ scheduler..."
	@$(PYTHON) manage.py rqscheduler

rq-clear:
	@echo "Clearing all RQ queues via Redis..."
	@redis-cli FLUSHDB
	@echo "All queues cleared"

rq-stats:
	@echo "RQ Queue Statistics:"
	@$(PYTHON) manage.py rqstats
