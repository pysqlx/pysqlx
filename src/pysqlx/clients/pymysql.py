"""MySQL client."""

from collections.abc import Sequence
from time import time
from typing import Any, override

from ..exceptions import ConnectionFailedError, MissingDependencyError
from ..logger import logger
from .i_client import IClient

_driver = "pymysql"

_preferred_drivers: dict[str, tuple[str, ...]] = {
    "mysql": (_driver,),
}


def _import_pymysql() -> Any:
    try:
        import pymysql
    except ImportError as e:
        raise MissingDependencyError(
            'pymysql could not be imported, install it with "pip install pysqlx[mysql]"'
        ) from e

    return pymysql


class Pymysql(IClient):
    """Client for a MySQL or MariaDB server, using ``pymysql``.

    ``pymysql`` is installed with ``pip install pysqlx[mysql]``.

    :param server_address: the address of the server
    :param user_name: the name of the user
    :param user_pass: the password of the user
    :param server_port: the port of the server, or ``None`` for the default
        one
    :param dialect_name: the name of the dialect, ``"mysql"``
    :param database_name: the name of the database to connect to, or ``None``
    :raises InvalidArgumentError: if an argument is invalid
    :raises MissingDependencyError: if ``pymysql`` is not installed
    :raises ConnectionFailedError: if the connection fails
    """

    @staticmethod
    @override
    def get_client_name() -> str:
        return "Pymysql"

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
        _import_pymysql()
        return (_driver,)

    def __init__(
        self,
        server_address: str,
        user_name: str,
        user_pass: str,
        server_port: int | None = None,
        dialect_name: str = "mysql",
        database_name: str | None = None,
    ) -> None:
        super().__init__(
            database_name=database_name,
        )

        self._check_server_arguments(server_address, user_name, user_pass, server_port)
        self._check_dialect(dialect_name)

        pymysql = _import_pymysql()

        tic = time()

        logger.info(f'authenticating for user "{user_name}"')

        arguments: dict[str, Any] = {
            "host": server_address,
            "user": user_name,
            "password": user_pass,
        }

        if server_port:
            arguments["port"] = server_port

        if database_name:
            arguments["database"] = database_name

        try:
            conn = pymysql.connect(autocommit=True, **arguments)
        except Exception as e:
            raise ConnectionFailedError(
                "could not authenticate DB, check username and password"
            ) from e

        logger.info(f"connection initalized in {time() - tic} seconds")

        self._set_connection(conn)
        self._set_dialect(dialect_name)

    @override
    def _begin_transaction(self) -> None:
        self._connection.begin()
