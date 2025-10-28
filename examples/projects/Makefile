.PHONY: help dev django frontend websocket api kill-ports

help:
	@echo "Django CFG Solution - Development Commands"
	@echo ""
	@echo "Available commands:"
	@echo "  make dev           - Start Django + Next.js Admin (8000 + 3000)"
	@echo "  make django        - Start only Django backend (port 8000)"
	@echo "  make frontend      - Start only Next.js demo app (port 3000)"
	@echo "  make websocket     - Start only WebSocket server (port 8765)"
	@echo "  make api           - Generate TypeScript API clients"
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

# Generate TypeScript API clients
api:
	@echo "🚀 Generating TypeScript API clients..."
	@echo "📁 Output: django_admin/apps/admin/src/api/generated/cfg/"
	@echo ""
	cd django && poetry run python manage.py generate_clients --typescript --no-python
	@echo ""
	@echo "📦 Copying cfg API clients to admin app..."
	mkdir -p django_admin/apps/admin/src/api/generated/cfg
	rm -rf django_admin/apps/admin/src/api/generated/cfg/generated django_admin/apps/admin/src/api/generated/cfg/BaseClient.ts
	cp -r django/openapi/clients/typescript/cfg/* django_admin/apps/admin/src/api/generated/cfg/
	@echo "✅ Copied cfg API clients to django_admin/apps/admin/src/api/generated/cfg!"
	@echo ""
	@echo "✅ TypeScript clients generated successfully!"
	@echo ""

# Start Django backend only
django: kill-ports
	@echo "🐍 Starting Django backend on port 8000..."
	@cd django && make dev

# Start Django backend + Next.js Admin in parallel with iframe mode
dev: kill-ports
	@echo "🚀 Starting Django backend + Next.js Admin in parallel..."
	@echo ""
	@echo "📍 Django backend: http://localhost:8000"
	@echo "📍 Next.js Admin:  http://localhost:3000"
	@echo ""
	@echo "⚡ Auto-detect mode: Port 3000 (Tab 2 External Admin)"
	@echo "   Django will auto-detect dev server and load iframe"
	@echo ""
	@echo "Press Ctrl+C to stop all services"
	@echo ""
	@sleep 2 && (command -v open >/dev/null && open http://localhost:3000 || command -v xdg-open >/dev/null && xdg-open http://localhost:3000) &
	@trap 'kill 0' EXIT; \
	(cd django && make dev) & \
	(cd django_admin/apps/admin && pnpm dev) & \
	wait

# Start Next.js demo frontend only
frontend: kill-ports
	@echo "⚛️  Starting Next.js demo app on port 3000..."
	@cd frontend/apps/demo && pnpm dev

# Start WebSocket server only
websocket: kill-ports
	@echo "🔗 Starting WebSocket server on port 8765..."
	@cd websocket && make dev