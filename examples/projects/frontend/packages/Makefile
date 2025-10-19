# Makefile for publishing @djangocfg packages to npm
#
# Usage:
#   make build          - Build all packages
#   make publish        - Publish all packages to npm (interactive)
#   make publish-minor  - Bump minor version and publish
#   make publish-patch  - Bump patch version and publish
#   make publish-major  - Bump major version and publish
#   make clean          - Clean all dist folders
#
# How it works:
#   - Creates temporary .tmp directory
#   - Copies packages to .tmp
#   - Replaces all workspace:* with actual versions
#   - Publishes from .tmp (keeps local workspace:* intact)

# Package directories
PACKAGES := api eslint-config layouts markdown og-image typescript-config ui
TMP_DIR := .tmp

# Colors for output
GREEN  := \033[0;32m
YELLOW := \033[0;33m
RED    := \033[0;31m
NC     := \033[0m # No Color

.PHONY: help
help:
	@echo "$(GREEN)@djangocfg packages - NPM Publishing$(NC)"
	@echo ""
	@echo "$(YELLOW)Available commands:$(NC)"
	@echo "  make build           - Build all packages locally"
	@echo "  make publish         - Publish all packages (interactive)"
	@echo "  make publish-patch   - Bump patch version and publish (1.0.0 -> 1.0.1)"
	@echo "  make publish-minor   - Bump minor version and publish (1.0.0 -> 1.1.0)"
	@echo "  make publish-major   - Bump major version and publish (1.0.0 -> 2.0.0)"
	@echo "  make clean           - Clean all dist folders and tmp"
	@echo "  make check           - Check npm login status"
	@echo "  make list            - Show all packages and versions"
	@echo ""
	@echo "$(YELLOW)How publishing works:$(NC)"
	@echo "  1. Creates temporary .tmp directory"
	@echo "  2. Copies all packages to .tmp"
	@echo "  3. Replaces workspace:* with actual npm versions"
	@echo "  4. Builds and publishes from .tmp"
	@echo "  5. Cleans up .tmp (local files stay unchanged)"
	@echo ""

.PHONY: check
check:
	@echo "$(YELLOW)Checking npm login status...$(NC)"
	@npm whoami || (echo "$(RED)Not logged in to npm. Run: npm login$(NC)" && exit 1)
	@echo "$(GREEN)✓ Logged in to npm$(NC)"

.PHONY: clean
clean:
	@echo "$(YELLOW)Cleaning dist folders and tmp...$(NC)"
	@for pkg in $(PACKAGES); do \
		if [ -d "$$pkg/dist" ]; then \
			echo "  Cleaning $$pkg/dist"; \
			rm -rf "$$pkg/dist"; \
		fi; \
	done
	@if [ -d "$(TMP_DIR)" ]; then \
		echo "  Cleaning $(TMP_DIR)"; \
		rm -rf "$(TMP_DIR)"; \
	fi
	@echo "$(GREEN)✓ Clean complete$(NC)"

.PHONY: build
build: clean
	@echo "$(YELLOW)Building all packages...$(NC)"
	@for pkg in $(PACKAGES); do \
		echo ""; \
		if grep -q '"build"' "$$pkg/package.json" 2>/dev/null; then \
			echo "$(YELLOW)Building $$pkg...$(NC)"; \
			cd "$$pkg" && pnpm build && cd ..; \
			if [ $$? -eq 0 ]; then \
				echo "$(GREEN)✓ $$pkg built successfully$(NC)"; \
			else \
				echo "$(RED)✗ $$pkg build failed$(NC)"; \
				exit 1; \
			fi; \
		else \
			echo "$(YELLOW)Skipping $$pkg (no build script)$(NC)"; \
		fi; \
	done
	@echo ""
	@echo "$(GREEN)✓ All packages processed successfully$(NC)"

.PHONY: prepare-tmp
prepare-tmp:
	@echo "$(YELLOW)Preparing temporary directory for publishing...$(NC)"
	@rm -rf "$(TMP_DIR)"
	@mkdir -p "$(TMP_DIR)"
	@for pkg in $(PACKAGES); do \
		echo "  Copying $$pkg to $(TMP_DIR)/$$pkg"; \
		rsync -a --exclude 'node_modules' --exclude 'dist' --exclude '.turbo' \
			"$$pkg/" "$(TMP_DIR)/$$pkg/"; \
	done
	@echo "$(YELLOW)Replacing workspace:* with actual versions...$(NC)"
	@for pkg in $(PACKAGES); do \
		version=$$(grep '"version"' "$$pkg/package.json" | head -1 | sed 's/.*: "\(.*\)".*/\1/'); \
		echo "  @djangocfg/$$pkg@$$version"; \
		find "$(TMP_DIR)" -name "package.json" -type f -exec sed -i '' \
			's|"@djangocfg/'$$pkg'": "workspace:\*"|"@djangocfg/'$$pkg'": "^'$$version'"|g' {} \; ; \
	done
	@echo "$(GREEN)✓ Temporary directory prepared$(NC)"

.PHONY: build-tmp
build-tmp: prepare-tmp
	@echo "$(YELLOW)Building packages in original directories (with monorepo deps)...$(NC)"
	@for pkg in $(PACKAGES); do \
		echo ""; \
		if grep -q '"build"' "$$pkg/package.json" 2>/dev/null; then \
			echo "$(YELLOW)Building $$pkg...$(NC)"; \
			cd "$$pkg" && pnpm build && cd ..; \
			if [ $$? -eq 0 ]; then \
				echo "$(GREEN)✓ $$pkg built successfully$(NC)"; \
				echo "  Copying dist to $(TMP_DIR)/$$pkg/"; \
				cp -r "$$pkg/dist" "$(TMP_DIR)/$$pkg/"; \
			else \
				echo "$(RED)✗ $$pkg build failed$(NC)"; \
				exit 1; \
			fi; \
		else \
			echo "$(YELLOW)Skipping $$pkg (no build script)$(NC)"; \
		fi; \
	done
	@echo ""
	@echo "$(GREEN)✓ All packages built successfully$(NC)"

.PHONY: publish
publish: check build-tmp
	@echo "$(YELLOW)Publishing all packages to npm from $(TMP_DIR)...$(NC)"
	@echo "$(RED)Warning: This will publish packages with current versions$(NC)"
	@read -p "Continue? (y/n) " -n 1 -r; \
	echo ""; \
	if [[ ! $$REPLY =~ ^[Yy]$$ ]]; then \
		echo "$(YELLOW)Publish cancelled$(NC)"; \
		rm -rf "$(TMP_DIR)"; \
		exit 1; \
	fi
	@for pkg in $(PACKAGES); do \
		if [ -d "$(TMP_DIR)/$$pkg" ]; then \
			echo ""; \
			echo "$(YELLOW)Publishing $$pkg...$(NC)"; \
			(cd "$(TMP_DIR)/$$pkg" && npm publish --access public); \
			if [ $$? -eq 0 ]; then \
				echo "$(GREEN)✓ $$pkg published$(NC)"; \
			else \
				echo "$(RED)✗ $$pkg publish failed$(NC)"; \
			fi; \
		else \
			echo "$(RED)✗ $(TMP_DIR)/$$pkg not found$(NC)"; \
		fi; \
	done
	@echo ""
	@echo "$(GREEN)✓ Publishing complete$(NC)"
	@echo "$(YELLOW)Cleaning up $(TMP_DIR)...$(NC)"
	@rm -rf "$(TMP_DIR)"
	@echo "$(GREEN)✓ Cleanup complete$(NC)"

.PHONY: publish-patch
publish-patch: check
	@echo "$(YELLOW)Bumping patch version and publishing...$(NC)"
	@$(MAKE) bump-version VERSION=patch
	@$(MAKE) publish

.PHONY: publish-minor
publish-minor: check
	@echo "$(YELLOW)Bumping minor version and publishing...$(NC)"
	@$(MAKE) bump-version VERSION=minor
	@$(MAKE) publish

.PHONY: publish-major
publish-major: check
	@echo "$(YELLOW)Bumping major version and publishing...$(NC)"
	@$(MAKE) bump-version VERSION=major
	@$(MAKE) publish

.PHONY: bump-version
bump-version:
	@for pkg in $(PACKAGES); do \
		if [ -f "$$pkg/package.json" ]; then \
			echo "$(YELLOW)Bumping $(VERSION) version in $$pkg...$(NC)"; \
			current_version=$$(grep '"version"' "$$pkg/package.json" | head -1 | sed 's/.*: "\(.*\)".*/\1/'); \
			echo "  Current: $$current_version"; \
			major=$$(echo $$current_version | cut -d. -f1); \
			minor=$$(echo $$current_version | cut -d. -f2); \
			patch=$$(echo $$current_version | cut -d. -f3); \
			if [ "$(VERSION)" = "patch" ]; then \
				patch=$$(($$patch + 1)); \
			elif [ "$(VERSION)" = "minor" ]; then \
				minor=$$(($$minor + 1)); \
				patch=0; \
			elif [ "$(VERSION)" = "major" ]; then \
				major=$$(($$major + 1)); \
				minor=0; \
				patch=0; \
			fi; \
			new_version="$$major.$$minor.$$patch"; \
			echo "  New: $$new_version"; \
			sed -i '' "s/\"version\": \"$$current_version\"/\"version\": \"$$new_version\"/" "$$pkg/package.json"; \
			echo "$(GREEN)✓ $$pkg bumped to $$new_version$(NC)"; \
		else \
			echo "$(RED)✗ $$pkg/package.json not found$(NC)"; \
		fi; \
	done

.PHONY: list
list:
	@echo "$(YELLOW)@djangocfg packages:$(NC)"
	@for pkg in $(PACKAGES); do \
		if [ -f "$$pkg/package.json" ]; then \
			version=$$(grep '"version"' "$$pkg/package.json" | head -1 | sed 's/.*: "\(.*\)".*/\1/'); \
			echo "  @djangocfg/$$pkg@$$version"; \
		fi; \
	done

# Default target
.DEFAULT_GOAL := help
