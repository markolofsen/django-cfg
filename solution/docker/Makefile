# DemoCFG Docker Management
# Domain: democfg.com (Demo environment with auto-reset)

.PHONY: help build up down restart logs status deploy createdb migrate

.DEFAULT_GOAL := help

# Colors
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[1;33m
RED := \033[0;31m
NC := \033[0m

##@ General

help: ## Display this help
	@echo "$(BLUE)DemoCFG Docker Management$(NC)"
	@echo "$(YELLOW)Domain: democfg.com$(NC)"
	@echo ""
	@awk 'BEGIN {FS = ":.*##"; printf "Usage:\n  make $(GREEN)<target>$(NC)\n"} /^[a-zA-Z_0-9-]+:.*?##/ { printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2 } /^##@/ { printf "\n$(YELLOW)%s$(NC)\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

##@ Build

build: ## Build all Docker images
	@echo "$(BLUE)Building DemoCFG images...$(NC)"
	@docker compose build

build-api: ## Build only API image
	@echo "$(BLUE)Building API image...$(NC)"
	@docker compose build api

build-frontend: ## Build frontend images
	@echo "$(BLUE)Building frontend images...$(NC)"
	@docker compose build frontend playground

##@ Services

up: ## Start all services
	@echo "$(BLUE)Starting DemoCFG services...$(NC)"
	@docker compose up -d

up-reset: ## Start all services including resetter
	@echo "$(BLUE)Starting DemoCFG services with resetter...$(NC)"
	@docker compose --profile demo-reset up -d

down: ## Stop all services
	@echo "$(YELLOW)Stopping DemoCFG services...$(NC)"
	@docker compose --profile demo-reset down

restart: ## Restart all services
	@docker compose restart

status: ## Show service status
	@docker compose ps

logs: ## Show logs (all services)
	@docker compose logs -f --tail=100

logs-api: ## Show API logs
	@docker compose logs -f api --tail=100

logs-rq: ## Show RQ worker logs
	@docker compose logs -f rq-worker --tail=100

##@ Database

createdb: ## Create democfg database with pgvector
	@echo "$(BLUE)Creating democfg database...$(NC)"
	@docker exec shared-db-postgres psql -U postgres -c "CREATE DATABASE democfg;" 2>/dev/null || echo "$(YELLOW)Database already exists$(NC)"
	@docker exec shared-db-postgres psql -U postgres -d democfg -c "CREATE EXTENSION IF NOT EXISTS vector;" 2>/dev/null || true
	@echo "$(GREEN)Database ready$(NC)"

dropdb: ## Drop democfg database (DESTRUCTIVE!)
	@echo "$(RED)Dropping democfg database...$(NC)"
	@docker exec shared-db-postgres psql -U postgres -c "DROP DATABASE IF EXISTS democfg;"

migrate: ## Run Django migrations
	@echo "$(BLUE)Running migrations...$(NC)"
	@docker exec democfg-api poetry run python manage.py migrate

##@ Deployment

deploy: createdb build up migrate status ## Full deployment
	@echo ""
	@echo "$(GREEN)DemoCFG deployed!$(NC)"
	@echo ""
	@echo "$(BLUE)Endpoints:$(NC)"
	@echo "  API:        https://api.democfg.com"
	@echo "  Frontend:   https://democfg.com"
	@echo "  Playground: https://playground.democfg.com"
	@echo "  WebSocket:  https://ws.democfg.com"
	@echo "  gRPC:       https://grpc.democfg.com"
	@echo ""

deploy-reset: createdb build up-reset migrate status ## Full deployment with resetter
	@echo ""
	@echo "$(GREEN)DemoCFG deployed with auto-reset!$(NC)"

##@ Maintenance

shell: ## Open Django shell
	@docker exec -it democfg-api poetry run python manage.py shell

bash: ## Open bash in API container
	@docker exec -it democfg-api bash

reset-db: ## Manually reset demo database
	@echo "$(YELLOW)Resetting demo database...$(NC)"
	@docker exec democfg-api poetry run python manage.py flush --no-input
	@docker exec democfg-api poetry run python manage.py migrate
	@docker exec democfg-api poetry run python manage.py createsuperuser --noinput || true
	@echo "$(GREEN)Database reset complete$(NC)"

collectstatic: ## Collect static files
	@docker exec democfg-api poetry run python manage.py collectstatic --noinput
