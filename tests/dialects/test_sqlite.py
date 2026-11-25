import pytest

from pysqlx.dialects import Sqlite as Dialect
from pysqlx.exceptions import UnsupportedOperationError

from .cases import read_std, reflect, render


def test_sqlite_queries() -> None:
    dialect = Dialect()

    assert dialect.dialect_name == "sqlite"
    assert render(dialect) == read_std(dialect)


def test_sqlite_quoting() -> None:
    dialect = Dialect()

    assert dialect.placeholder == "?"
    assert dialect.quote_identifier("a]b") == "[a]]b]"
    assert dialect.get_literal_string("it's") == "'it''s'"


def test_sqlite_reflection() -> None:
    dialect = Dialect()
    sql = "CREATE TABLE t ([id] integer NOT NULL PRIMARY KEY AUTOINCREMENT)"

    assert reflect(
        dialect,
        [
            ("id", "integer", 1, None, 1, sql),
            ("a", "nvarchar(50)", 1, None, 0, sql),
            ("b", "CHAR(3)", 0, "'x'", 0, sql),
            ("c", "text", 0, None, 0, sql),
            ("d", "real", 0, None, 0, sql),
            ("e", "datetime", 0, None, 0, sql),
            ("f", "date", 0, None, 0, sql),
            ("g", "boolean", 0, None, 0, sql),
            ("h", "decimal(10, 2)", 0, None, 0, sql),
            ("i", "blob", 0, None, 0, sql),
            ("j", "varchar", 0, None, 0, sql),
            ("k", "numeric", 0, None, 0, sql),
        ],
    ) == [
        ("IntegerColumn", "id", {"n_bytes": 8}, "KIR", None),
        ("CharStringColumn", "a", {"size": 50, "is_fixed": False, "is_unicode": True}, "R", None),
        ("CharStringColumn", "b", {"size": 3, "is_fixed": True, "is_unicode": False}, "", "'x'"),
        ("TextColumn", "c", {"is_unicode": False}, "", None),
        ("FloatColumn", "d", {"is_double": True}, "", None),
        ("DatetimeColumn", "e", {}, "", None),
        ("DateColumn", "f", {}, "", None),
        ("BooleanColumn", "g", {}, "", None),
        ("DecimalColumn", "h", {"precision": 10}, "", None),
        ("BinaryColumn", "i", {}, "", None),
        ("CharStringColumn", "j", {"size": 255, "is_fixed": False, "is_unicode": False}, "", None),
        ("DecimalColumn", "k", {"precision": 18}, "", None),
    ]

    # Without AUTOINCREMENT in its definition, the key is not an identity.
    assert reflect(dialect, [("id", "integer", 1, None, 1, "CREATE TABLE t (id integer)")]) == [
        ("IntegerColumn", "id", {"n_bytes": 8}, "KR", None),
    ]

    with pytest.raises(UnsupportedOperationError):
        reflect(dialect, [("a", "geometry", 0, None, 0, sql)])
