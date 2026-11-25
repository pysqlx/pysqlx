Security
========

This page describes what ``pysqlx`` does to keep the use of a database safe,
and what remains the responsibility of your code.

What is safe to take from anywhere
----------------------------------

Values
~~~~~~

The values of the conditions, and the values given to ``insert`` and
``update`` queries, are passed to the database as parameters. They are never
written into the SQL, so a value cannot change what a statement does,
whatever it contains and wherever it comes from:

.. code-block:: python

    name = "x' OR '1'='1"  # typed by a user

    rows = client.select(customers, condition=customer_name == name).execute()
    # no row: the whole text is compared with the names

See :doc:`conditions`.

Names
~~~~~

The names of databases, schemas, tables, columns and indexes are quoted in
the SQL, and the quote character is escaped inside a name. A name can
therefore be a reserved word or contain any character.

Even so, prefer names which your code defines. A name chosen by a user
decides *which* table or column a statement acts on, and quoting does not
make that choice a safe one.

What must come from your code
-----------------------------

Default values
~~~~~~~~~~~~~~

The ``default_value`` of a column is written into the statement which
creates the table as it is. This is what allows a default such as
``CURRENT_TIMESTAMP``, and it is why a string needs its own quotes:
``default_value="'new'"``.

.. warning::

   Never build a default value from untrusted input.

The SQL shown for reading
~~~~~~~~~~~~~~~~~~~~~~~~~

``get_query_string()`` writes the values into the SQL, escaped, so that a
query can be read. Its result is meant for people. Execute the query itself,
not this string.

Connections
-----------

Encryption
~~~~~~~~~~

Whether a connection is encrypted, and whether the certificate of the server
is checked, depends on the library and on the server. To require both, pass
the options of the library as ``connection_options``:

.. code-block:: python

    # PostgreSQL
    client = ClientFactory.get_postgresql_client(
        server_address="db.example.com",
        user_name="reporting",
        user_pass=password,
        connection_options={"sslmode": "verify-full"},
    )

    # MySQL
    client = ClientFactory.get_mysql_client(
        server_address="db.example.com",
        user_name="reporting",
        user_pass=password,
        connection_options={"ssl_ca": "ca.pem", "ssl_verify_identity": True},
    )

The ODBC driver 18 for SQL Server encrypts the connection and checks the
certificate by default. ``{"TrustServerCertificate": "yes"}`` turns the check
off: use it for a development server only.

Passwords
~~~~~~~~~

Do not write a password in the code. Read it from the environment or from a
secret store:

.. code-block:: python

    import os

    client = ClientFactory.get_postgresql_client(
        server_address="db.example.com",
        user_name="reporting",
        user_pass=os.environ["SHOP_DATABASE_PASSWORD"],
    )

``pysqlx`` never logs a password. In the connection string of the SQL Server
client, every value is escaped, so a value which contains ``;`` cannot add an
attribute to the connection string.

Least privilege
~~~~~~~~~~~~~~~

Connect with a user which has the rights the program needs and no more. A
program which only reads does not need the right to drop tables.

SQLite files
~~~~~~~~~~~~

The name of a SQLite database is used as a file name inside the given
directory. A name which would lead out of the directory, such as
``"../other"``, is rejected.

Logging
-------

At the level ``DEBUG``, the logger of the package records every statement,
the values of its parameters and the rows which were read. Do not enable this
level where the log can be read by people who may not see the data. See
:doc:`logging`.

Reporting a vulnerability
-------------------------

Report a vulnerability privately, as described in the
`security policy <https://github.com/pysqlx/pysqlx/security/policy>`_ of the
repository, not in a public issue.
