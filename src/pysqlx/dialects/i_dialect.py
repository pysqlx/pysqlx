"""Interface of the SQL dialects."""

from abc import ABC, abstractmethod

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
from ..structures import (
    CharStringColumn,
    Clause,
    Column,
    DatetimeColumn,
    FloatColumn,
    IntegerColumn,
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

    A dialect turns columns, clauses and queries into SQL strings. The
    methods :py:meth:`get_column_declaration`, :py:meth:`get_clause_string`
    and :py:meth:`get_query_string` select the method to call from the name
    of the class of their argument, and, for the queries, from the kind of
    structure which the query acts on.

    :param dialect_name: the name of the dialect
    """

    def __init__(self, dialect_name: str) -> None:
        self.__dialect_name = dialect_name

    @property
    def dialect_name(self) -> str:
        """Name of the dialect."""
        return self.__dialect_name

    @abstractmethod
    def get_table_qualifier(self, table: Table) -> str:
        """Get the name which refers to a table in a statement.

        :param table: the table
        :returns: the qualified name of the table
        """

    @abstractmethod
    def get_column_qualifier(self, column: Column) -> str:
        """Get the name which refers to a column in a statement.

        :param column: the column
        :returns: the quoted name of the column
        """

    @abstractmethod
    def get_CharStringColumn_declaration(self, column: CharStringColumn) -> str:
        """Get the declaration of a character string column.

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

    @abstractmethod
    def get_And_string(self, clause: And) -> str:
        """Get the SQL of a conjunction of two clauses.

        :param clause: the clause
        :returns: the SQL of the clause
        """

    @abstractmethod
    def get_Between_string(self, clause: Between) -> str:
        """Get the SQL of a between clause.

        :param clause: the clause
        :returns: the SQL of the clause
        """

    @abstractmethod
    def get_Equal_string(self, clause: Equal) -> str:
        """Get the SQL of an equality clause.

        :param clause: the clause
        :returns: the SQL of the clause
        """

    @abstractmethod
    def get_GreaterThan_string(self, clause: GreaterThan) -> str:
        """Get the SQL of a greater than clause.

        :param clause: the clause
        :returns: the SQL of the clause
        """

    @abstractmethod
    def get_GreaterThanEqual_string(self, clause: GreaterThanEqual) -> str:
        """Get the SQL of a greater than or equal clause.

        :param clause: the clause
        :returns: the SQL of the clause
        """

    @abstractmethod
    def get_InList_string(self, clause: InList) -> str:
        """Get the SQL of an in list clause.

        :param clause: the clause
        :returns: the SQL of the clause
        """

    @abstractmethod
    def get_IsNotNull_string(self, clause: IsNotNull) -> str:
        """Get the SQL of an is not null clause.

        :param clause: the clause
        :returns: the SQL of the clause
        """

    @abstractmethod
    def get_IsNull_string(self, clause: IsNull) -> str:
        """Get the SQL of an is null clause.

        :param clause: the clause
        :returns: the SQL of the clause
        """

    @abstractmethod
    def get_LessThan_string(self, clause: LessThan) -> str:
        """Get the SQL of a less than clause.

        :param clause: the clause
        :returns: the SQL of the clause
        """

    @abstractmethod
    def get_LessThanEqual_string(self, clause: LessThanEqual) -> str:
        """Get the SQL of a less than or equal clause.

        :param clause: the clause
        :returns: the SQL of the clause
        """

    @abstractmethod
    def get_Like_string(self, clause: Like) -> str:
        """Get the SQL of a like clause.

        :param clause: the clause
        :returns: the SQL of the clause
        """

    @abstractmethod
    def get_NotBetween_string(self, clause: NotBetween) -> str:
        """Get the SQL of a not between clause.

        :param clause: the clause
        :returns: the SQL of the clause
        """

    @abstractmethod
    def get_NotEqual_string(self, clause: NotEqual) -> str:
        """Get the SQL of an inequality clause.

        :param clause: the clause
        :returns: the SQL of the clause
        """

    @abstractmethod
    def get_NotInList_string(self, clause: NotInList) -> str:
        """Get the SQL of a not in list clause.

        :param clause: the clause
        :returns: the SQL of the clause
        """

    @abstractmethod
    def get_NotLike_string(self, clause: NotLike) -> str:
        """Get the SQL of a not like clause.

        :param clause: the clause
        :returns: the SQL of the clause
        """

    @abstractmethod
    def get_Or_string(self, clause: Or) -> str:
        """Get the SQL of a disjunction of two clauses.

        :param clause: the clause
        :returns: the SQL of the clause
        """

    def get_clause_string(self, clause: Clause) -> str:
        """Get the SQL of a clause of any type.

        :param clause: the clause
        :returns: the SQL of the clause
        """
        clause_string: str = getattr(self, f"get_{type(clause).__name__}_string")(clause)
        return clause_string

    @abstractmethod
    def get_Create_database_string(self, query: Create) -> str:
        """Get the SQL which creates a database.

        :param query: the query
        :returns: the SQL statement
        """

    @abstractmethod
    def get_Create_schema_string(self, query: Create) -> str:
        """Get the SQL which creates a schema.

        :param query: the query
        :returns: the SQL statement
        """

    @abstractmethod
    def get_Create_table_string(self, query: Create) -> str:
        """Get the SQL which creates a table.

        :param query: the query
        :returns: the SQL statement
        :raises RuntimeError: if the table has no columns
        """

    def get_Create_string(self, query: Create) -> str:
        """Get the SQL of a create query.

        :param query: the query
        :returns: the SQL statement
        """
        return self._get_structure_string("Create", query.structure.structure_name, query)

    @abstractmethod
    def get_Delete_table_string(self, query: Delete) -> str:
        """Get the SQL which removes rows of a table.

        :param query: the query
        :returns: the SQL statement
        """

    def get_Delete_string(self, query: Delete) -> str:
        """Get the SQL of a delete query.

        :param query: the query
        :returns: the SQL statement
        """
        return self._get_structure_string("Delete", query.structure.structure_name, query)

    @abstractmethod
    def get_Drop_database_string(self, query: Drop) -> str:
        """Get the SQL which drops a database.

        :param query: the query
        :returns: the SQL statement
        """

    @abstractmethod
    def get_Drop_schema_string(self, query: Drop) -> str:
        """Get the SQL which drops a schema.

        :param query: the query
        :returns: the SQL statement
        """

    @abstractmethod
    def get_Drop_table_string(self, query: Drop) -> str:
        """Get the SQL which drops a table.

        :param query: the query
        :returns: the SQL statement
        """

    def get_Drop_string(self, query: Drop) -> str:
        """Get the SQL of a drop query.

        :param query: the query
        :returns: the SQL statement
        """
        return self._get_structure_string("Drop", query.structure.structure_name, query)

    @abstractmethod
    def get_GetLength_table_string(self, query: GetLength) -> str:
        """Get the SQL which counts the rows of a table.

        :param query: the query
        :returns: the SQL statement
        """

    def get_GetLength_string(self, query: GetLength) -> str:
        """Get the SQL of a row count query.

        :param query: the query
        :returns: the SQL statement
        """
        return self._get_structure_string("GetLength", query.structure.structure_name, query)

    @abstractmethod
    def get_Insert_table_string(self, query: Insert) -> str:
        """Get the SQL which adds a row to a table.

        :param query: the query
        :returns: the SQL statement, with one placeholder per column
        """

    def get_Insert_string(self, query: Insert) -> str:
        """Get the SQL of an insert query.

        :param query: the query
        :returns: the SQL statement
        """
        return self._get_structure_string("Insert", query.structure.structure_name, query)

    @abstractmethod
    def get_IsEmpty_table_string(self, query: IsEmpty) -> str:
        """Get the SQL which checks whether a table has no rows.

        :param query: the query
        :returns: the SQL statement
        """

    def get_IsEmpty_string(self, query: IsEmpty) -> str:
        """Get the SQL of an emptiness query.

        :param query: the query
        :returns: the SQL statement
        """
        return self._get_structure_string("IsEmpty", query.structure.structure_name, query)

    @abstractmethod
    def get_IsExists_database_string(self, query: IsExists) -> str:
        """Get the SQL which checks whether a database exists.

        :param query: the query
        :returns: the SQL statement
        """

    @abstractmethod
    def get_IsExists_schema_string(self, query: IsExists) -> str:
        """Get the SQL which checks whether a schema exists.

        :param query: the query
        :returns: the SQL statement
        """

    @abstractmethod
    def get_IsExists_table_string(self, query: IsExists) -> str:
        """Get the SQL which checks whether a table exists.

        :param query: the query
        :returns: the SQL statement
        """

    def get_IsExists_string(self, query: IsExists) -> str:
        """Get the SQL of an existence query.

        :param query: the query
        :returns: the SQL statement
        """
        return self._get_structure_string("IsExists", query.structure.structure_name, query)

    @abstractmethod
    def get_Select_table_string(self, query: Select) -> str:
        """Get the SQL which reads rows of a table.

        :param query: the query
        :returns: the SQL statement
        """

    def get_Select_string(self, query: Select) -> str:
        """Get the SQL of a select query.

        :param query: the query
        :returns: the SQL statement
        """
        return self._get_structure_string("Select", query.structure.structure_name, query)

    @abstractmethod
    def get_SelectDistinct_table_string(self, query: SelectDistinct) -> str:
        """Get the SQL which reads distinct values of columns of a table.

        :param query: the query
        :returns: the SQL statement
        """

    def get_SelectDistinct_string(self, query: SelectDistinct) -> str:
        """Get the SQL of a select distinct query.

        :param query: the query
        :returns: the SQL statement
        """
        return self._get_structure_string("SelectDistinct", query.structure.structure_name, query)

    @abstractmethod
    def get_Truncate_table_string(self, query: Truncate) -> str:
        """Get the SQL which removes all rows of a table.

        :param query: the query
        :returns: the SQL statement
        """

    def get_Truncate_string(self, query: Truncate) -> str:
        """Get the SQL of a truncate query.

        :param query: the query
        :returns: the SQL statement
        """
        return self._get_structure_string("Truncate", query.structure.structure_name, query)

    @abstractmethod
    def get_Union_table_string(self, query: Union) -> str:
        """Get the SQL which combines the rows of several select queries.

        :param query: the query
        :returns: the SQL statement
        """

    def get_Union_string(self, query: Union) -> str:
        """Get the SQL of a union query.

        :param query: the query
        :returns: the SQL statement
        """
        return self._get_structure_string("Union", query.structure_list[0].structure_name, query)

    def get_query_string(self, query: Query) -> str:
        """Get the SQL of a query of any type.

        :param query: the query
        :returns: the SQL statement
        """
        query_string: str = getattr(self, f"get_{type(query).__name__}_string")(query)
        return query_string

    @abstractmethod
    def get_Update_table_string(self, query: Update) -> str:
        """Get the SQL which changes rows of a table.

        :param query: the query
        :returns: the SQL statement, with one placeholder per column
        """

    def get_Update_string(self, query: Update) -> str:
        """Get the SQL of an update query.

        :param query: the query
        :returns: the SQL statement
        """
        return self._get_structure_string("Update", query.structure.structure_name, query)

    def _get_structure_string(self, query_name: str, structure_name: str, query: Query) -> str:
        """Call the method for a type of query and a kind of structure."""
        structure_string: str = getattr(self, f"get_{query_name}_{structure_name}_string")(query)
        return structure_string
