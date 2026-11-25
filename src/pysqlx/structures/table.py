"""Table."""

import weakref
from collections.abc import Iterable
from typing import Any, Self

from .columntypes import (
    CharStringColumn,
    Column,
    DatetimeColumn,
    FloatColumn,
    IntegerColumn,
    TextColumn,
)
from .database import Database
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

        self.__cols: list[Column] = []

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

    @property
    def columns(self) -> list[Column]:
        """Columns of the table, in the order in which they were added."""
        return self.__cols

    def clear_columns(self) -> Self:
        """Remove all columns of the table.

        :returns: the table itself
        """
        self.__cols = []
        return self

    def append_column(self, col_obj: Column) -> Column:
        """Add a column object to the table.

        :param col_obj: the column, which must have been created for this
            table
        :returns: the column
        :raises RuntimeError: if the object is not a column or belongs to
            another table
        """
        if not isinstance(col_obj, Column):
            raise RuntimeError("invalid column object")

        if col_obj.table.table_name is not self.table_name:
            raise RuntimeError("column belongs to another table")

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
        is_prevent_null: bool = False,
    ) -> CharStringColumn:
        """Add a column which holds character strings of a limited size.

        :param column_name: the name of the column
        :param is_unicode: whether the column holds Unicode characters
        :param is_fixed: whether all values have the same size
        :param size: the maximum number of characters of a value
        :param default_value: the default value of the column, if any
        :param is_primary_key: whether the column is part of the primary key
        :param is_prevent_null: whether the column rejects null values
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
            is_prevent_null=is_prevent_null,
        )
        self.append_column(col_obj=column)
        return column

    def append_datetime_column(
        self,
        column_name: str,
        default_value: Any = None,
        is_primary_key: bool = False,
        is_prevent_null: bool = False,
    ) -> DatetimeColumn:
        """Add a column which holds dates with a time.

        :param column_name: the name of the column
        :param default_value: the default value of the column, if any
        :param is_primary_key: whether the column is part of the primary key
        :param is_prevent_null: whether the column rejects null values
        :returns: the new column
        """
        column = DatetimeColumn(
            column_name=column_name,
            table=weakref.proxy(self),
            default_value=default_value,
            is_primary_key=is_primary_key,
            is_prevent_null=is_prevent_null,
        )
        self.append_column(col_obj=column)
        return column

    def append_float_column(
        self,
        column_name: str,
        is_double: bool = True,
        default_value: Any = None,
        is_primary_key: bool = False,
        is_prevent_null: bool = False,
    ) -> FloatColumn:
        """Add a column which holds floating point numbers.

        :param column_name: the name of the column
        :param is_double: whether the values have double precision
        :param default_value: the default value of the column, if any
        :param is_primary_key: whether the column is part of the primary key
        :param is_prevent_null: whether the column rejects null values
        :returns: the new column
        """
        column = FloatColumn(
            column_name=column_name,
            table=weakref.proxy(self),
            is_double=is_double,
            default_value=default_value,
            is_primary_key=is_primary_key,
            is_prevent_null=is_prevent_null,
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
        is_prevent_null: bool = False,
    ) -> IntegerColumn:
        """Add a column which holds integers.

        :param column_name: the name of the column
        :param n_bytes: the size of a value in bytes: 1, 2, 4 or 8
        :param default_value: the default value of the column, if any
        :param is_identity: whether the database generates the values of the
            column
        :param is_primary_key: whether the column is part of the primary key
        :param is_prevent_null: whether the column rejects null values
        :returns: the new column
        """
        column = IntegerColumn(
            column_name=column_name,
            table=weakref.proxy(self),
            n_bytes=n_bytes,
            default_value=default_value,
            is_identity=is_identity,
            is_primary_key=is_primary_key,
            is_prevent_null=is_prevent_null,
        )
        self.append_column(col_obj=column)
        return column

    def append_text_column(
        self,
        column_name: str,
        is_unicode: bool = False,
        default_value: Any = None,
        is_primary_key: bool = False,
        is_prevent_null: bool = False,
    ) -> TextColumn:
        """Add a column which holds text of unlimited size.

        :param column_name: the name of the column
        :param is_unicode: whether the column holds Unicode characters
        :param default_value: the default value of the column, if any
        :param is_primary_key: whether the column is part of the primary key
        :param is_prevent_null: whether the column rejects null values
        :returns: the new column
        """
        column = TextColumn(
            column_name=column_name,
            table=weakref.proxy(self),
            is_unicode=is_unicode,
            default_value=default_value,
            is_primary_key=is_primary_key,
            is_prevent_null=is_prevent_null,
        )
        self.append_column(col_obj=column)
        return column
