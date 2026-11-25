"""Is null clause."""

from __future__ import annotations

from typing import TYPE_CHECKING, override

from .clause import Clause

if TYPE_CHECKING:
    from ..column import Column


class IsNull(Clause):
    """Clause which holds when a column is null.

    :param column: the column to test
    """

    def __init__(self, column: Column) -> None:
        super().__init__()

        self.__column = column

    @property
    def column(self) -> Column:
        """Column to test."""
        return self.__column

    @override
    def get_not_clause(self) -> Clause:
        from .is_not_null import IsNotNull

        return IsNotNull(column=self.__column)
