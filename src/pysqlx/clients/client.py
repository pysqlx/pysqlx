"""Interface of the clients."""

from abc import ABC, abstractmethod
from collections.abc import Callable, Iterator, Sequence
from contextlib import contextmanager, suppress
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from time import perf_counter
from types import TracebackType
from typing import Any, Self

from ..dialects import Dialect, MsSql, MySql, PostgreSql, Sqlite
from ..exceptions import (
    ConnectionFailedError,
    InvalidArgumentError,
    PysqlxError,
    TransactionError,
    UnsupportedOperationError,
)
from ..logger import logger
from ..queries import (
    CountRows,
    Create,
    Delete,
    Drop,
    Exists,
    Insert,
    IsEmpty,
    Query,
    Reflect,
    Select,
    SelectDistinct,
    Truncate,
    Union,
    Update,
)
from ..structures import (
    Aggregate,
    BooleanColumn,
    Clause,
    Column,
    Database,
    DateColumn,
    DatetimeColumn,
    DecimalColumn,
    Join,
    Schema,
    Structure,
    Table,
)

_dialect_types: dict[str, Callable[[], Dialect]] = {
    "sqlite": Sqlite,
    "mssql": MsSql,
    "postgresql": PostgreSql,
    "mysql": MySql,
}


def _find_column(table: Table, column_name: str) -> Column:
    """Find a column of a table by its name."""
    for column in table.columns:
        if column.column_name == column_name:
            return column

    for column in table.columns:
        if column.column_name.casefold() == str(column_name).casefold():
            return column

    raise PysqlxError(f'column "{column_name}" is not in table "{table.table_name}"')


def _convert_result_value(value: Any, item: Column | Aggregate) -> Any:
    """Convert a value read from a database to the type of its column."""
    if isinstance(item, Aggregate):
        if item.column is None or item.function_name not in ("MAX", "MIN"):
            return value

        item = item.column

    if value is None:
        return None

    if isinstance(item, DatetimeColumn):
        return datetime.fromisoformat(value) if isinstance(value, str) else value

    if isinstance(item, DateColumn):
        return date.fromisoformat(value) if isinstance(value, str) else value

    if isinstance(item, BooleanColumn):
        return bool(value)

    if isinstance(item, DecimalColumn):
        return value if isinstance(value, Decimal) else Decimal(str(value))

    return value


class Client(ABC):
    """Interface of the clients.

    A client holds a connection to a database. Its methods create queries,
    which are sent to the database when they are executed.

    A client can be used in a ``with`` statement, which closes its connection
    at the end.

    :param database_name: the name of the database to connect to, if any
    :raises InvalidArgumentError: if the name of the database is invalid
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
        :raises MissingDependencyError: if the library of the client is not
            installed
        """

    def __init__(self, database_name: str | None) -> None:
        ABC.__init__(self)

        self.__dialect: Dialect | None = None
        self.__conn: Any = None
        self.__is_in_transaction = False

        if not self._is_valid_database_name(database_name):
            raise InvalidArgumentError(f'database_name is invalid "{database_name}"')

        self.__database_name = database_name

    def __del__(self) -> None:
        # Nothing may be raised while an object is deleted, for example when
        # Python shuts down.
        with suppress(Exception):
            self.close()

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.close()

    def close(self) -> None:
        """Close the connection to the database.

        A transaction which is still open is rolled back. Closing a client
        which is already closed does nothing.
        """
        if self.__conn is None:
            return

        conn = self.__conn
        self.__conn = None
        self.__is_in_transaction = False

        conn.close()

        logger.debug("connection closed")

    @property
    def is_closed(self) -> bool:
        """Whether the connection to the database is closed."""
        return self.__conn is None

    @property
    def database_name(self) -> str | None:
        """Name of the database which the client is connected to, or ``None``."""
        return self.__database_name

    @property
    def dialect_name(self) -> str:
        """Name of the SQL dialect of the client."""
        return self._dialect.dialect_name

    @property
    def _dialect(self) -> Dialect:
        if self.__dialect is None:
            raise PysqlxError("dialect is not set")
        return self.__dialect

    @property
    def _connection(self) -> Any:
        if self.__conn is None:
            raise PysqlxError("connection is closed")
        return self.__conn

    def _is_valid_directory_path(self, directory_path: str | None) -> bool:
        return isinstance(directory_path, str) and Path(directory_path).is_dir()

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

    def _check_server_arguments(
        self,
        server_address: str,
        user_name: str,
        user_pass: str,
        server_port: int | None,
    ) -> None:
        if not self._is_valid_server_address(server_address):
            raise InvalidArgumentError(f'server_address is invalid "{server_address}"')

        if not self._is_valid_user_name(user_name):
            raise InvalidArgumentError(f'username is invalid "{user_name}"')

        if not self._is_valid_user_pass(user_pass):
            raise InvalidArgumentError("password is invalid")

        if not self._is_valid_server_port(server_port):
            raise InvalidArgumentError(f'server_port is invalid "{server_port}"')

    def _connect(self, user_name: str, connect: Callable[[], Any]) -> Any:
        """Open the connection to a server, and report how long it took."""
        tic = perf_counter()

        logger.info('authenticating for user "%s"', user_name)

        try:
            connection = connect()
        except Exception as e:
            raise ConnectionFailedError(
                "could not connect to the database, check the address, the username "
                "and the password"
            ) from e

        logger.info("connection initialized in %s seconds", perf_counter() - tic)

        return connection

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
        raise PysqlxError(f'could not find an installed driver for "{dialect_name}"')

    def _check_dialect(self, dialect_name: str) -> None:
        if dialect_name not in self.get_dialects_names():
            raise InvalidArgumentError(f'dialect_name is invalid "{dialect_name}"')

    def _set_dialect(self, dialect_name: str) -> None:
        self._check_dialect(dialect_name)

        if dialect_name not in _dialect_types:
            raise InvalidArgumentError(f'unsupported dialect "{dialect_name}"')

        self.__dialect = _dialect_types[dialect_name]()

    def _set_connection(self, obj: Any) -> None:
        self.__conn = obj

    def get_query_string(self, query: Query) -> str:
        """Get the SQL of a query, for reading.

        The values of the conditions are written into the SQL. When the
        query is executed, they are passed to the database separately, as
        parameters.

        :param query: the query
        :returns: the SQL statement, in the dialect of the client
        """
        return self._dialect.get_query_string(query)

    @property
    def is_in_transaction(self) -> bool:
        """Whether a transaction is open."""
        return self.__is_in_transaction

    def begin(self) -> None:
        """Start a transaction.

        The changes made by the queries executed from now on take effect
        together when :py:meth:`commit` is called, and are undone by
        :py:meth:`rollback`. Without a transaction, every query takes effect
        at once.

        :raises TransactionError: if a transaction is already open
        """
        if self.__is_in_transaction:
            raise TransactionError("a transaction is already open")

        self._begin_transaction()
        self.__is_in_transaction = True

        logger.debug("transaction started")

    def commit(self) -> None:
        """Make the changes of the open transaction permanent.

        :raises TransactionError: if no transaction is open
        """
        if not self.__is_in_transaction:
            raise TransactionError("no transaction is open")

        try:
            self._connection.commit()
        finally:
            self.__is_in_transaction = False
            self._end_transaction()

        logger.debug("transaction committed")

    def rollback(self) -> None:
        """Undo the changes of the open transaction.

        :raises TransactionError: if no transaction is open
        """
        if not self.__is_in_transaction:
            raise TransactionError("no transaction is open")

        try:
            self._connection.rollback()
        finally:
            self.__is_in_transaction = False
            self._end_transaction()

        logger.debug("transaction rolled back")

    @contextmanager
    def transaction(self) -> Iterator[None]:
        """Run the queries of a ``with`` block in one transaction.

        The transaction is committed at the end of the block, and rolled back
        if the block raises an exception.

        :raises TransactionError: if a transaction is already open
        """
        self.begin()

        try:
            yield
        except BaseException:
            self.rollback()
            raise

        self.commit()

    @abstractmethod
    def _begin_transaction(self) -> None: ...

    def _end_transaction(self) -> None:
        """Return to the mode in which every query takes effect at once."""
        return

    def _convert_parameters(self, parameters: Sequence[Any]) -> Sequence[Any]:
        """Convert the values which the library of the client cannot take."""
        return parameters

    def _convert_rows(
        self,
        rows: Sequence[Sequence[Any]],
        items: Sequence[Column | Aggregate],
    ) -> tuple[tuple[Any, ...], ...]:
        return tuple(
            tuple(
                _convert_result_value(value, item) for value, item in zip(row, items, strict=True)
            )
            for row in rows
        )

    def _execute(self, sql_string: str, parameters: Sequence[Any] | None = None) -> Any:
        tic = perf_counter()

        if not sql_string:
            raise InvalidArgumentError("invalid SQL request")

        cur = self._connection.cursor()

        if parameters:
            logger.debug('executing "%s" with parameters "%s"', sql_string, parameters)
            cur.execute(sql_string, self._convert_parameters(parameters))
        else:
            logger.debug('executing "%s"', sql_string)
            cur.execute(sql_string)

        logger.debug("executed in %s seconds", perf_counter() - tic)

        return cur

    def _execute_many(self, sql_string: str, parameters_list: Sequence[Sequence[Any]]) -> Any:
        tic = perf_counter()

        if not sql_string:
            raise InvalidArgumentError("invalid SQL request")

        logger.debug('executing "%s" with many parameters "%s"', sql_string, parameters_list)

        cur = self._connection.cursor()
        cur.executemany(sql_string, [self._convert_parameters(row) for row in parameters_list])

        logger.debug("executed in %s seconds", perf_counter() - tic)

        return cur

    def _run(self, query: Query, parameters: Sequence[Any] | None) -> Any:
        """Execute a query, with its own parameters before those of its conditions."""
        condition_parameters: list[Any] = []
        sql_string = self._dialect.get_query_string(query, condition_parameters)

        return self._execute(sql_string, [*(parameters or ()), *condition_parameters])

    def _run_many(self, query: Query, parameters_list: Sequence[Sequence[Any]]) -> Any:
        condition_parameters: list[Any] = []
        sql_string = self._dialect.get_query_string(query, condition_parameters)

        return self._execute_many(
            sql_string, [[*row, *condition_parameters] for row in parameters_list]
        )

    def _fetch(self, query: Query, parameters: Sequence[Any] | None) -> list[Any]:
        ret: list[Any] = self._run(query, parameters).fetchall()

        logger.debug('received "%s"', ret)

        return ret

    def execute(self, query: Query, parameters: Sequence[Any] | None = None) -> Any:
        """Execute a query once.

        :param query: the query
        :param parameters: the values of the parameters of the query, for
            the queries which take parameters
        :returns: the result of the query, which depends on its type
        """
        return getattr(
            self,
            "_execute_" + type(query).__name__,
        )(
            query=query,
            parameters=parameters,
        )

    def execute_many(self, query: Query, parameters_list: Sequence[Sequence[Any]]) -> Any:
        """Execute a query once for each set of parameter values.

        :param query: the query
        :param parameters_list: one sequence of parameter values per
            execution
        :returns: the result of the query, which depends on its type
        :raises UnsupportedOperationError: if the query does not support it
        """
        method = getattr(self, "_execute_many_" + type(query).__name__, None)

        if method is None:
            raise UnsupportedOperationError(
                f"{type(query).__name__} query does not support execute_many"
            )

        return method(query=query, parameters_list=parameters_list)

    def _execute_Create(self, query: Create, parameters: Sequence[Any] | None) -> None:
        self._run(query, parameters)

    def _execute_Delete(self, query: Delete, parameters: Sequence[Any] | None) -> None:
        self._run(query, parameters)

    def _execute_Drop(self, query: Drop, parameters: Sequence[Any] | None) -> None:
        self._run(query, parameters)

    def _execute_CountRows(self, query: CountRows, parameters: Sequence[Any] | None) -> int:
        return int(self._fetch(query, parameters)[0][0])

    def _execute_Insert(self, query: Insert, parameters: Sequence[Any] | None) -> None:
        self._run(query, parameters)

    def _execute_IsEmpty(self, query: IsEmpty, parameters: Sequence[Any] | None) -> bool:
        ret = self._fetch(query, parameters)

        return bool(ret and ret[0][0] == 0)

    def _execute_Exists(self, query: Exists, parameters: Sequence[Any] | None) -> bool:
        ret = self._fetch(query, parameters)

        return bool(ret and ret[0][0])

    def _execute_Reflect(self, query: Reflect, parameters: Sequence[Any] | None) -> Table:
        table = self._dialect.get_reflected_table(query, self._fetch(query, parameters))

        self._reflect_foreign_keys(table)

        return table

    def _reflect_foreign_keys(self, table: Table) -> None:
        """Add the foreign keys found in the database to a table read from it."""
        rows = self._execute(self._dialect.get_foreign_keys_string(table)).fetchall()

        logger.debug('received "%s"', rows)

        keys: dict[Any, list[Sequence[Any]]] = {}

        for row in rows:
            keys.setdefault(row[0], []).append(row)

        references: dict[tuple[Any, Any], Table] = {}

        for key_rows in keys.values():
            schema_name, table_name = key_rows[0][2], key_rows[0][3]

            if schema_name is None and table_name == table.table_name:
                reference = table
            elif (schema_name, table_name) in references:
                reference = references[schema_name, table_name]
            else:
                query = Reflect(
                    client=self,
                    table=self._dialect.get_reference_table(table, schema_name, table_name),
                )
                reference = self._dialect.get_reflected_table(query, self._fetch(query, None))
                references[schema_name, table_name] = reference

            if any(row[4] is None for row in key_rows):
                # The foreign key refers to the primary key without naming it.
                reference_columns = [col for col in reference.columns if col.is_primary_key]
            else:
                reference_columns = [_find_column(reference, row[4]) for row in key_rows]

            table.append_foreign_key(
                columns=[_find_column(table, row[1]) for row in key_rows],
                reference_columns=reference_columns,
            )

    def _execute_Select(
        self, query: Select, parameters: Sequence[Any] | None
    ) -> tuple[tuple[Any, ...], ...]:
        return self._convert_rows(self._fetch(query, parameters), query.columns)

    def _execute_SelectDistinct(
        self, query: SelectDistinct, parameters: Sequence[Any] | None
    ) -> tuple[tuple[Any, ...], ...]:
        return self._convert_rows(self._fetch(query, parameters), query.columns)

    def _execute_Truncate(self, query: Truncate, parameters: Sequence[Any] | None) -> None:
        self._run(query, parameters)

    def _execute_Union(
        self, query: Union, parameters: Sequence[Any] | None
    ) -> tuple[tuple[Any, ...], ...]:
        return self._convert_rows(self._fetch(query, parameters), query.columns_list[0])

    def _execute_Update(self, query: Update, parameters: Sequence[Any] | None) -> None:
        self._run(query, parameters)

    def _execute_many_Insert(self, query: Insert, parameters_list: Sequence[Sequence[Any]]) -> None:
        self._run_many(query, parameters_list)

    def _execute_many_Update(self, query: Update, parameters_list: Sequence[Sequence[Any]]) -> None:
        self._run_many(query, parameters_list)

    def create(self, structure: Structure) -> Create:
        """Create a query which creates a structure.

        :param structure: the database, the schema, the table or the index to
            create
        :returns: the query
        """
        return Create(client=self, structure=structure)

    def delete(self, table: Table, condition: Clause) -> Delete:
        """Create a query which removes the rows which satisfy a condition.

        :param table: the table to remove rows from
        :param condition: the condition which the removed rows satisfy
        :returns: the query
        """
        return Delete(client=self, table=table, condition=condition)

    def drop(self, structure: Structure) -> Drop:
        """Create a query which drops a structure.

        :param structure: the database, the schema, the table or the index to
            drop
        :returns: the query
        """
        return Drop(client=self, structure=structure)

    def exists(self, structure: Structure) -> Exists:
        """Create a query which checks whether a structure exists.

        :param structure: the database, the schema, the table or the index to
            look for
        :returns: the query, which gives a boolean when executed
        """
        return Exists(client=self, structure=structure)

    def is_empty(self, table: Table) -> IsEmpty:
        """Create a query which checks whether a table has no rows.

        :param table: the table to check
        :returns: the query, which gives a boolean when executed
        """
        return IsEmpty(client=self, table=table)

    def count_rows(self, table: Table) -> CountRows:
        """Create a query which counts the rows of a table.

        :param table: the table to count the rows of
        :returns: the query, which gives the number of rows when executed
        """
        return CountRows(client=self, table=table)

    def reflect(
        self,
        table_name: str,
        database: Database | None = None,
        schema: Schema | None = None,
    ) -> Reflect:
        """Create a query which reads the columns of a table from the database.

        Use it to work with a table which exists already, without describing
        its columns by hand.

        :param table_name: the name of the table
        :param database: the database which the table belongs to, if any
        :param schema: the schema which the table belongs to, if any
        :returns: the query, which gives a table with its columns when
            executed
        """
        return Reflect(
            client=self,
            table=Table(table_name=table_name, database=database, schema=schema),
        )

    def truncate(self, table: Table) -> Truncate:
        """Create a query which removes all rows of a table.

        :param table: the table to empty
        :returns: the query
        """
        return Truncate(client=self, table=table)

    def insert(self, table: Table, columns: Sequence[Column] | None = None) -> Insert:
        """Create a query which adds rows to a table.

        The values are given when the query is executed, one per column.

        :param table: the table to add rows to
        :param columns: the columns which values are given for. All columns
            of the table by default.
        :returns: the query
        :raises InvalidArgumentError: if the columns are empty or invalid
        """
        return Insert(client=self, table=table, columns=columns)

    def select(
        self,
        table: Table,
        columns: Sequence[Column | Aggregate] | None = None,
        limit: int | None = None,
        ascend_by: Sequence[Column] | None = None,
        descend_by: Sequence[Column] | None = None,
        condition: Clause | None = None,
        offset: int | None = None,
        group_by: Sequence[Column] | None = None,
        joins: Sequence[Join] | None = None,
        having: Clause | None = None,
    ) -> Select:
        """Create a query which reads rows of a table.

        :param table: the table to read from
        :param columns: the columns and the aggregates to read. All columns
            of the table, and of the joined tables, by default.
        :param limit: the maximum number of rows to read. All rows by default.
        :param ascend_by: the columns to sort by in ascending order
        :param descend_by: the columns to sort by in descending order
        :param condition: the condition which the rows satisfy
        :param offset: the number of rows to skip before reading
        :param group_by: the columns which define the groups of rows which
            the aggregates are computed over
        :param joins: the tables to join to the table of the query
        :param having: the condition which the groups of rows satisfy, built
            from aggregates
        :returns: the query, which gives a tuple of rows when executed
        :raises InvalidArgumentError: if an argument is invalid
        """
        return Select(
            client=self,
            table=table,
            columns=columns,
            limit=limit,
            ascend_by=ascend_by,
            descend_by=descend_by,
            condition=condition,
            offset=offset,
            group_by=group_by,
            joins=joins,
            having=having,
        )

    def select_distinct(
        self,
        table: Table,
        columns: Sequence[Column],
        ascend_by: Sequence[Column] | None = None,
        descend_by: Sequence[Column] | None = None,
        condition: Clause | None = None,
    ) -> SelectDistinct:
        """Create a query which reads the distinct values of columns.

        :param table: the table to read from
        :param columns: the columns to read
        :param ascend_by: the columns to sort by in ascending order, among
            those which are read
        :param descend_by: the columns to sort by in descending order, among
            those which are read
        :param condition: the condition which the rows satisfy
        :returns: the query, which gives a tuple of rows when executed
        :raises InvalidArgumentError: if an argument is invalid
        """
        return SelectDistinct(
            client=self,
            table=table,
            columns=columns,
            ascend_by=ascend_by,
            descend_by=descend_by,
            condition=condition,
        )

    def union(
        self,
        table_list: Sequence[Table],
        query_list: Sequence[Select],
        columns_list: Sequence[Sequence[Column] | None] | None = None,
        is_all: bool = False,
        ascend_by: Sequence[Column] | None = None,
        descend_by: Sequence[Column] | None = None,
        condition: Clause | None = None,
    ) -> Union:
        """Create a query which combines the rows of several select queries.

        :param table_list: the tables which the select queries read from
        :param query_list: the select queries to combine, one per table
        :param columns_list: the columns to read from each select query. All
            columns of the matching table by default.
        :param is_all: whether to keep duplicate rows
        :param ascend_by: the columns of the first table to sort by in
            ascending order
        :param descend_by: the columns of the first table to sort by in
            descending order
        :param condition: the condition which the rows satisfy
        :returns: the query, which gives a tuple of rows when executed
        :raises InvalidArgumentError: if an argument is invalid
        """
        return Union(
            client=self,
            table_list=table_list,
            query_list=query_list,
            columns_list=columns_list,
            is_all=is_all,
            ascend_by=ascend_by,
            descend_by=descend_by,
            condition=condition,
        )

    def update(
        self,
        table: Table,
        condition: Clause,
        columns: Sequence[Column] | None = None,
    ) -> Update:
        """Create a query which changes the rows which satisfy a condition.

        The new values are given when the query is executed, one per column.

        :param table: the table to change rows of
        :param condition: the condition which the changed rows satisfy
        :param columns: the columns to change. All columns of the table by
            default.
        :returns: the query
        :raises InvalidArgumentError: if the columns are invalid
        """
        return Update(
            client=self,
            table=table,
            columns=columns,
            condition=condition,
        )
