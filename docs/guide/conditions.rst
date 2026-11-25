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

A value can be a string, a number, a :py:class:`~datetime.datetime` or
another column.

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
    # SELECT [id] FROM orders WHERE ([customer] != 'Ada') AND ([total] NOT BETWEEN 10 AND 50)

Because ``==`` on a column creates a condition, columns cannot be compared
with each other in ordinary Python code. Use ``is`` to check whether two
variables hold the same column.

Values are written into the SQL
-------------------------------

.. warning::

   The values of a condition are written into the text of the SQL statement
   as they are, without escaping. A string which contains a quote breaks the
   statement, and a string chosen by someone else can change what the
   statement does. Do not build conditions from untrusted input.

The values of ``insert`` and ``update`` queries are different: they are
passed to the database separately from the statement, as parameters.
