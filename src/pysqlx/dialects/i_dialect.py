"""Interface of the SQL dialects."""

import re
from abc import ABC, abstractmethod
from collections.abc import Sequence
from datetime import date, datetime
from typing import Any, cast

from ..exceptions import InvalidArgumentError, UnsupportedOperationError
from ..queries import (
    Create,
    Delete,
    Drop,
    GetLength,
    Insert,
    IsEmpty,
    IsExists,
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
    BinaryColumn,
    BooleanColumn,
    CharStringColumn,
    Clause,
    Column,
    Database,
    DateColumn,
    DatetimeColumn,
    DecimalColumn,
    FloatColumn,
    Index,
    IntegerColumn,
    Schema,
    Table,
    TextColumn,
)
from ..structures.columntypes.logicalclause import (
    And,
    Between,
    Equal,
    GreaterThan,
    GreaterThanEqual,
    InList,
    IsNotNull,
    IsNull,
    LessThan,
    LessThanEqual,
    Like,
    NotBetween,
    NotEqual,
    NotInList,
    NotLike,
    Or,
)


class IDialect(ABC):
    """Interface of the SQL dialects.

    A dialect turns columns, clauses and queries into SQL strings. This class
    writes the SQL which the databases have in common, and each dialect
    overrides what its database does differently.

    The methods :py:meth:`get_column_declaration`, :py:meth:`get_clause_string`
    and :py:meth:`get_query_string` select the method to call from the name
    of the class of their argument, and, for the queries, from the kind of
    structure which the query acts on.

    The methods which write clauses and queries take an optional list of
    parameters. With it, each value of a condition is added to the list and
    replaced by a placeholder in the SQL, which is how the clients execute
    the queries. Without it, the values are written into the SQL, which is
    meant for reading.

    :param dialect_name: the name of the dialect
    """

    def __init__(self, dialect_name: str) -> None:
        self.__dialect_name = dialect_name

    @property
    def dialect_name(self) -> str:
        """Name of the dialect."""
        return self.__dialect_name

    @property
    def placeholder(self) -> str:
        """Marker which stands for a parameter in a statement."""
        return "?"

    def quote_identifier(self, name: str) -> str:
        """Quote the name of a structure, so that any name can be used.

        :param name: the name of a database, a schema, a table, a column or
            an index
        :returns: the quoted name
        """
        return '"' + name.replace('"', '""') + '"'

    @abstractmethod
    def get_table_qualifier(self, table: Table) -> str:
        """Get the name which refers to a table in a statement.

        :param table: the table
        :returns: the quoted and qualified name of the table
        """

    def get_column_qualifier(self, column: Column, is_qualified: bool = False) -> str:
        """Get the name which refers to a column in a statement.

        :param column: the column
        :param is_qualified: whether to put the name of the table before the
            name of the column
        :returns: the quoted name of the column
        """
        name = self.quote_identifier(column.column_name)

        if is_qualified:
            return self.get_table_qualifier(column.table) + "." + name

        return name

    def get_select_item_string(self, item: Column | Aggregate, is_qualified: bool = False) -> str:
        """Get the SQL of a column or an aggregate which a query reads.

        :param item: the column or the aggregate
        :param is_qualified: whether to qualify the columns with their table
        :returns: the SQL of the item
        """
        if isinstance(item, Aggregate):
            if item.column is None:
                return f"{item.function_name}(*)"

            column = self.get_column_qualifier(item.column, is_qualified)
            return f"{item.function_name}({column})"

        return self.get_column_qualifier(item, is_qualified)

    def get_literal_string(self, val: object) -> str:
        """Get the SQL which stands for a value.

        :param val: the value
        :returns: the value as it is written in a statement
        """
        if val is None:
            return "NULL"

        if isinstance(val, str):
            return "'" + val.replace("'", "''") + "'"

        if isinstance(val, datetime):
            return self.get_literal_string(self._get_datetime_string(val))

        if isinstance(val, date):
            return self.get_literal_string(val.isoformat())

        if isinstance(val, bool):
            return self._get_boolean_string(val)

        if isinstance(val, (bytes, bytearray)):
            return self._get_binary_string(bytes(val))

        if isinstance(val, (int, float)):
            return str(val)

        return self.get_literal_string(str(val))

    def _get_datetime_string(self, val: datetime) -> str:
        return val.isoformat(sep=" ", timespec="seconds")

    def _get_boolean_string(self, val: bool) -> str:
        return "1" if val else "0"

    def _get_binary_string(self, val: bytes) -> str:
        return "X'" + val.hex() + "'"

    def _convert_value(
        self,
        val: object,
        parameters: list[Any] | None,
        is_qualified: bool,
    ) -> str:
        if isinstance(val, Clause):
            return "(" + self.get_clause_string(val, parameters, is_qualified) + ")"

        if isinstance(val, Column):
            return self.get_column_qualifier(val, is_qualified)

        if parameters is None:
            return self.get_literal_string(val)

        parameters.append(val)
        return self.placeholder

    def _get_declaration_string(self, column: Column, type_string: str) -> str:
        return " ".join(
            x
            for x in (
                self.quote_identifier(column.column_name),
                type_string,
                "NOT NULL" if column.is_prevent_null else "",
                self._get_identity_string() if column.is_identity else "",
                f"DEFAULT {column.default_value}" if column.default_value is not None else "",
            )
            if x != ""
        )

    def _get_identity_string(self) -> str:
        return ""

    def _get_primary_key_columns(self, table: Table) -> list[Column]:
        return [col for col in table.columns if col.is_primary_key]

    def _get_table_constraints(self, table: Table) -> list[str]:
        constraints = []

        table_keys = self._get_primary_key_columns(table)

        if table_keys:
            constraints.append(
                "PRIMARY KEY ({})".format(
                    ", ".join(self.quote_identifier(col.column_name) for col in table_keys)
                )
            )

        for foreign_key in table.foreign_keys:
            constraints.append(
                "FOREIGN KEY ({}) REFERENCES {} ({})".format(
                    ", ".join(self.get_column_qualifier(col) for col in foreign_key.columns),
                    self.get_table_qualifier(foreign_key.reference_columns[0].table),
                    ", ".join(
                        self.get_column_qualifier(col) for col in foreign_key.reference_columns
                    ),
                )
            )

        return constraints

    @abstractmethod
    def get_BinaryColumn_declaration(self, column: BinaryColumn) -> str:
        """Get the declaration of a binary column.

        :param column: the column
        :returns: the declaration used when creating the table
        """

    @abstractmethod
    def get_BooleanColumn_declaration(self, column: BooleanColumn) -> str:
        """Get the declaration of a boolean column.

        :param column: the column
        :returns: the declaration used when creating the table
        """

    @abstractmethod
    def get_CharStringColumn_declaration(self, column: CharStringColumn) -> str:
        """Get the declaration of a character string column.

        :param column: the column
        :returns: the declaration used when creating the table
        """

    @abstractmethod
    def get_DateColumn_declaration(self, column: DateColumn) -> str:
        """Get the declaration of a date column.

        :param column: the column
        :returns: the declaration used when creating the table
        """

    @abstractmethod
    def get_DatetimeColumn_declaration(self, column: DatetimeColumn) -> str:
        """Get the declaration of a date and time column.

        :param column: the column
        :returns: the declaration used when creating the table
        """

    @abstractmethod
    def get_DecimalColumn_declaration(self, column: DecimalColumn) -> str:
        """Get the declaration of a decimal column.

        :param column: the column
        :returns: the declaration used when creating the table
        """

    @abstractmethod
    def get_FloatColumn_declaration(self, column: FloatColumn) -> str:
        """Get the declaration of a floating point column.

        :param column: the column
        :returns: the declaration used when creating the table
        """

    @abstractmethod
    def get_IntegerColumn_declaration(self, column: IntegerColumn) -> str:
        """Get the declaration of an integer column.

        :param column: the column
        :returns: the declaration used when creating the table
        """

    @abstractmethod
    def get_TextColumn_declaration(self, column: TextColumn) -> str:
        """Get the declaration of a text column.

        :param column: the column
        :returns: the declaration used when creating the table
        """

    def get_column_declaration(self, column: Column) -> str:
        """Get the declaration of a column of any type.

        :param column: the column
        :returns: the declaration used when creating the table
        """
        declaration: str = getattr(self, f"get_{type(column).__name__}_declaration")(column)
        return declaration

    def get_And_string(
        self,
        clause: And,
        parameters: list[Any] | None = None,
        is_qualified: bool = False,
    ) -> str:
        """Get the SQL of a conjunction of two clauses.

        :param clause: the clause
        :param parameters: the list which receives the values of the clause.
            Without it, the values are written into the SQL.
        :param is_qualified: whether to qualify the columns with their table
        :returns: the SQL of the clause
        """
        return " ".join(
            (
                self._convert_value(clause.clause0, parameters, is_qualified),
                "AND",
                self._convert_value(clause.clause1, parameters, is_qualified),
            )
        )

    def get_Between_string(
        self,
        clause: Between,
        parameters: list[Any] | None = None,
        is_qualified: bool = False,
    ) -> str:
        """Get the SQL of a between clause.

        :param clause: the clause
        :param parameters: the list which receives the values of the clause.
            Without it, the values are written into the SQL.
        :param is_qualified: whether to qualify the columns with their table
        :returns: the SQL of the clause
        """
        return " ".join(
            (
                self._convert_value(clause.column, parameters, is_qualified),
                "BETWEEN",
                self._convert_value(clause.value0, parameters, is_qualified),
                "AND",
                self._convert_value(clause.value1, parameters, is_qualified),
            )
        )

    def get_Equal_string(
        self,
        clause: Equal,
        parameters: list[Any] | None = None,
        is_qualified: bool = False,
    ) -> str:
        """Get the SQL of an equality clause.

        :param clause: the clause
        :param parameters: the list which receives the values of the clause.
            Without it, the values are written into the SQL.
        :param is_qualified: whether to qualify the columns with their table
        :returns: the SQL of the clause
        """
        return " = ".join(
            (
                self._convert_value(clause.lhs, parameters, is_qualified),
                self._convert_value(clause.rhs, parameters, is_qualified),
            )
        )

    def get_GreaterThan_string(
        self,
        clause: GreaterThan,
        parameters: list[Any] | None = None,
        is_qualified: bool = False,
    ) -> str:
        """Get the SQL of a greater than clause.

        :param clause: the clause
        :param parameters: the list which receives the values of the clause.
            Without it, the values are written into the SQL.
        :param is_qualified: whether to qualify the columns with their table
        :returns: the SQL of the clause
        """
        return " > ".join(
            (
                self._convert_value(clause.lhs, parameters, is_qualified),
                self._convert_value(clause.rhs, parameters, is_qualified),
            )
        )

    def get_GreaterThanEqual_string(
        self,
        clause: GreaterThanEqual,
        parameters: list[Any] | None = None,
        is_qualified: bool = False,
    ) -> str:
        """Get the SQL of a greater than or equal clause.

        :param clause: the clause
        :param parameters: the list which receives the values of the clause.
            Without it, the values are written into the SQL.
        :param is_qualified: whether to qualify the columns with their table
        :returns: the SQL of the clause
        """
        return " >= ".join(
            (
                self._convert_value(clause.lhs, parameters, is_qualified),
                self._convert_value(clause.rhs, parameters, is_qualified),
            )
        )

    def get_InList_string(
        self,
        clause: InList,
        parameters: list[Any] | None = None,
        is_qualified: bool = False,
    ) -> str:
        """Get the SQL of an in list clause.

        :param clause: the clause
        :param parameters: the list which receives the values of the clause.
            Without it, the values are written into the SQL.
        :param is_qualified: whether to qualify the columns with their table
        :returns: the SQL of the clause
        """
        return " ".join(
            (
                self._convert_value(clause.column, parameters, is_qualified),
                "IN (",
                ", ".join(
                    [self._convert_value(val, parameters, is_qualified) for val in clause.val_list]
                ),
                ")",
            )
        )

    def get_IsNotNull_string(
        self,
        clause: IsNotNull,
        parameters: list[Any] | None = None,
        is_qualified: bool = False,
    ) -> str:
        """Get the SQL of an is not null clause.

        :param clause: the clause
        :param parameters: the list which receives the values of the clause.
            Without it, the values are written into the SQL.
        :param is_qualified: whether to qualify the columns with their table
        :returns: the SQL of the clause
        """
        return " ".join(
            (
                self._convert_value(clause.column, parameters, is_qualified),
                "IS NOT NULL",
            )
        )

    def get_IsNull_string(
        self,
        clause: IsNull,
        parameters: list[Any] | None = None,
        is_qualified: bool = False,
    ) -> str:
        """Get the SQL of an is null clause.

        :param clause: the clause
        :param parameters: the list which receives the values of the clause.
            Without it, the values are written into the SQL.
        :param is_qualified: whether to qualify the columns with their table
        :returns: the SQL of the clause
        """
        return " ".join(
            (
                self._convert_value(clause.column, parameters, is_qualified),
                "IS NULL",
            )
        )

    def get_LessThan_string(
        self,
        clause: LessThan,
        parameters: list[Any] | None = None,
        is_qualified: bool = False,
    ) -> str:
        """Get the SQL of a less than clause.

        :param clause: the clause
        :param parameters: the list which receives the values of the clause.
            Without it, the values are written into the SQL.
        :param is_qualified: whether to qualify the columns with their table
        :returns: the SQL of the clause
        """
        return " < ".join(
            (
                self._convert_value(clause.lhs, parameters, is_qualified),
                self._convert_value(clause.rhs, parameters, is_qualified),
            )
        )

    def get_LessThanEqual_string(
        self,
        clause: LessThanEqual,
        parameters: list[Any] | None = None,
        is_qualified: bool = False,
    ) -> str:
        """Get the SQL of a less than or equal clause.

        :param clause: the clause
        :param parameters: the list which receives the values of the clause.
            Without it, the values are written into the SQL.
        :param is_qualified: whether to qualify the columns with their table
        :returns: the SQL of the clause
        """
        return " <= ".join(
            (
                self._convert_value(clause.lhs, parameters, is_qualified),
                self._convert_value(clause.rhs, parameters, is_qualified),
            )
        )

    def get_Like_string(
        self,
        clause: Like,
        parameters: list[Any] | None = None,
        is_qualified: bool = False,
    ) -> str:
        """Get the SQL of a like clause.

        :param clause: the clause
        :param parameters: the list which receives the values of the clause.
            Without it, the values are written into the SQL.
        :param is_qualified: whether to qualify the columns with their table
        :returns: the SQL of the clause
        """
        return " ".join(
            (
                self._convert_value(clause.column, parameters, is_qualified),
                "LIKE",
                self._convert_value(clause.value, parameters, is_qualified),
            )
        )

    def get_NotBetween_string(
        self,
        clause: NotBetween,
        parameters: list[Any] | None = None,
        is_qualified: bool = False,
    ) -> str:
        """Get the SQL of a not between clause.

        :param clause: the clause
        :param parameters: the list which receives the values of the clause.
            Without it, the values are written into the SQL.
        :param is_qualified: whether to qualify the columns with their table
        :returns: the SQL of the clause
        """
        return " ".join(
            (
                self._convert_value(clause.column, parameters, is_qualified),
                "NOT BETWEEN",
                self._convert_value(clause.value0, parameters, is_qualified),
                "AND",
                self._convert_value(clause.value1, parameters, is_qualified),
            )
        )

    def get_NotEqual_string(
        self,
        clause: NotEqual,
        parameters: list[Any] | None = None,
        is_qualified: bool = False,
    ) -> str:
        """Get the SQL of an inequality clause.

        :param clause: the clause
        :param parameters: the list which receives the values of the clause.
            Without it, the values are written into the SQL.
        :param is_qualified: whether to qualify the columns with their table
        :returns: the SQL of the clause
        """
        return " != ".join(
            (
                self._convert_value(clause.lhs, parameters, is_qualified),
                self._convert_value(clause.rhs, parameters, is_qualified),
            )
        )

    def get_NotInList_string(
        self,
        clause: NotInList,
        parameters: list[Any] | None = None,
        is_qualified: bool = False,
    ) -> str:
        """Get the SQL of a not in list clause.

        :param clause: the clause
        :param parameters: the list which receives the values of the clause.
            Without it, the values are written into the SQL.
        :param is_qualified: whether to qualify the columns with their table
        :returns: the SQL of the clause
        """
        return " ".join(
            (
                self._convert_value(clause.column, parameters, is_qualified),
                "NOT IN (",
                ", ".join(
                    [self._convert_value(val, parameters, is_qualified) for val in clause.val_list]
                ),
                ")",
            )
        )

    def get_NotLike_string(
        self,
        clause: NotLike,
        parameters: list[Any] | None = None,
        is_qualified: bool = False,
    ) -> str:
        """Get the SQL of a not like clause.

        :param clause: the clause
        :param parameters: the list which receives the values of the clause.
            Without it, the values are written into the SQL.
        :param is_qualified: whether to qualify the columns with their table
        :returns: the SQL of the clause
        """
        return " ".join(
            (
                self._convert_value(clause.column, parameters, is_qualified),
                "NOT LIKE",
                self._convert_value(clause.value, parameters, is_qualified),
            )
        )

    def get_Or_string(
        self,
        clause: Or,
        parameters: list[Any] | None = None,
        is_qualified: bool = False,
    ) -> str:
        """Get the SQL of a disjunction of two clauses.

        :param clause: the clause
        :param parameters: the list which receives the values of the clause.
            Without it, the values are written into the SQL.
        :param is_qualified: whether to qualify the columns with their table
        :returns: the SQL of the clause
        """
        return " ".join(
            (
                self._convert_value(clause.clause0, parameters, is_qualified),
                "OR",
                self._convert_value(clause.clause1, parameters, is_qualified),
            )
        )

    def get_clause_string(
        self,
        clause: Clause,
        parameters: list[Any] | None = None,
        is_qualified: bool = False,
    ) -> str:
        """Get the SQL of a clause of any type.

        :param clause: the clause
        :param parameters: the list which receives the values of the clause.
            Without it, the values are written into the SQL.
        :param is_qualified: whether to qualify the columns with their table
        :returns: the SQL of the clause
        """
        clause_string: str = getattr(self, f"get_{type(clause).__name__}_string")(
            clause, parameters, is_qualified
        )
        return clause_string

    def get_Create_database_string(self, query: Create, parameters: list[Any] | None = None) -> str:
        """Get the SQL which creates a database.

        :param query: the query
        :param parameters: the list which receives the values of the
            conditions. Without it, the values are written into the SQL.
        :returns: the SQL statement
        """
        database = cast(Database, query.structure)

        return f"CREATE DATABASE {self.quote_identifier(database.database_name)}"

    def get_Create_schema_string(self, query: Create, parameters: list[Any] | None = None) -> str:
        """Get the SQL which creates a schema.

        :param query: the query
        :param parameters: the list which receives the values of the
            conditions. Without it, the values are written into the SQL.
        :returns: the SQL statement
        """
        schema = cast(Schema, query.structure)

        sql_string = f"CREATE SCHEMA {self.quote_identifier(schema.schema_name)}"

        if not schema.owner_name:
            return sql_string

        return f"{sql_string} AUTHORIZATION {self.quote_identifier(schema.owner_name)}"

    def get_Create_table_string(self, query: Create, parameters: list[Any] | None = None) -> str:
        """Get the SQL which creates a table.

        :param query: the query
        :param parameters: the list which receives the values of the
            conditions. Without it, the values are written into the SQL.
        :returns: the SQL statement
        :raises InvalidArgumentError: if the table has no columns
        """
        table = cast(Table, query.structure)

        if not table.columns:
            raise InvalidArgumentError("table has no columns")

        table_cols = [self.get_column_declaration(col) for col in table.columns]
        table_cols += self._get_table_constraints(table)

        return "CREATE TABLE {} (\n{}\n)".format(
            self.get_table_qualifier(table),
            ",\n".join(table_cols),
        )

    def get_Create_index_string(self, query: Create, parameters: list[Any] | None = None) -> str:
        """Get the SQL which creates an index.

        :param query: the query
        :param parameters: the list which receives the values of the
            conditions. Without it, the values are written into the SQL.
        :returns: the SQL statement
        """
        index = cast(Index, query.structure)

        return "CREATE {}INDEX {} ON {} ({})".format(
            "UNIQUE " if index.is_unique else "",
            self.quote_identifier(index.index_name),
            self.get_table_qualifier(index.table),
            ", ".join(self.get_column_qualifier(col) for col in index.columns),
        )

    def get_Delete_table_string(self, query: Delete, parameters: list[Any] | None = None) -> str:
        """Get the SQL which removes rows of a table.

        :param query: the query
        :param parameters: the list which receives the values of the
            conditions. Without it, the values are written into the SQL.
        :returns: the SQL statement
        """
        return " ".join(
            (
                "DELETE FROM",
                self.get_table_qualifier(query.structure),
                "WHERE",
                self.get_clause_string(query.condition, parameters),
            )
        )

    def get_Drop_database_string(self, query: Drop, parameters: list[Any] | None = None) -> str:
        """Get the SQL which drops a database.

        :param query: the query
        :param parameters: the list which receives the values of the
            conditions. Without it, the values are written into the SQL.
        :returns: the SQL statement
        """
        database = cast(Database, query.structure)

        return f"DROP DATABASE {self.quote_identifier(database.database_name)}"

    def get_Drop_schema_string(self, query: Drop, parameters: list[Any] | None = None) -> str:
        """Get the SQL which drops a schema.

        :param query: the query
        :param parameters: the list which receives the values of the
            conditions. Without it, the values are written into the SQL.
        :returns: the SQL statement
        """
        schema = cast(Schema, query.structure)

        return f"DROP SCHEMA {self.quote_identifier(schema.schema_name)}"

    def get_Drop_table_string(self, query: Drop, parameters: list[Any] | None = None) -> str:
        """Get the SQL which drops a table.

        :param query: the query
        :param parameters: the list which receives the values of the
            conditions. Without it, the values are written into the SQL.
        :returns: the SQL statement
        """
        table = cast(Table, query.structure)

        return f"DROP TABLE {self.get_table_qualifier(table)}"

    def get_Drop_index_string(self, query: Drop, parameters: list[Any] | None = None) -> str:
        """Get the SQL which drops an index.

        :param query: the query
        :param parameters: the list which receives the values of the
            conditions. Without it, the values are written into the SQL.
        :returns: the SQL statement
        """
        index = cast(Index, query.structure)

        return f"DROP INDEX {self.quote_identifier(index.index_name)}"

    def get_GetLength_table_string(
        self, query: GetLength, parameters: list[Any] | None = None
    ) -> str:
        """Get the SQL which counts the rows of a table.

        :param query: the query
        :param parameters: the list which receives the values of the
            conditions. Without it, the values are written into the SQL.
        :returns: the SQL statement
        """
        return f"SELECT COUNT(*) FROM {self.get_table_qualifier(query.structure)}"

    def get_Insert_table_string(self, query: Insert, parameters: list[Any] | None = None) -> str:
        """Get the SQL which adds a row to a table.

        :param query: the query
        :param parameters: the list which receives the values of the
            conditions. Without it, the values are written into the SQL.
        :returns: the SQL statement
        """
        col_names = tuple(self.get_column_qualifier(col) for col in query.columns)

        return "INSERT INTO {} ({}) VALUES ({})".format(
            self.get_table_qualifier(query.structure),
            ",\n".join(col_names),
            ", ".join([self.placeholder] * len(col_names)),
        )

    def get_IsEmpty_table_string(self, query: IsEmpty, parameters: list[Any] | None = None) -> str:
        """Get the SQL which checks whether a table has no rows.

        :param query: the query
        :param parameters: the list which receives the values of the
            conditions. Without it, the values are written into the SQL.
        :returns: the SQL statement
        """
        return f"SELECT COUNT(*) FROM {self.get_table_qualifier(query.structure)}"

    @abstractmethod
    def get_IsExists_database_string(
        self, query: IsExists, parameters: list[Any] | None = None
    ) -> str:
        """Get the SQL which gives 1 when a database exists and 0 otherwise.

        :param query: the query
        :param parameters: the list which receives the values of the
            conditions. Without it, the values are written into the SQL.
        :returns: the SQL statement
        """

    @abstractmethod
    def get_IsExists_schema_string(
        self, query: IsExists, parameters: list[Any] | None = None
    ) -> str:
        """Get the SQL which gives 1 when a schema exists and 0 otherwise.

        :param query: the query
        :param parameters: the list which receives the values of the
            conditions. Without it, the values are written into the SQL.
        :returns: the SQL statement
        """

    @abstractmethod
    def get_IsExists_table_string(
        self, query: IsExists, parameters: list[Any] | None = None
    ) -> str:
        """Get the SQL which gives 1 when a table exists and 0 otherwise.

        :param query: the query
        :param parameters: the list which receives the values of the
            conditions. Without it, the values are written into the SQL.
        :returns: the SQL statement
        """

    @abstractmethod
    def get_IsExists_index_string(
        self, query: IsExists, parameters: list[Any] | None = None
    ) -> str:
        """Get the SQL which gives 1 when an index exists and 0 otherwise.

        :param query: the query
        :param parameters: the list which receives the values of the
            conditions. Without it, the values are written into the SQL.
        :returns: the SQL statement
        """

    @abstractmethod
    def get_Reflect_table_string(self, query: Reflect, parameters: list[Any] | None = None) -> str:
        """Get the SQL which reads the columns of a table.

        :param query: the query
        :param parameters: unused, as the query has no condition
        :returns: the SQL statement, whose rows :py:meth:`get_reflected_table`
            understands
        """

    def _get_information_schema_string(
        self,
        table: Table,
        schema_string: str,
        identity_string: str,
        type_string: str = "NULL",
    ) -> str:
        """Get the SQL which reads the columns of a table from the information schema."""
        return f"""SELECT c.column_name, c.data_type, c.character_maximum_length,
c.numeric_precision, c.numeric_scale, c.is_nullable, c.column_default,
(SELECT COUNT(*) FROM information_schema.table_constraints tc
JOIN information_schema.key_column_usage k ON k.constraint_name = tc.constraint_name
AND k.table_schema = tc.table_schema AND k.table_name = tc.table_name
WHERE tc.constraint_type = 'PRIMARY KEY' AND k.table_schema = c.table_schema
AND k.table_name = c.table_name AND k.column_name = c.column_name),
{identity_string}, {type_string}
FROM information_schema.columns c
WHERE c.table_name = {self.get_literal_string(table.table_name)}
AND c.table_schema = {schema_string}
ORDER BY c.ordinal_position"""

    def _get_reflected_type(
        self,
        data_type: str,
        size: int | None,
        precision: int | None,
        column_type: str | None,
    ) -> dict[str, Any]:
        """Get the kind of a column and its specific arguments from its type."""
        raise UnsupportedOperationError(f'unknown column type "{data_type}"')

    def get_reflected_table(self, query: Reflect, rows: Sequence[Sequence[Any]]) -> Table:
        """Create a table from the rows of a reflect query.

        :param query: the query
        :param rows: the rows which the database gave for the query
        :returns: a new table with the columns found in the database
        :raises InvalidArgumentError: if the table does not exist
        :raises UnsupportedOperationError: if a column has a type which the
            package does not know
        """
        table = self._get_empty_table(query, rows)

        for (
            column_name,
            data_type,
            size,
            precision,
            scale,
            is_nullable,
            default_value,
            key_count,
            is_identity,
            column_type,
        ) in rows:
            arguments = self._get_reflected_type(
                str(data_type).lower(),
                size,
                precision,
                None if column_type is None else str(column_type).lower(),
            )

            self._append_reflected_column(
                table,
                column_name=column_name,
                scale=scale,
                default_value=default_value,
                is_identity=bool(is_identity),
                is_primary_key=bool(key_count),
                is_prevent_null=str(is_nullable).upper() == "NO",
                **arguments,
            )

        return table

    def _get_empty_table(self, query: Reflect, rows: Sequence[Sequence[Any]]) -> Table:
        source = query.structure

        if not rows:
            raise InvalidArgumentError(f'table "{source.table_name}" does not exist')

        return Table(table_name=source.table_name, database=source.database, schema=source.schema)

    def _append_reflected_column(
        self,
        table: Table,
        column_name: str,
        kind: str,
        default_value: Any,
        is_identity: bool,
        is_primary_key: bool,
        is_prevent_null: bool,
        size: int | None = None,
        precision: int | None = None,
        scale: int | None = None,
        is_unicode: bool = False,
        is_fixed: bool = False,
        is_double: bool = True,
        n_bytes: int = 4,
    ) -> None:
        """Add a column read from the database to a table."""
        common: dict[str, Any] = {
            "column_name": column_name,
            # Identity and key columns have no default value of their own.
            "default_value": None if (is_identity or is_primary_key) else default_value,
            "is_primary_key": is_primary_key,
            "is_prevent_null": is_prevent_null,
        }

        if kind == "char":
            table.append_char_string_column(
                is_unicode=is_unicode, is_fixed=is_fixed, size=size or 255, **common
            )
        elif kind == "text":
            table.append_text_column(is_unicode=is_unicode, **common)
        elif kind == "integer":
            table.append_integer_column(n_bytes=n_bytes, is_identity=is_identity, **common)
        elif kind == "float":
            table.append_float_column(is_double=is_double, **common)
        elif kind == "datetime":
            table.append_datetime_column(**common)
        elif kind == "date":
            table.append_date_column(**common)
        elif kind == "boolean":
            table.append_boolean_column(**common)
        elif kind == "decimal":
            table.append_decimal_column(precision=precision or 18, scale=scale or 0, **common)
        elif kind == "binary":
            table.append_binary_column(**common)
        else:
            raise UnsupportedOperationError(f'unknown column kind "{kind}"')

    def _parse_type(self, type_string: str) -> tuple[str, list[int]]:
        """Split a type such as ``decimal(10, 2)`` into its name and its numbers."""
        match = re.fullmatch(r"\s*([^()]*?)\s*(?:\(([^()]*)\))?\s*", type_string)

        if match is None:
            return type_string.lower(), []

        numbers = [int(x) for x in (match.group(2) or "").split(",") if x.strip().isdigit()]

        return match.group(1).lower(), numbers

    def _get_limit_strings(
        self,
        top: int | None,
        offset: int | None,
        is_ordered: bool,
    ) -> tuple[str, str]:
        """Get what limits the rows, before the columns and at the end."""
        limit_ar = []

        if top is not None:
            limit_ar.append(f"LIMIT {top}")
        elif offset is not None:
            limit_ar.append(self._get_no_limit_string())

        if offset is not None:
            limit_ar.append(f"OFFSET {offset}")

        return "", " ".join(x for x in limit_ar if x != "")

    def _get_no_limit_string(self) -> str:
        return ""

    def _get_order_by_strings(
        self,
        ascend_by: Sequence[Column] | None,
        descend_by: Sequence[Column] | None,
        is_qualified: bool,
    ) -> list[str]:
        order_ar = []

        if ascend_by:
            order_ar += [self.get_column_qualifier(col, is_qualified) + " ASC" for col in ascend_by]

        if descend_by:
            order_ar += [
                self.get_column_qualifier(col, is_qualified) + " DESC" for col in descend_by
            ]

        return order_ar

    def get_Select_table_string(self, query: Select, parameters: list[Any] | None = None) -> str:
        """Get the SQL which reads rows of a table.

        :param query: the query
        :param parameters: the list which receives the values of the
            conditions. Without it, the values are written into the SQL.
        :returns: the SQL statement
        """
        is_qualified = bool(query.joins)
        order_ar = self._get_order_by_strings(query.ascend_by, query.descend_by, is_qualified)
        limit_prefix, limit_suffix = self._get_limit_strings(
            query.top, query.offset, bool(order_ar)
        )

        sql_ar = [
            "SELECT",
            limit_prefix,
            ",\n".join(self.get_select_item_string(item, is_qualified) for item in query.columns),
            "FROM",
            self.get_table_qualifier(query.structure),
        ]

        for join in query.joins or ():
            sql_ar += [
                f"{join.kind.upper()} JOIN",
                self.get_table_qualifier(join.table),
                "ON",
                self.get_clause_string(join.condition, parameters, is_qualified),
            ]

        if query.condition:
            sql_ar += [
                "WHERE",
                self.get_clause_string(query.condition, parameters, is_qualified),
            ]

        if query.group_by:
            sql_ar += [
                "GROUP BY",
                ", ".join(self.get_column_qualifier(col, is_qualified) for col in query.group_by),
            ]

        if order_ar:
            sql_ar += [
                "ORDER BY",
                ",\n".join(order_ar),
            ]

        sql_ar.append(limit_suffix)

        return " ".join(x for x in sql_ar if x != "")

    def get_SelectDistinct_table_string(
        self, query: SelectDistinct, parameters: list[Any] | None = None
    ) -> str:
        """Get the SQL which reads distinct values of columns of a table.

        :param query: the query
        :param parameters: the list which receives the values of the
            conditions. Without it, the values are written into the SQL.
        :returns: the SQL statement
        """
        sql_ar = [
            "SELECT DISTINCT",
            ", ".join(self.get_column_qualifier(col) for col in query.columns),
            "FROM",
            self.get_table_qualifier(query.structure),
        ]

        if query.condition:
            sql_ar += [
                "WHERE",
                self.get_clause_string(query.condition, parameters),
            ]

        order_ar = self._get_order_by_strings(query.ascend_by, query.descend_by, False)

        if order_ar:
            sql_ar += [
                "ORDER BY",
                ", ".join(order_ar),
            ]

        return " ".join(sql_ar)

    def get_Truncate_table_string(
        self, query: Truncate, parameters: list[Any] | None = None
    ) -> str:
        """Get the SQL which removes all rows of a table.

        :param query: the query
        :param parameters: the list which receives the values of the
            conditions. Without it, the values are written into the SQL.
        :returns: the SQL statement
        """
        return f"TRUNCATE TABLE {self.get_table_qualifier(query.structure)}"

    def get_Union_table_string(self, query: Union, parameters: list[Any] | None = None) -> str:
        """Get the SQL which combines the rows of several select queries.

        :param query: the query
        :param parameters: the list which receives the values of the
            conditions. Without it, the values are written into the SQL.
        :returns: the SQL statement
        """
        union_str = ("\nUNION{}\n".format(" ALL" if query.is_all else "")).join(
            [
                " ".join(
                    [
                        "SELECT",
                        ",\n".join(self.get_column_qualifier(col) for col in columns),
                        "FROM",
                        "(\n" + self.get_query_string(select, parameters) + "\n)",
                        self.quote_identifier(table.table_name),
                    ]
                )
                for columns, select, table in zip(
                    query.columns_list, query.query_list, query.structure_list, strict=True
                )
            ]
        ) + "\n"

        if query.condition:
            union_str += "WHERE\n" + self.get_clause_string(query.condition, parameters)

        order_ar = self._get_order_by_strings(query.ascend_by, query.descend_by, False)

        if order_ar:
            union_str += "ORDER BY\n" + ",\n".join(order_ar)

        return union_str

    def get_Update_table_string(self, query: Update, parameters: list[Any] | None = None) -> str:
        """Get the SQL which changes rows of a table.

        :param query: the query
        :param parameters: the list which receives the values of the
            conditions. Without it, the values are written into the SQL.
        :returns: the SQL statement
        """
        col_names = tuple(self.get_column_qualifier(col) for col in query.columns)

        return "UPDATE {}\nSET {}\nWHERE {}".format(
            self.get_table_qualifier(query.structure),
            ", ".join(col + "=" + self.placeholder for col in col_names),
            self.get_clause_string(query.condition, parameters),
        )

    def get_Create_string(self, query: Create, parameters: list[Any] | None = None) -> str:
        """Get the SQL of a create query.

        :param query: the query
        :param parameters: the list which receives the values of the
            conditions. Without it, the values are written into the SQL.
        :returns: the SQL statement
        :raises UnsupportedOperationError: if the dialect does not support
            the query for its kind of structure
        """
        return self._get_structure_string(
            "Create", query.structure.structure_name, query, parameters
        )

    def get_Delete_string(self, query: Delete, parameters: list[Any] | None = None) -> str:
        """Get the SQL of a delete query.

        :param query: the query
        :param parameters: the list which receives the values of the
            conditions. Without it, the values are written into the SQL.
        :returns: the SQL statement
        :raises UnsupportedOperationError: if the dialect does not support
            the query for its kind of structure
        """
        return self._get_structure_string(
            "Delete", query.structure.structure_name, query, parameters
        )

    def get_Drop_string(self, query: Drop, parameters: list[Any] | None = None) -> str:
        """Get the SQL of a drop query.

        :param query: the query
        :param parameters: the list which receives the values of the
            conditions. Without it, the values are written into the SQL.
        :returns: the SQL statement
        :raises UnsupportedOperationError: if the dialect does not support
            the query for its kind of structure
        """
        return self._get_structure_string("Drop", query.structure.structure_name, query, parameters)

    def get_GetLength_string(self, query: GetLength, parameters: list[Any] | None = None) -> str:
        """Get the SQL of a row count query.

        :param query: the query
        :param parameters: the list which receives the values of the
            conditions. Without it, the values are written into the SQL.
        :returns: the SQL statement
        :raises UnsupportedOperationError: if the dialect does not support
            the query for its kind of structure
        """
        return self._get_structure_string(
            "GetLength", query.structure.structure_name, query, parameters
        )

    def get_Insert_string(self, query: Insert, parameters: list[Any] | None = None) -> str:
        """Get the SQL of an insert query.

        :param query: the query
        :param parameters: the list which receives the values of the
            conditions. Without it, the values are written into the SQL.
        :returns: the SQL statement
        :raises UnsupportedOperationError: if the dialect does not support
            the query for its kind of structure
        """
        return self._get_structure_string(
            "Insert", query.structure.structure_name, query, parameters
        )

    def get_IsEmpty_string(self, query: IsEmpty, parameters: list[Any] | None = None) -> str:
        """Get the SQL of an emptiness query.

        :param query: the query
        :param parameters: the list which receives the values of the
            conditions. Without it, the values are written into the SQL.
        :returns: the SQL statement
        :raises UnsupportedOperationError: if the dialect does not support
            the query for its kind of structure
        """
        return self._get_structure_string(
            "IsEmpty", query.structure.structure_name, query, parameters
        )

    def get_IsExists_string(self, query: IsExists, parameters: list[Any] | None = None) -> str:
        """Get the SQL of an existence query.

        :param query: the query
        :param parameters: the list which receives the values of the
            conditions. Without it, the values are written into the SQL.
        :returns: the SQL statement
        :raises UnsupportedOperationError: if the dialect does not support
            the query for its kind of structure
        """
        return self._get_structure_string(
            "IsExists", query.structure.structure_name, query, parameters
        )

    def get_Reflect_string(self, query: Reflect, parameters: list[Any] | None = None) -> str:
        """Get the SQL of a reflect query.

        :param query: the query
        :param parameters: unused, as the query has no condition
        :returns: the SQL statement
        """
        return self._get_structure_string(
            "Reflect", query.structure.structure_name, query, parameters
        )

    def get_Select_string(self, query: Select, parameters: list[Any] | None = None) -> str:
        """Get the SQL of a select query.

        :param query: the query
        :param parameters: the list which receives the values of the
            conditions. Without it, the values are written into the SQL.
        :returns: the SQL statement
        :raises UnsupportedOperationError: if the dialect does not support
            the query for its kind of structure
        """
        return self._get_structure_string(
            "Select", query.structure.structure_name, query, parameters
        )

    def get_SelectDistinct_string(
        self, query: SelectDistinct, parameters: list[Any] | None = None
    ) -> str:
        """Get the SQL of a select distinct query.

        :param query: the query
        :param parameters: the list which receives the values of the
            conditions. Without it, the values are written into the SQL.
        :returns: the SQL statement
        :raises UnsupportedOperationError: if the dialect does not support
            the query for its kind of structure
        """
        return self._get_structure_string(
            "SelectDistinct", query.structure.structure_name, query, parameters
        )

    def get_Truncate_string(self, query: Truncate, parameters: list[Any] | None = None) -> str:
        """Get the SQL of a truncate query.

        :param query: the query
        :param parameters: the list which receives the values of the
            conditions. Without it, the values are written into the SQL.
        :returns: the SQL statement
        :raises UnsupportedOperationError: if the dialect does not support
            the query for its kind of structure
        """
        return self._get_structure_string(
            "Truncate", query.structure.structure_name, query, parameters
        )

    def get_Update_string(self, query: Update, parameters: list[Any] | None = None) -> str:
        """Get the SQL of an update query.

        :param query: the query
        :param parameters: the list which receives the values of the
            conditions. Without it, the values are written into the SQL.
        :returns: the SQL statement
        :raises UnsupportedOperationError: if the dialect does not support
            the query for its kind of structure
        """
        return self._get_structure_string(
            "Update", query.structure.structure_name, query, parameters
        )

    def get_Union_string(self, query: Union, parameters: list[Any] | None = None) -> str:
        """Get the SQL of a union query.

        :param query: the query
        :param parameters: the list which receives the values of the
            conditions. Without it, the values are written into the SQL.
        :returns: the SQL statement
        :raises UnsupportedOperationError: if the dialect does not support
            the query for its kind of structure
        """
        return self._get_structure_string(
            "Union", query.structure_list[0].structure_name, query, parameters
        )

    def get_query_string(self, query: Query, parameters: list[Any] | None = None) -> str:
        """Get the SQL of a query of any type.

        :param query: the query
        :param parameters: the list which receives the values of the
            conditions. Without it, the values are written into the SQL.
        :returns: the SQL statement
        :raises UnsupportedOperationError: if the dialect does not support
            the query for its kind of structure
        """
        query_string: str = getattr(self, f"get_{type(query).__name__}_string")(query, parameters)
        return query_string

    def _get_structure_string(
        self,
        query_name: str,
        structure_name: str,
        query: Query,
        parameters: list[Any] | None,
    ) -> str:
        """Call the method for a type of query and a kind of structure."""
        method = getattr(self, f"get_{query_name}_{structure_name}_string", None)

        if method is None:
            raise UnsupportedOperationError(
                f"{query_name} query does not support a {structure_name}"
            )

        structure_string: str = method(query, parameters)
        return structure_string
