# Django-CFG Docker Management
# Domain: djangocfg.com (Production environment)

.PHONY: help \
        build build-django build-frontend \
        up up-django up-infra up-frontend up-reset \
        down down-django down-infra down-frontend \
        restart status logs logs-django logs-rq \
        createdb dropdb migrate shell bash \
        prod deploy deploy-django deploy-reset \
        health collectstatic reset-db

.DEFAULT_GOAL := help

# Colors
BLUE   := \033[0;34m
GREEN  := \033[0;32m
YELLOW := \033[1;33m
RED    := \033[0;31m
NC     := \033[0m

# Compose definitions
ENV_PROD  := --env-file .env.prod
ENV_LOCAL := --env-file .env.local

DC_DJANGO   := docker compose -f docker-compose-prod.django.yaml   $(ENV_PROD)
DC_INFRA    := docker compose -f docker-compose-prod.infra.yaml    $(ENV_PROD)
DC_FRONTEND := docker compose -f docker-compose-prod.frontend.yaml $(ENV_PROD)
DC_LOCAL    := docker compose -f docker-compose-local.yaml         $(ENV_LOCAL)

##@ General

help: ## Display this help
	@echo "$(BLUE)Django-CFG Docker Management$(NC)"
	@echo "$(YELLOW)Domain: djangocfg.com$(NC)"
	@echo ""
	@awk 'BEGIN {FS = ":.*##"; printf "Usage:\n  make $(GREEN)<target>$(NC)\n"} /^[a-zA-Z_0-9-]+:.*?##/ { printf "  $(GREEN)%-22s$(NC) %s\n", $$1, $$2 } /^##@/ { printf "\n$(YELLOW)%s$(NC)\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

##@ Build

build: build-django build-frontend ## Build all production images

build-django: ## Build Django image
	@echo "$(BLUE)Building django-cfg-django image...$(NC)"
	@$(DC_DJANGO) build django

build-frontend: ## Build frontend image
	@echo "$(BLUE)Building django-cfg-frontend image...$(NC)"
	@$(DC_FRONTEND) build frontend

##@ Services

up: up-django up-infra up-frontend ## Start all production services

up-django: ## Start Django group (django, rq-worker, rq-scheduler, grpc)
	@echo "$(BLUE)Starting Django group...$(NC)"
	@$(DC_DJANGO) up -d

up-infra: ## Start infra group (centrifugo)
	@echo "$(BLUE)Starting infra group...$(NC)"
	@$(DC_INFRA) up -d

up-frontend: ## Start frontend group (frontend)
	@echo "$(BLUE)Starting frontend group...$(NC)"
	@$(DC_FRONTEND) up -d

up-reset: ## Start frontend group including demo-resetter
	@echo "$(BLUE)Starting frontend group with demo-resetter...$(NC)"
	@$(DC_FRONTEND) --profile demo-reset up -d

down: down-django down-infra down-frontend ## Stop all production services

down-django: ## Stop Django group
	@echo "$(YELLOW)Stopping Django group...$(NC)"
	@$(DC_DJANGO) down

down-infra: ## Stop infra group
	@echo "$(YELLOW)Stopping infra group...$(NC)"
	@$(DC_INFRA) down

down-frontend: ## Stop frontend group
	@echo "$(YELLOW)Stopping frontend group...$(NC)"
	@$(DC_FRONTEND) --profile demo-reset down

restart: ## Restart all production services
	@$(DC_DJANGO) restart
	@$(DC_INFRA) restart
	@$(DC_FRONTEND) restart

status: ## Show service status (all groups)
	@$(DC_DJANGO) ps
	@$(DC_INFRA) ps
	@$(DC_FRONTEND) ps

logs: ## Show logs for all Django-group services
	@$(DC_DJANGO) logs -f --tail=100

logs-django: ## Show django container logs
	@$(DC_DJANGO) logs -f django --tail=100

logs-rq: ## Show rq-worker logs
	@$(DC_DJANGO) logs -f rq-worker --tail=100

##@ Health

health: ## Wait until django-cfg-django is healthy
	@echo "$(BLUE)Waiting for django-cfg-django to be healthy...$(NC)"
	@until [ "$$(docker inspect -f '{{.State.Health.Status}}' django-cfg-django 2>/dev/null)" = "healthy" ]; do \
		echo "  ...waiting"; \
		sleep 5; \
	done
	@echo "$(GREEN)django-cfg-django is healthy$(NC)"

##@ Database

createdb: ## Create djangocfg database with pgvector
	@echo "$(BLUE)Creating djangocfg database...$(NC)"
	@docker exec shared-db-postgres psql -U postgres -c "CREATE DATABASE djangocfg;" 2>/dev/null || echo "$(YELLOW)Database already exists$(NC)"
	@docker exec shared-db-postgres psql -U postgres -d djangocfg -c "CREATE EXTENSION IF NOT EXISTS vector;" 2>/dev/null || true
	@echo "$(GREEN)Database ready$(NC)"

dropdb: ## Drop djangocfg database (DESTRUCTIVE!)
	@echo "$(RED)Dropping djangocfg database...$(NC)"
	@docker exec shared-db-postgres psql -U postgres -c "DROP DATABASE IF EXISTS djangocfg;"

migrate: ## Run Django migrations
	@echo "$(BLUE)Running migrations...$(NC)"
	@docker exec django-cfg-django uv run python manage.py migrate

##@ Deployment

prod: up-django health up-infra up-frontend ## Start full production stack (django first, then infra + frontend)
	@echo "$(GREEN)Production stack is up$(NC)"

deploy-django: build-django up-django health migrate ## Build + start Django group + wait healthy + migrate
	@echo ""
	@echo "$(GREEN)Django group deployed!$(NC)"
	@echo ""
	@echo "$(BLUE)Endpoints:$(NC)"
	@echo "  API:       https://api.djangocfg.com"
	@echo "  gRPC:      https://grpc.djangocfg.com"
	@echo "  WebSocket: https://ws.djangocfg.com"
	@echo ""

deploy: createdb build up-django health migrate up-infra up-frontend status ## Full production deployment
	@echo ""
	@echo "$(GREEN)Django-CFG deployed!$(NC)"
	@echo ""
	@echo "$(BLUE)Endpoints:$(NC)"
	@echo "  API:       https://api.djangocfg.com"
	@echo "  gRPC:      https://grpc.djangocfg.com"
	@echo "  WebSocket: https://ws.djangocfg.com"
	@echo ""

deploy-reset: createdb build up-django health migrate up-infra up-reset status ## Full deployment with demo-resetter
	@echo ""
	@echo "$(GREEN)Django-CFG deployed with auto-reset!$(NC)"

##@ Maintenance

shell: ## Open Django shell
	@docker exec -it django-cfg-django uv run python manage.py shell

bash: ## Open bash in django container
	@docker exec -it django-cfg-django bash

reset-db: ## Manually reset demo database
	@echo "$(YELLOW)Resetting demo database...$(NC)"
	@docker exec django-cfg-django uv run python manage.py flush --no-input
	@docker exec django-cfg-django uv run python manage.py migrate
	@docker exec django-cfg-django uv run python manage.py createsuperuser --noinput || true
	@echo "$(GREEN)Database reset complete$(NC)"

collectstatic: ## Collect static files
	@docker exec django-cfg-django uv run python manage.py collectstatic --noinput
