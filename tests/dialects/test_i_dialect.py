from datetime import date, datetime
from decimal import Decimal

import pytest

from pysqlx.clients import ClientFactory
from pysqlx.dialects import IDialect, PostgreSql
from pysqlx.exceptions import UnsupportedOperationError
from pysqlx.structures import Database


def test_i_dialect_is_abstract() -> None:
    with pytest.raises(TypeError):
        IDialect(dialect_name="x")  # type: ignore[abstract]


def test_i_dialect_literals() -> None:
    dialect = PostgreSql()

    assert dialect.get_literal_string(None) == "NULL"
    assert dialect.get_literal_string(3) == "3"
    assert dialect.get_literal_string(1.5) == "1.5"
    assert dialect.get_literal_string(Decimal("1.50")) == "'1.50'"
    assert dialect.get_literal_string(date(2024, 1, 2)) == "'2024-01-02'"
    assert dialect.get_literal_string(datetime(2024, 1, 2, 3, 4, 5)) == "'2024-01-02 03:04:05'"


def test_i_dialect_unsupported_structure() -> None:
    client = ClientFactory.get_sqlite3_client()

    with pytest.raises(UnsupportedOperationError):
        client.truncate(Database(database_name="d")).execute()  # type: ignore[arg-type]
