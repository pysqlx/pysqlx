Changelog
=========

All notable changes to ``pysqlx``, most recent first.

Unreleased
----------

Changed
~~~~~~~

* Python 3.11 is supported. Version 2.0.0 required Python 3.12.

2.0.0 (2026-11-25)
------------------

This version changes the project layout and toolchain, makes the queries safe
to use with any value, and adds databases and features. Code which only uses
the names exported by the packages, such as ``from pysqlx import Table`` or
``from pysqlx.clients import ClientFactory``, keeps working on a supported
version of Python, except where noted under "Changed".

Security
~~~~~~~~

* The values of the conditions are passed to the database as parameters.
  They used to be written into the SQL without escaping, so a value with a
  quote broke the statement and a value chosen by someone else could change
  it. ``get_query_string()`` still writes the values into the SQL, for
  reading, and now escapes them.

Added
~~~~~

* PostgreSQL, with ``ClientFactory.get_psycopg_client()``, and MySQL and
  MariaDB, with ``ClientFactory.get_pymysql_client()``.
* Transactions: ``begin()``, ``commit()``, ``rollback()`` and the
  ``transaction()`` context manager of the clients. See
  :doc:`/guide/transactions`.
* ``close()`` on the clients, which can also be used in a ``with`` statement.
* Joins, aggregates with ``group_by``, and ``offset`` in select queries. See
  :doc:`/guide/queries`.
* Columns for booleans, dates, decimal numbers and binary data, foreign keys
  and indexes. See :doc:`/guide/structures`.
* ``reflect()`` on the clients, which reads the columns of an existing table
  from the database.
* Exceptions of the package, in ``pysqlx.exceptions``. They derive from
  ``RuntimeError``, which was raised before. See :doc:`/guide/errors`.
* Type hints throughout, with a ``py.typed`` marker. ``execute()`` declares
  what each query returns.
* A docstring for every public class, method and function, and this
  documentation.
* The arguments of ``get_sqlite3_client()`` are optional: without them, the
  database is kept in memory.
* ``connection_options`` and the ODBC driver 18 for the SQL Server client.
* ``Pyodbc`` and ``SqliteThree`` can be imported from ``pysqlx.clients``,
  ``IDialect`` from ``pysqlx.dialects``, ``Structure`` from
  ``pysqlx.structures`` and every clause from
  ``pysqlx.structures.columntypes.logicalclause``.

Changed
~~~~~~~

* Python 3.12 or newer is required. Version 1.0.2 was declared for Python
  3.7 to 3.10.
* ``pyodbc`` is no longer installed with the package. Install it with
  ``pip install "pysqlx[odbc]"`` to use SQL Server. The package can be
  imported, and used with SQLite, without ``pyodbc`` and unixODBC.
* Every module is named in lower case after its class, for example
  ``pysqlx.clients.client_factory`` instead of
  ``pysqlx.clients.ClientFactory``. Import the classes from their package,
  which did not change: ``from pysqlx.clients import ClientFactory``.
* All names are quoted in the SQL, so they may be reserved words or contain
  spaces. The SQL of ``get_query_string()`` changed accordingly, for example
  ``FROM [orders]`` instead of ``FROM orders`` with SQLite.
* Columns are checked by identity, which makes the checks of the queries
  effective: a query now rejects a column of another table with
  ``InvalidArgumentError``.
* A select query can be sorted by a column which it does not read. A union
  is sorted by columns of its first table.
* ``top=0`` reads no rows with SQLite, as with SQL Server. It used to read
  all rows.
* A default value of ``0`` or of an empty string is written into the table
  definition. It used to be ignored.
* Column arguments of a wrong type raise ``InvalidArgumentError`` instead of
  ``AssertionError``.
* The SQLite client enforces foreign keys, and converts dates itself instead
  of relying on the converters of ``sqlite3`` which Python deprecated.
* ``IDialect`` and ``IClient`` implement what the databases have in common,
  so a new dialect or client only defines its differences. Dialects and
  clients written for version 1.0.2 need to be adapted.
* ``pysqlx.__version__`` is read from the installed package, and
  ``pysqlx.version_info`` was removed.

Removed
~~~~~~~

* ``pysqlx.queries.GetTableObject``, which no client could execute. Use
  ``reflect()`` instead.

Fixed
~~~~~

* ``ascend_by`` and ``descend_by`` can be used together.
* ``Column.get_index()`` returns the position of the column. It used to
  return 0 for every column.
* Reading a null value from a date and time column of SQLite no longer
  fails.
* A table with a primary key of several columns can be created in SQLite.
* A client whose creation fails no longer reports an ignored
  ``AttributeError`` when it is deleted.

1.0.2 (2022-05-03)
------------------

* Packaging fixes.

1.0.1 (2022-05-03)
------------------

* First release.
