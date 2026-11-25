"""Table."""

from __future__ import annotations

import weakref
from collections.abc import Iterable, Sequence
from typing import Any, Self

from ..exceptions import InvalidArgumentError
from .columntypes import (
    Aggregate,
    BinaryColumn,
    BooleanColumn,
    CharStringColumn,
    Column,
    DateColumn,
    DatetimeColumn,
    DecimalColumn,
    FloatColumn,
    IntegerColumn,
    TextColumn,
)
from .database import Database
from .foreign_key import ForeignKey
from .schema import Schema
from .structure import Structure


class Table(Structure):
    """Table of a database.

    A table is created without columns. Add them with the ``append_*_column``
    methods, which return the new column.

    :param table_name: the name of the table
    :param database: the database which the table belongs to, if any
    :param schema: the schema which the table belongs to, if any
    """

    def __init__(
        self,
        table_name: str,
        database: Database | None = None,
        schema: Schema | None = None,
    ) -> None:
        super().__init__(structure_name="table")

        self.__table_name = table_name
        self.__database = database
        self.__schema = schema

        self.__alias_name: str | None = None

        self.__cols: list[Column] = []
        self.__foreign_keys: list[ForeignKey] = []

    @property
    def table_name(self) -> str:
        """Name of the table."""
        return self.__table_name

    @property
    def database(self) -> Database | None:
        """Database which the table belongs to, or ``None``."""
        return self.__database

    @property
    def schema(self) -> Schema | None:
        """Schema which the table belongs to, or ``None``."""
        return self.__schema

    def _get_self(self) -> Table:
        """Give the table itself, when reached through the weak reference of a column."""
        return self

    @property
    def alias_name(self) -> str | None:
        """Name which stands for the table in a select query, or ``None``."""
        return self.__alias_name

    def alias(self, alias_name: str) -> Table:
        """Create a second reference to the table, under another name.

        The alias has copies of the columns of the table, in the same order.
        Use it to join a table to itself: the table and its alias are two
        tables to a select query.

        :param alias_name: the name which stands for the table in the query
        :returns: the alias, with its own columns
        :raises InvalidArgumentError: if the name is empty
        """
        if not isinstance(alias_name, str) or alias_name == "":
            raise InvalidArgumentError(f'invalid alias_name "{alias_name}"')

        table = Table(table_name=self.table_name, database=self.database, schema=self.schema)
        table.__alias_name = alias_name
        table.__cols = [column.copy_to(weakref.proxy(table)) for column in self.__cols]

        return table

    @property
    def columns(self) -> list[Column]:
        """Columns of the table, in the order in which they were added."""
        return self.__cols

    @property
    def foreign_keys(self) -> list[ForeignKey]:
        """Foreign keys of the table, in the order in which they were added."""
        return self.__foreign_keys

    def clear_columns(self) -> Self:
        """Remove all columns and foreign keys of the table.

        :returns: the table itself
        """
        self.__cols = []
        self.__foreign_keys = []
        return self

    def count(self) -> Aggregate:
        """Create an aggregate which counts rows.

        :returns: the aggregate, to read with a select query
        """
        return Aggregate(function_name="COUNT", column=None)

    def append_foreign_key(
        self,
        columns: Sequence[Column],
        reference_columns: Sequence[Column],
    ) -> ForeignKey:
        """Make columns of the table refer to the rows of another table.

        The foreign key takes effect when the table is created.

        :param columns: the columns of this table which refer to the other
            table
        :param reference_columns: the columns of the other table which they
            refer to, in the same order
        :returns: the new foreign key
        :raises InvalidArgumentError: if the columns are invalid
        """
        for column in columns:
            if not any(column is col for col in self.__cols):
                raise InvalidArgumentError("invalid columns")

        foreign_key = ForeignKey(columns=columns, reference_columns=reference_columns)
        self.__foreign_keys.append(foreign_key)
        return foreign_key

    def append_column(self, col_obj: Column) -> Column:
        """Add a column object to the table.

        :param col_obj: the column, which must have been created for this
            table
        :returns: the column
        :raises InvalidArgumentError: if the object is not a column or
            belongs to another table
        """
        if not isinstance(col_obj, Column):
            raise InvalidArgumentError("invalid column object")

        if col_obj.table.table_name != self.table_name:
            raise InvalidArgumentError("column belongs to another table")

        self.__cols.append(col_obj)

        return col_obj

    def append_columns(self, col_objs: Iterable[Column]) -> Self:
        """Add several column objects to the table.

        :param col_objs: the columns, which must have been created for this
            table
        :returns: the table itself
        """
        for obj in col_objs:
            self.append_column(col_obj=obj)
        return self

    def append_char_string_column(
        self,
        column_name: str,
        is_unicode: bool = False,
        is_fixed: bool = False,
        size: int = 255,
        default_value: Any = None,
        is_primary_key: bool = False,
        is_required: bool = False,
    ) -> CharStringColumn:
        """Add a column which holds character strings of a limited size.

        :param column_name: the name of the column
        :param is_unicode: whether the column holds Unicode characters
        :param is_fixed: whether all values have the same size
        :param size: the maximum number of characters of a value
        :param default_value: the default value of the column, if any
        :param is_primary_key: whether the column is part of the primary key
        :param is_required: whether the column rejects null values
        :returns: the new column
        """
        column = CharStringColumn(
            column_name=column_name,
            table=weakref.proxy(self),
            is_unicode=is_unicode,
            is_fixed=is_fixed,
            size=size,
            default_value=default_value,
            is_primary_key=is_primary_key,
            is_required=is_required,
        )
        self.append_column(col_obj=column)
        return column

    def append_datetime_column(
        self,
        column_name: str,
        default_value: Any = None,
        is_primary_key: bool = False,
        is_required: bool = False,
    ) -> DatetimeColumn:
        """Add a column which holds dates with a time.

        :param column_name: the name of the column
        :param default_value: the default value of the column, if any
        :param is_primary_key: whether the column is part of the primary key
        :param is_required: whether the column rejects null values
        :returns: the new column
        """
        column = DatetimeColumn(
            column_name=column_name,
            table=weakref.proxy(self),
            default_value=default_value,
            is_primary_key=is_primary_key,
            is_required=is_required,
        )
        self.append_column(col_obj=column)
        return column

    def append_float_column(
        self,
        column_name: str,
        is_double: bool = True,
        default_value: Any = None,
        is_primary_key: bool = False,
        is_required: bool = False,
    ) -> FloatColumn:
        """Add a column which holds floating point numbers.

        :param column_name: the name of the column
        :param is_double: whether the values have double precision
        :param default_value: the default value of the column, if any
        :param is_primary_key: whether the column is part of the primary key
        :param is_required: whether the column rejects null values
        :returns: the new column
        """
        column = FloatColumn(
            column_name=column_name,
            table=weakref.proxy(self),
            is_double=is_double,
            default_value=default_value,
            is_primary_key=is_primary_key,
            is_required=is_required,
        )
        self.append_column(col_obj=column)
        return column

    def append_integer_column(
        self,
        column_name: str,
        n_bytes: int = 4,
        default_value: Any = None,
        is_identity: bool = False,
        is_primary_key: bool = False,
        is_required: bool = False,
    ) -> IntegerColumn:
        """Add a column which holds integers.

        :param column_name: the name of the column
        :param n_bytes: the size of a value in bytes: 1, 2, 4 or 8
        :param default_value: the default value of the column, if any
        :param is_identity: whether the database generates the values of the
            column
        :param is_primary_key: whether the column is part of the primary key
        :param is_required: whether the column rejects null values
        :returns: the new column
        """
        column = IntegerColumn(
            column_name=column_name,
            table=weakref.proxy(self),
            n_bytes=n_bytes,
            default_value=default_value,
            is_identity=is_identity,
            is_primary_key=is_primary_key,
            is_required=is_required,
        )
        self.append_column(col_obj=column)
        return column

    def append_text_column(
        self,
        column_name: str,
        is_unicode: bool = False,
        default_value: Any = None,
        is_primary_key: bool = False,
        is_required: bool = False,
    ) -> TextColumn:
        """Add a column which holds text of unlimited size.

        :param column_name: the name of the column
        :param is_unicode: whether the column holds Unicode characters
        :param default_value: the default value of the column, if any
        :param is_primary_key: whether the column is part of the primary key
        :param is_required: whether the column rejects null values
        :returns: the new column
        """
        column = TextColumn(
            column_name=column_name,
            table=weakref.proxy(self),
            is_unicode=is_unicode,
            default_value=default_value,
            is_primary_key=is_primary_key,
            is_required=is_required,
        )
        self.append_column(col_obj=column)
        return column

    def append_boolean_column(
        self,
        column_name: str,
        default_value: Any = None,
        is_primary_key: bool = False,
        is_required: bool = False,
    ) -> BooleanColumn:
        """Add a column which holds booleans.

        :param column_name: the name of the column
        :param default_value: the default value of the column, if any
        :param is_primary_key: whether the column is part of the primary key
        :param is_required: whether the column rejects null values
        :returns: the new column
        """
        column = BooleanColumn(
            column_name=column_name,
            table=weakref.proxy(self),
            default_value=default_value,
            is_primary_key=is_primary_key,
            is_required=is_required,
        )
        self.append_column(col_obj=column)
        return column

    def append_date_column(
        self,
        column_name: str,
        default_value: Any = None,
        is_primary_key: bool = False,
        is_required: bool = False,
    ) -> DateColumn:
        """Add a column which holds dates without a time.

        :param column_name: the name of the column
        :param default_value: the default value of the column, if any
        :param is_primary_key: whether the column is part of the primary key
        :param is_required: whether the column rejects null values
        :returns: the new column
        """
        column = DateColumn(
            column_name=column_name,
            table=weakref.proxy(self),
            default_value=default_value,
            is_primary_key=is_primary_key,
            is_required=is_required,
        )
        self.append_column(col_obj=column)
        return column

    def append_decimal_column(
        self,
        column_name: str,
        precision: int = 18,
        scale: int = 2,
        default_value: Any = None,
        is_primary_key: bool = False,
        is_required: bool = False,
    ) -> DecimalColumn:
        """Add a column which holds decimal numbers with a fixed number of digits.

        :param column_name: the name of the column
        :param precision: the total number of digits
        :param scale: the number of digits after the decimal point
        :param default_value: the default value of the column, if any
        :param is_primary_key: whether the column is part of the primary key
        :param is_required: whether the column rejects null values
        :returns: the new column
        """
        column = DecimalColumn(
            column_name=column_name,
            table=weakref.proxy(self),
            precision=precision,
            scale=scale,
            default_value=default_value,
            is_primary_key=is_primary_key,
            is_required=is_required,
        )
        self.append_column(col_obj=column)
        return column

    def append_binary_column(
        self,
        column_name: str,
        default_value: Any = None,
        is_primary_key: bool = False,
        is_required: bool = False,
    ) -> BinaryColumn:
        """Add a column which holds binary data of unlimited size.

        :param column_name: the name of the column
        :param default_value: the default value of the column, if any
        :param is_primary_key: whether the column is part of the primary key
        :param is_required: whether the column rejects null values
        :returns: the new column
        """
        column = BinaryColumn(
            column_name=column_name,
            table=weakref.proxy(self),
            default_value=default_value,
            is_primary_key=is_primary_key,
            is_required=is_required,
        )
        self.append_column(col_obj=column)
        return column
