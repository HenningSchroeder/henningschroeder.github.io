.PHONY: help up down restart logs ps build clean status test

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

up: ## Start all services
	docker compose up -d

down: ## Stop all services
	docker compose down

restart: down up ## Restart all services

logs: ## Show logs for all services
	docker compose logs -f

ps: ## Show running containers
	docker compose ps

build: ## Build/rebuild all services
	docker compose build

rebuild: ## Rebuild and restart services
	docker compose up -d --build

clean: ## Remove all containers, networks, and volumes
	docker compose down -v
	docker system prune -f

status: ## Show service status
	@echo "=== Docker Compose Services ==="
	@docker compose ps
	@echo ""
	@echo "=== Docker System Info ==="
	@docker system df

test: ## Test the deployed services
	@echo "Testing Nginx..."
	@curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" http://localhost/
	@echo ""
	@echo "Testing API root..."
	@curl -s http://localhost/api/ | python3 -m json.tool
	@echo ""
	@echo "Testing API health..."
	@curl -s http://localhost/api/health | python3 -m json.tool
	@echo ""
	@echo "Testing API info..."
	@curl -s http://localhost/api/info | python3 -m json.tool
