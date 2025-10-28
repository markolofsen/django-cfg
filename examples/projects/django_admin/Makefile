# 🚀 Frontend Makefile
# API Generation and Build for Next.js Admin

.PHONY: help api admin dev

# Default target
help:
	@echo "🚀 Frontend Commands"
	@echo ""
	@echo "📦 API Generation:"
	@echo "  make api - Generate TypeScript API clients for Next.js Admin"
	@echo ""
	@echo "🏗️  Build:"
	@echo "  make admin  - Build Next.js Admin static export"
	@echo ""
	@echo "🚀 Development:"
	@echo "  make dev - Start Django backend + Next.js Admin in parallel"
	@echo ""

api:
	@echo "🚀 Generating TypeScript API clients..."
	@echo "📁 Output: packages/api/src/cfg/generated/"
	@echo ""
	cd ../../../../solution/projects/django && poetry run python manage.py generate_clients --typescript --no-python
	@echo ""
	@echo "📦 Copying cfg group to frontend packages..."
	rm -rf packages/api/src/cfg/generated
	mkdir -p packages/api/src/cfg/generated
	cp -r ../../../../solution/projects/django/openapi/clients/typescript/cfg/* packages/api/src/cfg/generated/
	@echo "✅ Copied cfg API clients to packages/api!"
	@echo ""
	@echo "📦 Copying cfg to admin app..."
	mkdir -p apps/admin/src/api/generated/cfg
	rm -rf apps/admin/src/api/generated/cfg/generated apps/admin/src/api/generated/cfg/BaseClient.ts
	cp -r ../../../../solution/projects/django/openapi/clients/typescript/cfg/* apps/admin/src/api/generated/cfg/
	@echo "✅ Copied cfg to apps/admin!"
	@echo ""
	@echo "🔨 Building API package..."
	cd packages/api && pnpm build
	@echo ""
	@echo "✅ TypeScript clients generated successfully!"
	@echo ""

admin:
	@echo "🏗️  Building Next.js Admin static export..."
	@echo "📁 Output: apps/admin/out/"
	@echo ""
	cd apps/admin && pnpm build:static
	@echo ""
	@echo "📦 Copying static build to django_cfg..."
	rm -rf ../django_cfg/static/frontend/admin
	mkdir -p ../django_cfg/static/frontend/admin
	cp -r apps/admin/out/* ../django_cfg/static/frontend/admin/
	@echo "✅ Copied to: src/django_cfg/static/frontend/admin/"
	@echo ""
	@echo "✅ Static build completed!"
	@echo ""
	@echo "📂 Build locations:"
	@echo "  - apps/admin/out/                       (Next.js build)"
	@echo "  - ../django_cfg/static/frontend/admin/  (Django static files)"
	@echo ""

dev:
	@echo "🚀 Starting Django backend + Next.js Admin in parallel..."
	@echo ""
	@echo "📍 Django backend: http://localhost:8000"
	@echo "📍 Next.js Admin:  http://localhost:3000"
	@echo ""
	@echo "⚡ Frontend Dev Mode: ENABLED"
	@echo "   (Django will load iframe from localhost:3000)"
	@echo ""
	@echo "Press Ctrl+C to stop all services"
	@echo ""
	@sleep 2 && (command -v open >/dev/null && open http://localhost:3000 || command -v xdg-open >/dev/null && xdg-open http://localhost:3000) &
	@trap 'kill 0' EXIT; \
	(cd ../../../../solution/projects/django && DJANGO_CFG_FRONTEND_DEV_MODE=true make dev) & \
	(cd apps/admin && pnpm dev) & \
	wait
