import pytest

from pysqlx.clients import ClientFactory
from pysqlx.exceptions import InvalidArgumentError
from pysqlx.structures import (
    BinaryColumn,
    BooleanColumn,
    Clause,
    DateColumn,
    DecimalColumn,
    ForeignKey,
    Index,
    Join,
    Table,
)


def test_table_new_columns() -> None:
    table = Table(table_name="t")

    assert isinstance(table.append_boolean_column(column_name="a"), BooleanColumn)
    assert isinstance(table.append_date_column(column_name="b"), DateColumn)
    assert isinstance(table.append_binary_column(column_name="c"), BinaryColumn)

    column = table.append_decimal_column(column_name="d", precision=10, scale=3)

    assert isinstance(column, DecimalColumn)
    assert (column.precision, column.scale) == (10, 3)
    assert [col.column_name for col in table.columns] == ["a", "b", "c", "d"]

    for precision, scale in ((0, 0), (10, -1), (2, 3)):
        with pytest.raises(InvalidArgumentError):
            table.append_decimal_column(column_name="e", precision=precision, scale=scale)


def test_table_invalid_columns() -> None:
    table = Table(table_name="t")
    other = Table(table_name="other")
    column = other.append_integer_column(column_name="a")

    with pytest.raises(InvalidArgumentError):
        table.append_column(column)

    with pytest.raises(InvalidArgumentError):
        table.append_column("nope")  # type: ignore[arg-type]

    with pytest.raises(InvalidArgumentError):
        table.append_integer_column(column_name="a", n_bytes=3)

    with pytest.raises(InvalidArgumentError):
        table.append_char_string_column(column_name="a", size="1")  # type: ignore[arg-type]

    with pytest.raises(InvalidArgumentError):
        table.append_integer_column(column_name="a", default_value=0, is_primary_key=True)


def test_table_column_identity() -> None:
    table = Table(table_name="t")
    first = table.append_integer_column(column_name="a")
    second = table.append_integer_column(column_name="b")

    assert first.get_index() == 0
    assert second.get_index() == 1
    assert len({first, second, first}) == 2

    table.clear_columns()

    with pytest.raises(InvalidArgumentError):
        first.get_index()


def test_table_foreign_key() -> None:
    parent = Table(table_name="parent")
    parent_id = parent.append_integer_column(column_name="id", is_primary_key=True)
    child = Table(table_name="child")
    child_parent = child.append_integer_column(column_name="parent_id")

    foreign_key = child.append_foreign_key(columns=[child_parent], reference_columns=[parent_id])

    assert isinstance(foreign_key, ForeignKey)
    assert child.foreign_keys == [foreign_key]
    assert foreign_key.columns[0] is child_parent
    assert foreign_key.reference_columns[0] is parent_id

    with pytest.raises(InvalidArgumentError):
        child.append_foreign_key(columns=[parent_id], reference_columns=[parent_id])

    with pytest.raises(InvalidArgumentError):
        child.append_foreign_key(columns=[], reference_columns=[])

    with pytest.raises(InvalidArgumentError):
        child.append_foreign_key(columns=[child_parent], reference_columns=[])

    with pytest.raises(InvalidArgumentError):
        ForeignKey(
            columns=[child_parent, child_parent], reference_columns=[parent_id, child_parent]
        )

    assert child.clear_columns().foreign_keys == []


def test_table_index_and_join() -> None:
    table = Table(table_name="t")
    column = table.append_integer_column(column_name="a")
    other = Table(table_name="other")
    other_column = other.append_integer_column(column_name="a")

    index = Index(index_name="i", table=table, columns=[column])

    assert index.structure_name == "index"
    assert (index.index_name, index.table, index.is_unique) == ("i", table, False)

    with pytest.raises(InvalidArgumentError):
        Index(index_name="i", table=table, columns=[])

    with pytest.raises(InvalidArgumentError):
        Index(index_name="i", table=table, columns=[other_column])

    join = Join(table=other, condition=column == other_column)

    assert (join.table, join.kind) == (other, "inner")

    with pytest.raises(InvalidArgumentError):
        Join(table=other, condition=column == other_column, kind="cross")


def test_table_aggregates() -> None:
    table = Table(table_name="t")
    column = table.append_integer_column(column_name="a")

    assert table.count().column is None
    assert table.count().function_name == "COUNT"

    for aggregate, function_name in (
        (column.count(), "COUNT"),
        (column.sum(), "SUM"),
        (column.avg(), "AVG"),
        (column.min(), "MIN"),
        (column.max(), "MAX"),
    ):
        assert aggregate.column is column
        assert aggregate.function_name == function_name


def test_table_query_validation() -> None:
    client = ClientFactory.get_sqlite_client()
    table = Table(table_name="t")
    first = table.append_integer_column(column_name="a")
    second = table.append_integer_column(column_name="b")
    other = Table(table_name="other")
    foreign = other.append_integer_column(column_name="a")

    for arguments in (
        {"columns": [foreign]},
        {"columns": [foreign.sum()]},
        {"ascend_by": [foreign]},
        {"descend_by": [foreign]},
        {"group_by": [foreign]},
        {"ascend_by": [first], "descend_by": [first]},
        {"limit": -1},
        {"limit": "1"},
        {"offset": -1},
        {"offset": True},
        {"joins": [other]},
    ):
        with pytest.raises(InvalidArgumentError):
            client.select(table, **arguments)

    # A table can be sorted by a column which is not read, in both directions.
    query = client.select(table, columns=[first], ascend_by=[second], descend_by=[first])

    assert list(query.columns) == [first]

    joined = client.select(table, joins=[Join(table=other, condition=first == foreign)])

    assert list(joined.columns) == [first, second, foreign]

    with pytest.raises(InvalidArgumentError):
        client.insert(table, columns=[foreign])

    with pytest.raises(InvalidArgumentError):
        client.insert(table, columns=[])

    with pytest.raises(InvalidArgumentError):
        client.update(table, columns=[foreign], condition=first == 1)

    with pytest.raises(InvalidArgumentError):
        client.select_distinct(table, columns=[first], ascend_by=[second])

    with pytest.raises(InvalidArgumentError):
        client.select_distinct(table, columns=[])

    with pytest.raises(InvalidArgumentError):
        client.union(table_list=(table,), query_list=(client.create(table),))  # type: ignore[arg-type]

    with pytest.raises(InvalidArgumentError):
        client.union(
            table_list=(table, other),
            query_list=(client.select(table), client.select(other)),
            columns_list=((first,), (foreign,)),
            ascend_by=[foreign],
        )

    with pytest.raises(InvalidArgumentError):
        (first == 1) & 5  # type: ignore[operator]


def test_table_alias() -> None:
    table = Table(table_name="t")
    first = table.append_integer_column(column_name="a", is_primary_key=True)
    table.append_char_string_column(column_name="b", size=7)

    assert table.alias_name is None

    alias = table.alias("other")

    assert alias is not table
    assert (alias.table_name, alias.alias_name) == ("t", "other")
    assert [col.column_name for col in alias.columns] == ["a", "b"]
    assert [type(col) for col in alias.columns] == [type(col) for col in table.columns]
    assert alias.columns[0] is not first
    assert alias.columns[0].is_primary_key is True
    assert alias.columns[0].table.alias_name == "other"
    assert first.table.alias_name is None
    assert alias.columns[1].get_index() == 1

    with pytest.raises(InvalidArgumentError):
        table.alias("")

    client = ClientFactory.get_sqlite_client()
    client.create(table).execute()
    client.insert(table).execute_many(parameters_list=[(1, "x"), (2, "y")])

    # A table and its alias are two tables to a query.
    assert client.select(
        table,
        columns=[first, alias.columns[0]],
        joins=[Join(table=alias, condition=first < alias.columns[0])],
    ).execute() == ((1, 2),)

    with pytest.raises(InvalidArgumentError):
        client.select(table, columns=[alias.columns[0]])


def test_table_aggregate_conditions() -> None:
    client = ClientFactory.get_sqlite_client()
    table = Table(table_name="t")
    key = table.append_integer_column(column_name="k")
    value = table.append_integer_column(column_name="v")

    client.create(table).execute()
    client.insert(table).execute_many(parameters_list=[(1, 1), (1, 2), (2, 5), (3, 1)])

    def keys(having: Clause) -> list[int]:
        query = client.select(table, columns=[key], group_by=[key], having=having, ascend_by=[key])
        return [row[0] for row in query.execute()]

    assert keys(value.sum() == 3) == [1]
    assert keys(value.sum() != 3) == [2, 3]
    assert keys(value.sum() > 3) == [2]
    assert keys(value.sum() >= 3) == [1, 2]
    assert keys(value.sum() < 3) == [3]
    assert keys(value.sum() <= 3) == [1, 3]
    assert keys(value.max().is_between(2, 5)) == [1, 2]
    assert keys(~(table.count() == 1)) == [1]
    assert len({value.sum(), value.sum()}) == 2
