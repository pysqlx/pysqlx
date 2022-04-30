
from datetime import datetime

from pysqlx.structures import Table

param_tuple0 = (
    'some str',
    datetime(1988, 1, 1),
    10.0,
    101,
    'some text',
)

param_tuple1 = (
    'some str2',
    datetime(1998, 1, 1),
    10.0,
    101,
    'some text',
)


def notest_pyodbc_client_init(pyodbc_client_general, remote_table):
    client = pyodbc_client_general
    table = remote_table

    database = table.database

    if client.is_exists(database).execute():
        client.drop(database).execute()

    assert not client.is_exists(database).execute()

    client.create(database).execute()

    assert client.is_exists(database).execute()


def test_pyodbc_client(pyodbc_client_db, remote_table):
    client = pyodbc_client_db
    table = remote_table

    if client.is_exists(table).execute():
        client.drop(table).execute()

    assert not client.is_exists(table).execute()

    client.create(table).execute()

    assert client.is_exists(table).execute()

    client.drop(table).execute()

    assert not client.is_exists(table).execute()

    client.create(table).execute()

    assert client.is_exists(table).execute()

    assert client.is_empty(table).execute()

    query = client.insert(table)

    query.execute(
        param_tuple=param_tuple0
    )

    assert not client.is_empty(table).execute()

    assert client.get_length(table).execute() == 1

    client.truncate(table).execute()

    assert client.is_empty(table).execute()

    assert client.get_length(table).execute() == 0

    query.execute_many(
        param_tuple_list=[param_tuple0] * 5 + [param_tuple1] * 5
    )

    assert client.get_length(table).execute() == 10

    ret = client.select_distinct(
        table,
        columns=[table.columns[0]]).execute()

    assert ret == (('some str',), ('some str2',))

    ret = client.select(
        table,
        columns=table.columns[1:3],
        top=3,
        ascend_by=[table.columns[0]],
        condition=table.columns[1] == param_tuple0[1]
    ).execute()

    assert ret == (
        (param_tuple0[1], 10.0),
        (param_tuple0[1], 10.0),
        (param_tuple0[1], 10.0),
    )

    ret = client.update(
        table,
        columns=table.columns[1:3],
        condition=table.columns[1] == param_tuple0[1]
    ).execute(param_tuple=(datetime(1990, 1, 1), 20.0))

    ret = client.select(
        table,
        columns=table.columns[1:3],
        top=3,
        ascend_by=[table.columns[0]],
        condition=table.columns[1] == datetime(1990, 1, 1)
    ).execute()

    assert ret == (
        (datetime(1990, 1, 1), 20.0),
        (datetime(1990, 1, 1), 20.0),
        (datetime(1990, 1, 1), 20.0),
    )

    assert client.get_length(table).execute() == 10

    client.delete(
        table,
        condition=table.columns[1] == datetime(1990, 1, 1)
    ).execute()

    ret = client.select(
        table,
        columns=table.columns[1:3],
        top=3,
        ascend_by=[table.columns[0]],
        condition=table.columns[1] == datetime(1990, 1, 1)
    ).execute()

    assert ret == tuple()

    assert client.get_length(table).execute() == 5


def test_sqlite3_client_union(sqlite3_client):
    client = sqlite3_client

    table0 = Table(table_name='t0')
    t0_city_col = table0.append_char_string_column(column_name='city')
    table0.append_char_string_column(column_name='country')
    client.create(table0).execute()

    table1 = Table(table_name='t1')
    t1_city_col = table1.append_char_string_column(column_name='city')
    table1.append_char_string_column(column_name='customer')
    client.create(table1).execute()

    client.insert(table0).execute_many(
        param_tuple_list=(
            ('Los Angles', 'US'),
            ('NYC', 'US'),
            ('London', 'UK'),
        )
    )

    client.insert(table1).execute_many(
        param_tuple_list=(
            ('Miami', 'US'),
            ('Paris', 'France'),
            ('Cairo', 'EG'),
        )
    )

    q = client.union(
        structure_list=(table0, table1),
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
        descend_by=[t0_city_col]
    )

    ret = q.execute()

    assert ret == (('Paris',), ('NYC',), ('Miami',),
                   ('Los Angles',), ('London',), ('Cairo',))

    q = client.union(
        structure_list=(table0, table1),
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
        descend_by=[t0_city_col]
    )

    ret = q.execute()

    assert ret == (('Paris',), ('NYC',), ('Miami',),
                   ('Los Angles',), ('London',), ('Cairo',))
