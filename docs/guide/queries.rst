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
     - creates a table, a schema or a database
     - ``None``
   * - ``drop(structure)``
     - drops a table, a schema or a database
     - ``None``
   * - ``is_exists(structure)``
     - checks whether a structure exists
     - a boolean
   * - ``is_empty(table)``
     - checks whether a table has no rows
     - a boolean
   * - ``get_length(table)``
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

Schemas and databases only exist on a SQL Server. See
:doc:`/guide/structures`.

Inserting
---------

The values are given at execution, in the order of the columns of the table:

.. code-block:: python

    client.insert(orders).execute(param_tuple=(1, "Ada", datetime(2026, 1, 5), 120.0))

To give some of the columns only, name them:

.. code-block:: python

    client.insert(orders, columns=[order_id, customer]).execute(param_tuple=(4, "Linus"))

``execute_many()`` executes the query once per row, which is faster than
executing it in a loop:

.. code-block:: python

    client.insert(orders).execute_many(
        param_tuple_list=[
            (2, "Grace", datetime(2026, 1, 7), 80.5),
            (3, "Ada", datetime(2026, 2, 1), 42.0),
        ]
    )

Selecting
---------

Without arguments, ``select()`` reads all columns of all rows:

.. code-block:: python

    print(client.select(orders).execute())
    # ((1, 'Ada', datetime.datetime(2026, 1, 5, 0, 0), 120.0),
    #  (2, 'Grace', datetime.datetime(2026, 1, 7, 0, 0), 80.5),
    #  (3, 'Ada', datetime.datetime(2026, 2, 1, 0, 0), 42.0))

Its optional arguments are:

* ``columns``, the columns to read
* ``condition``, described in :doc:`/guide/conditions`
* ``top``, the maximum number of rows
* ``ascend_by`` or ``descend_by``, the columns to sort by

.. code-block:: python

    query = client.select(orders, columns=[order_id, total], top=2, descend_by=[total])

    print(query.execute())
    # ((1, 120.0), (2, 80.5))

``select_distinct()`` returns each combination of values once:

.. code-block:: python

    query = client.select_distinct(orders, columns=[customer], ascend_by=[customer])

    print(query.execute())
    # (('Ada',), ('Grace',))

Combining selections
--------------------

``union()`` combines the rows of select queries on several tables. Give the
tables, one select query per table, and the columns to take from each:

.. code-block:: python

    archive = Table(table_name="archive")
    archived_customer = archive.append_char_string_column(column_name="customer", size=50)

    query = client.union(
        structure_list=(orders, archive),
        query_list=(
            client.select(orders, columns=[customer]),
            client.select(archive, columns=[archived_customer]),
        ),
        columns_list=((customer,), (archived_customer,)),
        ascend_by=[customer],
    )

Duplicate rows are removed unless ``is_all=True``.

Updating and deleting
---------------------

Both need a condition. The new values of an update are given at execution,
one per column to change:

.. code-block:: python

    client.update(orders, columns=[total], condition=order_id == 3).execute(param_tuple=(45.0,))

    client.delete(orders, condition=customer == "Grace").execute()

``truncate()`` removes all rows of a table and ``drop()`` removes the table
itself:

.. code-block:: python

    client.truncate(orders).execute()
    client.drop(orders).execute()

The SQL of a query
------------------

``get_query_string()`` gives the SQL which a client sends for a query. The
same query gives different SQL for different databases:

.. code-block:: python

    print(client.get_query_string(client.select(orders, top=10)))

With SQLite the statement ends with ``LIMIT (10)``, and with SQL Server it
starts with ``SELECT TOP (10)``.
