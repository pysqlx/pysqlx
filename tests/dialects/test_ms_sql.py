from datetime import datetime
from typing import Any

import pytest

from pysqlx.clients import ClientFactory
from pysqlx.dialects import MsSql as Dialect
from pysqlx.exceptions import InvalidArgumentError, UnsupportedOperationError
from pysqlx.structures import Database, Table

from .cases import read_std, reflect, render


def row(
    name: str,
    data_type: str,
    size: int | None = None,
    precision: int | None = None,
    scale: int | None = None,
    nullable: str = "YES",
    default: Any = None,
    keys: int = 0,
    identity: int = 0,
    column_type: str | None = None,
) -> tuple[Any, ...]:
    return (name, data_type, size, precision, scale, nullable, default, keys, identity, column_type)


def test_mssql_queries() -> None:
    dialect = Dialect()

    assert dialect.dialect_name == "mssql"
    assert render(dialect) == read_std(dialect)


def test_mssql_quoting() -> None:
    dialect = Dialect()

    assert dialect.placeholder == "?"
    assert dialect.quote_identifier("a]b") == "[a]]b]"
    assert dialect.get_literal_string("it's") == "'it''s'"
    assert dialect.get_literal_string(datetime(2024, 1, 2, 3, 4, 5, 678000)) == (
        "'2024-01-02T03:04:05.678'"
    )


def test_mssql_reflection() -> None:
    dialect = Dialect()

    assert reflect(
        dialect,
        [
            row("id", "bigint", precision=19, nullable="NO", keys=1, identity=1, default="x"),
            row("a", "nvarchar", size=50, nullable="NO"),
            row("b", "char", size=3, default="('x')"),
            row("c", "nvarchar", size=-1),
            row("d", "text"),
            row("e", "ntext"),
            row("f", "tinyint"),
            row("g", "smallint"),
            row("h", "INT"),
            row("i", "float", precision=53),
            row("j", "float", precision=24),
            row("k", "real", precision=24),
            row("l", "datetime"),
            row("m", "datetime2"),
            row("n", "date"),
            row("o", "bit"),
            row("p", "decimal", precision=10, scale=2),
            row("q", "numeric", precision=5, scale=0),
            row("r", "varbinary", size=-1),
            row("s", "image"),
        ],
    ) == [
        ("IntegerColumn", "id", {"n_bytes": 8}, "KIR", None),
        ("CharStringColumn", "a", {"size": 50, "is_fixed": False, "is_unicode": True}, "R", None),
        ("CharStringColumn", "b", {"size": 3, "is_fixed": True, "is_unicode": False}, "", "('x')"),
        ("TextColumn", "c", {"is_unicode": True}, "", None),
        ("TextColumn", "d", {"is_unicode": False}, "", None),
        ("TextColumn", "e", {"is_unicode": True}, "", None),
        ("IntegerColumn", "f", {"n_bytes": 1}, "", None),
        ("IntegerColumn", "g", {"n_bytes": 2}, "", None),
        ("IntegerColumn", "h", {"n_bytes": 4}, "", None),
        ("FloatColumn", "i", {"is_double": True}, "", None),
        ("FloatColumn", "j", {"is_double": False}, "", None),
        ("FloatColumn", "k", {"is_double": False}, "", None),
        ("DatetimeColumn", "l", {}, "", None),
        ("DatetimeColumn", "m", {}, "", None),
        ("DateColumn", "n", {}, "", None),
        ("BooleanColumn", "o", {}, "", None),
        ("DecimalColumn", "p", {"precision": 10}, "", None),
        ("DecimalColumn", "q", {"precision": 5}, "", None),
        ("BinaryColumn", "r", {}, "", None),
        ("BinaryColumn", "s", {}, "", None),
    ]

    with pytest.raises(UnsupportedOperationError):
        reflect(dialect, [row("a", "geography")])

    with pytest.raises(InvalidArgumentError):
        reflect(dialect, [])


def test_mssql_offset_needs_sorting() -> None:
    client = ClientFactory.get_sqlite_client()
    table = Table(table_name="t")
    column = table.append_integer_column(column_name="a")

    with pytest.raises(InvalidArgumentError):
        Dialect().get_query_string(client.select(table, offset=1))

    assert Dialect().get_query_string(client.select(table, offset=1, ascend_by=[column])) == (
        "SELECT [a] FROM [t] ORDER BY [a] ASC OFFSET 1 ROWS"
    )


def test_mssql_reference_table() -> None:
    dialect = Dialect()
    table = Table(table_name="t", database=Database(database_name="d"))

    same = dialect.get_reference_table(table, None, "other")
    foreign = dialect.get_reference_table(table, "s", "other")

    assert dialect.get_table_qualifier(same) == "[other]"
    assert dialect.get_table_qualifier(foreign) == "[d].[s].[other]"
