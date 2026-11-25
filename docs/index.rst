pysqlx
======

|tests| |docs| |pypi| |pyversions| |weekly| |total| |license|

.. |tests| image:: https://github.com/pysqlx/pysqlx/actions/workflows/tests.yml/badge.svg
    :target: https://github.com/pysqlx/pysqlx/actions/workflows/tests.yml
    :alt: Tests

.. |docs| image:: https://readthedocs.org/projects/pysqlx/badge/?version=latest
    :target: https://pysqlx.readthedocs.io/
    :alt: Documentation

.. |pypi| image:: https://img.shields.io/pypi/v/pysqlx
    :target: https://pypi.org/project/pysqlx/
    :alt: PyPI version

.. |pyversions| image:: https://img.shields.io/pypi/pyversions/pysqlx
    :target: https://pypi.org/project/pysqlx/
    :alt: Python versions

.. |weekly| image:: https://img.shields.io/pypi/dw/pysqlx?label=downloads%2Fweek
    :target: https://pypistats.org/packages/pysqlx
    :alt: Weekly downloads

.. |total| image:: https://img.shields.io/pepy/dt/pysqlx?label=total%20downloads
    :target: https://pepy.tech/projects/pysqlx
    :alt: Total downloads

.. |license| image:: https://img.shields.io/pypi/l/pysqlx
    :target: https://github.com/pysqlx/pysqlx/blob/master/LICENSE
    :alt: License


``pysqlx`` is a Python package for working with SQL databases without writing
SQL. Tables, conditions and queries are Python objects, and a client turns
them into the SQL of the database it is connected to.

.. code-block:: python

    from pysqlx import ClientFactory, Table

    client = ClientFactory.get_sqlite3_client()

    orders = Table(table_name="orders")
    customer = orders.append_char_string_column(column_name="customer", size=50)
    total = orders.append_float_column(column_name="total")

    client.create(orders).execute()
    client.insert(orders).execute_many(param_tuple_list=[("Ada", 120.0), ("Grace", 80.5)])

    rows = client.select(orders, condition=total > 100).execute()
    # (('Ada', 120.0),)

.. image:: /_static/overview-light.svg
    :alt: A query written in Python becomes a SQL statement and its parameters
    :width: 100%
    :class: only-light

.. image:: /_static/overview-dark.svg
    :alt: A query written in Python becomes a SQL statement and its parameters
    :width: 100%
    :class: only-dark

It supports four databases through one interface:

* SQLite, in a file or in memory, with nothing to install
* PostgreSQL, using ``psycopg``
* MySQL and MariaDB, using ``pymysql``
* Microsoft SQL Server, through ODBC, using ``pyodbc``

The values of the conditions are always passed to the database as parameters,
never written into the SQL.

``pysqlx`` is maintained by `Bassem Girgis <https://girgis.me>`_.

.. toctree::
   :maxdepth: 2
   :caption: Getting started

   getting-started/installation
   getting-started/quickstart

.. toctree::
   :maxdepth: 2
   :caption: User guide

   guide/clients
   guide/structures
   guide/conditions
   guide/queries
   guide/transactions
   guide/errors
   guide/logging
   guide/security

.. toctree::
   :maxdepth: 2
   :caption: Reference

   reference/index

.. toctree::
   :maxdepth: 2
   :caption: Project

   project/changelog
   project/development
   project/license

Indices
-------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
