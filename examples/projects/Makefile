.PHONY: help dev dev-django dev-frontend kill-ports

help:
	@echo "Django CFG Solution - Development Commands"
	@echo ""
	@echo "Available commands:"
	@echo "  make dev           - Start both Django backend (port 8000) and Next.js demo app (port 3000)"
	@echo "  make dev-django    - Start only Django backend on port 8000"
	@echo "  make dev-frontend  - Start only Next.js demo app on port 3000"
	@echo "  make kill-ports    - Kill processes on ports 8000 and 3000"
	@echo ""
	@echo "Quick start: make dev"

# Kill processes on ports 8000 (Django) and 3000 (Next.js)
kill-ports:
	@echo "🔪 Killing processes on ports 8000 and 3000..."
	@lsof -ti:8000 | xargs kill -9 2>/dev/null || true
	@lsof -ti:3000 | xargs kill -9 2>/dev/null || true
	@echo "✅ Ports cleared"

# Start Django backend only
dev-django: kill-ports
	@echo "🐍 Starting Django backend on port 8000..."
	@cd django && make dev

# Start Next.js frontend only
dev-frontend: kill-ports
	@echo "⚛️  Starting Next.js demo app on port 3000..."
	@cd frontend/apps/demo && pnpm dev

# Start both Django and Next.js in parallel
dev: kill-ports
	@echo "🚀 Starting development servers..."
	@echo "   Django:  http://localhost:8000"
	@echo "   Next.js: http://localhost:3000"
	@echo ""
	@(cd django && make dev) & (cd frontend/apps/demo && pnpm dev)
