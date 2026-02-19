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

.PHONY: help install install-local env test commit kill-ports kill-grpc kill-all dev dev-ngrok asgi grpc run-all manage migrate shell show-urls list-urls check-endpoints tree check config superuser api api-ws gen gen-ts gen-py gen-admin gen-dry gen-list claude

# Python from virtual environment (uv)
PYTHON := uv run python
# Path to local django-cfg for development
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
	@echo "  make gen       - Generate API clients (all)"
	@echo "  make gen-ts    - Generate TypeScript clients"
	@echo "  make gen-admin - Generate admin clients only"
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
	uv sync --no-sources
	@echo "Installed django-cfg from PyPI"
	@echo "To use local django-cfg: make install-local"

install-local:
	@echo "Switching to local django-cfg..."
	@echo "   Path: $(DJANGO_CFG_LOCAL)"
	@test -d $(DJANGO_CFG_LOCAL) || (echo "Error: $(DJANGO_CFG_LOCAL) not found" && exit 1)
	@# Remove existing [tool.uv.sources] if present
	@grep -q '^\[tool\.uv\.sources\]' pyproject.toml && \
		sed -i '' '/^\[tool\.uv\.sources\]/,/^$$/d' pyproject.toml || true
	@# Add local source override
	@echo '' >> pyproject.toml
	@echo '[tool.uv.sources]' >> pyproject.toml
	@echo 'django-cfg = { path = "$(DJANGO_CFG_LOCAL)", editable = true }' >> pyproject.toml
	@echo '' >> pyproject.toml
	@echo "Installing with local django-cfg..."
	uv sync
	@echo ""
	@echo "Local django-cfg installed (editable mode)"
	@echo "Changes in $(DJANGO_CFG_LOCAL) will be immediately reflected"

env:
	@uv run python -c "import sys; print(sys.prefix)"

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

dev-ngrok: kill-ports
	$(PYTHON) manage.py runserver_ngrok

asgi: kill-ports
	@echo "Starting ASGI server on port 8000 (uvicorn)..."
	uv run uvicorn api.asgi:application --host 0.0.0.0 --port 8000 --reload

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
		uv run uvicorn api.asgi:application --host 0.0.0.0 --port 8000 --reload & \
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

# API Generation (unified via generation.py config)
gen:
	$(PYTHON) manage.py gen

gen-ts:
	$(PYTHON) manage.py gen --ts

gen-py:
	$(PYTHON) manage.py gen --py

gen-admin:
	$(PYTHON) manage.py gen --target admin

gen-dry:
	$(PYTHON) manage.py gen --dry-run

gen-list:
	$(PYTHON) manage.py gen --list-targets

# Legacy aliases (deprecated - use gen commands)
api: gen
api-ws:
	$(PYTHON) manage.py generate_centrifugo_clients

# Start Claude Code with dangerously-skip-permissions flag
claude:
	claude --dangerously-skip-permissions --chrome

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
