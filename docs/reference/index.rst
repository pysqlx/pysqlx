API Reference
=============

This reference is generated from the docstrings of the package. It documents
every public class, method and function.

``ClientFactory``, ``Database``, ``Schema`` and ``Table`` can also be imported
directly from the top-level ``pysqlx`` package, for example
``from pysqlx import Table``.

Clients
-------

.. currentmodule:: pysqlx.clients

.. autosummary::
   :toctree: api
   :template: autosummary/class.rst
   :nosignatures:

   ClientFactory
   IClient
   SqliteThree
   Pyodbc

Structures
----------

.. currentmodule:: pysqlx.structures

.. autosummary::
   :toctree: api
   :template: autosummary/class.rst
   :nosignatures:

   Structure
   Database
   Schema
   Table

Columns
-------

.. currentmodule:: pysqlx.structures.columntypes

.. autosummary::
   :toctree: api
   :template: autosummary/class.rst
   :nosignatures:

   Column
   CharStringColumn
   DatetimeColumn
   FloatColumn
   IntegerColumn
   TextColumn

Conditions
----------

.. currentmodule:: pysqlx.structures.columntypes.logicalclause

.. autosummary::
   :toctree: api
   :template: autosummary/class.rst
   :nosignatures:

   Clause
   And
   Or
   Equal
   NotEqual
   GreaterThan
   GreaterThanEqual
   LessThan
   LessThanEqual
   Between
   NotBetween
   InList
   NotInList
   IsNull
   IsNotNull
   Like
   NotLike

Queries
-------

.. currentmodule:: pysqlx.queries

.. autosummary::
   :toctree: api
   :template: autosummary/class.rst
   :nosignatures:

   Query
   Create
   Drop
   IsExists
   IsEmpty
   GetLength
   Insert
   Select
   SelectDistinct
   Union
   Update
   Delete
   Truncate

Dialects
--------

.. currentmodule:: pysqlx.dialects

.. autosummary::
   :toctree: api
   :template: autosummary/class.rst
   :nosignatures:

   IDialect
   Sqlite
   MsSql
