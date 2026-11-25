Installation
============

Requirements
------------

``pysqlx`` requires Python 3.12 or newer. It depends on one package, which is
installed automatically:

* ``pyodbc`` 5.2 or newer, used to reach database servers through ODBC

It is tested on Python 3.12, 3.13 and 3.14 on Linux, macOS and Windows.

ODBC on macOS
~~~~~~~~~~~~~

On macOS, ``pyodbc`` needs the unixODBC library, and ``pysqlx`` cannot be
imported without it, even to use SQLite only. Install it with
`Homebrew <https://brew.sh>`_:

.. code-block:: bash

   brew install unixodbc

To connect to a Microsoft SQL Server, also install one of its ODBC drivers on
any operating system. See :doc:`/guide/clients`.

Installing from PyPI
--------------------

Install the latest release from
`PyPI <https://pypi.org/project/pysqlx/>`_ using ``pip``:

.. code-block:: bash

   pip install pysqlx

or add it to a project managed with ``uv``:

.. code-block:: bash

   uv add pysqlx

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
