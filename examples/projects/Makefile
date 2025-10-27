.PHONY: help dev dev-django dev-frontend dev-websocket kill-ports

help:
	@echo "Django CFG Solution - Development Commands"
	@echo ""
	@echo "Available commands:"
	@echo "  make dev           - Start all services: Django (8000), Next.js (3000), WebSocket (8765)"
	@echo "  make dev-django    - Start only Django backend on port 8000"
	@echo "  make dev-frontend  - Start only Next.js demo app on port 3000"
	@echo "  make dev-websocket - Start only WebSocket server on port 8765"
	@echo "  make kill-ports    - Kill processes on ports 8000, 3000, and 8765"
	@echo ""
	@echo "Quick start: make dev"

# Kill processes on ports 8000 (Django), 3000 (Next.js), and 8765 (WebSocket)
kill-ports:
	@echo "🔪 Killing processes on ports 8000, 3000, and 8765..."
	@lsof -ti:8000 | xargs kill -9 2>/dev/null || true
	@lsof -ti:3000 | xargs kill -9 2>/dev/null || true
	@lsof -ti:8765 | xargs kill -9 2>/dev/null || true
	@echo "✅ Ports cleared"

# Start Django backend only
dev-django: kill-ports
	@echo "🐍 Starting Django backend on port 8000..."
	@cd django && make dev

# Start Next.js frontend only
dev-frontend: kill-ports
	@echo "⚛️  Starting Next.js demo app on port 3000..."
	@cd frontend/apps/demo && pnpm dev

# Start WebSocket server only
dev-websocket: kill-ports
	@echo "🔗 Starting WebSocket server on port 8765..."
	@cd websocket && make dev

# Start all three services in parallel
dev: kill-ports
	@echo "🚀 Starting development servers..."
	@echo "   Django:    http://localhost:8000"
	@echo "   Next.js:   http://localhost:3000"
	@echo "   WebSocket: ws://localhost:8765"
	@echo ""
	@(cd django && make dev) & (cd frontend/apps/demo && pnpm dev) & wait