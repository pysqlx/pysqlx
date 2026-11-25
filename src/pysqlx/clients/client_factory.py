"""Factory of the clients."""

from collections.abc import Sequence

from .i_client import IClient
from .pyodbc import Pyodbc
from .sqlite_three import SqliteThree

_support_dict: dict[str, type[IClient]] = {
    "sqlite3": SqliteThree,
    "pyodbc": Pyodbc,
}


class ClientFactory:
    """Factory which lists the supported providers and creates the clients.

    A provider is the library used to reach a database: ``"sqlite3"`` or
    ``"pyodbc"``.
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
        """
        return _support_dict[provider_name].get_system_drivers()

    @staticmethod
    def get_sqlite3_client(
        directory_path: str | None,
        dialect_name: str,
        driver_name: str | None,
        database_name: str | None,
    ) -> SqliteThree:
        """Create a client for a SQLite database.

        :param directory_path: the directory of the database file. Only used
            by the ``"disk"`` driver.
        :param dialect_name: the name of the dialect, ``"sqlite"``
        :param driver_name: ``"disk"`` for a database stored in the file
            ``<database_name>.db``, or ``"memory"`` for a database kept in
            memory. The first available driver by default.
        :param database_name: the name of the database
        :returns: the client, connected to the database
        :raises RuntimeError: if an argument is invalid or the database
            cannot be opened
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
        dialect_name: str,
        server_port: int | None = None,
        is_trusted_connection: bool = False,
        driver_name: str | None = None,
        database_name: str | None = None,
    ) -> Pyodbc:
        """Create a client for a database server reached through ODBC.

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
        :returns: the client, connected to the server
        :raises RuntimeError: if an argument is invalid or the connection
            fails
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
        )
