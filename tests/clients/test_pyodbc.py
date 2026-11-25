import sys
from types import ModuleType
from typing import Any

import pytest

from pysqlx.clients import ClientFactory, Pyodbc
from pysqlx.exceptions import ConnectionFailedError, InvalidArgumentError, MissingDependencyError
from pysqlx.structures import Database, Schema, Table

from .scenario import run_scenario


class FakeConnection:
    def __init__(self, connection_string: str, autocommit: bool) -> None:
        self.connection_string = connection_string
        self.autocommit = autocommit
        self.calls: list[str] = []

    def commit(self) -> None:
        self.calls.append("commit")

    def rollback(self) -> None:
        self.calls.append("rollback")

    def close(self) -> None:
        self.calls.append("close")


@pytest.fixture(scope="function")
def fake_pyodbc(monkeypatch: pytest.MonkeyPatch) -> ModuleType:
    module: Any = ModuleType("pyodbc")
    module.drivers = lambda: ["SQL Server", "ODBC Driver 18 for SQL Server", "Other"]
    module.connections = []

    def connect(connection_string: str, autocommit: bool = False) -> FakeConnection:
        if "PWD=wrong" in connection_string:
            raise OSError("login failed")

        connection = FakeConnection(connection_string, autocommit)
        module.connections.append(connection)
        return connection

    module.connect = connect

    monkeypatch.setitem(sys.modules, "pyodbc", module)

    return module  # type: ignore[no-any-return]


def test_pyodbc_names() -> None:
    assert Pyodbc.get_client_name() == "Pyodbc"
    assert ClientFactory.get_dialects_names("pyodbc") == ("mssql",)
    assert ClientFactory.get_preferred_drivers("pyodbc", "mssql")[0] == (
        "ODBC Driver 18 for SQL Server"
    )


def test_pyodbc_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    # None in sys.modules makes the import fail.
    monkeypatch.setitem(sys.modules, "pyodbc", None)

    with pytest.raises(MissingDependencyError):
        ClientFactory.get_system_drivers("pyodbc")

    with pytest.raises(ImportError):
        ClientFactory.get_pyodbc_client(server_address="h", user_name="u", user_pass="p")


def test_pyodbc_connection(fake_pyodbc: Any) -> None:
    assert ClientFactory.get_system_drivers("pyodbc") == [
        "SQL Server",
        "ODBC Driver 18 for SQL Server",
        "Other",
    ]

    client = ClientFactory.get_pyodbc_client(server_address="h", user_name="u", user_pass="p")
    connection = fake_pyodbc.connections[-1]

    assert client.dialect_name == "mssql"
    assert bool(connection.autocommit) is True
    assert connection.connection_string == (
        "DRIVER=ODBC Driver 18 for SQL Server;UID=u;SERVER=h;PWD=p"
    )

    client = ClientFactory.get_pyodbc_client(
        server_address="h",
        user_name="u",
        user_pass="p",
        server_port=1433,
        is_trusted_connection=True,
        driver_name="SQL Server",
        database_name="shop",
        connection_options={"TrustServerCertificate": "yes"},
    )

    assert fake_pyodbc.connections[-1].connection_string == (
        "DRIVER=SQL Server;UID=u;SERVER=h,1433;DATABASE=shop;Trusted_Connection=Yes;"
        "TrustServerCertificate=yes;PWD=p"
    )


def test_pyodbc_invalid_arguments(fake_pyodbc: Any) -> None:
    def connect(**arguments: Any) -> Pyodbc:
        return ClientFactory.get_pyodbc_client(
            **{"server_address": "h", "user_name": "u", "user_pass": "p", **arguments}
        )

    for arguments in (
        {"server_address": ""},
        {"user_name": ""},
        {"user_pass": ""},
        {"server_port": "1"},
        {"is_trusted_connection": 1},
        {"dialect_name": "sqlite"},
        {"driver_name": "Other"},
        {"driver_name": "ODBC Driver 17 for SQL Server"},
        {"database_name": ""},
    ):
        with pytest.raises(InvalidArgumentError):
            connect(**arguments)

    with pytest.raises(ConnectionFailedError):
        connect(user_pass="wrong")


def test_pyodbc_transaction(fake_pyodbc: Any) -> None:
    client = ClientFactory.get_pyodbc_client(server_address="h", user_name="u", user_pass="p")
    connection = fake_pyodbc.connections[-1]

    client.begin()

    assert bool(connection.autocommit) is False

    client.commit()

    assert bool(connection.autocommit) is True

    with pytest.raises(ZeroDivisionError):
        with client.transaction():
            assert bool(connection.autocommit) is False
            raise ZeroDivisionError

    assert bool(connection.autocommit) is True

    client.close()

    assert connection.calls == ["commit", "rollback", "close"]


def test_pyodbc_scenario(pyodbc_client: Pyodbc) -> None:
    run_scenario(pyodbc_client)


def test_pyodbc_database_and_schema(pyodbc_client: Pyodbc) -> None:
    client = pyodbc_client

    database = Database(database_name="pysqlx database")
    schema = Schema(schema_name="pysqlx schema")
    table = Table(table_name="pysqlx table", schema=schema)
    column = table.append_integer_column(column_name="a column")

    if client.is_exists(database).execute():
        client.drop(database).execute()

    client.create(database).execute()

    assert client.is_exists(database).execute() is True

    client.drop(database).execute()

    assert client.is_exists(database).execute() is False

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

    assert client.is_exists(schema).execute() is False
