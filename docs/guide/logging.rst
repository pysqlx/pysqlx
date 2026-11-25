Logging
=======

``pysqlx`` reports what it does to the logger named ``pysqlx`` of the
:py:mod:`logging` module:

* opening a connection, at the level ``INFO``
* starting, committing and rolling back a transaction, at the level
  ``DEBUG``
* every statement sent to the database, its parameters, its duration and
  what was received, at the level ``DEBUG``

Nothing is shown by default. To see the statements while developing:

.. code-block:: python

    import logging

    logging.basicConfig(level=logging.DEBUG)

    client.select(orders, columns=[total], condition=order_id == 3).execute()
    # DEBUG:pysqlx:executing "SELECT [total] FROM [orders] WHERE [id] = ?" with parameters "[3]"
    # DEBUG:pysqlx:executed in 8.9e-05 seconds
    # DEBUG:pysqlx:received "[(45.0,)]"

The log shows the statement as it is sent, with a placeholder for each value
and the values next to it.

To change the level of ``pysqlx`` only:

.. code-block:: python

    logging.getLogger("pysqlx").setLevel(logging.INFO)

.. note::

   At the level ``DEBUG`` the log contains the values written to and read
   from the database. The password of a connection is never logged. See
   :doc:`security`.
