"""Decimal column."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ...exceptions import InvalidArgumentError
from .column import Column

if TYPE_CHECKING:
    from ..table import Table


class DecimalColumn(Column):
    """Column which holds decimal numbers with a fixed number of digits.

    :param column_name: the name of the column
    :param table: the table which the column belongs to
    :param precision: the total number of digits
    :param scale: the number of digits after the decimal point
    :param default_value: the default value of the column, if any
    :param is_primary_key: whether the column is part of the primary key
    :param is_prevent_null: whether the column rejects null values
    :raises InvalidArgumentError: if the precision or the scale is invalid
    """

    def __init__(
        self,
        column_name: str,
        table: Table,
        precision: int,
        scale: int,
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

        if not isinstance(precision, int) or precision < 1:
            raise InvalidArgumentError(f'invalid precision "{precision}"')

        if not isinstance(scale, int) or scale < 0 or scale > precision:
            raise InvalidArgumentError(f'invalid scale "{scale}"')

        self.__precision = precision
        self.__scale = scale

    @property
    def precision(self) -> int:
        """Total number of digits."""
        return self.__precision

    @property
    def scale(self) -> int:
        """Number of digits after the decimal point."""
        return self.__scale
