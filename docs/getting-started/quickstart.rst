Quickstart
==========

This page walks through the whole interface of ``pysqlx`` in a few minutes.
Working with a database takes four steps:

1. create a client, which connects to the database
2. describe a table and its columns
3. ask the client for a query
4. execute the query

Connecting
----------

A client is created by :py:class:`~pysqlx.clients.ClientFactory`. This one
keeps a SQLite database in memory, which needs no setup:

.. code-block:: python

    from pysqlx import ClientFactory

    client = ClientFactory.get_sqlite3_client(
        directory_path=None,
        dialect_name="sqlite",
        driver_name="memory",
        database_name="shop",
    )

Describing a table
------------------

A :py:class:`~pysqlx.structures.Table` starts without columns. Each
``append_*_column`` method adds a column and returns it. Keep the columns:
they are used to build conditions and to choose what a query reads.

.. code-block:: python

    from pysqlx import Table

    orders = Table(table_name="orders")
    order_id = orders.append_integer_column(column_name="id", is_primary_key=True)
    customer = orders.append_char_string_column(column_name="customer", size=50)
    placed = orders.append_datetime_column(column_name="placed")
    total = orders.append_float_column(column_name="total")

Describing a table does not touch the database. Creating it is a query:

.. code-block:: python

    print(client.is_exists(orders).execute())
    # False

    client.create(orders).execute()

    print(client.is_exists(orders).execute())
    # True

Adding rows
-----------

The values of a row are given when the query is executed, one per column.
``execute_many()`` adds several rows at once.

.. code-block:: python

    from datetime import datetime

    client.insert(orders).execute(param_tuple=(1, "Ada", datetime(2026, 1, 5), 120.0))

    client.insert(orders).execute_many(
        param_tuple_list=[
            (2, "Grace", datetime(2026, 1, 7), 80.5),
            (3, "Ada", datetime(2026, 2, 1), 42.0),
        ]
    )

    print(client.get_length(orders).execute())
    # 3

Reading rows
------------

Comparing a column with a value gives a condition. Conditions are combined
with ``&`` and ``|`` and negated with ``~``. Put each comparison in
parentheses.

.. code-block:: python

    query = client.select(
        orders,
        columns=[customer, total],
        condition=(customer == "Ada") & (total > 50),
    )

    print(query.execute())
    # (('Ada', 120.0),)

The result is a tuple of rows, and each row is a tuple of values.

Seeing the SQL
--------------

A query is a description, not a string. To see the SQL which a client sends
for it, use ``get_query_string()``:

.. code-block:: python

    print(client.get_query_string(query))
    # SELECT [customer],
    # [total] FROM orders WHERE ([customer] = 'Ada') AND ([total] > 50)

Changing and removing rows
--------------------------

.. code-block:: python

    client.update(orders, columns=[total], condition=order_id == 3).execute(param_tuple=(45.0,))

    client.delete(orders, condition=customer == "Grace").execute()

    print(client.get_length(orders).execute())
    # 2

Where to go next
----------------

* :doc:`/guide/clients` describes connecting to SQLite and to SQL Server
* :doc:`/guide/structures` describes tables and the types of columns
* :doc:`/guide/conditions` describes every condition
* :doc:`/guide/queries` describes every query and what it returns
* :doc:`/reference/index` documents every class and method
