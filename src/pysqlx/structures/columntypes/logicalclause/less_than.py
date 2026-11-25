"""Less than clause."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ...._compat import override
from .clause import Clause

if TYPE_CHECKING:
    from ..column import Column


class LessThan(Clause):
    """Clause which holds when a column is less than a value.

    :param lhs: the column on the left hand side
    :param rhs: the value, or the column, on the right hand side
    """

    def __init__(self, lhs: Column, rhs: Any) -> None:
        super().__init__()

        self.__lhs = lhs
        self.__rhs = rhs

    @property
    def lhs(self) -> Column:
        """Column on the left hand side."""
        return self.__lhs

    @property
    def rhs(self) -> Any:
        """Value, or column, on the right hand side."""
        return self.__rhs

    @override
    def get_not_clause(self) -> Clause:
        from .greater_than_equal import GreaterThanEqual

        return GreaterThanEqual(lhs=self.lhs, rhs=self.rhs)
