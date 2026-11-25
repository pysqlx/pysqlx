"""SQLite client."""

import os
import sqlite3
from collections.abc import Callable, Sequence
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Self, override

from ..exceptions import ConnectionFailedError, InvalidArgumentError
from ..logger import logger
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


def _convert_parameter(value: Any) -> Any:
    """Convert a value to one which SQLite can store."""
    if isinstance(value, datetime):
        return value.isoformat(" ")

    if isinstance(value, date):
        return value.isoformat()

    if isinstance(value, Decimal):
        return str(value)

    return value


def _get_connection(
    directory_path: str | None,
    driver_name: str,
    database_name: str | None,
    _info: Callable[[str], None],
) -> sqlite3.Connection:
    if driver_name == _disk_driver:
        if directory_path is None:
            raise InvalidArgumentError(f'directory_path is invalid "{directory_path}"')

        if database_name is None:
            raise InvalidArgumentError(f'database_name is invalid "{database_name}"')

        file_path = os.path.join(directory_path, database_name + ".db")
    else:
        file_path = ":memory:"

    _info(f'opening database at "{file_path}"')

    try:
        conn = sqlite3.connect(file_path, isolation_level=None)
        conn.execute("PRAGMA foreign_keys = ON")
    except Exception as e:
        raise ConnectionFailedError("could not open database, check file permissions") from e

    return conn


class SqliteThree(IClient):
    """Client for a SQLite database, using the ``sqlite3`` module.

    Dates, dates with a time and decimal numbers are stored as text, and
    booleans as integers. They are converted back when they are read from a
    column of the matching type.

    :param directory_path: the directory of the database file. Without it,
        the database is kept in memory.
    :param dialect_name: the name of the dialect, ``"sqlite"``
    :param driver_name: ``"disk"`` for a database stored in the file
        ``<database_name>.db``, or ``"memory"`` for a database kept in
        memory. By default, ``"disk"`` when a directory is given and
        ``"memory"`` otherwise.
    :param database_name: the name of the database, which the ``"disk"``
        driver needs
    :raises InvalidArgumentError: if an argument is invalid
    :raises ConnectionFailedError: if the database cannot be opened
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
        directory_path: str | None = None,
        dialect_name: str = "sqlite",
        driver_name: str | None = None,
        database_name: str | None = None,
    ) -> None:
        super().__init__(
            database_name=database_name,
        )

        self._check_dialect(dialect_name)

        if driver_name is None:
            driver_name = _memory_driver if directory_path is None else _disk_driver

        if not self._is_valid_driver(dialect_name, driver_name):
            raise InvalidArgumentError(f'driver_name is invalid "{driver_name}"')

        if driver_name == _disk_driver:
            if directory_path is not None:
                directory_path = os.path.abspath(directory_path)

            if not self._is_valid_directory_path(directory_path):
                raise InvalidArgumentError(f'directory_path is invalid "{directory_path}"')

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
    def _convert_parameters(self, parameters: Sequence[Any]) -> Sequence[Any]:
        return [_convert_parameter(value) for value in parameters]

    @override
    def _begin_transaction(self) -> None:
        self._connection.execute("BEGIN")

    def backup_to(self, other: Self) -> None:
        """Copy the database to the database of another client.

        :param other: the client of the database to copy to
        """
        self._connection.backup(other._connection)
