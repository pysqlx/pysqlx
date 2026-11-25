.DEFAULT_GOAL := help

.PHONY: help install lint format typecheck test coverage check \
	servers-up servers-down test-servers \
	docs docs-live docs-images docs-clean version build clean

help:  ## Show the available targets
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "} {printf "  %-14s %s\n", $$1, $$2}'

install:  ## Create the virtual environment and install all dependencies
	uv sync --locked

lint:  ## Check the code style and formatting with ruff
	uv run ruff check src tests docs
	uv run ruff format --check src tests docs

format:  ## Format the code and apply the safe lint fixes
	uv run ruff check --fix src tests docs
	uv run ruff format src tests docs

typecheck:  ## Check the types with mypy
	uv run mypy src tests

test:  ## Run the tests
	uv run pytest

coverage:  ## Run the tests in parallel with a coverage report
	uv run pytest -n auto --cov --cov-report=term-missing:skip-covered --cov-report=xml

check: lint typecheck test docs  ## Run every check that CI runs

servers-up:  ## Start throwaway PostgreSQL and MySQL servers with Docker
	docker run -d --rm --name pysqlx-test-postgres -e POSTGRES_PASSWORD=pysqlx_test \
		-p 55432:5432 postgres:17
	docker run -d --rm --name pysqlx-test-mysql -e MYSQL_ROOT_PASSWORD=pysqlx_test \
		-e MYSQL_DATABASE=pysqlx -p 53306:3306 mysql:8.4

servers-down:  ## Stop the servers started by servers-up
	docker stop pysqlx-test-postgres pysqlx-test-mysql

test-servers:  ## Run the tests of the clients against the servers of servers-up
	PYSQLX_TEST_POSTGRESQL=postgres:pysqlx_test@127.0.0.1:55432/postgres \
	PYSQLX_TEST_MYSQL=root:pysqlx_test@127.0.0.1:53306/pysqlx \
	uv run pytest tests/clients

docs:  ## Build the HTML documentation, treating warnings as errors
	uv run sphinx-build -b html -W --keep-going docs docs/_build/html

docs-live:  ## Serve the documentation and rebuild it on changes
	uv run sphinx-autobuild docs docs/_build/html

docs-images:  ## Regenerate the figures shown in the documentation
	uv run python docs/scripts/make_images.py

docs-clean:  ## Remove the built documentation
	rm -rf docs/_build

version:  ## Show the version derived from the git tags
	@uvx --quiet --with hatch-vcs hatchling version

build:  ## Build the source distribution and the wheel
	rm -rf dist
	uv build

clean: docs-clean  ## Remove build, test and cache artifacts
	rm -rf dist htmlcov coverage.xml .coverage .pytest_cache .mypy_cache .ruff_cache
