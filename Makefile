.PHONY: help up down build restart logs ps clean test lint format shell

# Default target
help:
	@echo "AgroVision — Farm Management Platform (modular monolith)"
	@echo ""
	@echo "Usage: make <target>"
	@echo ""
	@echo "Infrastructure:"
	@echo "  up             Start the stack (detached)"
	@echo "  down           Stop the stack"
	@echo "  build          Build the Docker image"
	@echo "  restart        Rebuild and restart the stack"
	@echo "  logs           Tail logs"
	@echo "  ps             Show running containers"
	@echo "  clean          Remove containers, volumes, and orphans"
	@echo ""
	@echo "Development:"
	@echo "  lint           Run ruff linter against app/"
	@echo "  format         Run ruff formatter against app/"
	@echo "  shell          Open a shell inside the running monolith container"
	@echo ""
	@echo "Note (M7, 2026-06-18): the 8 original microservices were migrated into"
	@echo "the modular monolith (app/) and removed. Alembic-on-startup wiring for"
	@echo "the monolith is deferred (see migration_decisions.md MD-008) — there is"
	@echo "currently no 'make migrate' target. tests/e2e/* is not yet portable to"
	@echo "app/<module> (see repository_cleanup_backlog.md CLEAN-05), so there is"
	@echo "no 'make test' target here either; run pytest directly against tests/."

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

# ── Development ──────────────────────────────────────────────────────────────

lint:
	docker compose exec monolith ruff check app/

format:
	docker compose exec monolith ruff format app/

shell:
	docker compose exec monolith /bin/bash
