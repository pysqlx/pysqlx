import sys
from types import ModuleType
from typing import Any

import pytest

from pysqlx.clients import ClientFactory, Pymysql
from pysqlx.exceptions import ConnectionFailedError, InvalidArgumentError
from pysqlx.structures import Database, Table

from .scenario import run_scenario


def test_pymysql_names() -> None:
    assert Pymysql.get_client_name() == "Pymysql"
    assert ClientFactory.get_dialects_names("pymysql") == ("mysql",)
    assert ClientFactory.get_preferred_drivers("pymysql", "mysql") == ("pymysql",)
    assert ClientFactory.get_system_drivers("pymysql") == ("pymysql",)


def test_pymysql_invalid_arguments() -> None:
    with pytest.raises(InvalidArgumentError):
        ClientFactory.get_pymysql_client(server_address="h", user_name="", user_pass="p")

    with pytest.raises(InvalidArgumentError):
        ClientFactory.get_pymysql_client(
            server_address="h", user_name="u", user_pass="p", dialect_name="mssql"
        )


def test_pymysql_connection_failure() -> None:
    with pytest.raises(ConnectionFailedError):
        ClientFactory.get_pymysql_client(
            server_address="127.0.0.1", user_name="u", user_pass="p", server_port=1
        )


def test_pymysql_connection_arguments(monkeypatch: pytest.MonkeyPatch) -> None:
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

    ClientFactory.get_pymysql_client(
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


def test_pymysql_scenario(pymysql_client: Pymysql) -> None:
    run_scenario(pymysql_client)


def test_pymysql_database(pymysql_client: Pymysql) -> None:
    client = pymysql_client

    database = Database(database_name="pysqlx database")
    table = Table(table_name="pysqlx table", database=database)
    column = table.append_integer_column(column_name="a column")

    if client.is_exists(database).execute():
        client.drop(database).execute()

    client.create(database).execute()
    client.create(table).execute()

    assert client.is_exists(database).execute() is True
    assert client.is_exists(table).execute() is True

    client.insert(table).execute(param_tuple=(7,))

    assert client.select(table, condition=column == 7).execute() == ((7,),)

    client.drop(table).execute()

    assert client.is_exists(table).execute() is False

    client.drop(database).execute()

    assert client.is_exists(database).execute() is False
