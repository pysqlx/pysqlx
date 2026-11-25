"""Factory of the clients."""

from collections.abc import Mapping, Sequence
from typing import Any

from .i_client import IClient
from .psycopg import Psycopg
from .pymysql import Pymysql
from .pyodbc import Pyodbc
from .sqlite_three import SqliteThree

_support_dict: dict[str, type[IClient]] = {
    "sqlite3": SqliteThree,
    "pyodbc": Pyodbc,
    "psycopg": Psycopg,
    "pymysql": Pymysql,
}


class ClientFactory:
    """Factory which lists the supported providers and creates the clients.

    A provider is the library used to reach a database: ``"sqlite3"``,
    ``"pyodbc"``, ``"psycopg"`` or ``"pymysql"``. Only ``sqlite3`` comes with
    Python; the others are installed on demand.
    """

    @staticmethod
    def get_providers_names() -> tuple[str, ...]:
        """List the supported providers.

        :returns: the names of the providers
        """
        return tuple(x for x in _support_dict)

    @staticmethod
    def get_dialects_names(provider_name: str) -> tuple[str, ...]:
        """List the SQL dialects which a provider supports.

        :param provider_name: the name of the provider
        :returns: the names of the dialects
        """
        return _support_dict[provider_name].get_dialects_names()

    @staticmethod
    def get_preferred_drivers(provider_name: str, dialect_name: str) -> tuple[str, ...]:
        """List the drivers which a provider can use for a dialect.

        :param provider_name: the name of the provider
        :param dialect_name: the name of the dialect
        :returns: the names of the drivers, most preferred first
        """
        return _support_dict[provider_name].get_preferred_drivers(dialect_name=dialect_name)

    @staticmethod
    def get_system_drivers(provider_name: str) -> Sequence[str]:
        """List the drivers of a provider which are installed on the system.

        :param provider_name: the name of the provider
        :returns: the names of the drivers
        :raises MissingDependencyError: if the library of the provider is not
            installed
        """
        return _support_dict[provider_name].get_system_drivers()

    @staticmethod
    def get_sqlite3_client(
        directory_path: str | None = None,
        dialect_name: str = "sqlite",
        driver_name: str | None = None,
        database_name: str | None = None,
    ) -> SqliteThree:
        """Create a client for a SQLite database.

        Without arguments, the database is kept in memory. With a directory
        and a database name, it is stored in the file
        ``<database_name>.db`` of the directory.

        :param directory_path: the directory of the database file
        :param dialect_name: the name of the dialect, ``"sqlite"``
        :param driver_name: ``"disk"`` or ``"memory"``. By default,
            ``"disk"`` when a directory is given and ``"memory"`` otherwise.
        :param database_name: the name of the database, which the ``"disk"``
            driver needs
        :returns: the client, connected to the database
        :raises InvalidArgumentError: if an argument is invalid
        :raises ConnectionFailedError: if the database cannot be opened
        """
        return SqliteThree(
            directory_path=directory_path,
            dialect_name=dialect_name,
            driver_name=driver_name,
            database_name=database_name,
        )

    @staticmethod
    def get_pyodbc_client(
        server_address: str,
        user_name: str,
        user_pass: str,
        dialect_name: str = "mssql",
        server_port: int | None = None,
        is_trusted_connection: bool = False,
        driver_name: str | None = None,
        database_name: str | None = None,
        connection_options: Mapping[str, str] | None = None,
    ) -> Pyodbc:
        """Create a client for a Microsoft SQL Server reached through ODBC.

        :param server_address: the address of the server
        :param user_name: the name of the user
        :param user_pass: the password of the user
        :param dialect_name: the name of the dialect, ``"mssql"``
        :param server_port: the port of the server, if not the default one
        :param is_trusted_connection: whether to authenticate with the
            account of the operating system
        :param driver_name: the name of the ODBC driver. The most preferred
            installed driver by default.
        :param database_name: the name of the database to connect to, if any
        :param connection_options: more attributes for the connection string,
            such as ``{"Encrypt": "yes"}``
        :returns: the client, connected to the server
        :raises InvalidArgumentError: if an argument is invalid
        :raises MissingDependencyError: if ``pyodbc`` is not installed
        :raises ConnectionFailedError: if the connection fails
        """
        return Pyodbc(
            server_address=server_address,
            user_name=user_name,
            user_pass=user_pass,
            server_port=server_port,
            is_trusted_connection=is_trusted_connection,
            dialect_name=dialect_name,
            driver_name=driver_name,
            database_name=database_name,
            connection_options=connection_options,
        )

    @staticmethod
    def get_psycopg_client(
        server_address: str,
        user_name: str,
        user_pass: str,
        dialect_name: str = "postgresql",
        server_port: int | None = None,
        database_name: str | None = None,
        connection_options: Mapping[str, Any] | None = None,
    ) -> Psycopg:
        """Create a client for a PostgreSQL server.

        :param server_address: the address of the server
        :param user_name: the name of the user
        :param user_pass: the password of the user
        :param dialect_name: the name of the dialect, ``"postgresql"``
        :param server_port: the port of the server, if not the default one
        :param database_name: the name of the database to connect to. The
            default database of the user by default.
        :param connection_options: more arguments for the connection of
            ``psycopg``, for example to require an encrypted connection, such
            as ``{"sslmode": "verify-full"}``
        :returns: the client, connected to the server
        :raises InvalidArgumentError: if an argument is invalid
        :raises MissingDependencyError: if ``psycopg`` is not installed
        :raises ConnectionFailedError: if the connection fails
        """
        return Psycopg(
            server_address=server_address,
            user_name=user_name,
            user_pass=user_pass,
            server_port=server_port,
            dialect_name=dialect_name,
            database_name=database_name,
            connection_options=connection_options,
        )

    @staticmethod
    def get_pymysql_client(
        server_address: str,
        user_name: str,
        user_pass: str,
        dialect_name: str = "mysql",
        server_port: int | None = None,
        database_name: str | None = None,
        connection_options: Mapping[str, Any] | None = None,
    ) -> Pymysql:
        """Create a client for a MySQL or MariaDB server.

        :param server_address: the address of the server
        :param user_name: the name of the user
        :param user_pass: the password of the user
        :param dialect_name: the name of the dialect, ``"mysql"``
        :param server_port: the port of the server, if not the default one
        :param database_name: the name of the database to connect to, if any
        :param connection_options: more arguments for the connection of
            ``pymysql``, for example to require an encrypted connection, such as
            ``{"ssl_verify_identity": True, "ssl_ca": "ca.pem"}``
        :returns: the client, connected to the server
        :raises InvalidArgumentError: if an argument is invalid
        :raises MissingDependencyError: if ``pymysql`` is not installed
        :raises ConnectionFailedError: if the connection fails
        """
        return Pymysql(
            server_address=server_address,
            user_name=user_name,
            user_pass=user_pass,
            server_port=server_port,
            dialect_name=dialect_name,
            database_name=database_name,
            connection_options=connection_options,
        )
