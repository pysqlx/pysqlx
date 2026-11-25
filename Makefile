.DEFAULT_GOAL := help

.PHONY: help install install-test lint format typecheck test coverage check \
	test-clients test-sql-server test-servers \
	servers-up servers-down sql-server-up sql-server-wait odbc-driver \
	docs docs-live docs-images docs-clean \
	version check-version build publish clean

help:  ## Show the available targets
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "} {printf "  %-16s %s\n", $$1, $$2}'

install:  ## Create the virtual environment and install all dependencies
	uv sync --locked

install-test:  ## Install the package and the dependencies of the tests only
	uv sync --locked --no-default-groups --group test

lint:  ## Check the code style and formatting with ruff
	uv run ruff check src tests docs .github/scripts
	uv run ruff format --check src tests docs .github/scripts

format:  ## Format the code and apply the safe lint fixes
	uv run ruff check --fix src tests docs .github/scripts
	uv run ruff format src tests docs .github/scripts

typecheck:  ## Check the types with mypy
	uv run mypy src tests .github/scripts

test:  ## Run the tests
	uv run pytest

coverage:  ## Run the tests in parallel with a coverage report
	uv run pytest -n auto --cov --cov-report=term-missing:skip-covered --cov-report=xml

check: lint typecheck test docs  ## Run every check that CI runs

test-clients:  ## Run the tests of the clients, against the servers given in the environment
	uv run pytest tests/clients

test-sql-server:  ## Run the tests of the SQL Server client only
	uv run pytest tests/clients/test_sql_server_client.py

test-servers:  ## Run the tests of the clients against the servers of servers-up
	PYSQLX_TEST_POSTGRESQL=postgres:pysqlx_test@127.0.0.1:55432/postgres \
	PYSQLX_TEST_MYSQL=root:pysqlx_test@127.0.0.1:53306/pysqlx \
	uv run pytest tests/clients

servers-up:  ## Start throwaway PostgreSQL and MySQL servers with Docker
	uv run --no-project python .github/scripts/test_servers.py up

servers-down:  ## Stop the servers started by servers-up and sql-server-up
	uv run --no-project python .github/scripts/test_servers.py down

sql-server-up:  ## Start a throwaway SQL Server with Docker, set up with Colima on macOS if needed
	uv run --no-project python .github/scripts/test_servers.py up --servers sql-server --colima

sql-server-wait:  ## Wait until the SQL Server given in the environment accepts connections
	uv run python .github/scripts/wait_for_sql_server.py

odbc-driver:  ## Install the ODBC driver for SQL Server
	uv run --no-project python .github/scripts/install_odbc_driver.py

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

check-version:  ## Check that the built distributions have the version of TAG, as in TAG=v2.1.0
	uv run --no-project python .github/scripts/check_release_version.py $(TAG)

build:  ## Build the source distribution and the wheel
	rm -rf dist
	uv build

publish:  ## Upload the built distributions to PyPI
	uv publish

clean: docs-clean  ## Remove build, test and cache artifacts
	rm -rf dist htmlcov coverage.xml .coverage .pytest_cache .mypy_cache .ruff_cache
