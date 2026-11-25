from pysqlx.dialects import Sqlite as Dialect

from .cases import read_std, render


def test_sqlite_queries() -> None:
    dialect = Dialect()

    assert dialect.dialect_name == "sqlite"
    assert render(dialect) == read_std(dialect)


def test_sqlite_quoting() -> None:
    dialect = Dialect()

    assert dialect.placeholder == "?"
    assert dialect.quote_identifier("a]b") == "[a]]b]"
    assert dialect.get_literal_string("it's") == "'it''s'"
