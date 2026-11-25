from pysqlx.dialects import PostgreSql as Dialect

from .cases import read_std, render


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
