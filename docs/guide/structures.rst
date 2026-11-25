Tables and Columns
==================

Structures describe what is in a database: databases, schemas, tables,
columns and indexes. Describing a structure does not touch the database; pass
it to a query to create it, read from it or drop it.

Tables
------

.. code-block:: python

    from pysqlx import Table

    orders = Table(table_name="orders")

A table can be placed in a schema and in a database:

.. code-block:: python

    from pysqlx import Database, Schema, Table

    orders = Table(
        table_name="orders",
        database=Database(database_name="shop"),
        schema=Schema(schema_name="sales"),
    )

How the table is then named depends on the database:
``[shop].[sales].[orders]`` on SQL Server, ``"sales"."orders"`` on
PostgreSQL, and ```shop`.`orders``` on MySQL. SQLite ignores both.

Names are quoted in the SQL, so they may contain spaces and reserved words.

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
   * - ``append_decimal_column()``
     - :py:class:`~decimal.Decimal` numbers
     - ``precision`` (18), ``scale`` (2)
   * - ``append_boolean_column()``
     - booleans
     -
   * - ``append_datetime_column()``
     - :py:class:`~datetime.datetime` values
     -
   * - ``append_date_column()``
     - :py:class:`~datetime.date` values
     -
   * - ``append_binary_column()``
     - :py:class:`bytes` of unlimited size
     -

All of them take the name of the column and these optional arguments:

* ``default_value``, the default value of the column
* ``is_primary_key``, whether the column is part of the primary key
* ``is_prevent_null``, whether the column rejects null values

An identity column gets its values from the database. Identity and primary
key columns always reject null values and cannot have a default value.

A default value is written into the SQL as it is, so a string needs its own
quotes: ``default_value="'new'"``.

.. code-block:: python

    order_id = orders.append_integer_column(
        column_name="id",
        is_identity=True,
        is_primary_key=True,
    )
    customer_id = orders.append_integer_column(column_name="customer_id")
    total = orders.append_decimal_column(column_name="total", precision=10, scale=2)

The columns of a table are available as ``orders.columns``.

Foreign keys
------------

A foreign key makes columns of a table refer to the rows of another table.
The database then rejects a row which refers to a row that does not exist.
It takes effect when the table is created.

.. code-block:: python

    customers = Table(table_name="customers")
    customer_key = customers.append_integer_column(column_name="id", is_primary_key=True)

    orders.append_foreign_key(columns=[customer_id], reference_columns=[customer_key])

    client.create(customers).execute()
    client.create(orders).execute()

Indexes
-------

An index speeds up looking rows up by the values of its columns. It is
created, looked for and dropped like a table. A unique index also rejects
rows with the same values in its columns.

.. code-block:: python

    from pysqlx import Index

    index = Index(index_name="orders_by_customer", table=orders, columns=[customer_id])

    client.create(index).execute()

    print(client.is_exists(index).execute())
    # True

    client.drop(index).execute()

Reading a table from the database
---------------------------------

To work with a table which exists already, read its columns from the database
instead of describing them:

.. code-block:: python

    orders = client.reflect("orders").execute()

    print([(type(col).__name__, col.column_name) for col in orders.columns])
    # [('IntegerColumn', 'id'), ('IntegerColumn', 'customer_id'), ...]

    order_id, customer_id = orders.columns[:2]

    rows = client.select(orders, condition=customer_id == 1).execute()

Foreign keys are not read. A column whose type the package does not know
raises :py:class:`~pysqlx.exceptions.UnsupportedOperationError`.

Databases and schemas
---------------------

On a database server, databases and schemas can be created, dropped and
looked for like tables:

.. code-block:: python

    from pysqlx import Database, Schema

    shop = Database(database_name="shop")

    if not client.is_exists(shop).execute():
        client.create(shop).execute()

    client.create(Schema(schema_name="sales")).execute()

With SQLite these queries raise
:py:class:`~pysqlx.exceptions.UnsupportedOperationError`.
