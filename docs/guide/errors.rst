Errors
======

The exceptions which ``pysqlx`` raises derive from
:py:class:`~pysqlx.exceptions.PysqlxError`:

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - Exception
     - Raised when
   * - :py:class:`~pysqlx.exceptions.InvalidArgumentError`
     - an argument has an invalid value or type, such as a column of another
       table
   * - :py:class:`~pysqlx.exceptions.ConnectionFailedError`
     - a client cannot connect to its database
   * - :py:class:`~pysqlx.exceptions.MissingDependencyError`
     - the library which a client needs is not installed
   * - :py:class:`~pysqlx.exceptions.UnsupportedOperationError`
     - a database or a query does not support an operation, such as creating
       a schema in SQLite
   * - :py:class:`~pysqlx.exceptions.TransactionError`
     - a transaction is started, committed or rolled back wrongly

.. code-block:: python

    from pysqlx.exceptions import InvalidArgumentError, PysqlxError

    try:
        client.select(orders, columns=[name])  # a column of another table
    except InvalidArgumentError as error:
        print(error)
        # invalid columns

    try:
        client = ClientFactory.get_psycopg_client(...)
    except PysqlxError as error:
        print(f"cannot use the database: {error}")

``PysqlxError`` derives from ``RuntimeError``, which earlier versions raised,
so code which catches ``RuntimeError`` keeps working.
``InvalidArgumentError`` is also a ``ValueError`` and
``MissingDependencyError`` an ``ImportError``.

Errors of the database
----------------------

An error which the database reports while a query is executed, such as a row
which breaks a foreign key, is raised as the exception of the library of the
client, for example ``sqlite3.IntegrityError`` or
``psycopg.errors.ForeignKeyViolation``. These exceptions are not converted.
