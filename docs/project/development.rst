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

On macOS, install unixODBC first, as described in
:doc:`/getting-started/installation`. Without it the package cannot be
imported, and neither the tests nor the documentation can run.

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
   * - ``make docs``
     - build this documentation, treating warnings as errors
   * - ``make docs-live``
     - serve the documentation and rebuild it on changes
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
       queries/       queries, one module per query
       structures/    databases, schemas, tables, columns and clauses
       logger.py      logger of the package
   tests/             tests, in the same layout
   docs/              this documentation

Every class has its own module, named after the class in lower case with
underscores, and is exported by the ``__init__.py`` of its package.

Dependencies are declared in ``pyproject.toml``. The development
dependencies are split into the groups ``test``, ``lint`` and ``docs``, and
the group ``dev`` includes all of them.

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

Adding a query
--------------

1. Add a module with the query class to ``pysqlx.queries``, derived from
   :py:class:`~pysqlx.queries.Query`, and export it from the package.
2. Add the abstract methods ``get_<Query>_<structure>_string()`` and the
   method ``get_<Query>_string()`` to
   :py:class:`~pysqlx.dialects.IDialect`, and implement the former in every
   dialect.
3. Add ``_execute_<Query>()`` and ``_execute_many_<Query>()`` to
   :py:class:`~pysqlx.clients.IClient` and to every client, and a method
   which creates the query.
4. Add tests, a section to ``docs/guide/queries.rst`` and the class to
   ``docs/reference/index.rst``.

Testing
-------

The tests use a SQLite database in memory and need no setup.

``tests/clients/notest_pyodbc.py`` holds the tests of the ODBC client. They
need a SQL Server and are not collected by ``pytest``. To run them, fill in
the connection settings at the top of ``tests/conftest.py`` and pass the file
to ``pytest``.

Documentation
-------------

The documentation is built with Sphinx. The pages in ``docs/reference/api``
are generated from the docstrings at build time and are not committed.

Keep the documentation in step with the code. A change to the behavior or to
the interface of the library updates, in the same pull request:

* the guide page of the feature in ``docs/guide``, including its examples
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
