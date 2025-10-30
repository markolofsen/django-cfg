# Django-CFG Docker Management
# Minimalist Makefile for essential Docker operations

.PHONY: help build up down restart logs status local prod

.DEFAULT_GOAL := help

# Colors
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[1;33m
NC := \033[0m

##@ General

help: ## Display this help
	@echo "$(BLUE)Django-CFG Docker Management$(NC)"
	@echo ""
	@awk 'BEGIN {FS = ":.*##"; printf "Usage:\n  make $(GREEN)<target>$(NC)\n"} /^[a-zA-Z_0-9-]+:.*?##/ { printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2 } /^##@/ { printf "\n$(YELLOW)%s$(NC)\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

##@ Build & Run

build: ## Build all Docker images (local)
	@echo "$(BLUE)Building images for local development...$(NC)"
	@docker compose -f docker-compose-local.yaml --env-file .env.local --env-file .env.local build

rebuild: down ## Full rebuild without cache (local)
	@echo "$(BLUE)Rebuilding from scratch...$(NC)"
	@docker compose -f docker-compose-local.yaml --env-file .env.local --env-file .env.local build --no-cache
	@docker compose -f docker-compose-local.yaml --env-file .env.local --env-file .env.local up -d

rebuild-frontend: ## Rebuild only frontend (local)
	@echo "$(BLUE)Rebuilding frontend...$(NC)"
	@docker compose -f docker-compose-local.yaml --env-file .env.local --env-file .env.local build --no-cache frontend-demo frontend-web

##@ Services (Local)

local: ## Start local development services
	@echo "$(BLUE)Starting local development services...$(NC)"
	@docker compose -f docker-compose-local.yaml --env-file .env.local --env-file .env.local up -d

up: local ## Alias for 'local'

down: ## Stop all services
	@echo "$(YELLOW)Stopping services...$(NC)"
	@docker compose -f docker-compose-local.yaml --env-file .env.local down
	@docker compose -f docker-compose-production.yaml down 2>/dev/null || true

restart: ## Restart all services (local)
	@docker compose -f docker-compose-local.yaml --env-file .env.local --env-file .env.local restart

status: ## Show service status
	@docker compose -f docker-compose-local.yaml --env-file .env.local ps

logs: ## Show logs (all services)
	@docker compose -f docker-compose-local.yaml --env-file .env.local logs -f --tail=100

##@ Services (Production)

prod: ## Start production services
	@echo "$(BLUE)Starting production services...$(NC)"
	@docker compose -f docker-compose-production.yaml --env-file .env.prod up -d

prod-build: ## Build production images
	@echo "$(BLUE)Building production images...$(NC)"
	@docker compose -f docker-compose-production.yaml --env-file .env.prod build

prod-down: ## Stop production services
	@echo "$(YELLOW)Stopping production services...$(NC)"
	@docker compose -f docker-compose-production.yaml down

##@ Quick Start

dev: build local status ## Full dev setup
	@echo ""
	@echo "$(GREEN)✓ Ready!$(NC)"
	@echo ""
	@echo "$(BLUE)Access points:$(NC)"
	@echo "  • Django API:     http://localhost:7301/cfg/health/"
	@echo "  • Demo Frontend:  http://localhost:7310/"
	@echo "  • Centrifugo:     http://localhost:7320/"
	@echo "  • Traefik:        http://localhost:7332/"
	@echo ""

quick: local status ## Quick start (no rebuild)
	@echo "$(GREEN)Services started$(NC)"

##@ Background Services (Redis, Centrifugo, ReArq)

services: ## Start background services (Redis, Centrifugo, ReArq)
	@echo "$(BLUE)Starting background services (Redis, Centrifugo, ReArq)...$(NC)"
	@docker compose -f docker-compose-local-services.yml --env-file .env.local up -d

services-down: ## Stop background services
	@echo "$(YELLOW)Stopping background services...$(NC)"
	@docker compose -f docker-compose-local-services.yml down

services-restart: ## Restart background services
	@docker compose -f docker-compose-local-services.yml --env-file .env.local restart

services-logs: ## Show logs for background services
	@docker compose -f docker-compose-local-services.yml logs -f --tail=100

services-status: ## Show status of background services
	@docker compose -f docker-compose-local-services.yml ps

services-build: ## Build background services
	@echo "$(BLUE)Building background services...$(NC)"
	@docker compose -f docker-compose-local-services.yml --env-file .env.local build

rearq: services ## Start ReArq (task queue) with services
	@echo ""
	@echo "$(GREEN)✓ ReArq is ready!$(NC)"
	@echo ""
	@echo "$(BLUE)Access points:$(NC)"
	@echo "  • ReArq Web UI:   http://localhost:7380/"
	@echo "  • API Docs:       http://localhost:7380/docs"
	@echo "  • Redis:          localhost:7379"
	@echo "  • Centrifugo:     http://localhost:7320/"
	@echo ""
