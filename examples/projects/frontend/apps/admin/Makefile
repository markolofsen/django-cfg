.PHONY: help api dev

help:
	@echo "Next.js Admin - Development Commands"
	@echo ""
	@echo "Available commands:"
	@echo "  make dev        - Start Next.js Admin on port 3000"
	@echo "  make api        - Generate TypeScript API clients"
	@echo ""

# Generate API clients (calls Django management command)
api:
	@echo "🚀 Generating API clients..."
	@echo ""
	@echo "📦 OpenAPI clients auto-copied to Next.js admin via NextJsAdminConfig"
	@echo ""
	cd ../../../django && poetry run python manage.py generate_api
	@echo ""
	@echo "✅ API generation completed!"
	@echo ""

# Start Next.js Admin development server
dev:
	@echo "⚛️  Starting Next.js Admin on port 3000..."
	@echo ""
	pnpm dev
