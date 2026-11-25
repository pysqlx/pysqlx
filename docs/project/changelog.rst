Changelog
=========

All notable changes to ``pysqlx``, most recent first.

Unreleased
----------

The project moved to a new layout and toolchain. Code which only uses the
names exported by the packages, such as ``from pysqlx import Table`` or
``from pysqlx.clients import ClientFactory``, keeps working on a supported
version of Python.

Changed
~~~~~~~

* Python 3.12 or newer is required, together with ``pyodbc`` 5.2 or newer.
  Version 1.0.2 was declared for Python 3.7 to 3.10.
* Every module is named in lower case after its class, for example
  ``pysqlx.clients.client_factory`` instead of
  ``pysqlx.clients.ClientFactory``. Import the classes from their package,
  which did not change: ``from pysqlx.clients import ClientFactory``.
* ``pysqlx.__version__`` is read from the installed package, and
  ``pysqlx.version_info`` was removed.
* Opening a SQLite database on disk without a directory or without a
  database name raises ``RuntimeError`` instead of ``TypeError``.

Added
~~~~~

* Type hints throughout, with a ``py.typed`` marker.
* A docstring for every public class, method and function, and this
  documentation.
* ``Pyodbc`` and ``SqliteThree`` can be imported from ``pysqlx.clients``,
  ``IDialect`` from ``pysqlx.dialects``, ``Structure`` from
  ``pysqlx.structures`` and every clause from
  ``pysqlx.structures.columntypes.logicalclause``.

Removed
~~~~~~~

* ``pysqlx.queries.GetTableObject``, which no client could execute.

Fixed
~~~~~

* A client whose creation fails no longer reports an ignored
  ``AttributeError`` when it is deleted.

1.0.2 (2022-05-03)
------------------

* Packaging fixes.

1.0.1 (2022-05-03)
------------------

* First release.
