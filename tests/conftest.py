
import pytest
from pysqlx.clients import ClientFactory
from pysqlx.dialects import Sqlite as SqliteDialect
from pysqlx.structures import Database, Schema, Table

_default_database_name = 'TestDatabase'
_default_schema_name = 'dbo'
_default_table_name = 'test'

_default_directory_path = None
_default_local_dialect_name = 'sqlite'
_default_local_driver_name = 'memory'


@pytest.fixture(scope='function')
def sqlite_dialect():
    return SqliteDialect()


@pytest.fixture(scope='function')
def sqlite3_client():
    return ClientFactory.get_sqlite3_client(
        directory_path=_default_directory_path,
        dialect_name=_default_local_dialect_name,
        driver_name=_default_local_driver_name,
        database_name=_default_database_name,
    )


@pytest.fixture(scope='function')
def pyodbc_client_general():
    return ClientFactory.get_pyodbc_client(
        server_address=_default_server_path,
        user_name=_default_user_name,
        user_pass=_default_user_pass,
        dialect_name=_default_remote_dialect_name,
        server_port=_default_server_port,
        is_trusted_connection=_default_is_trusted_connection,
        driver_name=_default_remote_driver_name,
        database_name=None,
    )


@pytest.fixture(scope='function')
def pyodbc_client_db():
    return ClientFactory.get_pyodbc_client(
        server_address=_default_server_path,
        user_name=_default_user_name,
        user_pass=_default_user_pass,
        dialect_name=_default_remote_dialect_name,
        server_port=_default_server_port,
        is_trusted_connection=_default_is_trusted_connection,
        driver_name=_default_remote_driver_name,
        database_name=_default_database_name,
    )


def _fill_table(test_table):

    test_table.append_char_string_column(
        column_name='char_string_column',
        is_unicode=False,
        is_fixed=False,
        size=255,
        is_primary_key=False,
        is_prevent_null=False
    )

    test_table.append_datetime_column(
        column_name='datetime_column',
        is_primary_key=False,
        is_prevent_null=False
    )

    test_table.append_float_column(
        column_name='float_column',
        is_double=True,
        is_primary_key=False,
        is_prevent_null=False
    )

    test_table.append_integer_column(
        column_name='integer_column',
        n_bytes=4,
        is_identity=False,
        is_primary_key=False,
        is_prevent_null=False
    )

    test_table.append_text_column(
        column_name='text_column',
        is_unicode=False,
        is_primary_key=False,
        is_prevent_null=False
    )


@pytest.fixture(scope='function')
def local_table():

    test_table = Table(table_name=_default_table_name)

    _fill_table(test_table)

    return test_table


@pytest.fixture(scope='function')
def remote_table():

    db = Database(database_name=_default_database_name)

    schema = Schema(schema_name=_default_schema_name)

    test_table = Table(
        table_name=_default_table_name,
        database=db,
        schema=schema
    )

    _fill_table(test_table)

    return test_table
