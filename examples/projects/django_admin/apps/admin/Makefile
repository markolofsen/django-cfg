.PHONY: help api rpc dev

help:
	@echo "Next.js Admin - Development Commands"
	@echo ""
	@echo "Available commands:"
	@echo "  make dev   - Start Next.js Admin on port 3000"
	@echo "  make api   - Generate TypeScript API clients"
	@echo "  make rpc   - Generate Centrifugo WebSocket RPC clients only"
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

# Generate Centrifugo RPC clients only
rpc:
	@echo "🔌 Generating Centrifugo WebSocket RPC clients..."
	@echo "📁 Output: src/rpc/generated/"
	@echo ""
	@echo "Step 1: Generate Centrifugo RPC clients in django"
	cd ../../../django && poetry run python manage.py generate_rpc
	@echo ""
	@echo "Step 2: Copy RPC clients to admin app..."
	mkdir -p src/rpc/generated
	rm -rf src/rpc/generated/*
	cp -r ../../../django/opensdk/typescript/*.ts src/rpc/generated/
	@echo "✅ Copied Centrifugo RPC clients to src/rpc/generated/"
	@echo ""
	@echo "✅ Centrifugo RPC clients generated and copied successfully!"
	@echo ""

# Start Next.js Admin development server
dev:
	@echo "⚛️  Starting Next.js Admin on port 3000..."
	@echo ""
	pnpm dev
