"""Character string column."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ...exceptions import InvalidArgumentError
from .column import Column

if TYPE_CHECKING:
    from ..table import Table


class CharStringColumn(Column):
    """Column which holds character strings of a limited size.

    :param column_name: the name of the column
    :param table: the table which the column belongs to
    :param is_unicode: whether the column holds Unicode characters
    :param is_fixed: whether all values have the same size
    :param size: the maximum number of characters of a value
    :param default_value: the default value of the column, if any
    :param is_primary_key: whether the column is part of the primary key
    :param is_prevent_null: whether the column rejects null values
    :raises InvalidArgumentError: if an argument has an invalid type or value
    """

    def __init__(
        self,
        column_name: str,
        table: Table,
        is_unicode: bool,
        is_fixed: bool,
        size: int,
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

        if not (isinstance(is_unicode, bool)):
            raise InvalidArgumentError(f'invalid is_unicode "{is_unicode}"')
        if not (isinstance(is_fixed, bool)):
            raise InvalidArgumentError(f'invalid is_fixed "{is_fixed}"')
        if not (isinstance(size, int)):
            raise InvalidArgumentError(f'invalid size "{size}"')

        self.__is_unicode = is_unicode
        self.__is_fixed = is_fixed
        self.__size = size

    @property
    def is_unicode(self) -> bool:
        """Whether the column holds Unicode characters."""
        return self.__is_unicode

    @property
    def is_fixed(self) -> bool:
        """Whether all values have the same size."""
        return self.__is_fixed

    @property
    def size(self) -> int:
        """Maximum number of characters of a value."""
        return self.__size
