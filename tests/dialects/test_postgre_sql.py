from typing import Any

import pytest

from pysqlx.dialects import PostgreSql as Dialect
from pysqlx.exceptions import UnsupportedOperationError

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


def test_postgresql_queries() -> None:
    dialect = Dialect()

    assert dialect.dialect_name == "postgresql"
    assert render(dialect) == read_std(dialect)


def test_postgresql_quoting() -> None:
    dialect = Dialect()

    assert dialect.placeholder == "%s"
    assert dialect.quote_identifier('a"b') == '"a""b"'
    assert dialect.get_literal_string("it's") == "'it''s'"
    assert dialect.get_literal_string(True) == "TRUE"
    assert dialect.get_literal_string(b"\x01") == "'\\x01'"


def test_postgresql_reflection() -> None:
    dialect = Dialect()

    assert reflect(
        dialect,
        [
            row("id", "integer", nullable="NO", keys=1, identity=1),
            row("a", "character varying", size=50, nullable="NO"),
            row("b", "character", size=3),
            row("c", "character varying"),
            row("d", "text"),
            row("e", "smallint"),
            row("f", "bigint"),
            row("g", "double precision"),
            row("h", "real"),
            row("i", "timestamp without time zone"),
            row("j", "timestamp with time zone"),
            row("k", "date"),
            row("l", "boolean", default="true"),
            row("m", "numeric", precision=10, scale=2),
            row("n", "bytea"),
        ],
    ) == [
        ("IntegerColumn", "id", {"n_bytes": 4}, "KIR", None),
        ("CharStringColumn", "a", {"size": 50, "is_fixed": False, "is_unicode": False}, "R", None),
        ("CharStringColumn", "b", {"size": 3, "is_fixed": True, "is_unicode": False}, "", None),
        ("TextColumn", "c", {"is_unicode": False}, "", None),
        ("TextColumn", "d", {"is_unicode": False}, "", None),
        ("IntegerColumn", "e", {"n_bytes": 2}, "", None),
        ("IntegerColumn", "f", {"n_bytes": 8}, "", None),
        ("FloatColumn", "g", {"is_double": True}, "", None),
        ("FloatColumn", "h", {"is_double": False}, "", None),
        ("DatetimeColumn", "i", {}, "", None),
        ("DatetimeColumn", "j", {}, "", None),
        ("DateColumn", "k", {}, "", None),
        ("BooleanColumn", "l", {}, "", "true"),
        ("DecimalColumn", "m", {"precision": 10}, "", None),
        ("BinaryColumn", "n", {}, "", None),
    ]

    with pytest.raises(UnsupportedOperationError):
        reflect(dialect, [row("a", "jsonb")])
