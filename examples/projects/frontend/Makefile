# Makefile for django_admin project
#
# Usage:
#   make update     - Update @djangocfg dependencies to latest
#   make install    - Install dependencies
#   make clean      - Clean node_modules and lock file

# Colors
GREEN  := \033[0;32m
YELLOW := \033[0;33m
RED    := \033[0;31m
NC     := \033[0m # No Color

.PHONY: help
help:
	@echo "$(GREEN)Django Admin - Dependencies Management$(NC)"
	@echo ""
	@echo "$(YELLOW)Available commands:$(NC)"
	@echo "  make update     - Update @djangocfg packages to latest"
	@echo "  make install    - Install dependencies"
	@echo "  make clean      - Clean node_modules and pnpm-lock.yaml"
	@echo ""

.PHONY: update
update:
	@echo "$(YELLOW)Updating @djangocfg dependencies...$(NC)"
	@pnpm update '@djangocfg/*@latest'
	@echo "$(GREEN)✓ Dependencies updated$(NC)"

.PHONY: install
install:
	@echo "$(YELLOW)Installing dependencies...$(NC)"
	@pnpm install
	@echo "$(GREEN)✓ Dependencies installed$(NC)"

.PHONY: clean
clean:
	@echo "$(YELLOW)Cleaning node_modules and pnpm-lock.yaml...$(NC)"
	@rm -rf node_modules pnpm-lock.yaml
	@echo "$(GREEN)✓ Clean complete$(NC)"

# Default target
.DEFAULT_GOAL := help
