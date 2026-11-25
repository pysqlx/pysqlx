"""Text column."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ...exceptions import InvalidArgumentError
from .column import Column

if TYPE_CHECKING:
    from ..table import Table


class TextColumn(Column):
    """Column which holds text of unlimited size.

    :param column_name: the name of the column
    :param table: the table which the column belongs to
    :param is_unicode: whether the column holds Unicode characters
    :param default_value: the default value of the column, if any
    :param is_primary_key: whether the column is part of the primary key
    :param is_required: whether the column rejects null values
    :raises InvalidArgumentError: if an argument has an invalid type or value
    """

    def __init__(
        self,
        column_name: str,
        table: Table,
        is_unicode: bool,
        default_value: Any,
        is_primary_key: bool,
        is_required: bool,
    ) -> None:
        super().__init__(
            column_name=column_name,
            table=table,
            default_value=default_value,
            is_identity=False,
            is_primary_key=is_primary_key,
            is_required=is_required,
        )

        if not (isinstance(is_unicode, bool)):
            raise InvalidArgumentError(f'invalid is_unicode "{is_unicode}"')

        self.__is_unicode = is_unicode

    @property
    def is_unicode(self) -> bool:
        """Whether the column holds Unicode characters."""
        return self.__is_unicode
