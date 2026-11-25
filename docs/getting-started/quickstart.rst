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

A client is created by :py:class:`~pysqlx.clients.ClientFactory`. Without
arguments, this one keeps a SQLite database in memory, which needs no setup:

.. code-block:: python

    from pysqlx import ClientFactory

    client = ClientFactory.get_sqlite3_client()

Describing a table
------------------

A :py:class:`~pysqlx.structures.Table` starts without columns. Each
``append_*_column`` method adds a column and returns it. Keep the columns:
they are used to build conditions and to choose what a query reads.

.. code-block:: python

    from pysqlx import Table

    orders = Table(table_name="orders")
    order_id = orders.append_integer_column(
        column_name="id", is_identity=True, is_primary_key=True
    )
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
The database generates the values of the identity column, so the query names
the other columns. ``execute_many()`` adds several rows at once.

.. code-block:: python

    from datetime import datetime

    insert = client.insert(orders, columns=[customer, placed, total])

    insert.execute(param_tuple=("Ada", datetime(2026, 1, 5), 120.0))

    insert.execute_many(
        param_tuple_list=[
            ("Grace", datetime(2026, 1, 7), 80.5),
            ("Ada", datetime(2026, 2, 1), 42.0),
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
        columns=[order_id, total],
        condition=(customer == "Ada") & (total > 50),
    )

    print(query.execute())
    # ((1, 120.0),)

The result is a tuple of rows, and each row is a tuple of values.

Seeing the SQL
--------------

A query is a description, not a string. To read the SQL of a query, use
``get_query_string()``:

.. code-block:: python

    print(client.get_query_string(query))
    # SELECT [id],
    # [total] FROM [orders] WHERE ([customer] = 'Ada') AND ([total] > 50)

When the query is executed, the values ``'Ada'`` and ``50`` are not written
into the SQL: they are passed to the database separately, as parameters. A
value can therefore contain any character and come from anywhere.

Changing and removing rows
--------------------------

.. code-block:: python

    client.update(orders, columns=[total], condition=order_id == 3).execute(param_tuple=(45.0,))

    client.delete(orders, condition=customer == "Grace").execute()

    print(client.get_length(orders).execute())
    # 2

Closing
-------

Close the client when you are done, or use it in a ``with`` statement, which
closes it at the end:

.. code-block:: python

    with ClientFactory.get_sqlite3_client() as client:
        client.create(orders).execute()

Where to go next
----------------

* :doc:`/guide/clients` describes connecting to each database
* :doc:`/guide/structures` describes tables, the types of columns, foreign
  keys and indexes
* :doc:`/guide/conditions` describes every condition
* :doc:`/guide/queries` describes every query and what it returns
* :doc:`/guide/transactions` describes grouping changes
* :doc:`/reference/index` documents every class and method
