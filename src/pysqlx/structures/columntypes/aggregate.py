"""Aggregate of a column."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ...exceptions import InvalidArgumentError
from .logicalclause import (
    Between,
    Equal,
    GreaterThan,
    GreaterThanEqual,
    LessThan,
    LessThanEqual,
    NotEqual,
)

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

    Comparing an aggregate with a value using ``==``, ``!=``, ``>``, ``>=``,
    ``<`` or ``<=`` creates a clause to use as the ``having`` of a select
    query, which keeps the groups of rows whose aggregate satisfies it.

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

    def __hash__(self) -> int:
        return id(self)

    def __eq__(self, other: object) -> Equal:  # type: ignore[override]
        return Equal(lhs=self, rhs=other)

    def __ne__(self, other: object) -> NotEqual:  # type: ignore[override]
        return NotEqual(lhs=self, rhs=other)

    def __gt__(self, other: Any) -> GreaterThan:
        return GreaterThan(lhs=self, rhs=other)

    def __ge__(self, other: Any) -> GreaterThanEqual:
        return GreaterThanEqual(lhs=self, rhs=other)

    def __lt__(self, other: Any) -> LessThan:
        return LessThan(lhs=self, rhs=other)

    def __le__(self, other: Any) -> LessThanEqual:
        return LessThanEqual(lhs=self, rhs=other)

    def is_between(self, value0: Any, value1: Any) -> Between:
        """Create a clause which holds when the aggregate is between two values.

        :param value0: the lower bound
        :param value1: the upper bound
        :returns: the clause
        """
        return Between(column=self, value0=value0, value1=value1)
