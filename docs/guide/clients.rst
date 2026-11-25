Clients
=======

A client holds the connection to a database and executes queries. Clients are
created by :py:class:`~pysqlx.clients.ClientFactory`.

.. list-table::
   :header-rows: 1
   :widths: 30 20 25 25

   * - Database
     - Provider
     - Client
     - Dialect
   * - SQLite
     - ``sqlite3``
     - :py:class:`~pysqlx.clients.SqliteThree`
     - ``sqlite``
   * - PostgreSQL
     - ``psycopg``
     - :py:class:`~pysqlx.clients.Psycopg`
     - ``postgresql``
   * - MySQL, MariaDB
     - ``pymysql``
     - :py:class:`~pysqlx.clients.Pymysql`
     - ``mysql``
   * - Microsoft SQL Server
     - ``pyodbc``
     - :py:class:`~pysqlx.clients.Pyodbc`
     - ``mssql``

The same tables and queries work with every client. The libraries of the
database servers are installed as extras, see
:doc:`/getting-started/installation`.

SQLite
------

Without arguments, the database is kept in memory. It is lost when the client
is closed.

.. code-block:: python

    from pysqlx import ClientFactory

    client = ClientFactory.get_sqlite3_client()

With a directory and a database name, the database is stored in the file
``<database_name>.db`` of the directory, which must exist. The file is
created if needed.

.. code-block:: python

    client = ClientFactory.get_sqlite3_client(
        directory_path="data",
        database_name="shop",  # data/shop.db
    )

``backup_to()`` copies a database to the database of another SQLite client,
for example to save a database kept in memory:

.. code-block:: python

    memory_client.backup_to(disk_client)

SQLite has no types for dates, decimal numbers and booleans. The client
stores dates and decimal numbers as text and booleans as integers, and
converts them back when they are read from a column of the matching type.
Decimal numbers are compared and added up as floating point numbers.

Foreign keys are enforced.

PostgreSQL
----------

.. code-block:: python

    client = ClientFactory.get_psycopg_client(
        server_address="db.example.com",
        user_name="reporting",
        user_pass="...",
        database_name="shop",
    )

MySQL and MariaDB
-----------------

.. code-block:: python

    client = ClientFactory.get_pymysql_client(
        server_address="db.example.com",
        user_name="reporting",
        user_pass="...",
        database_name="shop",
    )

SQL Server
----------

.. code-block:: python

    client = ClientFactory.get_pyodbc_client(
        server_address="db.example.com",
        user_name="reporting",
        user_pass="...",
        database_name="shop",
    )

Optional arguments ask for a trusted connection (``is_trusted_connection``),
choose the ODBC driver (``driver_name``) and add attributes to the connection
string (``connection_options``). For example, a server with a self-signed
certificate needs:

.. code-block:: python

    client = ClientFactory.get_pyodbc_client(
        server_address="localhost",
        user_name="sa",
        user_pass="...",
        connection_options={"TrustServerCertificate": "yes"},
    )

Without a ``driver_name``, the client uses the first installed driver among
those it knows, newest first. To see them:

.. code-block:: python

    print(ClientFactory.get_preferred_drivers("pyodbc", "mssql"))
    print(ClientFactory.get_system_drivers("pyodbc"))  # installed on this machine

All server clients take the port of the server as ``server_port`` when it is
not the default one.

Listing what is supported
-------------------------

.. code-block:: python

    print(ClientFactory.get_providers_names())
    # ('sqlite3', 'pyodbc', 'psycopg', 'pymysql')

    print(ClientFactory.get_dialects_names("psycopg"))
    # ('postgresql',)

Closing the connection
----------------------

``close()`` closes the connection of a client. A client can also be used in
a ``with`` statement, which closes it at the end, also when an exception is
raised:

.. code-block:: python

    with ClientFactory.get_sqlite3_client() as client:
        client.create(orders).execute()

    print(client.is_closed)
    # True

A client which is deleted closes its connection as well.

Differences between the databases
---------------------------------

The clients hide most differences. These remain:

* SQLite has neither databases nor schemas to create. MySQL has no schemas
  inside a database: a schema is another name for a database.
* SQL Server needs ``ascend_by`` or ``descend_by`` to use ``offset``.
* MySQL does not support full joins.
* MySQL ends an open transaction when a table is created or dropped.
* PostgreSQL compares strings with ``is_like()`` case-sensitively. MySQL and
  SQL Server usually do not.
