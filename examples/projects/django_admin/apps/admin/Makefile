.PHONY: help api dev

help:
	@echo "Next.js Admin - Development Commands"
	@echo ""
	@echo "Available commands:"
	@echo "  make dev        - Start Next.js Admin on port 3000"
	@echo "  make api        - Generate TypeScript API clients"
	@echo ""

# Generate TypeScript API clients
api:
	@echo "🚀 Generating TypeScript API clients..."
	@echo "📁 Output: src/api/generated/cfg/"
	@echo ""
	cd ../../../django && poetry run python manage.py generate_clients --typescript --no-python
	@echo ""
	@echo "📦 Copying cfg API clients to admin app..."
	mkdir -p src/api/generated/cfg
	rm -rf src/api/generated/cfg/generated src/api/generated/cfg/BaseClient.ts
	cp -r ../../../django/openapi/clients/typescript/cfg/* src/api/generated/cfg/
	@echo "✅ Copied cfg API clients to src/api/generated/cfg!"
	@echo ""
	@echo "✅ TypeScript clients generated successfully!"
	@echo ""

# Start Next.js Admin development server
dev:
	@echo "⚛️  Starting Next.js Admin on port 3000..."
	@echo ""
	pnpm dev
