# 🛠️ Makefile - Helper commands for graph_weave

# ----- Configuration Variables -----
ROOT_DIR := .
SRC_DIR := src
TEST_DIR := tests
PYTEST = poetry run pytest

# Main package name for coverage
PACKAGE_NAME = graph

# Test Directories
UNIT_TEST_DIR = $(TEST_DIR)/unit
INTEGRATION_TEST_DIR = $(TEST_DIR)/integration
BENCHMARK_DIR = $(TEST_DIR)/benchmark

# Coverage Options
COV_REPORT_TERM = --cov-report=term-missing
HTML_COV_SAVE_DIR = .tests_saves/htmlcov # Your directory for HTML cov
COVER_SAVE_DIR = .tests_saves/coverage   # Your directory for .coverage data (if needed)
BENCHMARK_SAVE_DIR = .tests_saves/benchmark # Your directory for saved benchmarks
PROFILE_SAVE_DIR = .tests_saves/profile # Your directory for profiling files

PROFILE_SAVE_DIR = .tests_saves/profile
PROFILE_OUTPUT_FILENAME = profile_output.prof
PROFILE_OUTPUT_FILE = $(PROFILE_SAVE_DIR)/$(PROFILE_OUTPUT_FILENAME)
ABS_PROFILE_OUTPUT_FILE = $(shell pwd)/$(PROFILE_OUTPUT_FILE)

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
	act-test act-release set-act monkeytype monkeytype-run monkeytype-apply \
	monkeytype-clean monkeytype-view monkeytype-trace-decorators monkeytype-all \
	no-optional check-no-optional \
	doc secrets secrets-scan bandit radon radon-mi radon-raw \
	isort clear test-all coverage coverage-html \
	benchmark benchmark-save benchmark-autosave benchmark-compare test-unit \
		test-integration profile profile-view infra-up infra-down\
		exec-mongo up down r \ 

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


# 🔁 GitHub Actions local (Act)
set-act: ## Sets up Act runner (if needed)
	@act -P ubuntu-latest=catthehacker/ubuntu:act-latest

act-test: ## Runs the 'test' CI job locally via Act
	@act -j test --bind --secret-file .env --container-architecture linux/amd64 --verbose

act-release: ## Runs the 'release' CI job locally via Act
	@act -j release --bind --secret-file .env --container-architecture linux/amd64 --verbose

# 🧪 Tests, Coverage and Benchmark

test-unit: ## Runs ONLY unit tests
	@echo "--- Running unit tests ---"
	@$(PYTEST) $(UNIT_TEST_DIR)

test: test-unit ## Runs unit tests (default behavior for 'make test')
	@true # test-unit target already executed as dependency

test-integration: ## Run only integration tests (requires RUN_INTEGRATION=true or export RUN_INTEGRATION_TESTS=true)
ifeq ($(RUN_INTEGRATION),true)
	@echo "--- Running integration tests ---"
	@echo "RUN_INTEGRATION flag: [$(RUN_INTEGRATION)]"
	@RUN_INTEGRATION_TESTS=true $(PYTEST) -m integration $(INTEGRATION_TEST_DIR)
else
	@echo "--- Skipping integration tests ---"
	@echo "Set 'RUN_INTEGRATION=true' or export 'RUN_INTEGRATION_TESTS=true' to enable them."
endif


benchmark-save: ## Runs benchmarks and saves with a name in $(BENCHMARK_SAVE_DIR) (e.g. make benchmark-save NAME=baseline_v1)
	@echo "--- Running benchmark and saving results as '$(NAME)' in $(BENCHMARK_SAVE_DIR) ---"
	@if [ -z "$(NAME)" ]; then \
		echo ""; \
		echo "ERROR: Name to save not provided."; \
		echo "Usage: make benchmark-save NAME=<name_to_save>"; \
		echo ""; \
		exit 1; \
	fi
	@if [ -d "$(BENCHMARK_DIR)" ]; then \
		echo "Running benchmarks in $(BENCHMARK_DIR)..." && \
		$(PYTEST) $(BENCHMARK_DIR) $(BENCHMARK_STORAGE_ARG) --benchmark-save=$(NAME) -m benchmark && \
		echo "Benchmark results saved under name: $(NAME) in $(BENCHMARK_SAVE_DIR)/"; \
	else \
		echo "Benchmark directory '$(BENCHMARK_DIR)' not found. Skipping."; \
	fi

benchmark-autosave: ## Runs benchmarks and automatically saves each result in $(BENCHMARK_SAVE_DIR)
	@echo "--- Running benchmark and autosaving results in $(BENCHMARK_SAVE_DIR) ---"
	@if [ -d "$(BENCHMARK_DIR)" ]; then \
		echo "Running benchmarks in $(BENCHMARK_DIR)..." && \
		$(PYTEST) $(BENCHMARK_DIR) $(BENCHMARK_STORAGE_ARG) --benchmark-autosave -m benchmark && \
		echo "Benchmark results autosaved in $(BENCHMARK_SAVE_DIR)/"; \
	else \
		echo "Benchmark directory '$(BENCHMARK_DIR)' not found. Skipping."; \
	fi


profile:  ## Runs profiling with cProfile and saves in $(PROFILE_SAVE_DIR)
	@echo "🔍 Running profiling with cProfile..."
	@echo "WARNING: Make sure graph.api.main is the correct entry point."
	@mkdir -p $(PROFILE_SAVE_DIR)
	@poetry run python -m cProfile -o $(ABS_PROFILE_OUTPUT_FILE) -m graph.api.main
	@echo "✅ Profiling completed. Results saved in $(PROFILE_OUTPUT_FILE)"
	@echo "Use 'snakeviz $(PROFILE_OUTPUT_FILE)' to visualize."

profile-view: ## Visualizes profiling file with snakeviz
	@echo "🔍 Visualizing profiling results with snakeviz..."
	@poetry run snakeviz $(ABS_PROFILE_OUTPUT_FILE)

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

# 🔐 Security
secrets: secrets-scan ## Alias for secrets-scan
	@true

secrets-scan: ## Runs detect-secrets to check for committed secrets
	@echo "--- Checking secrets with detect-secrets ---"
	@poetry run detect-secrets scan --baseline .secrets.baseline

bandit: ## Runs static security analysis with Bandit
	@echo "--- Checking security with Bandit ---"
	@poetry run bandit -r src/ -x tests/ -ll # Shows only medium/high issues

# 📊 Complexity and Metrics (Radon)
radon: radon-cc ## Runs MI complexity analysis (default)

radon-mi: ## Runs maintainability index analysis with Radon
	@echo "--- Calculating Maintainability Index (Radon MI) ---"
	@poetry run radon mi src/ -s

radon-cc: ## Runs cyclomatic complexity analysis with Radon
	@echo "--- Calculating Cyclomatic Complexity (Radon CC) ---"
	@poetry run radon cc src/ -s -a

radon-raw: ## Runs raw metrics analysis with Radon
	@echo "--- Calculating Raw Metrics (Radon Raw) ---"
	@poetry run radon raw src/ -s


# ----------------------------
# VARIABLES
# ----------------------------
COMPOSE_ALL=infra/docker-compose.all.yml
COMPOSE_MONITORING_ENV_FILE=monitoring/.env

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
# INFRA Monitoring
# ----------------------------

monitoring-up:
	@echo "docker compose -f $(COMPOSE_MONITORING) up -d --remove-orphans --force-recreate"
	@docker compose -f $(COMPOSE_MONITORING) up -d --remove-orphans --force-recreate
	@echo "Monitoring containers started successfully!"

monitoring-down:
	@docker compose -f $(COMPOSE_MONITORING) down --remove-orphans --volumes
	@echo "Monitoring containers stopped and volumes removed!"	


# ----------------------------
# MAIN SHORTCUTS
# ----------------------------

up: infra-up
down: infra-down

mup: monitoring-up
mdown: monitoring-down

r: down mdown up mup 

t:
	@poetry run pytest $(filter-out $@,$(MAKECMDGOALS))

ti:
	@poetry run pytest tests/integration

te: 
	@poetry run pytest -ra --maxfail=20 --tb=short $(filter-out $@,$(MAKECMDGOALS)) 

td:
	@poetry run pytest $(filter-out $@,$(MAKECMDGOALS)) -s -vv

# ----------------------------

# Ignore "No rule to make target" errors
%:
	@:
