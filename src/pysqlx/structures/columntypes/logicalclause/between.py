"""Between clause."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ...._compat import override
from .clause import Clause

if TYPE_CHECKING:
    from ..aggregate import Aggregate
    from ..column import Column


class Between(Clause):
    """Clause which holds when a column is between two values.

    :param column: the column, or the aggregate, to test
    :param value0: the lower bound
    :param value1: the upper bound
    """

    def __init__(self, column: Column | Aggregate, value0: Any, value1: Any) -> None:
        super().__init__()

        self.__column = column
        self.__value0 = value0
        self.__value1 = value1

    @property
    def column(self) -> Column | Aggregate:
        """Column, or aggregate, to test."""
        return self.__column

    @property
    def value0(self) -> Any:
        """Lower bound."""
        return self.__value0

    @property
    def value1(self) -> Any:
        """Upper bound."""
        return self.__value1

    @override
    def get_not_clause(self) -> Clause:
        from .not_between import NotBetween

        return NotBetween(column=self.__column, value0=self.__value0, value1=self.__value1)
