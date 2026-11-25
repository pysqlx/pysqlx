import os
from collections.abc import Iterator
from urllib.parse import SplitResult, unquote, urlsplit

import pytest

from pysqlx.clients import ClientFactory, Psycopg, Pymysql, Pyodbc, SqliteThree
from pysqlx.dialects import Sqlite as SqliteDialect
from pysqlx.structures import Table

_default_database_name = "TestDatabase"
_default_table_name = "test"


@pytest.fixture(scope="function")
def sqlite_dialect() -> SqliteDialect:
    return SqliteDialect()


@pytest.fixture(scope="function")
def sqlite3_client() -> Iterator[SqliteThree]:
    client = ClientFactory.get_sqlite3_client(database_name=_default_database_name)

    yield client

    client.close()


def _server(variable_name: str) -> SplitResult:
    """Read the address of a test server, given as user:password@host:port/database."""
    value = os.environ.get(variable_name)

    if not value:
        if os.environ.get("PYSQLX_TEST_REQUIRE_SERVERS"):
            pytest.fail(f"{variable_name} is not set")

        pytest.skip(f"{variable_name} is not set")

    return urlsplit("//" + value)


@pytest.fixture(scope="function")
def psycopg_client() -> Iterator[Psycopg]:
    server = _server("PYSQLX_TEST_POSTGRESQL")

    client = ClientFactory.get_psycopg_client(
        server_address=server.hostname or "",
        user_name=unquote(server.username or ""),
        user_pass=unquote(server.password or ""),
        server_port=server.port,
        database_name=server.path.lstrip("/") or None,
    )

    yield client

    client.close()


@pytest.fixture(scope="function")
def pymysql_client() -> Iterator[Pymysql]:
    server = _server("PYSQLX_TEST_MYSQL")

    client = ClientFactory.get_pymysql_client(
        server_address=server.hostname or "",
        user_name=unquote(server.username or ""),
        user_pass=unquote(server.password or ""),
        server_port=server.port,
        database_name=server.path.lstrip("/") or None,
    )

    yield client

    client.close()


@pytest.fixture(scope="function")
def pyodbc_client() -> Iterator[Pyodbc]:
    server = _server("PYSQLX_TEST_MSSQL")

    client = ClientFactory.get_pyodbc_client(
        server_address=server.hostname or "",
        user_name=unquote(server.username or ""),
        user_pass=unquote(server.password or ""),
        server_port=server.port,
        database_name=server.path.lstrip("/") or None,
        connection_options={"TrustServerCertificate": "yes"},
    )

    yield client

    client.close()


@pytest.fixture(scope="function")
def local_table() -> Table:
    test_table = Table(table_name=_default_table_name)

    test_table.append_char_string_column(
        column_name="char_string_column",
        is_unicode=False,
        is_fixed=False,
        size=255,
        is_primary_key=False,
        is_prevent_null=False,
    )

    test_table.append_datetime_column(
        column_name="datetime_column", is_primary_key=False, is_prevent_null=False
    )

    test_table.append_float_column(
        column_name="float_column", is_double=True, is_primary_key=False, is_prevent_null=False
    )

    test_table.append_integer_column(
        column_name="integer_column",
        n_bytes=4,
        is_identity=False,
        is_primary_key=False,
        is_prevent_null=False,
    )

    test_table.append_text_column(
        column_name="text_column", is_unicode=False, is_primary_key=False, is_prevent_null=False
    )

    return test_table
