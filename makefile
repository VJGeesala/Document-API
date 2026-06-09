.PHONY: help setup test test-cov lint format type-check check up down restart logs build clean

# Default target — runs when you type just `make`
help:
	@echo "Document API — available commands:"
	@echo ""
	@echo "  Setup"
	@echo "    make setup        Install dependencies in venv (run once after clone)"
	@echo "    make clean        Remove venv, caches, and database files"
	@echo ""
	@echo "  Quality checks"
	@echo "    make format       Auto-format code with black"
	@echo "    make lint         Check formatting without modifying files"
	@echo "    make type-check   Run mypy type checker"
	@echo "    make test         Run all tests"
	@echo "    make test-cov     Run tests with coverage report"
	@echo "    make check        Run all checks (lint + type-check + test-cov)"
	@echo ""
	@echo "  Docker"
	@echo "    make build        Build the Docker image"
	@echo "    make up           Start services with docker-compose"
	@echo "    make down         Stop and remove containers"
	@echo "    make restart      Restart all services"
	@echo "    make logs         Tail logs from running containers"

# ─── Setup ──────────────────────────────────────────────────────────────────

setup:
	@echo "Creating venv with Python 3.12..."
	python3.12 -m venv venv
	@echo "Installing dependencies..."
	./venv/bin/pip install --upgrade pip
	./venv/bin/pip install -r requirements.txt
	@echo ""
	@echo "Setup complete. Activate with: source venv/bin/activate"

clean:
	rm -rf venv .pytest_cache .coverage htmlcov
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -f documents.db test.db
	@echo "Cleaned"

# ─── Quality Checks ─────────────────────────────────────────────────────────

format:
	./venv/bin/black app/ tests/

lint:
	./venv/bin/black --check app/ tests/

type-check:
	./venv/bin/mypy app/ --ignore-missing-imports

test:
	./venv/bin/pytest tests/ -v

test-cov:
	./venv/bin/pytest tests/ --cov=app --cov-report=term-missing --cov-fail-under=80

check: lint type-check test-cov
	@echo ""
	@echo "All checks passed ✓"

# ─── Docker ─────────────────────────────────────────────────────────────────

build:
	docker build -t document-api:1.0.0 .

up:
	docker compose up -d
	@echo ""
	@echo "API running at http://localhost:8000"
	@echo "Docs at http://localhost:8000/docs"
	@echo "View logs with: make logs"

down:
	docker compose down

restart:
	docker compose restart

logs:
	docker compose logs -f