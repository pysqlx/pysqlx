"""Queries whose SQL is compared for every dialect."""

from collections.abc import Callable
from datetime import date, datetime
from pathlib import Path
from typing import Any

from pysqlx.clients import ClientFactory
from pysqlx.dialects import Dialect
from pysqlx.exceptions import PysqlxError
from pysqlx.queries import Query
from pysqlx.structures import Database, Index, Join, Schema, Table


def build_cases() -> dict[str, Callable[[], Query]]:
    """Create the queries, by name. They are built on demand, as some are invalid."""
    client = ClientFactory.get_sqlite_client()

    shop = Database(database_name="shop")
    sales = Schema(schema_name="sales", owner_name="me")

    customers = Table(table_name="customers", database=shop, schema=sales)
    customer_id = customers.append_integer_column(
        column_name="id", n_bytes=8, is_identity=True, is_primary_key=True
    )
    name = customers.append_char_string_column(
        column_name="full name", size=50, is_unicode=True, is_required=True
    )
    code = customers.append_char_string_column(column_name="code", size=3, is_fixed=True)
    customers.append_text_column(column_name="notes", is_unicode=True)
    customers.append_boolean_column(column_name="is_active", default_value=1)
    customers.append_date_column(column_name="joined")
    created = customers.append_datetime_column(column_name="created")
    customers.append_decimal_column(column_name="balance", precision=10, scale=2)
    customers.append_binary_column(column_name="photo")
    customers.append_float_column(column_name="score", is_double=False)
    customers.append_integer_column(column_name="level", n_bytes=1, default_value=0)

    orders = Table(table_name="orders")
    order_id = orders.append_integer_column(column_name="id", is_primary_key=True)
    line = orders.append_integer_column(column_name="line", is_primary_key=True)
    order_customer = orders.append_integer_column(column_name="customer_id", n_bytes=8)
    total = orders.append_float_column(column_name="total")
    orders.append_foreign_key(columns=[order_customer], reference_columns=[customer_id])

    index = Index(index_name="by name", table=customers, columns=[name, code], is_unique=True)
    other = orders.alias("o 2")

    condition = ((name == "O'Brien") & (created > datetime(2024, 1, 2, 3, 4, 5))) | ~(
        code.is_in_list(("a", "b")) | customer_id.is_between(1, 9)
    )

    return {
        "create_table": lambda: client.create(customers),
        "create_table_keys": lambda: client.create(orders),
        "create_database": lambda: client.create(shop),
        "create_schema": lambda: client.create(sales),
        "create_index": lambda: client.create(index),
        "drop_table": lambda: client.drop(customers),
        "drop_database": lambda: client.drop(shop),
        "drop_schema": lambda: client.drop(sales),
        "drop_index": lambda: client.drop(index),
        "exists_table": lambda: client.exists(customers),
        "exists_plain_table": lambda: client.exists(orders),
        "exists_database": lambda: client.exists(shop),
        "exists_schema": lambda: client.exists(sales),
        "exists_index": lambda: client.exists(index),
        "empty": lambda: client.is_empty(orders),
        "length": lambda: client.count_rows(orders),
        "truncate": lambda: client.truncate(orders),
        "insert": lambda: client.insert(orders),
        "insert_columns": lambda: client.insert(customers, columns=[name, code]),
        "update": lambda: client.update(orders, columns=[total], condition=order_id == 3),
        "delete": lambda: client.delete(orders, condition=condition),
        "select": lambda: client.select(orders),
        "select_condition": lambda: client.select(
            customers, columns=[customer_id, name], condition=condition
        ),
        "select_values": lambda: client.select(
            customers,
            columns=[customer_id],
            condition=(
                name.is_like("a%")
                & code.is_null()
                & (created != date(2024, 1, 2))
                & (code <= name)
                & (customer_id >= 1.5)
                & (name < True)
                & (code == b"\x01\xff")
                & (name == None)  # noqa: E711
            ),
        ),
        "select_top": lambda: client.select(orders, columns=[total], limit=5),
        "select_sorted": lambda: client.select(
            orders, columns=[total], ascend_by=[order_id], descend_by=[line, total]
        ),
        "select_offset": lambda: client.select(
            orders, columns=[total], limit=5, offset=10, ascend_by=[order_id]
        ),
        "select_offset_only": lambda: client.select(
            orders, columns=[total], offset=10, descend_by=[order_id]
        ),
        "select_offset_unsorted": lambda: client.select(orders, columns=[total], offset=10),
        "select_aggregates": lambda: client.select(
            orders,
            columns=[
                order_customer,
                orders.count(),
                total.count(),
                total.sum(),
                total.avg(),
                total.min(),
                total.max(),
            ],
            group_by=[order_customer],
            ascend_by=[order_customer],
        ),
        "select_join": lambda: client.select(
            orders,
            columns=[name, total.sum()],
            joins=[
                Join(table=customers, condition=order_customer == customer_id, kind="left"),
            ],
            condition=total > 10,
            group_by=[name],
            descend_by=[name],
            limit=3,
        ),
        "select_having": lambda: client.select(
            orders,
            columns=[order_customer, total.sum()],
            condition=total > 1,
            group_by=[order_customer],
            having=(total.sum() >= 10) & (orders.count() != 2) & total.avg().is_between(1, 5),
            ascend_by=[order_customer],
        ),
        "select_alias": lambda: client.select(
            orders,
            columns=[order_id, other.columns[0]],
            joins=[
                Join(
                    table=other,
                    condition=(order_customer == other.columns[2]) & (total < other.columns[3]),
                    kind="inner",
                ),
            ],
        ),
        "select_only_alias": lambda: client.select(other, columns=[other.columns[0]], limit=1),
        "reflect": lambda: client.reflect("customers", database=shop, schema=sales),
        "reflect_plain": lambda: client.reflect("orders"),
        "select_distinct": lambda: client.select_distinct(
            customers,
            columns=[name, code],
            ascend_by=[name],
            descend_by=[code],
            condition=code != "x",
        ),
        "union": lambda: client.union(
            table_list=(customers, orders),
            query_list=(
                client.select(customers, columns=[customer_id], condition=name == "a"),
                client.select(orders, columns=[order_customer], condition=total > 1),
            ),
            columns_list=((customer_id,), (order_customer,)),
            is_all=True,
            descend_by=[customer_id],
        ),
    }


def render(dialect: Dialect) -> str:
    """Write the SQL of every case, as text and with its parameters."""
    lines = []

    for case_name, build in build_cases().items():
        for is_parameterized in (False, True):
            parameters: list[Any] | None = [] if is_parameterized else None

            try:
                sql = dialect.get_query_string(build(), parameters)
            except PysqlxError as error:
                sql = f"{type(error).__name__}: {error}"

            if is_parameterized and not parameters:
                continue

            lines.append(f"-- {case_name}" + (f" {parameters!r}" if parameters else ""))
            lines.append(sql)

    for table in (
        Table(table_name="orders"),
        Table(
            table_name="customers",
            database=Database(database_name="shop"),
            schema=Schema(schema_name="sales"),
        ),
    ):
        lines.append(f"-- foreign keys of {table.table_name}")
        lines.append(dialect.get_foreign_keys_string(table))

    return "\n".join(lines) + "\n"


def reflect(dialect: Dialect, rows: list[tuple[Any, ...]]) -> list[tuple[Any, ...]]:
    """Describe the columns which a dialect creates from the rows of a reflect query."""
    client = ClientFactory.get_sqlite_client()
    table = dialect.get_reflected_table(client.reflect("t"), rows)

    described = []

    for column in table.columns:
        details = {
            name: getattr(column, name)
            for name in ("size", "is_fixed", "is_unicode", "is_double", "n_bytes", "precision")
            if hasattr(column, name)
        }
        flags = "".join(
            letter
            for letter, value in (
                ("K", column.is_primary_key),
                ("I", column.is_identity),
                ("R", column.is_required),
            )
            if value
        )
        described.append(
            (type(column).__name__, column.column_name, details, flags, column.default_value)
        )

    return described


def read_std(dialect: Dialect) -> str:
    """Read the expected SQL of a dialect."""
    return (Path(__file__).parent / "std" / f"{dialect.dialect_name}.sql").read_text()
