from typing import Any

import pytest

from pysqlx.clients import ClientFactory
from pysqlx.dialects import MySql as Dialect
from pysqlx.exceptions import UnsupportedOperationError
from pysqlx.structures import Schema, Table

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


def test_mysql_queries() -> None:
    dialect = Dialect()

    assert dialect.dialect_name == "mysql"
    assert render(dialect) == read_std(dialect)


def test_mysql_quoting() -> None:
    dialect = Dialect()

    assert dialect.placeholder == "%s"
    assert dialect.quote_identifier("a`b") == "`a``b`"
    assert dialect.get_literal_string("it's a \\") == "'it''s a \\\\'"


def test_mysql_reflection() -> None:
    dialect = Dialect()

    assert reflect(
        dialect,
        [
            row("id", "bigint", nullable="NO", keys=1, identity=1, column_type="bigint"),
            row("a", "varchar", size=50, nullable="NO", column_type="varchar(50)"),
            row("b", "char", size=3, column_type="char(3)"),
            row("c", "longtext", column_type="longtext"),
            row("d", "text", column_type="text"),
            row("e", "tinyint", column_type="tinyint(1)"),
            row("f", "tinyint", column_type="tinyint"),
            row("g", "smallint", column_type="smallint"),
            row("h", "mediumint", column_type="mediumint"),
            row("i", "int", column_type="int"),
            row("j", "double", column_type="double"),
            row("k", "float", column_type="float"),
            row("l", "datetime", column_type="datetime"),
            row("m", "timestamp", column_type="timestamp"),
            row("n", "date", column_type="date"),
            row("o", "decimal", precision=10, scale=2, column_type="decimal(10,2)"),
            row("p", "longblob", column_type="longblob"),
            row("q", "varbinary", column_type="varbinary(8)"),
        ],
    ) == [
        ("IntegerColumn", "id", {"n_bytes": 8}, "KIR", None),
        ("CharStringColumn", "a", {"size": 50, "is_fixed": False, "is_unicode": False}, "R", None),
        ("CharStringColumn", "b", {"size": 3, "is_fixed": True, "is_unicode": False}, "", None),
        ("TextColumn", "c", {"is_unicode": False}, "", None),
        ("TextColumn", "d", {"is_unicode": False}, "", None),
        ("BooleanColumn", "e", {}, "", None),
        ("IntegerColumn", "f", {"n_bytes": 1}, "", None),
        ("IntegerColumn", "g", {"n_bytes": 2}, "", None),
        ("IntegerColumn", "h", {"n_bytes": 4}, "", None),
        ("IntegerColumn", "i", {"n_bytes": 4}, "", None),
        ("FloatColumn", "j", {"is_double": True}, "", None),
        ("FloatColumn", "k", {"is_double": False}, "", None),
        ("DatetimeColumn", "l", {}, "", None),
        ("DatetimeColumn", "m", {}, "", None),
        ("DateColumn", "n", {}, "", None),
        ("DecimalColumn", "o", {"precision": 10}, "", None),
        ("BinaryColumn", "p", {}, "", None),
        ("BinaryColumn", "q", {}, "", None),
    ]

    with pytest.raises(UnsupportedOperationError):
        reflect(dialect, [row("a", "json", column_type="json")])


def test_mysql_structures() -> None:
    dialect = Dialect()
    client = ClientFactory.get_sqlite_client()

    with pytest.raises(UnsupportedOperationError):
        dialect.get_query_string(client.create(Schema(schema_name="s", owner_name="me")))

    table = Table(table_name="t", schema=Schema(schema_name="s"))

    # Without a database, the schema of a table stands for its database.
    assert dialect.get_table_qualifier(table) == "`s`.`t`"

    same = dialect.get_reference_table(table, None, "other")
    foreign = dialect.get_reference_table(table, "d", "other")

    assert dialect.get_table_qualifier(same) == "`s`.`other`"
    assert dialect.get_table_qualifier(foreign) == "`d`.`other`"
