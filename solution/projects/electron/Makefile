.PHONY: dev start build package make sign clean install lint help

# Default target
help:
	@echo "Electron App Commands:"
	@echo "  make dev       - Start development server"
	@echo "  make build     - Build production bundles"
	@echo "  make package   - Package app (no installer)"
	@echo "  make make      - Create distributable (zip/dmg)"
	@echo "  make sign      - Build and sign for macOS"
	@echo "  make clean     - Remove build artifacts"
	@echo "  make install   - Install dependencies"
	@echo "  make lint      - Run linter"
	@echo "  make open      - Open built app"

# Development
dev start:
	npm run start

# Build
build:
	npm run package

package:
	npm run package

make:
	npm run make

# Sign and build for macOS
sign:
	@rm -rf out
	npm run make

# Open built app
open:
	@if [ -d "out/electron-darwin-arm64/electron.app" ]; then \
		open "out/electron-darwin-arm64/electron.app"; \
	elif [ -d "out/electron-darwin-x64/electron.app" ]; then \
		open "out/electron-darwin-x64/electron.app"; \
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
	npm install

# Lint
lint:
	npm run lint
