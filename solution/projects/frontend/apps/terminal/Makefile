.PHONY: help api dev

help:
	@echo "Terminal App - Development Commands"
	@echo ""
	@echo "Available commands:"
	@echo "  make dev     - Start Terminal app on port 3002"
	@echo "  make api     - Copy Terminal API client from admin"
	@echo ""

# Copy Terminal API client from admin app
# Uses the generated client from Django's generate_api command
api:
	@echo "📦 Copying Terminal API client from admin..."
	@echo ""
	@mkdir -p app/_lib/api/generated
	@cp -r ../admin/app/_lib/api/generated/terminal app/_lib/api/generated/
	@echo "✅ Terminal API client copied to app/_lib/api/generated/terminal"
	@echo ""

# Start development server
dev:
	@echo "⚛️  Starting Terminal app on port 3002..."
	@echo ""
	pnpm dev
