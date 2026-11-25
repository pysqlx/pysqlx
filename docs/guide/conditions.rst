Conditions
==========

A condition selects the rows which a query reads, changes or removes. It is
built from the columns of a table.

Comparisons
-----------

.. list-table::
   :header-rows: 1
   :widths: 45 55

   * - Expression
     - SQL
   * - ``customer == "Ada"``
     - ``[customer] = 'Ada'``
   * - ``customer != "Ada"``
     - ``[customer] != 'Ada'``
   * - ``total > 50``, ``total >= 50``
     - ``[total] > 50``, ``[total] >= 50``
   * - ``total < 50``, ``total <= 50``
     - ``[total] < 50``, ``[total] <= 50``
   * - ``total.is_between(10, 50)``
     - ``[total] BETWEEN 10 AND 50``
   * - ``customer.is_in_list(("Ada", "Grace"))``
     - ``[customer] IN ( 'Ada', 'Grace' )``
   * - ``customer.is_like("A%")``
     - ``[customer] LIKE 'A%'``
   * - ``placed.is_null()``
     - ``[placed] IS NULL``
   * - ``placed.is_not_null()``
     - ``[placed] IS NOT NULL``

A value can be anything which the database accepts for the column: a string,
a number, a :py:class:`~datetime.datetime`, a :py:class:`~datetime.date`, a
:py:class:`~decimal.Decimal`, a boolean or :py:class:`bytes`. It can also be
another column.

To look for null values, use ``is_null()``: in SQL, nothing is equal to null,
so ``column == None`` never holds.

Combining conditions
--------------------

Use ``&`` for *and*, ``|`` for *or* and ``~`` for *not*. These operators bind
more tightly than comparisons, so each comparison needs its own parentheses.

.. code-block:: python

    condition = (customer == "Ada") & (total > 50)

Negating a condition rewrites it instead of wrapping it in ``NOT``:

.. code-block:: python

    condition = ~((customer == "Ada") | total.is_between(10, 50))

    query = client.select(orders, columns=[order_id], condition=condition)
    print(client.get_query_string(query))
    # SELECT [id] FROM [orders] WHERE ([customer] != 'Ada') AND ([total] NOT BETWEEN 10 AND 50)

Because ``==`` on a column creates a condition, columns cannot be compared
with each other in ordinary Python code. Use ``is`` to check whether two
variables hold the same column.

Values are parameters
---------------------

When a query is executed, the values of its condition are not written into
the SQL. The statement is sent with a placeholder for each value, and the
values are passed to the database separately:

.. code-block:: python

    query = client.select(customers, condition=name == "O'Brien")

    print(query.execute())
    # ((3, "O'Brien"),)

A value can therefore contain quotes or any other character, and a value
chosen by someone else cannot change what the statement does.

``get_query_string()`` writes the values into the SQL, because its result is
meant for reading:

.. code-block:: python

    print(client.get_query_string(query))
    # SELECT [id],
    # [name] FROM [customers] WHERE [name] = 'O''Brien'

To see the statement and the parameters which are really sent, turn on
:doc:`logging`.
