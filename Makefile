.PHONY: help install dev migrate-init migrate upgrade downgrade celery test format lint clean

# Variables
PYTHON := uv run python
UVICORN := uv run uvicorn
ALEMBIC := uv run alembic
CELERY := uv run celery
PYTEST := uv run pytest
BLACK := uv run black
RUFF := uv run ruff

help:
	@echo "Available commands:"
	@echo "  make install        - Install all dependencies"
	@echo "  make dev           - Run development server"
	@echo "  make migrate-init  - Initialize alembic migrations"
	@echo "  make migrate       - Create a new migration"
	@echo "  make upgrade       - Apply migrations"
	@echo "  make downgrade     - Rollback last migration"
	@echo "  make celery        - Run celery worker"
	@echo "  make celery-beat   - Run celery beat scheduler"
	@echo "  make test          - Run tests"
	@echo "  make format        - Format code with black"
	@echo "  make lint          - Lint code with ruff"
	@echo "  make clean         - Clean cache files"

install:
	uv sync
	

dev:
	$(UVICORN) app.main:app --reload --host 0.0.0.0 --port 8000

migrate-init:
	$(ALEMBIC) init -t async alembic

migrate:
	@read -p "Enter migration message: " msg; \
	$(ALEMBIC) revision --autogenerate -m "$$msg"

upgrade:
	$(ALEMBIC) upgrade head

downgrade:
	$(ALEMBIC) downgrade -1

celery:
	$(CELERY) -A app.celery_app worker --loglevel=info

celery-beat:
	$(CELERY) -A app.celery_app beat --loglevel=info

celery-flower:
	$(CELERY) -A app.celery_app flower --port=5555

test:
	$(PYTEST) -v

test-cov:
	$(PYTEST) --cov=app --cov-report=html --cov-report=term

format:
	$(BLACK) app/
	$(RUFF) check app/ --fix

lint:
	$(RUFF) check app/
	$(BLACK) app/ --check

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	rm -rf htmlcov/
	rm -rf .coverage

# Development workflow shortcuts
.PHONY: run-all stop-all

run-all:
	@echo "Starting all services..."
	@$(MAKE) dev & $(MAKE) celery & $(MAKE) celery-beat &

db-reset:
	@echo "Resetting database..."
	$(ALEMBIC) downgrade base
	$(ALEMBIC) upgrade head
	@echo "Database reset complete!"

db-seed:
	$(PYTHON) -m app.scripts.seed_db

# Docker shortcuts (if you're using Docker)
.PHONY: docker-build docker-up docker-down

docker-build:
	docker-compose build

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down