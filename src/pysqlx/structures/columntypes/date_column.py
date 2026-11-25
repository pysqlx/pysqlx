"""Date column."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .column import Column

if TYPE_CHECKING:
    from ..table import Table


class DateColumn(Column):
    """Column which holds dates without a time.

    :param column_name: the name of the column
    :param table: the table which the column belongs to
    :param default_value: the default value of the column, if any
    :param is_primary_key: whether the column is part of the primary key
    :param is_required: whether the column rejects null values
    """

    def __init__(
        self,
        column_name: str,
        table: Table,
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
