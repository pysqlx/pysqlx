Transactions
============

By default, every query takes effect at once. A transaction groups several
queries: their changes take effect together when the transaction is
committed, or not at all when it is rolled back.

The ``transaction()`` method of a client runs the queries of a ``with`` block
in one transaction. It commits at the end of the block, and rolls back if the
block raises an exception:

.. code-block:: python

    with client.transaction():
        client.insert(customers).execute(param_tuple=(4, "Linus"))
        client.insert(orders, columns=[customer_id, total]).execute(param_tuple=(4, 10.0))

If the second insert fails, the first one is undone and the exception is
raised again:

.. code-block:: python

    try:
        with client.transaction():
            client.delete(orders, condition=customer_id == 1).execute()
            raise ValueError("changed my mind")
    except ValueError:
        pass

    print(client.get_length(orders).execute())  # as before

A transaction can also be controlled step by step:

.. code-block:: python

    client.begin()

    client.delete(orders, condition=customer_id == 1).execute()

    if client.get_length(orders).execute() == 0:
        client.rollback()
    else:
        client.commit()

``is_in_transaction`` tells whether a transaction is open. A client has one
transaction at a time: starting a second one, or committing without one,
raises :py:class:`~pysqlx.exceptions.TransactionError`. Closing a client
rolls back its open transaction.

.. note::

   MySQL ends an open transaction when a table is created or dropped, so
   these queries cannot be rolled back there.
