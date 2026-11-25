"""ODBC client."""

from collections.abc import Callable, Mapping, Sequence
from time import time
from typing import Any, override

from ..exceptions import ConnectionFailedError, InvalidArgumentError, MissingDependencyError
from ..logger import logger
from .i_client import IClient

_preferred_drivers: dict[str, tuple[str, ...]] = {
    "mssql": (
        "ODBC Driver 18 for SQL Server",
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


def _import_pyodbc() -> Any:
    try:
        import pyodbc
    except ImportError as e:
        raise MissingDependencyError(
            'pyodbc could not be imported, install it with "pip install pysqlx[odbc]"; '
            "on macOS it also needs unixODBC"
        ) from e

    return pyodbc


def _get_connection(
    server_address: str,
    user_name: str,
    user_pass: str,
    server_port: int | None,
    is_trusted_connection: bool,
    driver_name: str,
    database_name: str | None,
    connection_options: Mapping[str, str] | None,
    _info: Callable[[str], None],
) -> Any:
    pyodbc = _import_pyodbc()

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

    for key, value in (connection_options or {}).items():
        conn_ar.append(f"{key}={value}")

    conn_ar.append("PWD=")

    _info(f'connection string "{";".join(conn_ar)}*"')

    try:
        conn = pyodbc.connect(";".join(conn_ar) + user_pass, autocommit=True)
    except Exception as e:
        raise ConnectionFailedError("could not authenticate DB, check username and password") from e

    _info(f"connection initalized in {time() - tic} seconds")

    return conn


class Pyodbc(IClient):
    """Client for a database server reached through ODBC, using ``pyodbc``.

    ``pyodbc`` is installed with ``pip install pysqlx[odbc]``.

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
    :param connection_options: more attributes for the connection string,
        such as ``{"TrustServerCertificate": "yes"}``
    :raises InvalidArgumentError: if an argument is invalid
    :raises MissingDependencyError: if ``pyodbc`` is not installed
    :raises ConnectionFailedError: if the connection fails
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
        drivers: list[str] = _import_pyodbc().drivers()
        return drivers

    def __init__(
        self,
        server_address: str,
        user_name: str,
        user_pass: str,
        server_port: int | None = None,
        is_trusted_connection: bool = False,
        dialect_name: str = "mssql",
        driver_name: str | None = None,
        database_name: str | None = None,
        connection_options: Mapping[str, str] | None = None,
    ) -> None:
        super().__init__(
            database_name=database_name,
        )

        self._check_server_arguments(server_address, user_name, user_pass, server_port)

        if not isinstance(is_trusted_connection, bool):
            raise InvalidArgumentError(
                f'is_trusted_connection is invalid "{is_trusted_connection}"'
            )

        self._check_dialect(dialect_name)

        if driver_name is None:
            driver_name = self._get_default_driver(dialect_name)

        if not self._is_valid_driver(dialect_name, driver_name):
            raise InvalidArgumentError(f'driver_name is invalid "{driver_name}"')

        self._set_connection(
            _get_connection(
                server_address,
                user_name,
                user_pass,
                server_port,
                is_trusted_connection,
                driver_name,
                database_name,
                connection_options,
                logger.info,
            )
        )
        self._set_dialect(dialect_name)

    @override
    def _begin_transaction(self) -> None:
        self._connection.autocommit = False

    @override
    def _end_transaction(self) -> None:
        self._connection.autocommit = True
