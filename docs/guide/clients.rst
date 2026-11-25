Clients
=======

A client holds the connection to a database and executes queries. Clients are
created by :py:class:`~pysqlx.clients.ClientFactory`.

.. list-table::
   :header-rows: 1
   :widths: 20 30 20 30

   * - Provider
     - Client
     - Dialect
     - Database
   * - ``sqlite3``
     - :py:class:`~pysqlx.clients.SqliteThree`
     - ``sqlite``
     - SQLite, in a file or in memory
   * - ``pyodbc``
     - :py:class:`~pysqlx.clients.Pyodbc`
     - ``mssql``
     - Microsoft SQL Server, through ODBC

SQLite
------

The ``memory`` driver keeps the database in memory. It is lost when the
client is deleted.

.. code-block:: python

    from pysqlx import ClientFactory

    client = ClientFactory.get_sqlite3_client(
        directory_path=None,
        dialect_name="sqlite",
        driver_name="memory",
        database_name="shop",
    )

The ``disk`` driver stores the database in the file ``<database_name>.db`` of
an existing directory, and creates the file if needed:

.. code-block:: python

    client = ClientFactory.get_sqlite3_client(
        directory_path="data",
        dialect_name="sqlite",
        driver_name="disk",
        database_name="shop",  # data/shop.db
    )

``backup_to()`` copies a database to the database of another SQLite client,
for example to save a database kept in memory:

.. code-block:: python

    memory_client.backup_to(disk_client)

SQL Server
----------

.. code-block:: python

    from pysqlx import ClientFactory

    client = ClientFactory.get_pyodbc_client(
        server_address="db.example.com",
        user_name="reporting",
        user_pass="...",
        dialect_name="mssql",
        database_name="shop",
    )

Optional arguments give the port of the server (``server_port``), ask for a
trusted connection (``is_trusted_connection``) and choose the ODBC driver
(``driver_name``).

Without a ``driver_name``, the client uses the first installed driver among
those it knows for the dialect, newest first. To see them:

.. code-block:: python

    print(ClientFactory.get_preferred_drivers("pyodbc", "mssql"))
    print(ClientFactory.get_system_drivers("pyodbc"))  # installed on this machine

Connecting fails with ``RuntimeError`` when none of them is installed.

Listing what is supported
-------------------------

.. code-block:: python

    print(ClientFactory.get_providers_names())
    # ('sqlite3', 'pyodbc')

    print(ClientFactory.get_dialects_names("sqlite3"))
    # ('sqlite',)

    print(ClientFactory.get_preferred_drivers("sqlite3", "sqlite"))
    # ('disk', 'memory')

Closing the connection
----------------------

A client closes its connection when it is deleted. There is no method to
close it earlier.
