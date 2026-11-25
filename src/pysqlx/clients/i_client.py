"""Interface of the clients."""

import os
from abc import ABC, abstractmethod
from collections.abc import Sequence
from time import time
from typing import Any

from ..dialects import IDialect, MsSql, Sqlite
from ..logger import logger
from ..queries import (
    Create,
    Delete,
    Drop,
    GetLength,
    Insert,
    IsEmpty,
    IsExists,
    Query,
    Select,
    SelectDistinct,
    Truncate,
    Union,
    Update,
)
from ..structures import Clause, Column, Structure, Table


class IClient(ABC):
    """Interface of the clients.

    A client holds a connection to a database. Its methods create queries,
    which are sent to the database when they are executed.

    :param database_name: the name of the database to connect to, if any
    :raises RuntimeError: if the name of the database is invalid
    """

    @staticmethod
    @abstractmethod
    def get_client_name() -> str:
        """Get the name of the client.

        :returns: the name of the client
        """

    @staticmethod
    @abstractmethod
    def get_dialects_names() -> tuple[str, ...]:
        """List the SQL dialects which the client supports.

        :returns: the names of the dialects
        """

    @staticmethod
    @abstractmethod
    def get_preferred_drivers(dialect_name: str) -> tuple[str, ...]:
        """List the drivers which the client can use for a dialect.

        :param dialect_name: the name of the dialect
        :returns: the names of the drivers, most preferred first
        """

    @staticmethod
    @abstractmethod
    def get_system_drivers() -> Sequence[str]:
        """List the drivers of the client which are installed on the system.

        :returns: the names of the drivers
        """

    def __init__(self, database_name: str | None) -> None:
        ABC.__init__(self)

        self.__dialect: IDialect | None = None
        self.__conn: Any = None

        if not self._is_valid_database_name(database_name):
            raise RuntimeError(f'database_name is invalid "{database_name}"')

        self.__database_name = database_name

    def __del__(self) -> None:
        if self.__conn:
            self.__conn.close()
            self.__conn = None

        logger.debug("connection closed")

    @property
    def database_name(self) -> str | None:
        """Name of the database which the client is connected to, or ``None``."""
        return self.__database_name

    @property
    def dialect_name(self) -> str:
        """Name of the SQL dialect of the client."""
        return self._dialect.dialect_name

    @property
    def _dialect(self) -> IDialect:
        if self.__dialect is None:
            raise RuntimeError("dialect is not set")
        return self.__dialect

    @property
    def _connection(self) -> Any:
        return self.__conn

    def _is_valid_directory_path(self, directory_path: str | None) -> bool:
        return isinstance(directory_path, str) and os.path.exists(directory_path)

    def _is_valid_server_address(self, server_address: str) -> bool:
        return isinstance(server_address, str) and server_address != ""

    def _is_valid_user_name(self, user_name: str) -> bool:
        return isinstance(user_name, str) and user_name != ""

    def _is_valid_user_pass(self, user_pass: str) -> bool:
        return isinstance(user_pass, str) and user_pass != ""

    def _is_valid_server_port(self, server_port: int | None) -> bool:
        return any(
            (
                server_port is None,
                isinstance(server_port, int),
            )
        )

    def _is_valid_database_name(self, database_name: str | None) -> bool:
        return any(
            (
                database_name is None,
                isinstance(database_name, str) and database_name != "",
            )
        )

    def _is_valid_driver(self, dialect_name: str, driver_name: str) -> bool:
        return all(
            (
                driver_name in self.get_system_drivers(),
                driver_name in self.get_preferred_drivers(dialect_name=dialect_name),
            )
        )

    def _get_default_driver(self, dialect_name: str) -> str:
        sys_drivers = self.get_system_drivers()
        for driver_name in self.get_preferred_drivers(dialect_name=dialect_name):
            if driver_name in sys_drivers:
                return driver_name
        raise RuntimeError("Could not find a valid driver")

    def _set_dialect(self, dialect_name: str) -> None:
        if dialect_name not in self.get_dialects_names():
            raise RuntimeError(f'dialect_name is invalid "{dialect_name}"')

        obj: IDialect

        if dialect_name == "sqlite":
            obj = Sqlite()
        elif dialect_name == "mssql":
            obj = MsSql()
        else:
            raise RuntimeError(f'unsupported dialect "{dialect_name}"')

        self.__dialect = obj

    def _set_connection(self, obj: Any) -> None:
        self.__conn = obj

    def get_query_string(self, query: Query) -> str:
        """Get the SQL which the client sends for a query.

        :param query: the query
        :returns: the SQL statement, in the dialect of the client
        """
        return self._dialect.get_query_string(query)

    def _execute(self, sql_string: str, param_tuple: Sequence[Any] | None = None) -> Any:
        tic = time()

        if not sql_string:
            raise RuntimeError("invalid SQL request")

        if param_tuple:
            logger.debug(f'executing "{sql_string}" with parameters "{param_tuple}"')
        else:
            logger.debug(f'executing "{sql_string}"')

        cur = self._execute_sql_string(
            sql_string=sql_string,
            param_tuple=param_tuple,
        )

        logger.debug(f"executed in {time() - tic} seconds")

        return cur

    def _execute_many(self, sql_string: str, param_tuple_list: Sequence[Sequence[Any]]) -> Any:
        tic = time()

        if not sql_string:
            raise RuntimeError("invalid SQL request")

        logger.debug(f'executing "{sql_string}" with many parameters "{param_tuple_list}"')

        cur = self._execute_many_sql_string(
            sql_string=sql_string,
            param_tuple_list=param_tuple_list,
        )

        logger.debug(f"executed in {time() - tic} seconds")

        return cur

    def execute(self, query: Query, param_tuple: Sequence[Any] | None = None) -> Any:
        """Execute a query once.

        :param query: the query
        :param param_tuple: the values of the parameters of the query, for
            the queries which take parameters
        :returns: the result of the query, which depends on its type
        """
        return getattr(
            self,
            "_execute_" + type(query).__name__,
        )(
            query=query,
            param_tuple=param_tuple,
        )

    def execute_many(self, query: Query, param_tuple_list: Sequence[Sequence[Any]]) -> Any:
        """Execute a query once for each set of parameter values.

        :param query: the query
        :param param_tuple_list: one sequence of parameter values per
            execution
        :returns: the result of the query, which depends on its type
        :raises RuntimeError: if the query does not support it
        """
        return getattr(
            self,
            "_execute_many_" + type(query).__name__,
        )(
            query=query,
            param_tuple_list=param_tuple_list,
        )

    @abstractmethod
    def _execute_sql_string(self, sql_string: str, param_tuple: Sequence[Any] | None) -> Any: ...

    @abstractmethod
    def _execute_many_sql_string(
        self, sql_string: str, param_tuple_list: Sequence[Sequence[Any]]
    ) -> Any: ...

    @abstractmethod
    def _execute_Create(self, query: Create, param_tuple: Sequence[Any] | None) -> None: ...

    @abstractmethod
    def _execute_Delete(self, query: Delete, param_tuple: Sequence[Any] | None) -> None: ...

    @abstractmethod
    def _execute_Drop(self, query: Drop, param_tuple: Sequence[Any] | None) -> None: ...

    @abstractmethod
    def _execute_GetLength(self, query: GetLength, param_tuple: Sequence[Any] | None) -> Any: ...

    @abstractmethod
    def _execute_Insert(self, query: Insert, param_tuple: Sequence[Any] | None) -> None: ...

    @abstractmethod
    def _execute_IsEmpty(self, query: IsEmpty, param_tuple: Sequence[Any] | None) -> bool: ...

    @abstractmethod
    def _execute_IsExists(self, query: IsExists, param_tuple: Sequence[Any] | None) -> bool: ...

    @abstractmethod
    def _execute_Select(
        self, query: Select, param_tuple: Sequence[Any] | None
    ) -> tuple[tuple[Any, ...], ...]: ...

    @abstractmethod
    def _execute_SelectDistinct(
        self, query: SelectDistinct, param_tuple: Sequence[Any] | None
    ) -> tuple[tuple[Any, ...], ...]: ...

    @abstractmethod
    def _execute_Truncate(self, query: Truncate, param_tuple: Sequence[Any] | None) -> None: ...

    @abstractmethod
    def _execute_Union(
        self, query: Union, param_tuple: Sequence[Any] | None
    ) -> tuple[tuple[Any, ...], ...]: ...

    @abstractmethod
    def _execute_Update(self, query: Update, param_tuple: Sequence[Any] | None) -> None: ...

    def _execute_many_Create(
        self, query: Create, param_tuple_list: Sequence[Sequence[Any]]
    ) -> None:
        raise RuntimeError("Create query does not support execute_many")

    def _execute_many_Delete(
        self, query: Delete, param_tuple_list: Sequence[Sequence[Any]]
    ) -> None:
        raise RuntimeError("Delete query does not support execute_many")

    def _execute_many_Drop(self, query: Drop, param_tuple_list: Sequence[Sequence[Any]]) -> None:
        raise RuntimeError("Drop query does not support execute_many")

    def _execute_many_GetLength(
        self, query: GetLength, param_tuple_list: Sequence[Sequence[Any]]
    ) -> None:
        raise RuntimeError("GetLength query does not support execute_many")

    @abstractmethod
    def _execute_many_Insert(
        self, query: Insert, param_tuple_list: Sequence[Sequence[Any]]
    ) -> None: ...

    def _execute_many_IsEmpty(
        self, query: IsEmpty, param_tuple_list: Sequence[Sequence[Any]]
    ) -> None:
        raise RuntimeError("IsEmpty query does not support execute_many")

    def _execute_many_IsExists(
        self, query: IsExists, param_tuple_list: Sequence[Sequence[Any]]
    ) -> None:
        raise RuntimeError("IsExists query does not support execute_many")

    def _execute_many_Select(
        self, query: Select, param_tuple_list: Sequence[Sequence[Any]]
    ) -> None:
        raise RuntimeError("Select query does not support execute_many")

    def _execute_many_SelectDistinct(
        self, query: SelectDistinct, param_tuple_list: Sequence[Sequence[Any]]
    ) -> None:
        raise RuntimeError("SelectDistinct query does not support execute_many")

    def _execute_many_Truncate(
        self, query: Truncate, param_tuple_list: Sequence[Sequence[Any]]
    ) -> None:
        raise RuntimeError("Truncate query does not support execute_many")

    def _execute_many_Union(self, query: Union, param_tuple_list: Sequence[Sequence[Any]]) -> None:
        raise RuntimeError("Union query does not support execute_many")

    @abstractmethod
    def _execute_many_Update(
        self, query: Update, param_tuple_list: Sequence[Sequence[Any]]
    ) -> None: ...

    def create(self, structure: Structure) -> Create:
        """Create a query which creates a database, a schema or a table.

        :param structure: the structure to create
        :returns: the query
        """
        return Create(client=self, structure=structure)

    def delete(self, structure: Table, condition: Clause) -> Delete:
        """Create a query which removes the rows which satisfy a condition.

        :param structure: the table to remove rows from
        :param condition: the condition which the removed rows satisfy
        :returns: the query
        """
        return Delete(client=self, structure=structure, condition=condition)

    def drop(self, structure: Structure) -> Drop:
        """Create a query which drops a database, a schema or a table.

        :param structure: the structure to drop
        :returns: the query
        """
        return Drop(client=self, structure=structure)

    def is_exists(self, structure: Structure) -> IsExists:
        """Create a query which checks whether a structure exists.

        :param structure: the database, the schema or the table to look for
        :returns: the query, which gives a boolean when executed
        """
        return IsExists(client=self, structure=structure)

    def is_empty(self, structure: Table) -> IsEmpty:
        """Create a query which checks whether a table has no rows.

        :param structure: the table to check
        :returns: the query, which gives a boolean when executed
        """
        return IsEmpty(client=self, structure=structure)

    def get_length(self, structure: Table) -> GetLength:
        """Create a query which counts the rows of a table.

        :param structure: the table to count the rows of
        :returns: the query, which gives the number of rows when executed
        """
        return GetLength(client=self, structure=structure)

    def truncate(self, structure: Table) -> Truncate:
        """Create a query which removes all rows of a table.

        :param structure: the table to empty
        :returns: the query
        """
        return Truncate(client=self, structure=structure)

    def insert(self, structure: Table, columns: Sequence[Column] | None = None) -> Insert:
        """Create a query which adds rows to a table.

        The values are given when the query is executed, one per column.

        :param structure: the table to add rows to
        :param columns: the columns which values are given for. All columns
            of the table by default.
        :returns: the query
        :raises RuntimeError: if the columns are empty or invalid
        """
        return Insert(client=self, structure=structure, columns=columns)

    def select(
        self,
        structure: Table,
        columns: Sequence[Column] | None = None,
        top: int | None = None,
        ascend_by: Sequence[Column] | None = None,
        descend_by: Sequence[Column] | None = None,
        condition: Clause | None = None,
    ) -> Select:
        """Create a query which reads rows of a table.

        :param structure: the table to read from
        :param columns: the columns to read. All columns of the table by
            default.
        :param top: the maximum number of rows to read. All rows by default.
        :param ascend_by: the columns to sort by in ascending order
        :param descend_by: the columns to sort by in descending order
        :param condition: the condition which the rows satisfy
        :returns: the query, which gives a tuple of rows when executed
        :raises RuntimeError: if an argument is invalid
        """
        return Select(
            client=self,
            structure=structure,
            columns=columns,
            top=top,
            ascend_by=ascend_by,
            descend_by=descend_by,
            condition=condition,
        )

    def select_distinct(
        self,
        structure: Table,
        columns: Sequence[Column],
        ascend_by: Sequence[Column] | None = None,
        descend_by: Sequence[Column] | None = None,
        condition: Clause | None = None,
    ) -> SelectDistinct:
        """Create a query which reads the distinct values of columns.

        :param structure: the table to read from
        :param columns: the columns to read
        :param ascend_by: the columns to sort by in ascending order
        :param descend_by: the columns to sort by in descending order
        :param condition: the condition which the rows satisfy
        :returns: the query, which gives a tuple of rows when executed
        :raises RuntimeError: if an argument is invalid
        """
        return SelectDistinct(
            client=self,
            structure=structure,
            columns=columns,
            ascend_by=ascend_by,
            descend_by=descend_by,
            condition=condition,
        )

    def union(
        self,
        structure_list: Sequence[Table],
        query_list: Sequence[Select],
        columns_list: Sequence[Sequence[Column] | None] | None = None,
        is_all: bool = False,
        ascend_by: Sequence[Column] | None = None,
        descend_by: Sequence[Column] | None = None,
        condition: Clause | None = None,
    ) -> Union:
        """Create a query which combines the rows of several select queries.

        :param structure_list: the tables which the select queries read from
        :param query_list: the select queries to combine, one per table
        :param columns_list: the columns to read from each select query. All
            columns of the matching table by default.
        :param is_all: whether to keep duplicate rows
        :param ascend_by: the columns to sort by in ascending order
        :param descend_by: the columns to sort by in descending order
        :param condition: the condition which the rows satisfy
        :returns: the query, which gives a tuple of rows when executed
        :raises RuntimeError: if an argument is invalid
        """
        return Union(
            client=self,
            structure_list=structure_list,
            query_list=query_list,
            columns_list=columns_list,
            is_all=is_all,
            ascend_by=ascend_by,
            descend_by=descend_by,
            condition=condition,
        )

    def update(
        self,
        structure: Table,
        condition: Clause,
        columns: Sequence[Column] | None = None,
    ) -> Update:
        """Create a query which changes the rows which satisfy a condition.

        The new values are given when the query is executed, one per column.

        :param structure: the table to change rows of
        :param condition: the condition which the changed rows satisfy
        :param columns: the columns to change. All columns of the table by
            default.
        :returns: the query
        :raises RuntimeError: if the columns are invalid
        """
        return Update(
            client=self,
            structure=structure,
            columns=columns,
            condition=condition,
        )
