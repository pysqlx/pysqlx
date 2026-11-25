Logging
=======

``pysqlx`` reports what it does to the logger named ``pysqlx`` of the
:py:mod:`logging` module:

* opening a connection, at the level ``INFO``
* every statement sent to the database, its parameters, its duration and
  what was received, at the level ``DEBUG``

Nothing is shown by default. To see the statements while developing:

.. code-block:: python

    import logging

    logging.basicConfig(level=logging.DEBUG)

    client.get_length(orders).execute()
    # DEBUG:pysqlx:executing "SELECT COUNT(*) FROM orders"
    # DEBUG:pysqlx:executed in 7.4e-05 seconds
    # DEBUG:pysqlx:received "[(3,)]"

To change the level of ``pysqlx`` only:

.. code-block:: python

    logging.getLogger("pysqlx").setLevel(logging.INFO)

.. note::

   At the level ``DEBUG`` the log contains the values written to and read
   from the database. The password of a connection is never logged.
