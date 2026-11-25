import logging

import pytest

from pysqlx import ClientFactory, Table
from pysqlx.logger import logger


def test_logger_is_silent_by_default() -> None:
    assert logger.name == "pysqlx"
    assert any(isinstance(handler, logging.NullHandler) for handler in logger.handlers)


def test_logger_reports_statements(caplog: pytest.LogCaptureFixture) -> None:
    table = Table(table_name="t")
    column = table.append_char_string_column(column_name="a")

    with caplog.at_level(logging.DEBUG, logger="pysqlx"):
        with ClientFactory.get_sqlite3_client() as client:
            client.create(table).execute()
            client.select(table, condition=column == "secret").execute()

    messages = [record.getMessage() for record in caplog.records]

    assert (
        'executing "SELECT [a] FROM [t] WHERE [a] = ?" with parameters "[\'secret\']"' in messages
    )
    assert "connection closed" in messages
