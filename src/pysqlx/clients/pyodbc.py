"""ODBC client."""

from collections.abc import Callable, Sequence
from time import time
from typing import Any, override

import pyodbc

from ..logger import logger
from ..queries import (
    Create,
    Delete,
    Drop,
    GetLength,
    Insert,
    IsEmpty,
    IsExists,
    Select,
    SelectDistinct,
    Truncate,
    Union,
    Update,
)
from ..structures import Column
from .i_client import IClient

_preferred_drivers: dict[str, tuple[str, ...]] = {
    "mssql": (
        "ODBC Driver 17 for SQL Server",
        "ODBC Driver 13.1 for SQL Server",
        "ODBC Driver 13 for SQL Server",
        "ODBC Driver 11 for SQL Server",
        "SQL Server Native Client 11.0",
        "SQL Server Native Client 10.0",
        "SQL Native Client",
        "SQL Server",
        "PSQL",
    ),
}

_system_drivers: list[str] = pyodbc.drivers()


def _convert_fetch_all(
    ret_list: Sequence[Sequence[Any]],
    _columns: Sequence[Column],
) -> tuple[tuple[Any, ...], ...]:
    return tuple(tuple(x[i] for i in range(len(x))) for x in ret_list)


def _get_connection(
    server_address: str,
    user_name: str,
    user_pass: str,
    server_port: int | None,
    is_trusted_connection: bool,
    driver_name: str,
    database_name: str | None,
    _info: Callable[[str], None],
) -> Any:
    tic = time()

    _info(f'authenticating for user "{user_name}"')

    conn_ar = [
        f"DRIVER={driver_name}",
        f"UID={user_name}",
    ]

    if server_port:
        conn_ar.append(f"SERVER={server_address},{server_port}")
    else:
        conn_ar.append(f"SERVER={server_address}")

    if database_name:
        conn_ar.append(f"DATABASE={database_name}")

    if is_trusted_connection:
        conn_ar.append("Trusted_Connection=Yes")

    conn_ar.append("PWD=")

    _info(f'connection string "{";".join(conn_ar)}*"')

    try:
        conn = pyodbc.connect(";".join(conn_ar) + user_pass, autocommit=True)
    except Exception as e:
        raise RuntimeError("could not authenticate DB, check username and password") from e

    _info(f"connection initalized in {time() - tic} seconds")

    return conn


class Pyodbc(IClient):
    """Client for a database server reached through ODBC, using ``pyodbc``.

    :param server_address: the address of the server
    :param user_name: the name of the user
    :param user_pass: the password of the user
    :param server_port: the port of the server, or ``None`` for the default
        one
    :param is_trusted_connection: whether to authenticate with the account
        of the operating system
    :param dialect_name: the name of the dialect, ``"mssql"``
    :param driver_name: the name of the ODBC driver, or ``None`` for the most
        preferred installed driver
    :param database_name: the name of the database to connect to, or ``None``
    :raises RuntimeError: if an argument is invalid or the connection fails
    """

    @staticmethod
    @override
    def get_client_name() -> str:
        return "Pyodbc"

    @staticmethod
    @override
    def get_dialects_names() -> tuple[str, ...]:
        return tuple(x for x in _preferred_drivers)

    @staticmethod
    @override
    def get_preferred_drivers(dialect_name: str) -> tuple[str, ...]:
        return _preferred_drivers[dialect_name]

    @staticmethod
    @override
    def get_system_drivers() -> Sequence[str]:
        return _system_drivers

    def __init__(
        self,
        server_address: str,
        user_name: str,
        user_pass: str,
        server_port: int | None,
        is_trusted_connection: bool,
        dialect_name: str,
        driver_name: str | None,
        database_name: str | None,
    ) -> None:
        super().__init__(
            database_name=database_name,
        )

        if not self._is_valid_server_address(server_address):
            raise RuntimeError(f'server_address is invalid "{server_address}"')

        if not self._is_valid_user_name(user_name):
            raise RuntimeError(f'username is invalid "{user_name}"')

        if not self._is_valid_user_pass(user_pass):
            raise RuntimeError("password is invalid")

        if not self._is_valid_server_port(server_port):
            raise RuntimeError(f'server_port is invalid "{server_port}"')

        if not isinstance(is_trusted_connection, bool):
            raise RuntimeError(f'is_trusted_connection is invalid "{is_trusted_connection}"')

        if driver_name is None:
            driver_name = self._get_default_driver(dialect_name)

        if not self._is_valid_driver(dialect_name, driver_name):
            raise RuntimeError(f'driver_name is invalid "{driver_name}"')

        self._set_connection(
            _get_connection(
                server_address,
                user_name,
                user_pass,
                server_port,
                is_trusted_connection,
                driver_name,
                database_name,
                logger.info,
            )
        )
        self._set_dialect(dialect_name)

    @override
    def _execute_sql_string(self, sql_string: str, param_tuple: Sequence[Any] | None) -> Any:
        cur = self._connection.cursor()

        if param_tuple:
            cur.execute(sql_string, param_tuple)
        else:
            cur.execute(sql_string)

        return cur

    @override
    def _execute_many_sql_string(
        self, sql_string: str, param_tuple_list: Sequence[Sequence[Any]]
    ) -> Any:
        return self._connection.cursor().executemany(sql_string, param_tuple_list)

    @override
    def _execute_Create(self, query: Create, param_tuple: Sequence[Any] | None) -> None:
        self._execute(sql_string=self.get_query_string(query), param_tuple=param_tuple)

    @override
    def _execute_Delete(self, query: Delete, param_tuple: Sequence[Any] | None) -> None:
        self._execute(sql_string=self.get_query_string(query), param_tuple=param_tuple)

    @override
    def _execute_Drop(self, query: Drop, param_tuple: Sequence[Any] | None) -> None:
        self._execute(sql_string=self.get_query_string(query), param_tuple=param_tuple)

    @override
    def _execute_GetLength(self, query: GetLength, param_tuple: Sequence[Any] | None) -> Any:
        ret = self._execute(
            sql_string=self.get_query_string(query), param_tuple=param_tuple
        ).fetchall()

        logger.debug(f'received "{ret}"')

        return ret[0][0]

    @override
    def _execute_Insert(self, query: Insert, param_tuple: Sequence[Any] | None) -> None:
        self._execute(sql_string=self.get_query_string(query), param_tuple=param_tuple)

    @override
    def _execute_IsEmpty(self, query: IsEmpty, param_tuple: Sequence[Any] | None) -> bool:
        ret = self._execute(
            sql_string=self.get_query_string(query), param_tuple=param_tuple
        ).fetchall()

        logger.debug(f'received "{ret}"')

        return True if (ret and ret[0][0] == 0) else False

    @override
    def _execute_IsExists(self, query: IsExists, param_tuple: Sequence[Any] | None) -> bool:
        ret = self._execute(
            sql_string=self.get_query_string(query), param_tuple=param_tuple
        ).fetchall()

        logger.debug(f'received "{ret}"')

        exists: bool = ret[0][0] == 1
        return exists

    @override
    def _execute_Select(
        self, query: Select, param_tuple: Sequence[Any] | None
    ) -> tuple[tuple[Any, ...], ...]:
        ret = self._execute(
            sql_string=self.get_query_string(query), param_tuple=param_tuple
        ).fetchall()

        logger.debug(f'received "{ret}"')

        return _convert_fetch_all(ret, query.columns)

    @override
    def _execute_SelectDistinct(
        self, query: SelectDistinct, param_tuple: Sequence[Any] | None
    ) -> tuple[tuple[Any, ...], ...]:
        ret = self._execute(
            sql_string=self.get_query_string(query), param_tuple=param_tuple
        ).fetchall()

        logger.debug(f'received "{ret}"')

        return _convert_fetch_all(ret, query.columns)

    @override
    def _execute_Truncate(self, query: Truncate, param_tuple: Sequence[Any] | None) -> None:
        self._execute(sql_string=self.get_query_string(query), param_tuple=param_tuple)

    @override
    def _execute_Union(
        self, query: Union, param_tuple: Sequence[Any] | None
    ) -> tuple[tuple[Any, ...], ...]:
        ret = self._execute(
            sql_string=self.get_query_string(query), param_tuple=param_tuple
        ).fetchall()

        logger.debug(f'received "{ret}"')

        return _convert_fetch_all(ret, query.columns_list[0])

    @override
    def _execute_Update(self, query: Update, param_tuple: Sequence[Any] | None) -> None:
        self._execute(sql_string=self.get_query_string(query), param_tuple=param_tuple)

    @override
    def _execute_many_Insert(
        self, query: Insert, param_tuple_list: Sequence[Sequence[Any]]
    ) -> None:
        self._execute_many(
            sql_string=self.get_query_string(query), param_tuple_list=param_tuple_list
        )

    @override
    def _execute_many_Update(
        self, query: Update, param_tuple_list: Sequence[Sequence[Any]]
    ) -> None:
        self._execute_many(
            sql_string=self.get_query_string(query), param_tuple_list=param_tuple_list
        )
