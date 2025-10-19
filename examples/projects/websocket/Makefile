.PHONY: help install install-ipc env dev kill-ports test health logs run-prod

help:
	@echo "Unrealon WebSocket Server - Make Commands"
	@echo ""
	@echo "Setup & Installation:"
	@echo "  make install       - Install dependencies (production mode)"
	@echo "  make install-ipc   - Install with local django-ipc package"
	@echo ""
	@echo "Development:"
	@echo "  make dev           - Run WebSocket server (development mode)"
	@echo "  make kill-ports    - Kill processes on ports 8765-8766"
	@echo ""
	@echo "Production:"
	@echo "  make run-prod      - Run WebSocket server (production mode)"
	@echo ""
	@echo "Monitoring:"
	@echo "  make health        - Check WebSocket server health"
	@echo "  make logs          - Show server logs"
	@echo ""
	@echo "Testing:"
	@echo "  make test          - Run tests"
	@echo ""
	@echo "Environment:"
	@echo "  make env           - Show Poetry environment info"
	@echo ""

install:
	@echo "📦 Installing dependencies (production mode)..."
	poetry install --no-dev

install-ipc:
	@echo "📦 Installing with local django-ipc package..."
	@echo "🔗 Using django-ipc from ~/djangoipc..."
	@rm -f poetry.lock
	@poetry add --group local --editable ~/djangoipc --lock
	@poetry install --with local --no-root

env:
	@poetry env info

kill-ports:
	@echo "🔪 Killing processes on ports 8765-8766..."
	@lsof -i :8765 | awk 'NR>1 {print $$2}' | xargs kill -9 2>/dev/null || true
	@lsof -i :8766 | awk 'NR>1 {print $$2}' | xargs kill -9 2>/dev/null || true
	@echo "✅ Ports cleared"

dev: kill-ports
	@echo "🚀 Starting WebSocket server (development mode)..."
	@echo "📡 WebSocket: ws://localhost:8765/ws"
	@echo "🏥 Health: http://localhost:8766/health"
	@echo ""
	@export ENVIRONMENT=development && poetry run python src/main.py

run-prod:
	@echo "🚀 Starting WebSocket server (production mode)..."
	@export ENVIRONMENT=production && poetry run python src/main.py

health:
	@echo "🏥 Checking WebSocket server health..."
	@curl -s http://localhost:8766/health | jq '.' || echo "❌ Server not responding"

logs:
	@echo "📋 Showing server logs..."
	@tail -f logs/websocket.log 2>/dev/null || echo "No logs found"

test:
	@echo "🧪 Running tests..."
	@poetry run pytest tests/ -v

# Generate TypeScript and Python clients
api:
	@echo "🔧 Generating TypeScript and Python clients..."
	@poetry run python src/generate_client.py
	@echo ""
	@echo "📦 Next steps:"
	@echo "  TypeScript: cd clients/typescript && npm install && npm run build"
	@echo "  Python:     cd clients/python && pip install -e ."

# Run with custom port
dev-port:
	@echo "🚀 Starting WebSocket server on custom port..."
	@export WS_PORT=$(PORT) && poetry run python src/main.py

# Docker commands (будут добавлены позже)
docker-build:
	@echo "🐳 Building Docker image..."
	@docker build -t unrealon/websocket:latest .

docker-run:
	@echo "🐳 Running Docker container..."
	@docker run -p 8765:8765 -p 8766:8766 --env-file .env unrealon/websocket:latest
