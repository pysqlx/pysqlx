"""Scenario which every client must pass, whatever its database."""

from datetime import date, datetime
from decimal import Decimal

import pytest

from pysqlx.clients import Client
from pysqlx.exceptions import InvalidArgumentError, TransactionError
from pysqlx.structures import CharStringColumn, DecimalColumn, Index, Join, Table

ROWS = (
    (
        1,
        "O'Brien",
        date(2024, 1, 5),
        True,
        Decimal("10.50"),
        b"\x00\x01\xff",
        "it's 100% \\ done",
        datetime(2024, 1, 5, 8, 30, 0),
        1.5,
    ),
    (
        2,
        "Grace",
        date(2024, 2, 1),
        False,
        Decimal("0.25"),
        b"\x10",
        None,
        datetime(2024, 2, 1, 0, 0, 0),
        2.5,
    ),
    (3, "Ada", None, True, Decimal("99.99"), b"", "", None, None),
)


def run_scenario(client: Client) -> None:
    customers = Table(table_name="pysqlx_customers")
    customer_id = customers.append_integer_column(column_name="id", is_primary_key=True)
    name = customers.append_char_string_column(
        column_name="name", size=50, is_unicode=True, is_required=True
    )
    joined = customers.append_date_column(column_name="joined")
    is_active = customers.append_boolean_column(column_name="is_active")
    balance = customers.append_decimal_column(column_name="balance", precision=10, scale=2)
    customers.append_binary_column(column_name="photo")
    notes = customers.append_text_column(column_name="notes")
    created = customers.append_datetime_column(column_name="created")
    score = customers.append_float_column(column_name="score")

    # "order" and "select" are reserved words, which the quoting must handle.
    orders = Table(table_name="pysqlx_orders")
    order_id = orders.append_integer_column(
        column_name="order", is_identity=True, is_primary_key=True
    )
    order_customer = orders.append_integer_column(column_name="select", is_required=True)
    total = orders.append_float_column(column_name="total")
    orders.append_foreign_key(columns=[order_customer], reference_columns=[customer_id])

    for table in (orders, customers):
        if client.exists(table).execute():
            client.drop(table).execute()

    assert client.exists(customers).execute() is False

    client.create(customers).execute()
    client.create(orders).execute()

    assert client.exists(customers).execute() is True
    assert client.is_empty(customers).execute() is True

    # Reading the tables back from the database.
    reflected = client.reflect("pysqlx_customers").execute()

    assert [(type(col).__name__, col.column_name) for col in reflected.columns] == [
        (type(col).__name__, col.column_name) for col in customers.columns
    ]
    assert [col.is_primary_key for col in reflected.columns] == [True] + [False] * 8
    assert [col.is_required for col in reflected.columns] == [True, True] + [False] * 7
    assert [col.is_identity for col in reflected.columns] == [False] * 9

    reflected_name = reflected.columns[1]
    reflected_balance = reflected.columns[4]

    assert isinstance(reflected_name, CharStringColumn)
    assert (reflected_name.size, reflected_name.is_fixed) == (50, False)
    assert isinstance(reflected_balance, DecimalColumn)
    assert (reflected_balance.precision, reflected_balance.scale) == (10, 2)

    reflected_orders = client.reflect("pysqlx_orders").execute()

    assert [col.column_name for col in reflected_orders.columns] == ["order", "select", "total"]
    assert [col.is_identity for col in reflected_orders.columns] == [True, False, False]
    assert client.select(reflected_orders).execute() == ()

    assert reflected.foreign_keys == []
    assert len(reflected_orders.foreign_keys) == 1

    foreign_key = reflected_orders.foreign_keys[0]

    assert [col.column_name for col in foreign_key.columns] == ["select"]
    assert [col.column_name for col in foreign_key.reference_columns] == ["id"]
    assert foreign_key.reference_table.table_name == "pysqlx_customers"
    assert foreign_key.reference_columns[0].table.table_name == "pysqlx_customers"

    with pytest.raises(InvalidArgumentError):
        client.reflect("pysqlx_missing").execute()

    # Rows, with every type of column.
    client.insert(customers).execute(parameters=ROWS[0])
    client.insert(customers).execute_many(parameters_list=ROWS[1:])

    assert client.is_empty(customers).execute() is False
    assert client.count_rows(customers).execute() == 3
    assert client.select(customers, ascend_by=[customer_id]).execute() == ROWS
    assert client.select(reflected, ascend_by=[reflected.columns[0]]).execute() == ROWS

    def ids(**arguments: object) -> list[int]:
        query = client.select(customers, columns=[customer_id], **arguments)  # type: ignore[arg-type]
        return [row[0] for row in query.execute()]

    def sorted_ids(condition: object) -> list[int]:
        return ids(condition=condition, ascend_by=[customer_id])

    # Conditions, whose values are parameters.
    assert sorted_ids(name == "O'Brien") == [1]
    assert sorted_ids(name != "O'Brien") == [2, 3]
    assert sorted_ids(notes == "it's 100% \\ done") == [1]
    assert sorted_ids(name == "x' OR '1'='1") == []
    assert sorted_ids(name.is_like("%ra%")) == [2]
    assert sorted_ids(~name.is_like("%ra%")) == [1, 3]
    assert sorted_ids(customer_id.is_in_list((1, 3))) == [1, 3]
    assert sorted_ids(~customer_id.is_in_list((1, 3))) == [2]
    assert sorted_ids(customer_id.is_between(2, 3)) == [2, 3]
    assert sorted_ids(balance > Decimal("5")) == [1, 3]
    assert sorted_ids(joined.is_null()) == [3]
    assert sorted_ids(joined.is_not_null()) == [1, 2]
    assert sorted_ids(joined < date(2024, 1, 31)) == [1]
    assert sorted_ids(created >= datetime(2024, 2, 1)) == [2]
    assert sorted_ids(is_active == True) == [1, 3]  # noqa: E712
    assert sorted_ids((customer_id > 1) & (score <= 2.5)) == [2]
    assert sorted_ids((customer_id == 1) | (customer_id == 3)) == [1, 3]
    assert sorted_ids(~((customer_id == 1) | (customer_id == 3))) == [2]

    # Sorting in both directions, limits and offsets.
    assert ids(ascend_by=[is_active], descend_by=[customer_id]) == [2, 3, 1]
    assert ids(descend_by=[customer_id]) == [3, 2, 1]
    assert ids(limit=2, ascend_by=[customer_id]) == [1, 2]
    assert ids(limit=1, offset=1, ascend_by=[customer_id]) == [2]
    assert ids(offset=2, ascend_by=[customer_id]) == [3]
    assert ids(limit=0, ascend_by=[customer_id]) == []

    # Identity column and foreign key.
    client.insert(orders, columns=[order_customer, total]).execute_many(
        parameters_list=[(1, 10.0), (1, 20.0), (2, 5.0)]
    )

    assert client.select(orders, ascend_by=[order_id]).execute() == (
        (1, 1, 10.0),
        (2, 1, 20.0),
        (3, 2, 5.0),
    )

    with pytest.raises(Exception):  # noqa: B017
        client.insert(orders, columns=[order_customer, total]).execute(parameters=(99, 1.0))

    assert client.count_rows(orders).execute() == 3

    # Aggregates.
    assert client.select(
        orders,
        columns=[order_customer, total.sum(), orders.count(), total.min(), total.max()],
        group_by=[order_customer],
        ascend_by=[order_customer],
    ).execute() == ((1, 30.0, 2, 10.0, 20.0), (2, 5.0, 1, 5.0, 5.0))

    assert client.select(orders, columns=[total.avg()]).execute()[0][0] == pytest.approx(35 / 3)
    assert client.select(customers, columns=[joined.count()]).execute() == ((2,),)
    assert client.select(customers, columns=[created.min(), joined.max()]).execute() == (
        (datetime(2024, 1, 5, 8, 30, 0), date(2024, 2, 1)),
    )

    # Groups which satisfy a condition on an aggregate.
    assert client.select(
        orders,
        columns=[order_customer, total.sum()],
        group_by=[order_customer],
        having=total.sum() > 10,
        ascend_by=[order_customer],
    ).execute() == ((1, 30.0),)

    assert client.select(
        orders,
        columns=[order_customer, orders.count()],
        condition=total > 6,
        group_by=[order_customer],
        having=(orders.count() >= 1) & total.max().is_between(15, 25),
    ).execute() == ((1, 2),)

    # A table joined to itself, through an alias.
    other = orders.alias("other order")
    other_id, other_customer, other_total = other.columns

    assert client.select(
        orders,
        columns=[order_id, other_id, other_total],
        joins=[
            Join(
                table=other,
                condition=(order_customer == other_customer) & (total < other_total),
            )
        ],
        ascend_by=[order_id],
    ).execute() == ((1, 2, 20.0),)

    # Joins.
    assert client.select(
        orders,
        columns=[name, total],
        joins=[Join(table=customers, condition=order_customer == customer_id)],
        condition=total > 1,
        ascend_by=[total],
    ).execute() == (("Grace", 5.0), ("O'Brien", 10.0), ("O'Brien", 20.0))

    assert client.select(
        customers,
        columns=[name, total.count()],
        joins=[Join(table=orders, condition=customer_id == order_customer, kind="left")],
        group_by=[name],
        ascend_by=[name],
    ).execute() == (("Ada", 0), ("Grace", 1), ("O'Brien", 2))

    # Distinct values and unions.
    assert client.select_distinct(
        orders, columns=[order_customer], descend_by=[order_customer]
    ).execute() == ((2,), (1,))

    assert client.union(
        table_list=(customers, orders),
        query_list=(
            client.select(customers, columns=[customer_id], condition=customer_id > 1),
            client.select(orders, columns=[order_customer], condition=total < 15),
        ),
        columns_list=((customer_id,), (order_customer,)),
        ascend_by=[customer_id],
    ).execute() == ((1,), (2,), (3,))

    # Indexes.
    index = Index(index_name="pysqlx_customers_name", table=customers, columns=[name])
    unique_index = Index(
        index_name="pysqlx_customers_key",
        table=customers,
        columns=[name, customer_id],
        is_unique=True,
    )

    for one_index in (index, unique_index):
        assert client.exists(one_index).execute() is False
        client.create(one_index).execute()
        assert client.exists(one_index).execute() is True
        client.drop(one_index).execute()
        assert client.exists(one_index).execute() is False

    # Updates, whose own parameters come before those of the condition.
    client.update(customers, columns=[score, notes], condition=name == "Ada").execute(
        parameters=(9.5, "new")
    )

    assert client.select(
        customers, columns=[score, notes], condition=customer_id == 3
    ).execute() == ((9.5, "new"),)

    client.update(customers, columns=[score], condition=customer_id < 3).execute_many(
        parameters_list=[(7.0,)]
    )

    assert sorted_ids(score == 7.0) == [1, 2]

    # Transactions.
    assert bool(client.is_in_transaction) is False

    with pytest.raises(TransactionError):
        client.commit()

    with pytest.raises(TransactionError):
        client.rollback()

    with pytest.raises(ZeroDivisionError):
        with client.transaction():
            client.delete(customers, condition=customer_id == 3).execute()
            assert bool(client.is_in_transaction) is True
            assert client.count_rows(customers).execute() == 2

            with pytest.raises(TransactionError):
                client.begin()

            raise ZeroDivisionError

    assert bool(client.is_in_transaction) is False
    assert client.count_rows(customers).execute() == 3

    with client.transaction():
        client.delete(customers, condition=customer_id == 3).execute()

    assert client.count_rows(customers).execute() == 2

    client.begin()
    client.delete(orders, condition=total > 15).execute()
    client.rollback()

    assert client.count_rows(orders).execute() == 3

    client.begin()
    client.delete(orders, condition=total > 15).execute()
    client.commit()

    assert client.count_rows(orders).execute() == 2

    # Emptying and dropping.
    client.truncate(orders).execute()

    assert client.is_empty(orders).execute() is True

    client.drop(orders).execute()
    client.drop(customers).execute()

    assert client.exists(orders).execute() is False
    assert client.exists(customers).execute() is False
