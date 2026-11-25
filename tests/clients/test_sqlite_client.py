import csv
from datetime import datetime
from pathlib import Path

import pytest

from pysqlx.clients import ClientFactory, SqliteClient
from pysqlx.exceptions import InvalidArgumentError, PysqlxError, UnsupportedOperationError
from pysqlx.structures import Database, Schema, Table

from .scenario import run_scenario

parameters0 = (
    "some str",
    datetime(1988, 1, 1),
    10.0,
    101,
    "some text",
)

parameters1 = (
    "some str2",
    datetime(1998, 1, 1),
    10.0,
    101,
    "some text",
)

_std_dir = Path(__file__).parent.parent / "std"


def test_sqlite_client(sqlite_client: SqliteClient, local_table: Table, tmp_path: Path) -> None:
    client = sqlite_client
    table = local_table

    assert not client.exists(table).execute()

    client.create(table).execute()

    assert client.exists(table).execute()

    client.drop(table).execute()

    assert not client.exists(table).execute()

    client.create(table).execute()

    assert client.exists(table).execute()

    assert client.is_empty(table).execute()

    query = client.insert(table)

    query.execute(parameters=parameters0)

    assert not client.is_empty(table).execute()

    assert client.count_rows(table).execute() == 1

    client.truncate(table).execute()

    assert client.is_empty(table).execute()

    assert client.count_rows(table).execute() == 0

    query.execute_many(parameters_list=[parameters0] * 5 + [parameters1] * 5)

    assert client.count_rows(table).execute() == 10

    ret = client.select_distinct(table, columns=[table.columns[0]]).execute()

    assert ret == (("some str",), ("some str2",))

    ret = client.select(
        table,
        columns=table.columns[1:3],
        limit=3,
        ascend_by=[table.columns[0]],
        condition=table.columns[1] == parameters0[1],
    ).execute()

    assert ret == (
        (parameters0[1], 10.0),
        (parameters0[1], 10.0),
        (parameters0[1], 10.0),
    )

    client.update(
        table, columns=table.columns[1:3], condition=table.columns[1] == parameters0[1]
    ).execute(parameters=(datetime(1990, 1, 1), 20.0))

    ret = client.select(
        table,
        columns=table.columns[1:3],
        limit=3,
        ascend_by=[table.columns[0]],
        condition=table.columns[1] == datetime(1990, 1, 1),
    ).execute()

    assert ret == (
        (datetime(1990, 1, 1), 20.0),
        (datetime(1990, 1, 1), 20.0),
        (datetime(1990, 1, 1), 20.0),
    )

    assert client.count_rows(table).execute() == 10

    database_name = client.database_name
    assert database_name is not None

    backup_db = ClientFactory.get_sqlite_client(
        directory_path=str(tmp_path),
        dialect_name=client.dialect_name,
        driver_name="disk",
        database_name=database_name,
    )

    client.backup_to(backup_db)

    assert backup_db.select(table).execute() == client.select(table).execute()

    del backup_db

    assert (tmp_path / (database_name + ".db")).is_file()

    with open(_std_dir / (database_name + ".csv"), newline="") as std_file:
        header, *std_rows = csv.reader(std_file)

    assert header == [col.column_name for col in table.columns]

    assert client.select(table).execute() == tuple(
        (row[0], datetime.fromisoformat(row[1]), float(row[2]), int(row[3]), row[4])
        for row in std_rows
    )

    client.delete(table, condition=table.columns[1] == datetime(1990, 1, 1)).execute()

    ret = client.select(
        table,
        columns=table.columns[1:3],
        limit=3,
        ascend_by=[table.columns[0]],
        condition=table.columns[1] == datetime(1990, 1, 1),
    ).execute()

    assert ret == tuple()

    assert client.count_rows(table).execute() == 5


def test_sqlite_client_union(sqlite_client: SqliteClient) -> None:
    client = sqlite_client

    table0 = Table(table_name="t0")
    t0_city_col = table0.append_char_string_column(column_name="city")
    table0.append_char_string_column(column_name="country")
    client.create(table0).execute()

    table1 = Table(table_name="t1")
    t1_city_col = table1.append_char_string_column(column_name="city")
    table1.append_char_string_column(column_name="customer")
    client.create(table1).execute()

    client.insert(table0).execute_many(
        parameters_list=(
            ("Los Angles", "US"),
            ("NYC", "US"),
            ("London", "UK"),
        )
    )

    client.insert(table1).execute_many(
        parameters_list=(
            ("Miami", "US"),
            ("Paris", "France"),
            ("Cairo", "EG"),
        )
    )

    q = client.union(
        table_list=(table0, table1),
        query_list=(
            client.select(
                table0,
                columns=[t0_city_col],
            ),
            client.select(
                table1,
                columns=[t1_city_col],
            ),
        ),
        columns_list=((t0_city_col,), (t1_city_col,)),
        is_all=False,
        descend_by=[t0_city_col],
    )

    ret = q.execute()

    assert ret == (("Paris",), ("NYC",), ("Miami",), ("Los Angles",), ("London",), ("Cairo",))

    q = client.union(
        table_list=(table0, table1),
        query_list=(
            client.select(
                table0,
                columns=[t0_city_col],
            ),
            client.select(
                table1,
                columns=[t1_city_col],
            ),
        ),
        columns_list=((t0_city_col,), (t1_city_col,)),
        is_all=True,
        descend_by=[t0_city_col],
    )

    ret = q.execute()

    assert ret == (("Paris",), ("NYC",), ("Miami",), ("Los Angles",), ("London",), ("Cairo",))


def test_sqlite_scenario(sqlite_client: SqliteClient) -> None:
    run_scenario(sqlite_client)


def test_sqlite_defaults(tmp_path: Path) -> None:
    memory_client = ClientFactory.get_sqlite_client()

    assert memory_client.dialect_name == "sqlite"
    assert memory_client.database_name is None

    table = Table(table_name="t")
    table.append_integer_column(column_name="a")

    with ClientFactory.get_sqlite_client(
        directory_path=str(tmp_path), database_name="shop"
    ) as disk_client:
        disk_client.create(table).execute()

    assert (tmp_path / "shop.db").is_file()


def test_sqlite_invalid_arguments(tmp_path: Path) -> None:
    with pytest.raises(InvalidArgumentError):
        ClientFactory.get_sqlite_client(driver_name="nope")

    with pytest.raises(InvalidArgumentError):
        ClientFactory.get_sqlite_client(dialect_name="mssql")

    with pytest.raises(InvalidArgumentError):
        ClientFactory.get_sqlite_client(database_name="")

    with pytest.raises(InvalidArgumentError):
        ClientFactory.get_sqlite_client(driver_name="disk")

    with pytest.raises(InvalidArgumentError):
        ClientFactory.get_sqlite_client(directory_path=str(tmp_path / "missing"))

    with pytest.raises(InvalidArgumentError):
        ClientFactory.get_sqlite_client(directory_path=str(tmp_path))

    # The name of the database must not lead out of the directory.
    for database_name in ("../outside", "a/b", "..", "."):
        with pytest.raises(InvalidArgumentError):
            ClientFactory.get_sqlite_client(
                directory_path=str(tmp_path), database_name=database_name
            )

    assert list(tmp_path.parent.glob("outside.db")) == []

    # The exceptions of the package are also the RuntimeError of earlier versions.
    with pytest.raises(RuntimeError):
        ClientFactory.get_sqlite_client(driver_name="nope")


def test_sqlite_close() -> None:
    client = ClientFactory.get_sqlite_client()
    table = Table(table_name="t")
    table.append_integer_column(column_name="a")

    assert bool(client.is_closed) is False

    with client as same_client:
        assert same_client is client
        client.create(table).execute()

    assert bool(client.is_closed) is True

    client.close()

    with pytest.raises(PysqlxError):
        client.count_rows(table).execute()


def test_sqlite_close_rolls_back(tmp_path: Path) -> None:
    table = Table(table_name="t")
    table.append_integer_column(column_name="a")

    def connect() -> SqliteClient:
        return ClientFactory.get_sqlite_client(directory_path=str(tmp_path), database_name="db")

    with connect() as client:
        client.create(table).execute()
        client.begin()
        client.insert(table).execute(parameters=(1,))

    with connect() as client:
        assert client.count_rows(table).execute() == 0


def test_sqlite_unsupported() -> None:
    client = ClientFactory.get_sqlite_client()
    table = Table(table_name="t")
    table.append_integer_column(column_name="a")

    with pytest.raises(UnsupportedOperationError):
        client.create(Database(database_name="d")).execute()

    with pytest.raises(UnsupportedOperationError):
        client.exists(Schema(schema_name="s")).execute()

    with pytest.raises(UnsupportedOperationError):
        client.create(table).execute_many(parameters_list=[(1,)])

    with pytest.raises(UnsupportedOperationError):
        client.select(table).execute_many(parameters_list=[(1,)])
