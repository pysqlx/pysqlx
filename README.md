# pysqlx

[![Tests](https://github.com/pysqlx/pysqlx/actions/workflows/tests.yml/badge.svg)](https://github.com/pysqlx/pysqlx/actions/workflows/tests.yml)
[![Documentation](https://readthedocs.org/projects/pysqlx/badge/?version=latest)](https://pysqlx.readthedocs.io/)
[![PyPI version](https://img.shields.io/pypi/v/pysqlx)](https://pypi.org/project/pysqlx/)
[![Python versions](https://img.shields.io/pypi/pyversions/pysqlx)](https://pypi.org/project/pysqlx/)
[![Weekly downloads](https://img.shields.io/pypi/dw/pysqlx?label=downloads%2Fweek)](https://pypistats.org/packages/pysqlx)
[![Total downloads](https://img.shields.io/pepy/dt/pysqlx?label=total%20downloads)](https://pepy.tech/projects/pysqlx)
[![License](https://img.shields.io/pypi/l/pysqlx)](https://github.com/pysqlx/pysqlx/blob/master/LICENSE)

Work with SQL databases without writing SQL. Tables, conditions and queries are Python objects, and a client turns them into the SQL of the database it is connected to.

```python
from pysqlx import ClientFactory, Table

client = ClientFactory.get_sqlite3_client()  # a database in memory

orders = Table(table_name="orders")
customer = orders.append_char_string_column(column_name="customer", size=50)
total = orders.append_float_column(column_name="total")

client.create(orders).execute()
client.insert(orders).execute_many(param_tuple_list=[("Ada", 120.0), ("Grace", 80.5)])

rows = client.select(orders, condition=total > 100).execute()
# (('Ada', 120.0),)
```

- **Four databases, one interface**: SQLite, PostgreSQL, MySQL and Microsoft SQL Server
- **Conditions in Python**: `(customer == "Ada") & (total > 50)`, with `&`, `|` and `~`
- **Safe by construction**: values are always passed to the database as parameters, never written into the SQL
- **More than tables**: joins, aggregates, indexes, foreign keys and transactions
- **Inspectable**: `client.get_query_string(query)` shows the SQL of a query
- **Typed**: type hints throughout, checked with mypy in strict mode
- **Light**: no required dependency; the library of each database server is an extra

Full documentation: **https://pysqlx.readthedocs.io/**

## Installation

```shell
pip install pysqlx                 # SQLite
pip install "pysqlx[postgresql]"   # PostgreSQL, with psycopg
pip install "pysqlx[mysql]"        # MySQL and MariaDB, with pymysql
pip install "pysqlx[odbc]"         # Microsoft SQL Server, with pyodbc
```

`pysqlx` requires Python 3.11 or newer.

## Quickstart

### Describe a table

A table starts without columns. Each `append_*_column` method adds a column and returns it.

```python
from pysqlx import ClientFactory, Table

client = ClientFactory.get_sqlite3_client()

orders = Table(table_name="orders")
order_id = orders.append_integer_column(column_name="id", is_identity=True, is_primary_key=True)
customer = orders.append_char_string_column(column_name="customer", size=50)
placed = orders.append_datetime_column(column_name="placed")
total = orders.append_float_column(column_name="total")
```

### Create it and add rows

The methods of a client create queries, and nothing is sent to the database before `execute()`.

```python
from datetime import datetime

client.create(orders).execute()

client.insert(orders, columns=[customer, placed, total]).execute_many(
    param_tuple_list=[
        ("Ada", datetime(2026, 1, 5), 120.0),
        ("Grace", datetime(2026, 1, 7), 80.5),
        ("Ada", datetime(2026, 2, 1), 42.0),
    ]
)

print(client.get_length(orders).execute())  # 3
```

### Read rows

Comparing a column with a value gives a condition. Put each comparison in parentheses when combining them.

```python
query = client.select(
    orders,
    columns=[order_id, total],
    condition=(customer == "Ada") & (total > 50),
)

print(query.execute())  # ((1, 120.0),)
print(client.get_query_string(query))
# SELECT [id],
# [total] FROM [orders] WHERE ([customer] = 'Ada') AND ([total] > 50)
```

When the query is executed, `'Ada'` and `50` are passed to the database as parameters, so a value can contain any character and come from anywhere.

### Aggregate and join

```python
query = client.select(
    orders,
    columns=[customer, orders.count(), total.sum()],
    group_by=[customer],
    ascend_by=[customer],
)

print(query.execute())  # (('Ada', 2, 162.0), ('Grace', 1, 80.5))
```

Tables are joined with `joins=[Join(table=..., condition=...)]`.

### Change rows in a transaction

```python
with client.transaction():
    client.update(orders, columns=[total], condition=order_id == 3).execute(param_tuple=(45.0,))
    client.delete(orders, condition=customer == "Grace").execute()
```

The changes take effect together at the end of the block, or not at all if it raises an exception.

### Connect to a database server

```python
client = ClientFactory.get_psycopg_client(  # or get_pymysql_client, get_pyodbc_client
    server_address="db.example.com",
    user_name="reporting",
    user_pass="...",
    database_name="shop",
)
```

The same tables and queries work with every client. A client is closed with `close()` or by a `with` statement.

## Queries

| Method of the client | Does | `execute()` returns |
| --- | --- | --- |
| `create`, `drop` | creates or drops a table, an index, a schema or a database | `None` |
| `is_exists` | checks whether a structure exists | a boolean |
| `reflect` | reads the columns of an existing table | a table |
| `is_empty`, `get_length` | checks for rows, counts the rows | a boolean, an integer |
| `insert`, `update` | adds rows, changes rows | `None` |
| `select`, `select_distinct`, `union` | reads rows | a tuple of rows |
| `delete`, `truncate` | removes rows, removes all rows | `None` |

SQLite has neither schemas nor databases to create.

## Documentation

The documentation at https://pysqlx.readthedocs.io/ contains:

- a [quickstart](https://pysqlx.readthedocs.io/en/latest/getting-started/quickstart.html)
- a [security](https://pysqlx.readthedocs.io/en/latest/guide/security.html) page
- a user guide for [clients](https://pysqlx.readthedocs.io/en/latest/guide/clients.html), [tables and columns](https://pysqlx.readthedocs.io/en/latest/guide/structures.html), [conditions](https://pysqlx.readthedocs.io/en/latest/guide/conditions.html), [queries](https://pysqlx.readthedocs.io/en/latest/guide/queries.html), [transactions](https://pysqlx.readthedocs.io/en/latest/guide/transactions.html) and [errors](https://pysqlx.readthedocs.io/en/latest/guide/errors.html)
- a [changelog](https://pysqlx.readthedocs.io/en/latest/project/changelog.html)
- an [API reference](https://pysqlx.readthedocs.io/en/latest/reference/index.html) for every class and method

## Development

The project is managed with [uv](https://docs.astral.sh/uv/) and `make`.

```shell
git clone https://github.com/pysqlx/pysqlx.git
cd pysqlx
make install  # create the environment
make check    # lint, type check, test and build the docs
```

Run `make` to list all targets. Bug reports and pull requests are welcome on [GitHub](https://github.com/pysqlx/pysqlx/issues).

## License

`pysqlx` is released under the [MIT license](https://github.com/pysqlx/pysqlx/blob/master/LICENSE).

It is maintained by [Bassem Girgis](https://girgis.me).
