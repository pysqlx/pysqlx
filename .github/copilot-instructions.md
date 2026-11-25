# Instructions for coding agents

`pysqlx` is a Python package for working with SQL databases without writing SQL. Tables, conditions and queries are objects, and a client turns them into the SQL of SQLite, PostgreSQL, MySQL or Microsoft SQL Server.

## Read these first

- `docs/project/decisions.rst`: what was decided about the design and the project, and why. Follow it. If a task conflicts with a decision, say so before changing anything.
- `docs/project/roadmap.rst`: what is open: planned work, known defects and questions waiting for an answer.
- `docs/project/development.rst`: the layout, the `make` targets, how a query becomes SQL, and how to add a query or a database.

## Where knowledge goes

Do not use your own memory or notes for anything about this project. The repository is the only record, so that every agent and every person sees the same.

- An open item (work left to do, a defect you found and did not fix, a question for the maintainer) goes into `docs/project/roadmap.rst`. Remove it when it is done.
- A decision (a choice between alternatives, with its reason) goes into `docs/project/decisions.rst`, with the date.
- A change of the package goes into the "Unreleased" section of `docs/project/changelog.rst`.

Make these edits in the same pull request as the work they belong to. If you finish a task with something left open and it is not on the road map, you are not done.

Only what is about a machine and not about the project, such as which tools are installed, may stay in your own memory.

## Commands

Use the `make` targets. Run `make` to list them.

- `make install`: create the environment with all dependencies
- `make check`: lint, type check, test and build the documentation, as CI does. Run it before you say that a change works.
- `make format`: format the code and apply the safe lint fixes
- `make servers-up`, `make test-servers`, `make servers-down`: run the tests of the clients against PostgreSQL and MySQL servers in Docker

The tests of the SQL Server client need a server and its ODBC driver. If you cannot run them, say that CI is their first run.

## Conventions

- Write American English, in code, comments, documentation and commit messages.
- One class per module. The module is named after the class in lower case with underscores, and the class is exported by the `__init__.py` of its package.
- Every public module, class, method and function has a docstring with Sphinx field lists (`:param name:`, `:returns:`, `:raises Error:`). Types are in the type hints, not in the docstrings. The parameters of a class are documented in the class docstring.
- The code passes `mypy` in strict mode and `ruff` with the rules of `pyproject.toml`.
- Compare columns with `is`, never with `==` or `in`: `==` on a column creates a condition.
- Never write a value into SQL which is executed. Values are parameters. Names are quoted with `quote_identifier()`.
- The library of a database server is imported inside its client, so that the package works without it.
- Tests mirror the layout of the source. A change of the SQL of a dialect updates the files in `tests/dialects/std`, after reviewing the difference. Something every database must do goes into `tests/clients/scenario.py`.
- A workflow step is a `make` target. What needs more than a command is a Python script in `.github/scripts`, using the standard library only.
- Keep the documentation in step with the code, in the same pull request: the guide in `docs/guide`, the README when a first-time reader is affected, and the figures of `docs/scripts/make_images.py`.

## Git

- Commit, push and open a pull request only when the maintainer asks.
- Never commit to `master`. Work on a branch; every change is a squashed pull request whose required checks pass. Do not bypass them.
- A breaking change of the interface needs a new major version and a table of the old and new names in the changelog.
- To release, follow "Releasing" in `docs/project/development.rst`.
