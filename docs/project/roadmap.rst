Road Map
========

What is open: work which is planned, defects which are known, and questions
which wait for an answer. An item leaves this page when it is done, and is
then described in the :doc:`changelog`. The reasons behind what was decided
are in :doc:`decisions`.

This page is the only list of open work. Do not keep such a list anywhere
else.

To check
--------

* **First daily runs.** The Tests and CodeQL workflows run daily on
  ``master`` since version 2.1.0. Check that the first runs started and
  passed, as the badge of the README shows their result.
* **Settings of the repository.** Confirm that these are enabled: private
  vulnerability reporting, which ``SECURITY.md`` sends reporters to, secret
  scanning with push protection, and the security updates of Dependabot.

To decide
---------

* **The required check on macOS.** ``SQL Server / macos-15-intel`` is
  required to merge. It waits for a scarce runner and then takes about 11
  minutes, also for a change of the documentation alone. Options: keep it,
  require it no longer and rely on the daily run, or run it daily only.
* **Names which were not changed in version 3.** They were noticed in the
  audit of the names, and need a new major version: ``ascend_by`` and
  ``descend_by``, ``val_list``, ``clause0`` and ``clause1``, ``value0`` and
  ``value1``, ``col_obj``, ``append_char_string_column()``, and the capital
  letters in the methods of the dialects, such as
  ``get_Select_table_string()``.
* **Default values.** The ``default_value`` of a column is written into the
  SQL as it is. Accepting a Python value, written as an escaped literal,
  would be safer, but changes what a string means.

Known defects
-------------

* **Union with a condition.** The ``condition`` of a union is written after
  the last select query, so it only applies to that one.
* **Empty lists.** ``is_in_list()`` with no value writes ``IN ( )``, which
  the databases reject.
* **Conditions are not checked.** A query accepts a condition, or a
  ``having``, which uses a column of a table that is not part of the query,
  and fails in the database.
* **Tables in a schema on SQL Server.** ``exists()`` looks a table up by
  its name alone, in every schema.
* **Foreign keys with the same name on PostgreSQL.** ``reflect()`` can mix
  up two foreign keys of different tables which have the same name.
* **Decimal numbers on SQLite.** They are stored as text and compared as
  floating point numbers, so large or precise values lose digits.
* **Dates in the SQL shown for reading.** With SQLite,
  ``get_query_string()`` shows a date and time without its microseconds,
  while the value which is executed keeps them.

Features
--------

* Sort by an aggregate, for example the customers by the sum of their
  orders.
* Read the indexes of a table with ``reflect()``.
* Keep the Unicode flag of character columns in ``reflect()`` on PostgreSQL
  and MySQL.
* Columns for more types, such as times, JSON and UUID. ``reflect()`` raises
  ``UnsupportedOperationError`` for a column of an unknown type.

Project
-------

* A figure in the README, which needs a PNG as PyPI does not show SVG.
* Tests of the PostgreSQL and MySQL clients on Windows and macOS, if their
  libraries ever behave differently there.
