Queries
=======

The methods of a client create queries. A query holds what to do, and
nothing is sent to the database before it is executed:

.. code-block:: python

    query = client.select(orders)  # nothing happens yet
    rows = query.execute()         # the SQL is sent now

A query can be executed more than once.

.. list-table::
   :header-rows: 1
   :widths: 30 40 30

   * - Method of the client
     - Does
     - ``execute()`` returns
   * - ``create(structure)``
     - creates a table, an index, a schema or a database
     - ``None``
   * - ``drop(structure)``
     - drops a table, an index, a schema or a database
     - ``None``
   * - ``exists(structure)``
     - checks whether a structure exists
     - a boolean
   * - ``reflect(table_name)``
     - reads the columns of a table
     - a table
   * - ``is_empty(table)``
     - checks whether a table has no rows
     - a boolean
   * - ``count_rows(table)``
     - counts the rows of a table
     - an integer
   * - ``insert(table)``
     - adds rows
     - ``None``
   * - ``select(table)``
     - reads rows
     - a tuple of rows
   * - ``select_distinct(table, columns)``
     - reads distinct values
     - a tuple of rows
   * - ``union(...)``
     - combines select queries
     - a tuple of rows
   * - ``update(table, condition)``
     - changes rows
     - ``None``
   * - ``delete(table, condition)``
     - removes rows
     - ``None``
   * - ``truncate(table)``
     - removes all rows
     - ``None``

The return types are declared, so a type checker knows that
``client.is_empty(orders).execute()`` is a boolean.

Inserting
---------

The values are given at execution, in the order of the columns of the table:

.. code-block:: python

    client.insert(customers).execute(parameters=(1, "Ada"))

To give some of the columns only, name them. This is needed when the table
has an identity column, whose values come from the database:

.. code-block:: python

    insert = client.insert(orders, columns=[customer_id, placed, total])

    insert.execute(parameters=(1, datetime(2026, 1, 5), 120.0))

``execute_many()`` executes the query once per row, which is faster than
executing it in a loop:

.. code-block:: python

    insert.execute_many(
        parameters_list=[
            (2, datetime(2026, 1, 7), 80.5),
            (1, datetime(2026, 2, 1), 42.0),
        ]
    )

Selecting
---------

Without arguments, ``select()`` reads all columns of all rows:

.. code-block:: python

    print(client.select(orders).execute())
    # ((1, 1, datetime.datetime(2026, 1, 5, 0, 0), 120.0),
    #  (2, 2, datetime.datetime(2026, 1, 7, 0, 0), 80.5),
    #  (3, 1, datetime.datetime(2026, 2, 1, 0, 0), 42.0))

Its optional arguments are:

* ``columns``, the columns to read
* ``condition``, described in :doc:`/guide/conditions`
* ``ascend_by`` and ``descend_by``, the columns to sort by. A table can be
  sorted by a column which is not read.
* ``limit``, the maximum number of rows, and ``offset``, the number of rows to
  skip first
* ``group_by`` and ``joins``, described below

.. code-block:: python

    query = client.select(orders, columns=[order_id, total], limit=2, descend_by=[total])

    print(query.execute())
    # ((1, 120.0), (2, 80.5))

``limit`` and ``offset`` read a table page by page. Sort the rows, so that the
pages are well defined:

.. code-block:: python

    query = client.select(orders, columns=[order_id], limit=1, offset=1, ascend_by=[order_id])

    print(query.execute())
    # ((2,),)

``select_distinct()`` returns each combination of values once:

.. code-block:: python

    query = client.select_distinct(orders, columns=[customer_id], ascend_by=[customer_id])

    print(query.execute())
    # ((1,), (2,))

Aggregates
----------

An aggregate is a value computed over several rows. The methods ``count()``,
``sum()``, ``avg()``, ``min()`` and ``max()`` of a column create aggregates,
which a select query reads in place of columns. ``count()`` of a table counts
rows.

.. code-block:: python

    print(client.select(orders, columns=[total.max()]).execute())
    # ((120.0,),)

With ``group_by``, the aggregates are computed for each group of rows which
have the same values in the given columns:

.. code-block:: python

    query = client.select(
        orders,
        columns=[customer_id, orders.count(), total.sum()],
        group_by=[customer_id],
        ascend_by=[customer_id],
    )

    print(query.execute())
    # ((1, 2, 162.0), (2, 1, 80.5))

To keep some of the groups only, give a condition on an aggregate as
``having``. A ``condition`` selects rows before they are grouped; ``having``
selects groups afterwards.

.. code-block:: python

    query = client.select(
        orders,
        columns=[customer_id, total.sum()],
        group_by=[customer_id],
        having=total.sum() > 100,
    )

    print(query.execute())
    # ((1, 162.0),)

Joins
-----

A join adds the columns of another table to a select query. Its condition
relates the rows of the two tables, usually by comparing two columns.

.. code-block:: python

    from pysqlx import Join

    query = client.select(
        orders,
        columns=[name, total],
        joins=[Join(table=customers, condition=customer_id == customer_key)],
        ascend_by=[total],
    )

    print(query.execute())
    # (('Ada', 42.0), ('Grace', 80.5), ('Ada', 120.0))

.. image:: /_static/joins-light.svg
    :alt: The rows which an inner, a left, a right and a full join keep
    :width: 100%
    :class: only-light

.. image:: /_static/joins-dark.svg
    :alt: The rows which an inner, a left, a right and a full join keep
    :width: 100%
    :class: only-dark

The ``kind`` of a join says which rows without a match are kept: none for
``"inner"``, the default, those of the table of the query for ``"left"``,
those of the joined table for ``"right"``, and both for ``"full"``.

The columns, the conditions and the sorting of the query can use the columns
of all its tables.

To join a table to itself, join it to an alias. ``alias()`` gives a second
reference to a table under another name, with its own copies of the columns,
in the same order. This query pairs each order with the larger orders of the
same customer:

.. code-block:: python

    larger = orders.alias("larger")
    larger_id, larger_customer, _, larger_total = larger.columns

    query = client.select(
        orders,
        columns=[order_id, larger_id],
        joins=[
            Join(
                table=larger,
                condition=(customer_id == larger_customer) & (total < larger_total),
            )
        ],
    )

    print(query.execute())
    # ((3, 1),)

Combining selections
--------------------

``union()`` combines the rows of select queries on several tables. Give the
tables, one select query per table, and the columns to take from each:

.. code-block:: python

    query = client.union(
        table_list=(customers, orders),
        query_list=(
            client.select(customers, columns=[customer_key]),
            client.select(orders, columns=[customer_id]),
        ),
        columns_list=((customer_key,), (customer_id,)),
        ascend_by=[customer_key],
    )

Duplicate rows are removed unless ``is_all=True``. The rows are sorted by
columns of the first table.

Updating and deleting
---------------------

Both need a condition. The new values of an update are given at execution,
one per column to change:

.. code-block:: python

    client.update(orders, columns=[total], condition=order_id == 3).execute(parameters=(45.0,))

    client.delete(orders, condition=customer_id == 2).execute()

``truncate()`` removes all rows of a table and ``drop()`` removes the table
itself:

.. code-block:: python

    client.truncate(orders).execute()
    client.drop(orders).execute()

The SQL of a query
------------------

``get_query_string()`` gives the SQL of a query, for reading. The same query
gives different SQL for different databases:

.. code-block:: python

    print(client.get_query_string(client.select(orders, columns=[total], limit=10)))

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Database
     - SQL
   * - SQLite
     - ``SELECT [total] FROM [orders] LIMIT 10``
   * - PostgreSQL
     - ``SELECT "total" FROM "orders" LIMIT 10``
   * - MySQL
     - ``SELECT `total` FROM `orders` LIMIT 10``
   * - SQL Server
     - ``SELECT TOP (10) [total] FROM [orders]``
