"""Aggregate of a column."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ...exceptions import InvalidArgumentError

if TYPE_CHECKING:
    from .column import Column

_function_names = (
    "AVG",
    "COUNT",
    "MAX",
    "MIN",
    "SUM",
)


class Aggregate:
    """Value computed from a column over several rows, such as a sum.

    Aggregates are created by the methods of a column, such as
    ``total.sum()``, and by ``Table.count()``. They are read by a select
    query, in place of a column.

    :param function_name: the name of the function: ``"AVG"``, ``"COUNT"``,
        ``"MAX"``, ``"MIN"`` or ``"SUM"``
    :param column: the column to aggregate, or ``None`` to count rows
    :raises InvalidArgumentError: if the function is unknown, or if a
        function other than ``"COUNT"`` is given no column
    """

    def __init__(self, function_name: str, column: Column | None) -> None:
        if function_name not in _function_names:
            raise InvalidArgumentError(f'invalid aggregate function "{function_name}"')

        if column is None and function_name != "COUNT":
            raise InvalidArgumentError(f'aggregate function "{function_name}" needs a column')

        self.__function_name = function_name
        self.__column = column

    @property
    def function_name(self) -> str:
        """Name of the function."""
        return self.__function_name

    @property
    def column(self) -> Column | None:
        """Column to aggregate, or ``None`` when counting rows."""
        return self.__column
