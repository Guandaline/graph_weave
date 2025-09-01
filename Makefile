# 🛠️ Makefile - Helper commands for graph_weave

# ----- Configuration Variables -----
ROOT_DIR := .
SRC_DIR := src
TEST_DIR := tests
PYTEST = poetry run pytest

# Main package name for coverage
PACKAGE_NAME = graph

# HTML coverage report command variable, using your directory
COV_REPORT_HTML = --cov-report=html:$(HTML_COV_SAVE_DIR)
# Benchmark storage variable, using your directory
BENCHMARK_STORAGE_ARG = --benchmark-storage=file://$(BENCHMARK_SAVE_DIR)

# Integration test control
RUN_INTEGRATION ?= false

# Monkeytype tools (kept from your original)
MONKEYTYPE := PYTHONPATH=src poetry run monkeytype
MONKEYTYPE_RUN := $(MONKEYTYPE) -v run helpers/run_tests.py

# ----------------------------
# DEFAULT TARGET
# ----------------------------
.DEFAULT_GOAL := help

# ----- Phony Targets (Avoids conflicts with file names) -----
.PHONY: help install run lint test format mypy commit \
	undo-release set-version release \
	monkeytype monkeytype-run monkeytype-apply \
	monkeytype-clean monkeytype-view monkeytype-trace-decorators monkeytype-all \
	no-optional check-no-optional \
	secrets secrets-scan bandit radon radon-mi radon-raw \
	isort clear infra-up infra-down up down r \ 

# ----- Main Commands -----

# 📘 Help
help: ## Shows help for available commands
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' Makefile | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-25s\033[0m %s\n", $$1, $$2}'

h: help ## Shows help for available commands

# 🚀 Setup and Run Commands
install: setup ## Alias for setup (install dependencies)
	@true

setup: ## Sets up local environment with Poetry
	@echo "--- Setting up environment with Poetry ---"
	@chmod +x bin/setup.sh && source bin/setup.sh

run: ## Runs the project locally with reload (Uvicorn)
	@echo "🚀 Running the project..."
	@poetry run uvicorn src.graph.api.main:app --host 0.0.0.0 --port 8000 --reload

# ----
# Git Commands
# ----

release: ## Creates new version and release via semantic-release
	@echo "--- Creating release with semantic-release ---"
	@poetry run dotenv run -- poetry run semantic-release version --print
	@poetry run dotenv run -- poetry run semantic-release publish

undo-release: ## Reverts a Git release (requires VERSION=x.y.z)
	ifndef VERSION
		$(error ❌ You need to set the VERSION variable, e.g. make undo-release VERSION=0.1.0)
	endif
		@echo "--- Undoing release $(VERSION) ---"
		@git tag -d $(VERSION) || echo "⚠️ Tag $(VERSION) not found locally"
		@git push origin :refs/tags/$(VERSION) || echo "⚠️ Tag $(VERSION) not found remotely"
		@echo "Reminder: The version bump commit was NOT automatically reverted."


# 🎨 Quality, Style and Fixes
lint: ## Runs linters (Ruff check, Black check)
	@echo "--- Running linters ---"
	@poetry run ruff check . --fix
	@poetry run black --check .

format: ## Automatically formats code (Ruff format, Black, isort, ruff --fix)
	@echo "--- Formatting code ---"
	@poetry run ruff format .
	@poetry run black .
	@poetry run isort .
	@poetry run ruff check . --fix

# 🧠 Monkeytype (Type Generation)
monkeytype-run: ## Runs test script for Monkeytype collection
	@echo "🐒 Collecting types with Monkeytype..."
	@$(MONKEYTYPE_RUN)

monkeytype-apply: ## Applies types collected by Monkeytype
	@echo "📦 Applying Monkeytype types..."
	@$(MONKEYTYPE) list-modules | grep -vE '(^test_|conftest$$)' | while read module; do \
		echo "➞⃣  Applying: $$module"; \
		$(MONKEYTYPE) apply "$$module" || echo "⚠️  Failed to apply: $$module"; \
	done
	@echo "✅ Application completed."

monkeytype-view: ## Views Monkeytype stubs with fzf
	@$(MONKEYTYPE) list-modules | fzf | xargs $(MONKEYTYPE) stub

monkeytype-clean: ## Removes Monkeytype database
	@rm -rf monkeytype.sqlite3

monkeytype: monkeytype-run monkeytype-apply monkeytype-clean ## Runs full Monkeytype cycle (run, apply, clean)
	@true

monkeytype-all: monkeytype-trace-decorators monkeytype-run monkeytype-apply monkeytype-clean ## Runs all Monkeytype steps
	@true

# 📚 Documentation
doc: ## Generates and serves documentation locally with MkDocs
	@echo "--- Serving documentation with MkDocs ---"
	@poetry run mkdocs serve

# ----------------------------
# VARIABLES
# ----------------------------
COMPOSE_ALL=infra/docker-compose.yml

# ----------------------------
# GENERAL INFRA
# ----------------------------

infra-up:
	@docker compose -f $(COMPOSE_ALL) up -d --remove-orphans --force-recreate
	@echo "Infrastructure containers started successfully!"

infra-down:
	@docker compose -f $(COMPOSE_ALL) down --remove-orphans --volumes
	@echo "Infrastructure containers stopped and volumes removed!"


# ----------------------------
# MAIN SHORTCUTS
# ----------------------------

up: infra-up
down: infra-down

t:
	@poetry run pytest $(filter-out $@,$(MAKECMDGOALS))

td:
	@poetry run pytest $(filter-out $@,$(MAKECMDGOALS)) -s -vv

# ----------------------------

# Ignore "No rule to make target" errors
%:
	@:
