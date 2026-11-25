"""Integer column."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ...exceptions import InvalidArgumentError
from .column import Column

if TYPE_CHECKING:
    from ..table import Table

_valid_bytes = (
    1,
    2,
    4,
    8,
)


class IntegerColumn(Column):
    """Column which holds integers.

    :param column_name: the name of the column
    :param table: the table which the column belongs to
    :param n_bytes: the size of a value in bytes: 1, 2, 4 or 8
    :param default_value: the default value of the column, if any
    :param is_identity: whether the database generates the values of the
        column
    :param is_primary_key: whether the column is part of the primary key
    :param is_prevent_null: whether the column rejects null values
    :raises InvalidArgumentError: if an argument has an invalid type or value
    """

    def __init__(
        self,
        column_name: str,
        table: Table,
        n_bytes: int,
        default_value: Any,
        is_identity: bool,
        is_primary_key: bool,
        is_prevent_null: bool,
    ) -> None:
        super().__init__(
            column_name=column_name,
            table=table,
            default_value=default_value,
            is_identity=is_identity,
            is_primary_key=is_primary_key,
            is_prevent_null=is_prevent_null,
        )

        if not (isinstance(n_bytes, int)):
            raise InvalidArgumentError(f'invalid n_bytes "{n_bytes}"')
        if n_bytes not in _valid_bytes:
            raise InvalidArgumentError(f'invalid n_bytes "{n_bytes}"')

        self.__n_bytes = n_bytes

    @property
    def n_bytes(self) -> int:
        """Size of a value in bytes."""
        return self.__n_bytes
