# Makefile for frontend monorepo
#
# Usage:
#   make update  - Clean install with latest @djangocfg packages

# Colors
GREEN  := \033[0;32m
YELLOW := \033[0;33m
NC     := \033[0m

.PHONY: update
update:
	@echo "$(YELLOW)Cleaning and updating dependencies...$(NC)"
	@rm -rf node_modules apps/*/node_modules packages/*/node_modules pnpm-lock.yaml
	@pnpm install
	@pnpm update '@djangocfg/*@latest'
	@echo "$(GREEN)Done$(NC)"

.DEFAULT_GOAL := update
