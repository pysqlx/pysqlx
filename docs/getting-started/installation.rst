Installation
============

Requirements
------------

``pysqlx`` requires Python 3.12 or newer. It has no required dependency:
SQLite works with Python alone.

It is tested on Python 3.12, 3.13 and 3.14 on Linux, macOS and Windows, and
against PostgreSQL, MySQL and Microsoft SQL Server servers.

Installing from PyPI
--------------------

Install the latest release from
`PyPI <https://pypi.org/project/pysqlx/>`_ using ``pip``:

.. code-block:: bash

   pip install pysqlx

or add it to a project managed with ``uv``:

.. code-block:: bash

   uv add pysqlx

Database servers
----------------

The library which reaches a database server is installed on demand, as an
extra:

.. list-table::
   :header-rows: 1
   :widths: 30 35 35

   * - Database
     - Install
     - Library
   * - SQLite
     - ``pip install pysqlx``
     - ``sqlite3``, part of Python
   * - PostgreSQL
     - ``pip install "pysqlx[postgresql]"``
     - ``psycopg``
   * - MySQL, MariaDB
     - ``pip install "pysqlx[mysql]"``
     - ``pymysql``
   * - Microsoft SQL Server
     - ``pip install "pysqlx[odbc]"``
     - ``pyodbc``
   * - All of them
     - ``pip install "pysqlx[all]"``
     -

Creating a client whose library is missing raises
:py:class:`~pysqlx.exceptions.MissingDependencyError`.

ODBC
~~~~

``pyodbc`` needs an ODBC driver manager, which Windows includes. On macOS and
Linux, install unixODBC:

.. code-block:: bash

   brew install unixodbc         # macOS
   sudo apt install unixodbc     # Debian, Ubuntu

It also needs the
`ODBC driver for SQL Server <https://learn.microsoft.com/sql/connect/odbc/download-odbc-driver-for-sql-server>`_.
See :doc:`/guide/clients`.

Installing from GitHub
----------------------

To use changes which are not released yet, install from the
`GitHub repository <https://github.com/pysqlx/pysqlx>`_:

.. code-block:: bash

   pip install git+https://github.com/pysqlx/pysqlx.git

Checking the installation
-------------------------

.. code-block:: python

    import pysqlx

    print(pysqlx.__version__)

Installing for development
--------------------------

To work on ``pysqlx`` itself, see :doc:`/project/development`.
