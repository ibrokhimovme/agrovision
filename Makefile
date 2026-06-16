.PHONY: help up down build restart logs ps clean migrate test lint format

# Default target
help:
	@echo "AgroVision — Farm Management Platform"
	@echo ""
	@echo "Usage: make <target>"
	@echo ""
	@echo "Infrastructure:"
	@echo "  up             Start all services (detached)"
	@echo "  down           Stop all services"
	@echo "  build          Build all Docker images"
	@echo "  restart        Rebuild and restart all services"
	@echo "  logs           Tail all service logs"
	@echo "  ps             Show running containers"
	@echo "  clean          Remove containers, volumes, and orphans"
	@echo ""
	@echo "Database:"
	@echo "  migrate        Run Alembic migrations for all services"
	@echo "  migrate-<svc>  Run migrations for a specific service (e.g. make migrate-identity)"
	@echo ""
	@echo "Development:"
	@echo "  test           Run all test suites"
	@echo "  lint           Run ruff linter across all services"
	@echo "  format         Run ruff formatter across all services"
	@echo "  shell-<svc>    Open a shell inside a running service container"

# ── Infrastructure ──────────────────────────────────────────────────────────

up:
	docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d

down:
	docker compose -f docker-compose.yml -f docker-compose.dev.yml down

build:
	docker compose -f docker-compose.yml -f docker-compose.dev.yml build

restart:
	$(MAKE) down
	$(MAKE) build
	$(MAKE) up

logs:
	docker compose -f docker-compose.yml -f docker-compose.dev.yml logs -f

ps:
	docker compose -f docker-compose.yml -f docker-compose.dev.yml ps

clean:
	docker compose -f docker-compose.yml -f docker-compose.dev.yml down -v --remove-orphans

# ── Database Migrations ──────────────────────────────────────────────────────

SERVICES := identity-service farm-service livestock-service inventory-service finance-service notification-service reporting-service

migrate:
	@for svc in $(SERVICES); do \
		echo "--- Running migrations for $$svc ---"; \
		docker compose exec $$svc alembic upgrade head; \
	done

migrate-%:
	docker compose exec $* alembic upgrade head

# ── Development ──────────────────────────────────────────────────────────────

test:
	@for svc in $(SERVICES); do \
		echo "--- Testing $$svc ---"; \
		docker compose exec $$svc pytest tests/ -v; \
	done

lint:
	@for svc in $(SERVICES) api-gateway; do \
		echo "--- Linting $$svc ---"; \
		docker compose exec $$svc ruff check app/ tests/; \
	done

format:
	@for svc in $(SERVICES) api-gateway; do \
		echo "--- Formatting $$svc ---"; \
		docker compose exec $$svc ruff format app/ tests/; \
	done

shell-%:
	docker compose exec $* /bin/bash
