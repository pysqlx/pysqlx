import sys
from types import ModuleType
from typing import Any

import pytest

from pysqlx.clients import ClientFactory, MySqlClient
from pysqlx.exceptions import ConnectionFailedError, InvalidArgumentError
from pysqlx.structures import Database, Table

from .scenario import run_scenario


def test_mysql_names() -> None:
    assert MySqlClient.get_client_name() == "MySqlClient"
    assert ClientFactory.get_dialects_names("pymysql") == ("mysql",)
    assert ClientFactory.get_preferred_drivers("pymysql", "mysql") == ("pymysql",)
    assert ClientFactory.get_system_drivers("pymysql") == ("pymysql",)


def test_mysql_invalid_arguments() -> None:
    with pytest.raises(InvalidArgumentError):
        ClientFactory.get_mysql_client(server_address="h", user_name="", user_pass="p")

    with pytest.raises(InvalidArgumentError):
        ClientFactory.get_mysql_client(
            server_address="h", user_name="u", user_pass="p", dialect_name="mssql"
        )


def test_mysql_connection_failure() -> None:
    with pytest.raises(ConnectionFailedError):
        ClientFactory.get_mysql_client(
            server_address="127.0.0.1", user_name="u", user_pass="p", server_port=1
        )


def test_mysql_connection_arguments(monkeypatch: pytest.MonkeyPatch) -> None:
    received: dict[str, Any] = {}

    class FakeConnection:
        def close(self) -> None:
            pass

    def connect(**arguments: Any) -> FakeConnection:
        received.update(arguments)
        return FakeConnection()

    module: Any = ModuleType("pymysql")
    module.connect = connect
    monkeypatch.setitem(sys.modules, "pymysql", module)

    ClientFactory.get_mysql_client(
        server_address="h",
        user_name="u",
        user_pass="p",
        server_port=1234,
        database_name="shop",
        connection_options={"connect_timeout": 5, "host": "other", "autocommit": False},
    )

    # The options are passed on, but cannot replace the arguments of the client.
    assert received["connect_timeout"] == 5
    assert (received["host"], received["user"], received["password"]) == ("h", "u", "p")
    assert (received["port"], received["autocommit"]) == (1234, True)
    assert "shop" in received.values()


def test_mysql_scenario(mysql_client: MySqlClient) -> None:
    run_scenario(mysql_client)


def test_mysql_database(mysql_client: MySqlClient) -> None:
    client = mysql_client

    database = Database(database_name="pysqlx database")
    table = Table(table_name="pysqlx table", database=database)
    column = table.append_integer_column(column_name="a column")

    if client.exists(database).execute():
        client.drop(database).execute()

    client.create(database).execute()
    client.create(table).execute()

    assert client.exists(database).execute() is True
    assert client.exists(table).execute() is True

    client.insert(table).execute(parameters=(7,))

    assert client.select(table, condition=column == 7).execute() == ((7,),)

    client.drop(table).execute()

    assert client.exists(table).execute() is False

    client.drop(database).execute()

    assert client.exists(database).execute() is False
