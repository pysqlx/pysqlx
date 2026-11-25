Tables and Columns
==================

Structures describe what is in a database: databases, schemas, tables and
columns. Describing a structure does not touch the database; pass it to a
query to create it, read from it or drop it.

Tables
------

.. code-block:: python

    from pysqlx import Table

    orders = Table(table_name="orders")

On a SQL Server, a table can be placed in a schema and in a database, which
gives its qualified name ``[shop].[sales].[orders]``:

.. code-block:: python

    from pysqlx import Database, Schema, Table

    orders = Table(
        table_name="orders",
        database=Database(database_name="shop"),
        schema=Schema(schema_name="sales"),
    )

SQLite ignores the database and the schema of a table.

Columns
-------

Columns are added with the ``append_*_column`` methods of the table, in the
order in which they appear in the table. Each method returns the new column.

.. list-table::
   :header-rows: 1
   :widths: 36 28 36

   * - Method
     - Holds
     - Specific arguments
   * - ``append_char_string_column()``
     - strings of a limited size
     - ``size`` (255), ``is_unicode``, ``is_fixed``
   * - ``append_text_column()``
     - text of unlimited size
     - ``is_unicode``
   * - ``append_integer_column()``
     - integers
     - ``n_bytes`` (1, 2, 4 or 8), ``is_identity``
   * - ``append_float_column()``
     - floating point numbers
     - ``is_double`` (true by default)
   * - ``append_datetime_column()``
     - dates with a time
     -

All of them take the name of the column and these optional arguments:

* ``default_value``, the default value of the column
* ``is_primary_key``, whether the column is part of the primary key
* ``is_prevent_null``, whether the column rejects null values

An identity column gets its values from the database. Identity and primary
key columns always reject null values and cannot have a default value.

.. code-block:: python

    order_id = orders.append_integer_column(
        column_name="id",
        is_identity=True,
        is_primary_key=True,
    )
    customer = orders.append_char_string_column(
        column_name="customer",
        size=50,
        is_unicode=True,
    )

The columns of a table are available as ``orders.columns``.

Databases and schemas
---------------------

On a SQL Server, databases and schemas can be created, dropped and looked
for like tables:

.. code-block:: python

    from pysqlx import Database, Schema

    shop = Database(database_name="shop")

    if not client.is_exists(shop).execute():
        client.create(shop).execute()

    client.create(Schema(schema_name="sales", owner_name="dbo")).execute()

With SQLite these queries raise ``RuntimeError``.
