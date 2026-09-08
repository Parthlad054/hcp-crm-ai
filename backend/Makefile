.PHONY: run dev test test-unit test-integration test-smoke migrate seed docker-up docker-down lint format help

# ── Development ────────────────────────────────────────────────────────────────

run:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev: run  ## Alias for run

# ── Testing ────────────────────────────────────────────────────────────────────

test:  ## Run all tests
	pytest tests/ -v --tb=short

test-unit:  ## Run only unit tests
	pytest tests/unit/ -v --tb=short

test-integration:  ## Run only integration tests
	pytest tests/integration/ -v --tb=short

test-smoke:  ## Run smoke tests (fast, for CI/CD)
	pytest tests/smoke/ -v --tb=short

test-cov:  ## Run tests with coverage report
	pytest tests/ --cov=app --cov-report=term-missing --cov-report=html

# ── Database ───────────────────────────────────────────────────────────────────

migrate:  ## Apply all pending Alembic migrations
	alembic upgrade head

migrate-down:  ## Rollback one Alembic migration
	alembic downgrade -1

migration:  ## Create a new Alembic migration (usage: make migration msg="add column foo")
	alembic revision --autogenerate -m "$(msg)"

seed:  ## Seed the database with sample data
	python scripts/seed_db.py

# ── Docker ─────────────────────────────────────────────────────────────────────

docker-up:  ## Build and start all Docker services
	docker-compose up --build

docker-up-d:  ## Build and start all Docker services in detached mode
	docker-compose up --build -d

docker-down:  ## Stop and remove Docker containers
	docker-compose down

docker-logs:  ## Tail logs from the API container
	docker-compose logs -f api

# ── Code Quality ───────────────────────────────────────────────────────────────

lint:  ## Run ruff linter
	ruff check app/ tests/

format:  ## Auto-format with ruff
	ruff format app/ tests/

# ── Help ───────────────────────────────────────────────────────────────────────

help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'
