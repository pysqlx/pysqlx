Development
===========

``pysqlx`` is developed on `GitHub <https://github.com/pysqlx/pysqlx>`_. Bug
reports, feature requests and pull requests are welcome, in particular for
additional dialects and clients.

Setting up
----------

The project is managed with `uv <https://docs.astral.sh/uv/>`_, and the
common tasks are available as ``make`` targets.

.. code-block:: bash

   git clone https://github.com/pysqlx/pysqlx.git
   cd pysqlx
   make install

``make install`` creates a virtual environment in ``.venv`` with the package
and all development dependencies, exactly as pinned in ``uv.lock``.

Make targets
------------

Run ``make`` without arguments to list the targets.

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Target
     - Description
   * - ``make install``
     - create the virtual environment and install all dependencies
   * - ``make lint``
     - check the code style and formatting with ``ruff``
   * - ``make format``
     - format the code and apply the safe lint fixes
   * - ``make typecheck``
     - check the types with ``mypy``
   * - ``make test``
     - run the tests
   * - ``make coverage``
     - run the tests in parallel with a coverage report
   * - ``make check``
     - run every check that CI runs
   * - ``make servers-up``
     - start throwaway PostgreSQL and MySQL servers with Docker
   * - ``make test-servers``
     - run the tests of the clients against these servers
   * - ``make servers-down``
     - stop these servers
   * - ``make docs``
     - build this documentation, treating warnings as errors
   * - ``make docs-live``
     - serve the documentation and rebuild it on changes
   * - ``make docs-images``
     - regenerate the figures shown in the documentation
   * - ``make version``
     - show the version derived from the git tags
   * - ``make build``
     - build the source distribution and the wheel
   * - ``make clean``
     - remove build, test and cache artifacts

Project layout
--------------

.. code-block:: text

   src/pysqlx/
       clients/       clients, which connect to a database and execute queries
       dialects/      dialects, which turn queries into SQL
       exceptions/    exceptions of the package
       queries/       queries, one module per query
       structures/    databases, schemas, tables, columns, clauses and indexes
       logger.py      logger of the package
   tests/             tests, in the same layout
   docs/              this documentation

Every class has its own module, named after the class in lower case with
underscores, and is exported by the ``__init__.py`` of its package.

Dependencies are declared in ``pyproject.toml``. The development
dependencies are split into the groups ``test``, ``lint`` and ``docs``, and
the group ``dev`` includes all of them. The libraries of the database
servers are optional dependencies of the package and part of the group
``test``. The package only imports them when a client is created.

Code style
----------

* The code is formatted and linted with ``ruff`` and type checked with
  ``mypy`` in strict mode.
* Every public module, class, method and function has a docstring. The
  docstrings use Sphinx field lists (``:param name:``, ``:returns:`` and
  ``:raises Error:``). Types are not repeated in the docstrings; they are
  taken from the type hints.
* The parameters of a class are documented in the class docstring.

How a query becomes SQL
-----------------------

A client finds the method which executes a query from the name of the class
of the query: a ``Select`` query is executed by ``_execute_Select()``. A
dialect finds the method which writes the SQL in the same way, also using the
kind of structure which the query acts on: ``get_Select_table_string()``.
This is why these methods keep the capital letters of the class names.

The dialect writes the SQL in one of two ways. Given a list of parameters, it
adds each value of a condition to the list and writes a placeholder, which is
what the clients execute. Without the list, it writes the values into the
SQL, which is what ``get_query_string()`` returns for reading.

:py:class:`~pysqlx.dialects.IDialect` writes the SQL which the databases have
in common, and :py:class:`~pysqlx.clients.IClient` executes every query. A
dialect or a client only defines what its database does differently.

Adding a query
--------------

1. Add a module with the query class to ``pysqlx.queries``, derived from
   :py:class:`~pysqlx.queries.Query`, and export it from the package.
   Override ``execute()`` to declare what the query returns.
2. Add the methods ``get_<Query>_<structure>_string()`` and
   ``get_<Query>_string()`` to :py:class:`~pysqlx.dialects.IDialect`, and
   override the former in the dialects whose SQL differs.
3. Add ``_execute_<Query>()`` to :py:class:`~pysqlx.clients.IClient`, and a
   method which creates the query. Add ``_execute_many_<Query>()`` if the
   query can be executed with several sets of parameters.
4. Add the query to the cases of ``tests/dialects/cases.py`` and to the
   scenario of ``tests/clients/scenario.py``, a section to
   ``docs/guide/queries.rst`` and the class to ``docs/reference/index.rst``.

Adding a database
-----------------

1. Add a dialect derived from :py:class:`~pysqlx.dialects.IDialect`, which
   defines how names are quoted, the types of the columns and the queries
   which look structures up.
2. Add a client derived from :py:class:`~pysqlx.clients.IClient`, which
   opens the connection and starts a transaction. Import the library of the
   database inside the client, so that the package works without it, and add
   the library as an optional dependency.
3. Add a method to :py:class:`~pysqlx.clients.ClientFactory`.
4. Add tests which run the scenario of ``tests/clients/scenario.py``, the
   expected SQL to ``tests/dialects/std``, and a server to the ``servers-linux``
   job of ``.github/workflows/tests.yml``.

Testing
-------

``make test`` uses SQLite databases in memory and needs no setup. The tests
which need a database server are skipped.

Every client runs the same scenario, in ``tests/clients/scenario.py``,
against its database. A server is given to the tests as an environment
variable of the form ``user:password@host:port/database``:

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - Variable
     - Server
   * - ``PYSQLX_TEST_POSTGRESQL``
     - PostgreSQL
   * - ``PYSQLX_TEST_MYSQL``
     - MySQL or MariaDB
   * - ``PYSQLX_TEST_MSSQL``
     - Microsoft SQL Server, which also needs its ODBC driver

The scenario creates and drops tables whose names start with ``pysqlx``. Use
servers which hold nothing else.

With Docker, ``make servers-up`` starts a PostgreSQL and a MySQL server,
``make test-servers`` runs the tests of the clients against them and
``make servers-down`` stops them. CI runs the scenario against the three
servers on Linux in the ``servers-linux`` job, and against SQL Server on
Windows and macOS in the ``sql-server-desktop`` job. The ``unit`` job runs the
whole test suite with SQLite on every supported system and version of Python.

The tests run for a pull request which changes the package, the tests, the
dependencies or the workflow itself. A pull request which only changes the
documentation skips them. They also run daily on ``master``.

The SQL which each dialect writes for a set of queries is compared with the
files of ``tests/dialects/std``. When the SQL changes on purpose, review the
difference and update these files.

Documentation
-------------

The documentation is built with Sphinx. The pages in ``docs/reference/api``
are generated from the docstrings at build time and are not committed.

Keep the documentation in step with the code. A change to the behavior or to
the interface of the library updates, in the same pull request:

* the guide page of the feature in ``docs/guide``, including its examples
* the figures, which ``docs/scripts/make_images.py`` writes to
  ``docs/_static`` for the light and for the dark theme
* the "Unreleased" section of ``docs/project/changelog.rst``
* ``README.md`` when the change affects what a first-time reader should know

.. code-block:: bash

   make docs       # build into docs/_build/html
   make docs-live  # serve at http://127.0.0.1:8000 and rebuild on changes

Releasing
---------

The version of the package is not written in any file. It is read from the
git tag of the release: the tag ``v1.0.2`` gives the version ``1.0.2``.

To release, rename the "Unreleased" section of ``docs/project/changelog.rst``
to the new version and its date, merge that change, and create a GitHub
release on ``master`` with a new tag of the form ``vX.Y.Z``. Publishing the
release runs the ``Publish`` workflow, which builds the distributions, checks
that their version matches the tag and uploads them to PyPI using trusted
publishing.

Between releases the version is derived from the most recent tag and the
number of commits since, for example ``1.0.3.dev3+g1a2b3c4``.
