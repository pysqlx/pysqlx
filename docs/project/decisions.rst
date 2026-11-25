Decisions
=========

What was decided about the design of the package and about how the project
works, and why. Read it before proposing a change: something which looks odd
is often here with its reason.

Add a decision when one is made, most recent last in its section, with the
reason and the date. To change a decision, replace its entry and say what it
replaced. Do not keep decisions anywhere else. What is still open is in the
:doc:`roadmap`.

Design of the package
---------------------

One class per module (2026-11-25)
   Every class has its own module, named after the class in lower case with
   underscores, and is exported by the ``__init__.py`` of its package. A
   module with functions or constants only is fine.

   *Why:* a class is found by its name, and a change touches one file.

Values are parameters (2026-11-25)
   The values of the conditions are passed to the database as parameters.
   ``get_query_string()`` writes them into the SQL, escaped, and is meant for
   reading only.

   *Why:* a value written into the SQL can change the statement. The SQL for
   reading stays, because seeing a query is useful and tests compare it.

Default values are written as given (2026-11-25)
   The ``default_value`` of a column is written into the table definition
   without escaping.

   *Why:* it allows defaults such as ``CURRENT_TIMESTAMP``, and changing it
   would change what a string means for existing code. The road map has the
   alternative.

Names are quoted (2026-11-25)
   Every name of a database, schema, table, column or index is quoted in the
   SQL, with the quote character of the dialect.

   *Why:* names may be reserved words or contain spaces.

Columns are compared by identity (2026-11-25)
   ``==`` on a column creates a condition, so the package compares columns
   with ``is``, never with ``==`` or ``in``.

   *Why:* ``column in columns`` is always true, which made every check of
   the queries pass in version 1.

A column refers to its table weakly, a foreign key strongly (2026-11-25)
   Columns hold a weak reference to their table. A foreign key holds the
   table it refers to.

   *Why:* a table and its columns would otherwise refer to each other. A
   foreign key needs the other table when the SQL is written, even if no
   variable holds it any more.

The base classes do the common work (2026-11-25)
   ``Dialect`` writes the SQL which the databases have in common and
   ``Client`` executes every query. A dialect or a client defines its
   differences only.

   *Why:* the two dialects of version 1 shared most of their code, as copies.

Methods are found by the name of a class (2026-11-25)
   A client executes a ``Select`` query with ``_execute_Select()``, and a
   dialect writes it with ``get_Select_table_string()``. These methods keep
   the capital letters of the class names.

   *Why:* a new query needs no table of types. Renaming the methods is on
   the road map.

The libraries of the databases are optional (2026-11-25)
   ``psycopg``, ``pymysql`` and ``pyodbc`` are extras, imported when a client
   is created. The package has no required dependency.

   *Why:* importing ``pyodbc`` fails without unixODBC, which broke the
   import of the package, and the build of the documentation, for users of
   SQLite.

Exceptions derive from ``RuntimeError`` (2026-11-25)
   The exceptions of the package derive from ``PysqlxError``, which derives
   from ``RuntimeError``. Errors of a database are raised as they are.

   *Why:* version 1 raised ``RuntimeError``, so code which catches it keeps
   working.

Names say what something is (2026-11-25)
   In version 3: clients are named after their database, not after their
   library (``PostgreSqlClient``), and so are the methods of the factory
   which create them. ``Client`` and ``Dialect`` have no ``I`` prefix, as
   they are base classes. ``exists``, ``count_rows``, ``is_required``,
   ``parameters`` and ``limit`` replaced names which were unclear. Queries
   which only act on a table take a ``table``.

   The old names were removed without aliases. The names of the providers,
   such as ``"sqlite3"``, did not change, as they name the libraries.

   *Why:* the maintainer chose a clean break in a major version over a
   period with two names for everything.

Python 3.11 or newer (2026-11-25)
   ``override``, which Python 3.12 added, comes from ``pysqlx._compat``.

   *Why:* supporting Python 3.11 was asked for, and a module of a few lines
   avoids a dependency on ``typing_extensions``.

How the project works
---------------------

The package is in ``src`` (2026-11-25)
   The code is in ``src/pysqlx``, the tests in ``tests`` and the
   documentation in ``docs``.

   *Why:* with a ``src`` layout, the tests and the documentation import the
   installed package, not the files which happen to be in the working
   directory. What is tested is what users get.

One file describes the project (2026-11-25)
   ``pyproject.toml`` holds the metadata, the dependencies and the settings
   of every tool. There is no ``setup.py``, ``requirements.txt`` or separate
   file for a tool.

   *Why:* one place to look, and nothing to keep in step.

The version comes from the git tag (2026-11-25)
   The package is built with ``hatchling`` and ``hatch-vcs``. No file holds
   the version: the tag ``v3.0.0`` gives the version ``3.0.0``, and
   ``pysqlx.__version__`` reads it from the installed package.

   *Why:* a version written in a file can differ from the tag of its
   release. Here they cannot, and the Publish workflow checks it once more.

``uv`` manages the environment (2026-11-25)
   ``uv`` creates the environment and installs the dependencies as pinned in
   ``uv.lock``, which is committed. The development dependencies are split
   into the groups ``test``, ``lint`` and ``docs``.

   *Why:* the lock file makes every machine, and CI, use the same versions,
   so a failure can be reproduced. The groups let a job install only what it
   needs.

``make`` is the interface (2026-11-25)
   Every task is a ``make`` target, with a description which ``make`` lists.
   ``make check`` runs what CI runs.

   *Why:* nobody has to remember the commands and options of the tools, and
   a contributor can run the same checks as CI before pushing.

``ruff`` formats and lints (2026-11-25)
   ``ruff`` is the only formatter and linter, with a line length of 100. Its
   rules cover errors, imports, likely bugs, outdated syntax, ``print``
   calls and docstrings. Every public module, class, method and function
   needs a docstring.

   *Why:* one fast tool replaces several which had to agree with each other.
   Requiring docstrings keeps the reference of the documentation complete,
   as it is generated from them.

``mypy`` checks the types strictly (2026-11-25)
   The package and its tests pass ``mypy`` in strict mode, and the package
   ships a ``py.typed`` marker.

   *Why:* the queries are built from many small objects, and the types catch
   a wrong argument before anything is sent to a database. The marker gives
   users the same checks in their own code.

The documentation fails on a warning (2026-11-25)
   The documentation is built with Sphinx and the Furo theme. The reference
   is generated from the docstrings, with the types taken from the type
   hints. A warning, such as a broken cross-reference, fails the build, in
   CI and on Read the Docs.

   *Why:* documentation which is generated cannot drift from the code, and a
   build which fails on a warning cannot be published half broken.

Tests mirror the source (2026-11-25)
   The tests have the layout of the package, one module of tests per module
   or per class. They are written for ``pytest`` and are type checked like
   the package.

   *Why:* the tests of a class are found where the class is.

American English (2026-11-25)
   Code, comments, documentation and commit messages are written in American
   English.

Every change goes through a pull request (2026-11-25)
   ``master`` only accepts squashed pull requests whose required checks
   pass. Nobody can bypass it.

Workflows call ``make`` (2026-11-25)
   Every step of a workflow is a ``make`` target. A step which needs more
   than a command is a Python script in ``.github/scripts``, which uses the
   standard library only.

   *Why:* CI can be run on a development machine in the same way, and Python
   reads the same on every system.

Workflows run for pull requests and daily (2026-11-25)
   The Tests, Quality and CodeQL workflows run for pull requests, not for
   pushes to ``master``. Tests and CodeQL also run daily on ``master``. A
   new push to a pull request cancels the runs of the previous one.

   *Why:* nothing reaches ``master`` without a pull request, so the push
   runs repeated the checks. The daily runs keep the badge and the results
   of CodeQL current.

Tests run for every pull request (2026-11-25)
   The Tests workflow has no filter on the changed files.

   *Why:* skipping the tests for changes of the documentation was tried and
   withdrawn. A required check which never reports blocks a pull request.

Every client runs one scenario (2026-11-25)
   ``tests/clients/scenario.py`` is run against SQLite and, in CI, against
   PostgreSQL, MySQL and SQL Server servers. The SQL of each dialect is
   compared with files in ``tests/dialects/std``.

   *Why:* the databases must behave alike, which only real servers show.

SQL Server on macOS uses an Intel runner (2026-11-25)
   The job starts SQL Server in a container with Colima on
   ``macos-15-intel``. On Windows, SQL Server is installed by
   ``potatoqualitee/mssqlsuite``, pinned to a commit.

   *Why:* the Arm runners of macOS cannot run containers, and the action
   does not work on the Intel runner. macOS runners are scarce, so the unit
   tests only run the oldest and the newest version of Python there.

Releases are published by GitHub (2026-11-25)
   A release is a GitHub release with a tag ``vX.Y.Z`` on ``master``, after
   a pull request which names the section of the changelog. The Publish
   workflow uploads to PyPI with trusted publishing, without a token.

Dependencies are updated monthly (2026-11-25)
   Dependabot opens one grouped pull request a month for the actions and one
   for the Python packages.

Figures are generated (2026-11-25)
   The figures of the documentation are SVG files written by
   ``docs/scripts/make_images.py``, for the light and for the dark theme.

   *Why:* they stay consistent, and need no drawing tool or dependency.

Development builds of the documentation have a plain name (2026-11-25)
   Between releases the documentation is titled "pysqlx (development
   version)", not with the version derived from git.
