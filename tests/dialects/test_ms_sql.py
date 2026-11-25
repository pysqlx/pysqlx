from datetime import datetime

from pysqlx.dialects import MsSql as Dialect

from .cases import read_std, render


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
