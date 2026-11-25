"""Is not null clause."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ...._compat import override
from .clause import Clause

if TYPE_CHECKING:
    from ..column import Column


class IsNotNull(Clause):
    """Clause which holds when a column is not null.

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
        from .is_null import IsNull

        return IsNull(column=self.__column)
