from pysqlx.dialects import MySql as Dialect

from .cases import read_std, render


def test_mysql_queries() -> None:
    dialect = Dialect()

    assert dialect.dialect_name == "mysql"
    assert render(dialect) == read_std(dialect)


def test_mysql_quoting() -> None:
    dialect = Dialect()

    assert dialect.placeholder == "%s"
    assert dialect.quote_identifier("a`b") == "`a``b`"
    assert dialect.get_literal_string("it's a \\") == "'it''s a \\\\'"
