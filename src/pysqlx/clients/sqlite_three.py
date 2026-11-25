"""SQLite client."""

import os
import sqlite3
from collections.abc import Callable, Sequence
from datetime import datetime
from typing import Any, Self, cast, override

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
from ..structures import Column, DatetimeColumn, Table
from .i_client import IClient

_disk_driver = "disk"
_memory_driver = "memory"

_preferred_drivers: dict[str, tuple[str, ...]] = {
    "sqlite": (
        _disk_driver,
        _memory_driver,
    ),
}

_system_drivers: tuple[str, ...] = (
    _disk_driver,
    _memory_driver,
)


def _convert_fetch_all(
    ret_list: Sequence[Sequence[Any]],
    columns: Sequence[Column],
) -> tuple[tuple[Any, ...], ...]:
    return tuple(
        tuple(
            datetime.fromisoformat(x[i]) if isinstance(columns[i], DatetimeColumn) else x[i]
            for i in range(len(x))
        )
        for x in ret_list
    )


def _get_connection(
    directory_path: str | None,
    driver_name: str,
    database_name: str | None,
    _info: Callable[[str], None],
) -> sqlite3.Connection:
    if driver_name == _disk_driver:
        if directory_path is None:
            raise RuntimeError(f'directory_path is invalid "{directory_path}"')

        if database_name is None:
            raise RuntimeError(f'database_name is invalid "{database_name}"')

        file_path = os.path.join(directory_path, database_name + ".db")
    else:
        file_path = ":memory:"

    _info(f'opening database at "{file_path}"')

    try:
        if driver_name == _disk_driver:
            conn = sqlite3.connect(f"file:{file_path}", isolation_level=None, uri=True)
        else:
            conn = sqlite3.connect(file_path, isolation_level=None)
    except Exception as e:
        raise RuntimeError("could not open database, check file permissions") from e

    return conn


class SqliteThree(IClient):
    """Client for a SQLite database, using the ``sqlite3`` module.

    :param directory_path: the directory of the database file. Only used by
        the ``"disk"`` driver.
    :param dialect_name: the name of the dialect, ``"sqlite"``
    :param driver_name: ``"disk"`` for a database stored in the file
        ``<database_name>.db``, or ``"memory"`` for a database kept in
        memory. The first available driver by default.
    :param database_name: the name of the database
    :raises RuntimeError: if an argument is invalid or the database cannot be
        opened
    """

    @staticmethod
    @override
    def get_client_name() -> str:
        return "SqliteThree"

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
        directory_path: str | None,
        dialect_name: str,
        driver_name: str | None,
        database_name: str | None,
    ) -> None:
        super().__init__(
            database_name=database_name,
        )

        if driver_name is None:
            driver_name = self._get_default_driver(dialect_name)

        if not self._is_valid_driver(dialect_name, driver_name):
            raise RuntimeError(f'driver_name is invalid "{driver_name}"')

        if driver_name == _disk_driver:
            if directory_path is not None:
                directory_path = os.path.abspath(directory_path)

            if not self._is_valid_directory_path(directory_path):
                raise RuntimeError(f'directory_path is invalid "{directory_path}"')

        self._set_connection(
            _get_connection(
                directory_path,
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

        table = cast(Table, query.structure)
        return True if (ret and ret[0][0] == table.table_name) else False

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

    def backup_to(self, other: Self) -> None:
        """Copy the database to the database of another client.

        :param other: the client of the database to copy to
        """
        from_db = self._connection
        to_db = other._connection
        with from_db, to_db:
            from_db.backup(to_db)
