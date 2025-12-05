.PHONY: dev start build build-unsigned package dist sign notarize clean install lint help open

# App name (must match productName in package.json)
APP_NAME = DjangoCfg

# Code signing identity
SIGN_IDENTITY = Developer ID Application: Igor Korotin (8GS9P4SZWC)

# Apple credentials (from .env or environment)
APPLE_ID ?= $(shell grep APPLE_ID .env 2>/dev/null | cut -d= -f2)
APPLE_PASSWORD ?= $(shell grep APPLE_PASSWORD .env 2>/dev/null | cut -d= -f2)
APPLE_TEAM_ID ?= 8GS9P4SZWC

# Paths
APP_PATH = out/$(APP_NAME)-darwin-arm64/$(APP_NAME).app
ZIP_PATH = out/$(APP_NAME)-darwin-arm64.zip

# Default target
help:
	@echo "Electron App Commands:"
	@echo "  make dev            - Start development server"
	@echo "  make build          - Build, sign and notarize for macOS"
	@echo "  make build-unsigned - Build without signing (for dev)"
	@echo "  make sign           - Sign the built app"
	@echo "  make notarize       - Notarize the signed app"
	@echo "  make dist           - Create distributable (zip)"
	@echo "  make clean          - Remove build artifacts"
	@echo "  make install        - Install dependencies"
	@echo "  make open           - Open built app"

# Development
dev start:
	cd ../.. && pnpm --filter @djangocfg/electron run start

# Build, sign and notarize (production)
build: clean package sign notarize
	@echo "✅ Build complete: $(APP_PATH)"

# Build without signing (development)
build-unsigned: clean package
	@echo "Build complete (unsigned): $(APP_PATH)"

# Package only
package:
	cd ../.. && pnpm --filter @djangocfg/electron run package

# Sign the app
sign:
	@echo "🔏 Signing app..."
	codesign --force --deep --options runtime --sign "$(SIGN_IDENTITY)" \
		--entitlements entitlements.plist "$(APP_PATH)"
	@echo "✅ App signed"

# Notarize the app (requires APPLE_ID and APPLE_PASSWORD)
notarize:
	@if [ -z "$(APPLE_ID)" ] || [ -z "$(APPLE_PASSWORD)" ]; then \
		echo "⚠️  Skipping notarization (APPLE_ID or APPLE_PASSWORD not set)"; \
	else \
		echo "📤 Creating zip for notarization..."; \
		ditto -c -k --keepParent "$(APP_PATH)" "$(ZIP_PATH)"; \
		echo "📤 Submitting to Apple for notarization..."; \
		xcrun notarytool submit "$(ZIP_PATH)" \
			--apple-id "$(APPLE_ID)" \
			--password "$(APPLE_PASSWORD)" \
			--team-id "$(APPLE_TEAM_ID)" \
			--wait; \
		echo "📎 Stapling notarization ticket..."; \
		xcrun stapler staple "$(APP_PATH)"; \
		rm -f "$(ZIP_PATH)"; \
		echo "✅ Notarization complete"; \
	fi

# Create distributable
dist: build
	cd ../.. && pnpm --filter @djangocfg/electron run make
	@echo "Distributable: out/make/zip/darwin/arm64/"

# Open built app
open:
	@if [ -d "$(APP_PATH)" ]; then \
		open "$(APP_PATH)"; \
	else \
		echo "App not found. Run 'make build' first."; \
	fi

# Clean
clean:
	rm -rf out .vite node_modules/.vite

clean-all: clean
	rm -rf node_modules package-lock.json

# Install
install:
	cd ../.. && pnpm install

# Lint
lint:
	cd ../.. && pnpm --filter @djangocfg/electron run lint
