"""Floating point column."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .column import Column

if TYPE_CHECKING:
    from ..table import Table


class FloatColumn(Column):
    """Column which holds floating point numbers.

    :param column_name: the name of the column
    :param table: the table which the column belongs to
    :param is_double: whether the values have double precision
    :param default_value: the default value of the column, if any
    :param is_primary_key: whether the column is part of the primary key
    :param is_prevent_null: whether the column rejects null values
    """

    def __init__(
        self,
        column_name: str,
        table: Table,
        is_double: bool,
        default_value: Any,
        is_primary_key: bool,
        is_prevent_null: bool,
    ) -> None:
        super().__init__(
            column_name=column_name,
            table=table,
            default_value=default_value,
            is_identity=False,
            is_primary_key=is_primary_key,
            is_prevent_null=is_prevent_null,
        )

        assert isinstance(is_double, bool)

        self.__is_double = is_double

    @property
    def is_double(self) -> bool:
        """Whether the values have double precision."""
        return self.__is_double
