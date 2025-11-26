.PHONY: help api dev images images-sync images-scan images-generate

help:
	@echo "Next.js Admin - Development Commands"
	@echo ""
	@echo "Available commands:"
	@echo "  make dev            - Start Next.js Admin on port 3000"
	@echo "  make api            - Generate TypeScript API clients"
	@echo ""
	@echo "🎨 Image Generation:"
	@echo "  make images         - Interactive image generation with AI (DALL-E 3)"
	@echo "  make images-sync    - Sync images.ts config from public/static/images"
	@echo "  make images-scan    - Scan and list all images in project"
	@echo "  make images-generate PROMPT=\"...\" - Generate single image"
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

# ============================================================================
# 🎨 IMAGE GENERATION (imgai)
# ============================================================================

# imgai CLI via pnpm
IMGAI = pnpm exec imgai

# Default style settings - Cinematic Noir Sci-Fi (Max Payne style)
STYLE_PREFIX = Cinematic movie still, photorealistic, astronaut and alien characters in dramatic scene involving
STYLE_SUFFIX = , dark space station environment, noir dramatic lighting with harsh shadows, intense emotional expressions, dynamic action pose, rain or particle effects, cinematic wide angle shot, hyper-detailed textures, gritty atmosphere, Max Payne noir aesthetic, Unreal Engine 5 quality, 8K ultra realistic
DALLE_STYLE = natural

images:
	@echo "🎨 Starting interactive image generation..."
	@echo ""
	@$(IMGAI) --root $(shell pwd)

images-sync:
	@echo "⚡ Syncing images.ts config..."
	@echo ""
	@$(IMGAI) sync --root $(shell pwd) --output src/core/images.ts
	@echo ""
	@echo "✅ images.ts synced to src/core/images.ts"

images-scan:
	@echo "🔍 Scanning images..."
	@echo ""
	@$(IMGAI) scan --root $(shell pwd)

images-generate:
	@echo "🎨 Generate single image"
	@echo "Usage: make images-generate PROMPT=\"your prompt here\""
	@echo ""
	@if [ -z "$(PROMPT)" ]; then \
		echo "❌ Error: PROMPT is required"; \
		echo "Example: make images-generate PROMPT=\"A beautiful sunset\""; \
		exit 1; \
	fi
	@$(IMGAI) generate "$(PROMPT)" \
		--root $(shell pwd) \
		--prefix "$(STYLE_PREFIX)" \
		--suffix "$(STYLE_SUFFIX)" \
		--dalle-style $(DALLE_STYLE) \
		--category portfolio
