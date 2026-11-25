"""PostgreSQL client."""

from collections.abc import Mapping, Sequence
from typing import Any

from .._compat import override
from ..exceptions import MissingDependencyError
from .client import Client

_driver = "psycopg"

_preferred_drivers: dict[str, tuple[str, ...]] = {
    "postgresql": (_driver,),
}


def _import_psycopg() -> Any:
    try:
        import psycopg
    except ImportError as e:
        raise MissingDependencyError(
            'psycopg could not be imported, install it with "pip install pysqlx[postgresql]"'
        ) from e

    return psycopg


class PostgreSqlClient(Client):
    """Client for a PostgreSQL server, using ``psycopg``.

    ``psycopg`` is installed with ``pip install pysqlx[postgresql]``.

    :param server_address: the address of the server
    :param user_name: the name of the user
    :param user_pass: the password of the user
    :param server_port: the port of the server, or ``None`` for the default
        one
    :param dialect_name: the name of the dialect, ``"postgresql"``
    :param database_name: the name of the database to connect to, or ``None``
        for the default database of the user
    :param connection_options: more arguments for the connection of ``psycopg``,
        for example to require an encrypted connection, such as
        ``{"sslmode": "verify-full"}``
    :raises InvalidArgumentError: if an argument is invalid
    :raises MissingDependencyError: if ``psycopg`` is not installed
    :raises ConnectionFailedError: if the connection fails
    """

    @staticmethod
    @override
    def get_client_name() -> str:
        return "PostgreSqlClient"

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
        _import_psycopg()
        return (_driver,)

    def __init__(
        self,
        server_address: str,
        user_name: str,
        user_pass: str,
        server_port: int | None = None,
        dialect_name: str = "postgresql",
        database_name: str | None = None,
        connection_options: Mapping[str, Any] | None = None,
    ) -> None:
        super().__init__(
            database_name=database_name,
        )

        self._check_server_arguments(server_address, user_name, user_pass, server_port)
        self._check_dialect(dialect_name)

        psycopg = _import_psycopg()

        arguments: dict[str, Any] = {
            **(connection_options or {}),
            "host": server_address,
            "user": user_name,
            "password": user_pass,
            "autocommit": True,
        }

        if server_port:
            arguments["port"] = server_port

        if database_name:
            arguments["dbname"] = database_name

        self._set_connection(self._connect(user_name, lambda: psycopg.connect(**arguments)))
        self._set_dialect(dialect_name)

    @override
    def _begin_transaction(self) -> None:
        self._connection.autocommit = False

    @override
    def _end_transaction(self) -> None:
        self._connection.autocommit = True
