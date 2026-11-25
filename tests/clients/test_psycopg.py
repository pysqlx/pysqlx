import sys
from types import ModuleType
from typing import Any

import pytest

from pysqlx.clients import ClientFactory, Psycopg
from pysqlx.exceptions import ConnectionFailedError, InvalidArgumentError
from pysqlx.structures import Schema, Table

from .scenario import run_scenario


def test_psycopg_names() -> None:
    assert Psycopg.get_client_name() == "Psycopg"
    assert ClientFactory.get_dialects_names("psycopg") == ("postgresql",)
    assert ClientFactory.get_preferred_drivers("psycopg", "postgresql") == ("psycopg",)
    assert ClientFactory.get_system_drivers("psycopg") == ("psycopg",)


def test_psycopg_invalid_arguments() -> None:
    with pytest.raises(InvalidArgumentError):
        ClientFactory.get_psycopg_client(server_address="", user_name="u", user_pass="p")

    with pytest.raises(InvalidArgumentError):
        ClientFactory.get_psycopg_client(
            server_address="h", user_name="u", user_pass="p", dialect_name="mysql"
        )


def test_psycopg_connection_failure() -> None:
    with pytest.raises(ConnectionFailedError):
        ClientFactory.get_psycopg_client(
            server_address="127.0.0.1", user_name="u", user_pass="p", server_port=1
        )


def test_psycopg_connection_arguments(monkeypatch: pytest.MonkeyPatch) -> None:
    received: dict[str, Any] = {}

    class FakeConnection:
        def close(self) -> None:
            pass

    def connect(**arguments: Any) -> FakeConnection:
        received.update(arguments)
        return FakeConnection()

    module: Any = ModuleType("psycopg")
    module.connect = connect
    monkeypatch.setitem(sys.modules, "psycopg", module)

    ClientFactory.get_psycopg_client(
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


def test_psycopg_scenario(psycopg_client: Psycopg) -> None:
    run_scenario(psycopg_client)


def test_psycopg_schema(psycopg_client: Psycopg) -> None:
    client = psycopg_client

    schema = Schema(schema_name="pysqlx schema")
    table = Table(table_name="pysqlx table", schema=schema)
    column = table.append_integer_column(column_name="a column")

    if client.is_exists(table).execute():
        client.drop(table).execute()

    if client.is_exists(schema).execute():
        client.drop(schema).execute()

    client.create(schema).execute()
    client.create(table).execute()

    assert client.is_exists(schema).execute() is True
    assert client.is_exists(table).execute() is True

    client.insert(table).execute(param_tuple=(7,))

    assert client.select(table, condition=column == 7).execute() == ((7,),)

    client.drop(table).execute()
    client.drop(schema).execute()

    assert client.is_exists(table).execute() is False
    assert client.is_exists(schema).execute() is False
