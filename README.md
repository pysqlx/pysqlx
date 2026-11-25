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

client = ClientFactory.get_sqlite3_client(
    directory_path=None,
    dialect_name="sqlite",
    driver_name="memory",
    database_name="shop",
)

orders = Table(table_name="orders")
customer = orders.append_char_string_column(column_name="customer", size=50)
total = orders.append_float_column(column_name="total")

client.create(orders).execute()
client.insert(orders).execute_many(param_tuple_list=[("Ada", 120.0), ("Grace", 80.5)])

rows = client.select(orders, condition=total > 100).execute()
# (('Ada', 120.0),)
```

- **Two databases, one interface**: SQLite through `sqlite3`, and Microsoft SQL Server through `pyodbc`
- **Conditions in Python**: `(customer == "Ada") & (total > 50)`, with `&`, `|` and `~`
- **Inspectable**: `client.get_query_string(query)` shows the SQL before anything is sent
- **Typed**: type hints throughout, checked with mypy in strict mode
- **Light**: depends only on `pyodbc`

Full documentation: **https://pysqlx.readthedocs.io/**

## Installation

```shell
pip install pysqlx
```

`pysqlx` requires Python 3.12 or newer and `pyodbc` 5.2 or newer.

On macOS, `pyodbc` needs unixODBC, also when only SQLite is used: `brew install unixodbc`.

## Quickstart

### Describe a table

A table starts without columns. Each `append_*_column` method adds a column and returns it.

```python
from pysqlx import Table

orders = Table(table_name="orders")
order_id = orders.append_integer_column(column_name="id", is_primary_key=True)
customer = orders.append_char_string_column(column_name="customer", size=50)
placed = orders.append_datetime_column(column_name="placed")
total = orders.append_float_column(column_name="total")
```

### Create it and add rows

The methods of a client create queries, and nothing is sent to the database before `execute()`.

```python
from datetime import datetime

client.create(orders).execute()

client.insert(orders).execute_many(
    param_tuple_list=[
        (1, "Ada", datetime(2026, 1, 5), 120.0),
        (2, "Grace", datetime(2026, 1, 7), 80.5),
        (3, "Ada", datetime(2026, 2, 1), 42.0),
    ]
)

print(client.get_length(orders).execute())  # 3
```

### Read rows

Comparing a column with a value gives a condition. Put each comparison in parentheses when combining them.

```python
query = client.select(
    orders,
    columns=[customer, total],
    condition=(customer == "Ada") & (total > 50),
)

print(query.execute())  # (('Ada', 120.0),)
print(client.get_query_string(query))
# SELECT [customer],
# [total] FROM orders WHERE ([customer] = 'Ada') AND ([total] > 50)
```

The values of a condition are written into the SQL as they are, without escaping. Do not build conditions from untrusted input.

### Change and remove rows

```python
client.update(orders, columns=[total], condition=order_id == 3).execute(param_tuple=(45.0,))
client.delete(orders, condition=customer == "Grace").execute()
```

### Connect to SQL Server

```python
from pysqlx import ClientFactory

client = ClientFactory.get_pyodbc_client(
    server_address="db.example.com",
    user_name="reporting",
    user_pass="...",
    dialect_name="mssql",
    database_name="shop",
)
```

The same tables and queries work with both clients.

## Queries

| Method of the client | Does | `execute()` returns |
| --- | --- | --- |
| `create`, `drop` | creates or drops a table, a schema or a database | `None` |
| `is_exists` | checks whether a structure exists | a boolean |
| `is_empty`, `get_length` | checks for rows, counts the rows | a boolean, an integer |
| `insert`, `update` | adds rows, changes rows | `None` |
| `select`, `select_distinct`, `union` | reads rows | a tuple of rows |
| `delete`, `truncate` | removes rows, removes all rows | `None` |

Schemas and databases only exist on a SQL Server.

## Documentation

The documentation at https://pysqlx.readthedocs.io/ contains:

- a [quickstart](https://pysqlx.readthedocs.io/en/latest/getting-started/quickstart.html)
- a user guide for [clients](https://pysqlx.readthedocs.io/en/latest/guide/clients.html), [tables and columns](https://pysqlx.readthedocs.io/en/latest/guide/structures.html), [conditions](https://pysqlx.readthedocs.io/en/latest/guide/conditions.html) and [queries](https://pysqlx.readthedocs.io/en/latest/guide/queries.html)
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
